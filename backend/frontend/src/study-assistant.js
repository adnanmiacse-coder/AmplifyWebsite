import { loadEnvConfig, getGroqKeys, getOpenRouterKeys, getGroqBase, getOpenRouterBase, getViteEnv } from './env-config.js';

let _config = {};
const _env = getViteEnv();
loadEnvConfig().then(cfg => { _config = cfg; });

function groqKeys() { return getGroqKeys(_config, _env); }
function openRouterKeys() { return getOpenRouterKeys(_config, _env); }
function groqBase() { return getGroqBase(_config, _env); }
function openRouterBase() { return getOpenRouterBase(_config, _env); }const NUMERIC_FORMAT_INSTRUCTION =
  'CRITICAL NUMERIC FORMATTING RULE: Do not ever mention or use any fractional digits or fraction notation (such as 1/2, 3/4, or fractions). If a fractional digit appears, ensure it is converted to and written as a decimal number (for example, write 1/2 as 0.5, 3/4 as 0.75, 1/4 as 0.25). Never output fractions or fractional digits; express all fractional values strictly as decimal numbers throughout your response.';

/**
 * Groq chat completion for PDF Tutor, using the same model family as other pages.
 */
async function felcloudChatCompletion(messages, { tier = 'compact', maxTokens = 700, temperature = 0.35, signal } = {}) {
  await loadEnvConfig().then(cfg => { _config = cfg; });

  const isFast = tier === 'compact';
  // Standard Groq models that are reliably available
  const gModels = isFast
    ? ['llama-3.1-8b-instant', 'llama-3.3-70b-versatile']
    : ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'];

  // OpenRouter fallback models (using rotated keys)
  const orModels = isFast
    ? ['openrouter/free', 'google/gemini-2.0-flash-lite-001']
    : ['openrouter/free', 'google/gemini-2.0-flash-001', 'qwen/qwen-2.5-72b-instruct'];

  const systemMessage = {
    role: 'system',
    content: NUMERIC_FORMAT_INSTRUCTION,
  };

  const finalMessages = [systemMessage, ...messages];

  // 1. Try Groq first
  const gKeys = groqKeys();
  if (gKeys.length > 0) {
    for (const model of gModels) {
      for (const key of gKeys) {
        try {
          const res = await fetch(`${groqBase()}/chat/completions`, {
            method: 'POST',
            signal,
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${key}`,
            },
            body: JSON.stringify({
              model,
              messages: finalMessages,
              max_tokens: maxTokens,
              temperature,
            }),
          });
          if (res.ok) {
            const data = await res.json();
            const reply = data.choices?.[0]?.message?.content?.trim();
            if (reply) return reply;
          }
          if (res.status === 429) {
            await new Promise(r => setTimeout(r, 400));
          }
        } catch (err) {
          if (err.name === 'AbortError') throw err;
        }
      }
    }
  }

  // 2. Fallback to OpenRouter
  const orKeys = openRouterKeys();
  if (orKeys.length > 0) {
    for (const model of orModels) {
      for (let key of orKeys) {
        try {
          const res = await fetch(`${openRouterBase()}/chat/completions`, {
            method: 'POST',
            signal,
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${key}`,
              'HTTP-Referer': typeof window !== 'undefined' ? window.location.origin : 'http://localhost',
              'X-Title': 'Amplify PDF Tutor',
            },
            body: JSON.stringify({
              model,
              messages: finalMessages,
              max_tokens: maxTokens,
              temperature,
            }),
          });
          if (res.ok) {
            const data = await res.json();
            const reply = data.choices?.[0]?.message?.content?.trim();
            if (reply) return reply;
          }
          if (res.status === 429) {
            await new Promise(r => setTimeout(r, 400));
          }
        } catch (err) {
          if (err.name === 'AbortError') throw err;
        }
      }
    }
  }

  throw new Error('All AI providers are currently busy or unavailable. Please try again shortly.');
}

const MAX_FILE_BYTES = 20 * 1024 * 1024;
const MAX_PAGES = 35;
const FAST_MODEL = 'compact';
const REASONING_MODELS = ['midsize'];
const MODEL_TIMEOUT_MS = 90_000;

const elements = {
  dropzone: document.getElementById('dropzone'),
  pdfFile: document.getElementById('pdfFile'),
  fileStatus: document.getElementById('fileStatus'),
  progressWrap: document.getElementById('progressWrap'),
  progressFill: document.getElementById('progressFill'),
  progressText: document.getElementById('progressText'),
  diagnosticForm: document.getElementById('diagnosticForm'),
  startLesson: document.getElementById('startLesson'),
  profileCard: document.getElementById('profileCard'),
  profileSummary: document.getElementById('profileSummary'),
  editProfile: document.getElementById('editProfile'),
  levelSelect: document.getElementById('levelSelect'),
  styleSelect: document.getElementById('styleSelect'),
  languageSelect: document.getElementById('languageSelect'),
  priorKnowledge: document.getElementById('priorKnowledge'),
  chatMessages: document.getElementById('chatMessages'),
  tutorStatus: document.getElementById('tutorStatus'),
  chatForm: document.getElementById('chatForm'),
  messageInput: document.getElementById('messageInput'),
  sendButton: document.getElementById('sendButton'),
};

let pdfPages = [];
let conversation = [];
let busy = false;
let readingPdf = false;
let learningProfile = null;
let ocrWorker = null;
let ocrWorkerLanguage = '';
let activeSpeechButton = null;
let activeUtterance = null;
let activeSpeechAudio = null;
let activeSpeechUrl = '';
let activeSpeechController = null;

const SPEECH_LANGUAGES = {
  English: { locale: 'en-US', voices: ['en-US', 'en-GB', 'en'], azureVoice: 'en-US-JennyNeural' },
  Bangla: { locale: 'bn-BD', voices: ['bn-BD', 'bn-IN', 'bn', 'bengali'], azureVoice: 'bn-BD-NabanitaNeural' },
  Bengali: { locale: 'bn-BD', voices: ['bn-BD', 'bn-IN', 'bn', 'bengali'], azureVoice: 'bn-BD-NabanitaNeural' },
  French: { locale: 'fr-FR', voices: ['fr-FR', 'fr-CA', 'fr'], azureVoice: 'fr-FR-DeniseNeural' },
  Arabic: { locale: 'ar', voices: ['ar', 'ar-SA', 'ar-EG'], azureVoice: 'ar-SA-ZariyahNeural' },
  'Moroccan Darija': { locale: 'ar-MA', voices: ['ar-MA', 'ar'], azureVoice: 'ar-MA-MounaNeural' },
};

function resetSpeechButton() {
  if (activeSpeechButton) {
    activeSpeechButton.textContent = activeSpeechButton.dataset.listenLabel;
    activeSpeechButton.setAttribute('aria-pressed', 'false');
  }
  if (activeSpeechAudio) {
    activeSpeechAudio.pause();
    activeSpeechAudio.src = '';
  }
  if (activeSpeechUrl) URL.revokeObjectURL(activeSpeechUrl);
  activeSpeechAudio = null;
  activeSpeechUrl = '';
  activeSpeechController = null;
  activeSpeechButton = null;
  activeUtterance = null;
}

function stopSpeech() {
  globalThis.speechSynthesis?.cancel();
  activeSpeechController?.abort();
  resetSpeechButton();
}

function findSpeechVoice(language) {
  const settings = SPEECH_LANGUAGES[language] || SPEECH_LANGUAGES.English;
  const voices = globalThis.speechSynthesis?.getVoices() || [];
  const normalized = voice => (voice.lang || '').replaceAll('_', '-').toLowerCase();

  if (language === 'Bangla' || language === 'Bengali') {
    if (typeof window !== 'undefined' && window.AmplifyVoice) {
      const best = window.AmplifyVoice.getBestVoices('bn');
      if (best.length) return best[0];
    }
  }

  for (const preferred of settings.voices) {
    const match = voices.find(voice => normalized(voice).includes(preferred.toLowerCase()));
    if (match) return match;
  }
  const languageCode = settings.locale.split('-')[0].toLowerCase();
  return voices.find(voice => normalized(voice).split('-')[0] === languageCode);
}

function createSpeechButton(text, language) {
  const settings = SPEECH_LANGUAGES[language] || SPEECH_LANGUAGES.English;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'speech-button';
  button.dataset.listenLabel = `🔊 Listen · ${language}`;
  button.textContent = button.dataset.listenLabel;
  button.setAttribute('aria-label', `Read this response aloud in ${language}`);
  button.setAttribute('aria-pressed', 'false');
  button.addEventListener('click', async () => {
    if (activeSpeechButton === button) {
      stopSpeech();
      return;
    }

    stopSpeech();
    activeSpeechButton = button;
    button.textContent = 'Preparing audio…';
    button.setAttribute('aria-pressed', 'true');

    const controller = new AbortController();
    activeSpeechController = controller;

    // Try Azure TTS if keys are present in environment
    const env = window.AMPLIFY_ENV || _config || {};
    const azureKey = env.AZURE_SPEECH_KEY || env.VITE_AZURE_SPEECH_KEY || '';
    const azureRegion = env.AZURE_SPEECH_REGION || env.VITE_AZURE_SPEECH_REGION || 'southeastasia';

    if (azureKey) {
      try {
        const azureVoice = settings.azureVoice || 'en-US-JennyNeural';
        const ssml = `<speak version='1.0' xml:lang='${settings.locale}'><voice name='${azureVoice}'><prosody rate='-2%' pitch='+1%'>${text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</prosody></voice></speak>`;

        const res = await fetch(`https://${azureRegion}.tts.speech.microsoft.com/cognitiveservices/v1`, {
          method: 'POST',
          headers: {
            'Ocp-Apim-Subscription-Key': azureKey,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
          },
          body: ssml,
          signal: controller.signal,
        });

        if (res.ok) {
          const audioBlob = await res.blob();
          if (audioBlob.size > 0 && !controller.signal.aborted) {
            activeSpeechUrl = URL.createObjectURL(audioBlob);
            activeSpeechAudio = new Audio(activeSpeechUrl);
            button.textContent = '⏹ Stop reading';
            await new Promise((resolve, reject) => {
              activeSpeechAudio.onended = resolve;
              activeSpeechAudio.onerror = () => reject(new Error('Audio playback failed.'));
              activeSpeechAudio.play().catch(reject);
            });
            if (activeSpeechButton === button) resetSpeechButton();
            return;
          }
        }
      } catch (err) {
        if (controller.signal.aborted) return;
        console.warn('[PDF Tutor] Azure TTS threw, falling back to Web Speech:', err.message);
      }
    }

    // Fallback to browser SpeechSynthesis
    if (controller.signal.aborted) return;
    if (activeSpeechButton === button) resetSpeechButton();

    if (!globalThis.speechSynthesis || typeof globalThis.SpeechSynthesisUtterance !== 'function') {
      elements.tutorStatus.textContent = 'Voice playback is unavailable in this browser.';
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = settings.locale;
    utterance.rate = 0.95;
    const voice = findSpeechVoice(language);
    if (voice) utterance.voice = voice;
    activeSpeechButton = button;
    activeUtterance = utterance;
    button.textContent = '⏹ Stop reading';
    button.setAttribute('aria-pressed', 'true');
    const finish = () => {
      if (activeUtterance === utterance) resetSpeechButton();
    };
    utterance.onend = finish;
    utterance.onerror = event => {
      if (activeUtterance !== utterance) return;
      finish();
      if (event.error !== 'canceled' && event.error !== 'interrupted') {
        elements.tutorStatus.textContent = `Speech playback failed (${event.error}).`;
      }
    };
    try {
      globalThis.speechSynthesis.speak(utterance);
    } catch (speechError) {
      resetSpeechButton();
      elements.tutorStatus.textContent = `Speech playback could not start: ${speechError.message}`;
    }
  });
  return button;
}

function setStatus(message, kind = '') {
  elements.fileStatus.textContent = message;
  elements.fileStatus.className = `file-status ${kind}`.trim();
}

function setProgress(percent, message) {
  elements.progressWrap.classList.remove('hidden');
  elements.progressFill.style.width = `${percent}%`;
  elements.progressText.textContent = message;
}

async function requestModel(model, messages, { maxTokens = 700, temperature = 0.35 } = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), MODEL_TIMEOUT_MS);
  try {
    const content = await felcloudChatCompletion(messages, {
      tier: model === 'compact' ? 'compact' : 'midsize',
      maxTokens,
      temperature,
      signal: controller.signal,
    });
    if (!content.trim()) throw new Error('AI returned an empty tutor response.');
    return content.replace(/<think[^>]*>[\s\S]*?<\/think>/gi, '').trim();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error(`The AI model request timed out after ${MODEL_TIMEOUT_MS / 1000} seconds.`);
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

async function requestWithFallback(models, messages, options) {
  let lastError;
  for (const model of models) {
    try {
      return await requestModel(model, messages, options);
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error('No AI model is available.');
}

function getOcrLanguage() {
  switch (elements.languageSelect.value) {
    case 'Bangla':
    case 'Bengali': return 'ben';
    case 'French': return 'fra';
    case 'Arabic': return 'ara';
    case 'Moroccan Darija': return 'ara+fra';
    default: return 'eng';
  }
}

async function getOcrWorker(language) {
  if (!globalThis.Tesseract?.createWorker) {
    throw new Error('The local OCR engine did not load. Check your connection and reload the page.');
  }
  if (ocrWorker && ocrWorkerLanguage !== language) {
    await ocrWorker.terminate();
    ocrWorker = null;
  }
  if (!ocrWorker) {
    setStatus(`Loading local ${language.toUpperCase()} OCR…`);
    ocrWorker = await Tesseract.createWorker(language, 1, {
      logger: message => {
        if (message.status === 'recognizing text') {
          setStatus(`Reading scanned page… ${Math.round(message.progress * 100)}%`);
        }
      },
    });
    ocrWorkerLanguage = language;
  }
  return ocrWorker;
}

async function ocrPage(page, pageNumber, language) {
  const viewport = page.getViewport({ scale: 1.5 });
  const canvas = document.createElement('canvas');
  canvas.width = viewport.width;
  canvas.height = viewport.height;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('This browser could not prepare a PDF page for OCR.');
  try {
    setStatus(`Preparing scanned page ${pageNumber} for local OCR…`);
    await page.render({ canvasContext: context, viewport }).promise;
    const worker = await getOcrWorker(language);
    setStatus(`Running local OCR on scanned page ${pageNumber}…`);
    const { data } = await worker.recognize(canvas);
    return data.text.trim();
  } finally {
    canvas.width = 0;
    canvas.height = 0;
  }
}

async function readPdf(file) {
  if (!file || (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf'))) {
    throw new Error('Choose a PDF file to start.');
  }
  if (file.size > MAX_FILE_BYTES) throw new Error('This PDF is larger than 20 MB. Choose a smaller file.');
  if (!globalThis.pdfjsLib) throw new Error('The PDF reader did not load. Check your connection and reload the page.');
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  setStatus(`Reading ${file.name}…`);
  setProgress(2, 'Opening your PDF…');
  const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(await file.arrayBuffer()) }).promise;
  const pageCount = Math.min(pdf.numPages, MAX_PAGES);
  const ocrLanguage = getOcrLanguage();
  const pages = [];
  for (let number = 1; number <= pageCount; number++) {
    setProgress(Math.round(number / pageCount * 95), `Reading page ${number} of ${pageCount}…`);
    const page = await pdf.getPage(number);
    const content = await page.getTextContent();
    let text = content.items.map(item => item.str).join(' ').trim();
    if (text.replace(/\s/g, '').length < 35) {
      setProgress(Math.round(number / pageCount * 95), `Using OCR on scanned page ${number} of ${pageCount}…`);
      try {
        text = await ocrPage(page, number, ocrLanguage);
      } catch (e) {
        console.warn(`[OCR] page ${number} failed:`, e.message);
      }
    }
    if (text && text.trim()) pages.push({ number, text: text.trim() });
  }
  if (!pages.length) throw new Error('No readable text was found. Try a clearer PDF or another file.');
  pdfPages = pages;
  conversation = [];
  setProgress(100, `Ready · ${pages.length} readable page${pages.length === 1 ? '' : 's'}${pdf.numPages > MAX_PAGES ? ` (first ${MAX_PAGES} pages)` : ''}`);
  setStatus(`${file.name} · ${pages.length} page${pages.length === 1 ? '' : 's'} indexed, including OCR for scanned pages.`, 'success');
  elements.startLesson.disabled = false;
}

function addMessage(role, text, actions = [], speechLanguage = '', speechText = text) {
  const bubble = document.createElement('article');
  bubble.className = `message ${role}`;
  bubble.dir = 'auto';
  const label = document.createElement('span');
  label.className = 'message-label';
  label.textContent = role === 'assistant' ? 'Your tutor' : 'You';
  const body = document.createElement('div');
  body.textContent = text;
  bubble.append(label, body);
  if (actions.length) {
    const actionRow = document.createElement('div');
    actionRow.className = 'message-actions';
    for (const action of actions) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = action.label;
      button.addEventListener('click', action.onClick);
      actionRow.append(button);
    }
    bubble.append(actionRow);
  }
  if (role === 'assistant' && speechLanguage) {
    const actionRow = bubble.querySelector('.message-actions') || document.createElement('div');
    actionRow.className = 'message-actions';
    actionRow.append(createSpeechButton(speechText, speechLanguage));
    if (!actionRow.parentElement) bubble.append(actionRow);
  }
  elements.chatMessages.append(bubble);
  elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
  return bubble;
}

function setBusy(value, status) {
  busy = value;
  elements.pdfFile.disabled = value || readingPdf;
  elements.sendButton.disabled = value || !learningProfile;
  elements.messageInput.disabled = value || !learningProfile;
  elements.startLesson.disabled = value || !pdfPages.length || !!learningProfile;
  elements.diagnosticForm.querySelectorAll('select, textarea').forEach(input => { input.disabled = value || !!learningProfile; });
  elements.chatMessages.querySelectorAll('.message-actions button').forEach(button => { button.disabled = value; });
  elements.tutorStatus.textContent = status;
}

async function runDiagnostic() {
  const language = elements.languageSelect.value;
  const answers = {
    selfAssessedLevel: elements.levelSelect.value,
    preferredMethod: elements.styleSelect.value,
    language,
    priorKnowledge: elements.priorKnowledge.value.trim() || 'Not provided yet',
  };
  setBusy(true, 'A quick learning check-in is underway…');
  elements.startLesson.textContent = 'Finding your learning fit…';
  try {
    const summary = await requestModel(FAST_MODEL, [
      {
        role: 'system',
        content: `You are a concise learning diagnostic. Use the learner's self-assessment and their low-stakes explanation exercise, comparing their response with the PDF context, to identify a starting level, likely useful explanation approach, and one adaptation to watch for as they learn. Do not claim certainty about a fixed learning style or judge the learner. Reply in ${language}, in 2 short sentences, in a warm and non-judgmental tone.\n\n${NUMERIC_FORMAT_INSTRUCTION}`,
      },
      {
        role: 'user',
        content: JSON.stringify({
          ...answers,
          diagnosticExercise: answers.priorKnowledge,
          pdfContext: relevantContext('key ideas concepts definitions', 2200),
        }),
      },
    ], { maxTokens: 220, temperature: 0.2 });

    learningProfile = { ...answers, summary };
    elements.profileSummary.textContent = summary;
    elements.profileCard.classList.remove('hidden');
    elements.chatMessages.innerHTML = '';
    elements.messageInput.disabled = false;
    elements.messageInput.placeholder = language === 'Bangla' || language === 'Bengali'
      ? 'একটি ধারণা সম্পর্কে জিজ্ঞাসা করুন, অথবা কী বুঝতে সমস্যা হচ্ছে জানান…'
      : 'Ask about a concept, or tell me what feels confusing…';
    elements.messageInput.focus();
    elements.sendButton.disabled = false;

    const welcomeOpening = language === 'Bangla' || language === 'Bengali'
      ? `${summary}\n\nআমি আপনার PDF পড়েছি। আপনি প্রথমে কোনটি বুঝতে চান? আমি একটি ইঙ্গিত ও নির্দেশক প্রশ্ন দিয়ে শুরু করতে পারি।`
      : `${summary}\n\nI’ve read your PDF. What would you like to understand first? I can start with a hint and a guiding question.`;

    addMessage('assistant', welcomeOpening, [], language, summary);
    setBusy(false, `${answers.language} · ${answers.selfAssessedLevel} · ${answers.preferredMethod}`);
    elements.diagnosticForm.querySelectorAll('select, textarea').forEach(input => { input.disabled = true; });
    elements.startLesson.textContent = 'Learning plan ready';
  } catch (error) {
    setBusy(false, 'The learning check-in could not be completed.');
    elements.startLesson.textContent = 'Try the check-in again';
    addMessage('assistant', error.message);
  }
}

function relevantContext(query, limit = 9000) {
  const terms = new Set(query.toLowerCase().match(/[\p{L}\p{N}]{3,}/gu) || []);
  const ranked = pdfPages.map(page => {
    const pageTerms = page.text.toLowerCase().match(/[\p{L}\p{N}]{3,}/gu) || [];
    const counts = new Map();
    for (const term of pageTerms) counts.set(term, (counts.get(term) || 0) + 1);
    const score = [...terms].reduce((total, term) => total + (counts.has(term) ? 1 + Math.log(counts.get(term)) : 0), 0);
    return { ...page, score };
  }).sort((a, b) => b.score - a.score);
  const selected = (ranked.some(page => page.score > 0) ? ranked.filter(page => page.score > 0).slice(0, 4) : ranked.slice(0, 2));
  return selected.map(page => `[PDF page ${page.number}]\n${page.text}`).join('\n\n').slice(0, limit);
}

async function classifyTurn(userText) {
  const language = learningProfile.language;
  const result = await requestModel(FAST_MODEL, [
    {
      role: 'system',
      content: `Classify the learner’s latest message using the prior learning profile and conversation. Return only valid JSON with keys "confused" (boolean), "level" (beginner/intermediate/advanced), "approach" (one short phrase), and "reason" (one short phrase). Treat explicit confusion or repeated misunderstanding as confused. Do not infer ability from grammar or language.\n\n${NUMERIC_FORMAT_INSTRUCTION}`,
    },
    { role: 'user', content: JSON.stringify({ language, profile: learningProfile, recentConversation: conversation.slice(-6), latestMessage: userText }) },
  ], { maxTokens: 120, temperature: 0.1 });

  const json = result.match(/\{[\s\S]*\}/)?.[0];
  if (!json) throw new Error('The learning diagnostic returned an unreadable result. Please try your question again.');
  try {
    const profile = JSON.parse(json);
    if (typeof profile.confused !== 'boolean' || !['beginner', 'intermediate', 'advanced'].includes(profile.level)) {
      throw new Error('invalid diagnostic fields');
    }
    return profile;
  } catch {
    throw new Error('The learning diagnostic returned an invalid result. Please try your question again.');
  }
}

function addTyping(message) {
  const typing = document.createElement('div');
  typing.className = 'typing';
  typing.setAttribute('role', 'status');
  typing.textContent = message;
  elements.chatMessages.append(typing);
  elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
  return typing;
}

async function askForHint(question, diagnostic) {
  const language = learningProfile.language;
  const context = relevantContext(question);
  const system = `You are a patient, Socratic AI tutor. Answer in ${language}. Learner level: ${diagnostic.level}. Preferred approach: ${diagnostic.approach || learningProfile.preferredMethod}. ${diagnostic.confused ? 'The learner appears confused: simplify substantially, validate the difficulty without judgment, use one concrete analogy, and avoid jargon.' : 'Adapt to the learner’s current understanding.'} Use the provided PDF context as the source of truth. First respond with a useful hint and one guiding question only; do not give the complete answer. Keep it short and specific. If the answer is not in the PDF, say so and distinguish general knowledge clearly.\n\n${NUMERIC_FORMAT_INSTRUCTION}`;

  return requestWithFallback(REASONING_MODELS, [
    { role: 'system', content: system },
    { role: 'user', content: `PDF context:\n${context}\n\nLearner question: ${question}` },
  ], { maxTokens: 500, temperature: 0.45 });
}

async function revealExplanation(question, hintBubble, diagnostic) {
  if (busy) return;
  setBusy(true, 'Building a clear explanation…');
  const typing = addTyping('Putting the idea together…');
  try {
    const context = relevantContext(question);
    const history = conversation.slice(-8).map(item => `${item.role}: ${item.content}`).join('\n');
    const answer = await requestWithFallback(REASONING_MODELS, [
      {
        role: 'system',
        content: `You are a patient, accessible AI tutor. Respond in ${learningProfile.language}. Explain at ${diagnostic.level} level using ${diagnostic.approach || learningProfile.preferredMethod}. ${diagnostic.confused ? 'The learner has signaled confusion: start from the simplest idea, use short steps and a different everyday example, and check understanding gently.' : 'Use plain language and concrete examples.'} Give a complete but focused explanation grounded in the supplied PDF. Define difficult terms and never shame the learner. Do not invent claims from the document.\n\n${NUMERIC_FORMAT_INSTRUCTION}`,
      },
      { role: 'user', content: `Relevant PDF context:\n${context}\n\nRecent conversation:\n${history}\n\nExplain the answer to: ${question}` },
    ], { maxTokens: 900, temperature: 0.4 });

    typing.remove();
    addMessage('assistant', answer, [], learningProfile.language);
    conversation.push({ role: 'assistant', content: answer });
  } catch (error) {
    typing.remove();
    addMessage('assistant', error.message);
  } finally {
    setBusy(false, `${learningProfile.language} · ${diagnostic.level} · ${diagnostic.approach || learningProfile.preferredMethod}`);
  }
}

async function submitQuestion(question) {
  if (busy || !learningProfile || !question.trim()) return;
  const cleanQuestion = question.trim();
  addMessage('user', cleanQuestion);
  conversation.push({ role: 'user', content: cleanQuestion });
  elements.messageInput.value = '';
  setBusy(true, 'Checking what would help you most…');
  const typing = addTyping('Noticing how this idea is landing…');
  try {
    const diagnostic = await classifyTurn(cleanQuestion);
    learningProfile.level = diagnostic.level;
    learningProfile.approach = diagnostic.approach;
    const hint = await askForHint(cleanQuestion, diagnostic);
    typing.remove();
    const isBn = learningProfile.language === 'Bangla' || learningProfile.language === 'Bengali';
    const hintBubble = addMessage('assistant', hint, [{
      label: isBn ? 'সম্পূর্ণ ব্যাখ্যা দেখুন' : 'Show the full explanation',
      onClick: () => revealExplanation(cleanQuestion, hintBubble, diagnostic),
    }, {
      label: isBn ? 'এখনও বুঝতে পারিনি' : 'I’m still confused',
      onClick: () => submitQuestion(isBn ? `আমি এটি এখনও বুঝতে পারিনি। অনুগ্রহ করে অন্যভাবে বুঝিয়ে বলুন: ${cleanQuestion}` : `I’m still confused about this. Please explain it differently: ${cleanQuestion}`),
    }], learningProfile.language);
    conversation.push({ role: 'assistant', content: hint });
  } catch (error) {
    typing.remove();
    addMessage('assistant', error.message);
  } finally {
    setBusy(false, `${learningProfile.language} · ${learningProfile.level} · ${learningProfile.approach || learningProfile.preferredMethod}`);
  }
}

elements.pdfFile.addEventListener('change', async () => {
  const file = elements.pdfFile.files?.[0];
  if (!file || readingPdf) return;
  readingPdf = true;
  elements.pdfFile.disabled = true;
  pdfPages = [];
  conversation = [];
  elements.startLesson.disabled = true;
  elements.profileCard.classList.add('hidden');
  learningProfile = null;
  elements.messageInput.disabled = true;
  elements.sendButton.disabled = true;
  elements.messageInput.placeholder = 'Complete your learning check-in to continue…';
  elements.chatMessages.replaceChildren();
  try {
    await readPdf(file);
  } catch (error) {
    setStatus(error.message, 'error');
    elements.progressWrap.classList.add('hidden');
  } finally {
    readingPdf = false;
    elements.pdfFile.disabled = false;
  }
});

elements.dropzone.addEventListener('dragover', event => {
  event.preventDefault();
  elements.dropzone.classList.add('dragging');
});
elements.dropzone.addEventListener('dragleave', () => elements.dropzone.classList.remove('dragging'));
elements.dropzone.addEventListener('drop', event => {
  event.preventDefault();
  elements.dropzone.classList.remove('dragging');
  if (readingPdf || busy) return;
  const [file] = event.dataTransfer.files;
  if (!file) return;
  const transfer = new DataTransfer();
  transfer.items.add(file);
  elements.pdfFile.files = transfer.files;
  elements.pdfFile.dispatchEvent(new Event('change'));
});

elements.diagnosticForm.addEventListener('submit', event => {
  event.preventDefault();
  runDiagnostic();
});

elements.editProfile.addEventListener('click', () => {
  learningProfile = null;
  elements.profileCard.classList.add('hidden');
  elements.diagnosticForm.querySelectorAll('select, textarea').forEach(input => { input.disabled = false; });
  elements.startLesson.disabled = !pdfPages.length;
  elements.startLesson.textContent = 'Analyze & start lesson';
  elements.messageInput.disabled = true;
  elements.sendButton.disabled = true;
  elements.messageInput.placeholder = 'Complete your learning check-in to continue…';
});

elements.chatForm.addEventListener('submit', event => {
  event.preventDefault();
  submitQuestion(elements.messageInput.value);
});

elements.messageInput.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    elements.chatForm.requestSubmit();
  }
});
