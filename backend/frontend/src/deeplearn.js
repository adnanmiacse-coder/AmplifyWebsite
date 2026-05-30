// ══════════════════════════════════════════════
//  গভীর শিক্ষা — deeplearn.js
//  3 Expert Agents · Groq multi-model · Bangla Deep Discussion
// ══════════════════════════════════════════════

import { loadEnvConfig, getGroqKeys, getOpenRouterKeys, getGroqBase, getOpenRouterBase, getViteEnv } from './env-config.js';

let _config = {};
const _env = getViteEnv();
loadEnvConfig().then(cfg => { _config = cfg; });

function groqKeys() { return getGroqKeys(_config, _env); }
function openRouterKeys() { return getOpenRouterKeys(_config, _env); }
function groqBase() { return getGroqBase(_config, _env); }
function openRouterBase() { return getOpenRouterBase(_config, _env); }

const OPENROUTER_MODELS = [
  'meta-llama/llama-3.3-70b-instruct:free',
  'deepseek/deepseek-r1-0528:free',
  'google/gemma-3n-e4b-it:free',
  'tngtech/deepseek-r1t-chimera:free',
];
const GROQ_MODELS        = ['llama-3.3-70b-versatile','llama-3.3-70b-specdec','gemma2-9b-it','llama-3.1-8b-instant'];
const VISION_MODEL       = 'meta-llama/llama-4-scout-17b-16e-instruct';

// ── Expert Config ──────────────────────────────
const MODEL_FALLBACK = 'llama-3.1-8b-instant';


// ══════════════════════════════════════════════
//  PDF PIPELINE (pdf.js + TF-IDF VectorStore)
// ══════════════════════════════════════════════
const CHUNK_WORDS   = 150;
const CHUNK_OVERLAP = 30;
const MAX_PAGES     = 60;
const TOP_K         = 6;
const PAGE_SCALE    = 2.0;
const IMG_QUALITY   = 0.85;

pdfjsLib.GlobalWorkerOptions.workerSrc =
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

class VectorStore {
  constructor() { this.reset(); }
  reset() { this.chunks = []; this.tfidf = []; this.idf = {}; this.vocab = new Set(); this.ready = false; }
  tokenize(text) {
    return text.toLowerCase().replace(/[।,!?;:()\[\]{}"'\/\\]/g, ' ').split(/\s+/).filter(t => t.length > 1);
  }
  build() {
    const tfRaw = this.chunks.map(c => {
      const tokens = this.tokenize(c.text), freq = {};
      for (const t of tokens) { freq[t] = (freq[t] || 0) + 1; this.vocab.add(t); }
      const maxF = Math.max(1, ...Object.values(freq)), tf = {};
      for (const [t, f] of Object.entries(freq)) tf[t] = f / maxF;
      return tf;
    });
    const N = this.chunks.length, df = {};
    for (const tf of tfRaw) for (const t of Object.keys(tf)) df[t] = (df[t] || 0) + 1;
    this.idf = {};
    for (const [t, d] of Object.entries(df)) this.idf[t] = Math.log((N + 1) / (d + 1)) + 1;
    this.tfidf = tfRaw.map(tf => {
      const v = {};
      for (const [t, s] of Object.entries(tf)) v[t] = s * (this.idf[t] || 1);
      return v;
    });
    this.ready = true;
  }
  addChunk(chunk) { this.chunks.push(chunk); }
  qvec(text) {
    const tokens = this.tokenize(text), freq = {};
    for (const t of tokens) freq[t] = (freq[t] || 0) + 1;
    const maxF = Math.max(1, ...Object.values(freq)), v = {};
    for (const [t, f] of Object.entries(freq)) v[t] = (f / maxF) * (this.idf[t] || 0.3);
    return v;
  }
  cosine(a, b) {
    let dot = 0, na = 0, nb = 0;
    for (const [t, v] of Object.entries(a)) { dot += v * (b[t] || 0); na += v * v; }
    for (const v of Object.values(b)) nb += v * v;
    return (na && nb) ? dot / (Math.sqrt(na) * Math.sqrt(nb)) : 0;
  }
  retrieve(query, k = TOP_K) {
    if (!this.tfidf.length) return [];
    const qv = this.qvec(query);
    const scores = this.tfidf.map((v, i) => ({ i, rel: this.cosine(qv, v) }));
    scores.sort((a, b) => b.rel - a.rel);
    const lambda = 0.6, selected = [], remaining = [...scores];
    while (selected.length < k && remaining.length) {
      let best = -Infinity, bi = 0;
      for (let j = 0; j < remaining.length; j++) {
        const r = remaining[j];
        const maxSim = selected.length ? Math.max(...selected.map(s => this.cosine(this.tfidf[r.i], this.tfidf[s.i]))) : 0;
        const sc = lambda * r.rel - (1 - lambda) * maxSim;
        if (sc > best) { best = sc; bi = j; }
      }
      selected.push(remaining[bi]); remaining.splice(bi, 1);
    }
    return selected.filter(s => s.rel > 0).map(s => ({ ...this.chunks[s.i], chunkIdx: s.i, score: s.rel }));
  }
}

const store = new VectorStore();
let pdfPages = [];

function chunkText(text, pageNum) {
  const sentences = text.replace(/([।.!?])\s+/g, '$1\n').split('\n').map(s => s.trim()).filter(s => s.length > 4);
  const chunks = []; let buf = [], wc = 0;
  for (const sent of sentences) {
    const sw = sent.split(/\s+/).length;
    if (wc + sw > CHUNK_WORDS && buf.length) {
      const ct = buf.join(' ');
      if (ct.trim().length > 20) chunks.push({ text: ct, pageNum, wordCount: wc });
      const overlap = buf.join(' ').split(/\s+/).slice(-CHUNK_OVERLAP).join(' ');
      buf = overlap ? [overlap] : []; wc = buf[0] ? buf[0].split(/\s+/).length : 0;
    }
    buf.push(sent); wc += sw;
  }
  if (buf.length) { const ct = buf.join(' ').trim(); if (ct.length > 20) chunks.push({ text: ct, pageNum, wordCount: wc }); }
  return chunks;
}

function getRelevantContext(query, maxChars = 5000) {
  if (!store.ready || !store.chunks.length)
    return pdfPages.map(p => `[পৃষ্ঠা ${p.page}]\n${p.text}`).join('\n\n').slice(0, maxChars);
  const results = store.retrieve(query, TOP_K);
  if (!results.length) return '';
  let out = '', chars = 0;
  for (const r of results) {
    const block = `[পৃষ্ঠা ${r.pageNum}]\n${r.text}`;
    if (chars + block.length > maxChars) break;
    out += block + '\n\n'; chars += block.length;
  }
  return out.trim();
}

async function extractPageText(page) {
  const tc = await page.getTextContent();
  return tc.items.map(i => i.str).join(' ').trim();
}

async function pageToBase64(page) {
  const vp = page.getViewport({ scale: PAGE_SCALE });
  const canvas = document.createElement('canvas');
  canvas.width = vp.width; canvas.height = vp.height;
  await page.render({ canvasContext: canvas.getContext('2d'), viewport: vp }).promise;
  return canvas.toDataURL('image/jpeg', IMG_QUALITY).split(',')[1];
}

async function detectPDFMode(doc) {
  const n = Math.min(5, doc.numPages); let total = 0;
  for (let i = 1; i <= n; i++) {
    const pg = await doc.getPage(i);
    total += (await extractPageText(pg)).length;
  }
  return (total / n) < 50 ? 'image' : 'text';
}

async function groqVisionOCR(base64Img, pageNum) {
  for (let ki = 0; ki < groqKeys().length; ki++) {
    try {
      const res = await fetch(`${groqBase()}/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${groqKeys()[ki]}` },
        body: JSON.stringify({
          model: VISION_MODEL, max_tokens: 2048,
          messages: [{ role: 'user', content: [
            { type: 'image_url', image_url: { url: `data:image/jpeg;base64,${base64Img}` } },
            { type: 'text', text: 'Transcribe ALL text visible on this page exactly. Output only raw text, no commentary.' }
          ]}],
        }),
      });
      if (res.status === 429) { await sleep(4000); continue; }
      if (!res.ok) continue;
      const d = await res.json();
      return d.choices?.[0]?.message?.content || '';
    } catch (e) { console.warn(`[OCR] key ${ki+1}: ${e.message}`); }
  }
  return '';
}

async function loadAndIndexPDF(file, onProgress) {
  store.reset(); pdfPages = [];
  onProgress?.('PDF খোলা হচ্ছে…');
  const buf    = await file.arrayBuffer();
  const pdfDoc = await pdfjsLib.getDocument({ data: new Uint8Array(buf) }).promise;
  const pages  = Math.min(pdfDoc.numPages, MAX_PAGES);
  const mode   = await detectPDFMode(pdfDoc);
  for (let i = 1; i <= pages; i++) {
    onProgress?.(`পৃষ্ঠা ${i}/${pages} পড়া হচ্ছে…`);
    const pg = await pdfDoc.getPage(i);
    let pageText = await extractPageText(pg);
    if (pageText.trim().length < 30 && mode === 'image') {
      try {
        const b64 = await pageToBase64(pg);
        const ocr = await groqVisionOCR(b64, i);
        if (ocr && ocr.trim().length > pageText.length) pageText = ocr;
      } catch (e) { console.warn(`[PDF OCR p${i}]:`, e.message); }
    }
    if (pageText.trim().length > 10) {
      pdfPages.push({ page: i, text: pageText });
      for (const c of chunkText(pageText, i)) store.addChunk(c);
    }
  }
  if (store.chunks.length === 0) { onProgress?.('⚠️ কোনো পাঠ্য পাওয়া যায়নি।'); return; }
  store.build();
  onProgress?.(`প্রস্তুত! (${store.chunks.length} অংশ)`);
}


const EXPERTS = {
  expert1: {
    id:    'expert1',
    name:  'ড. আরিফ',
    nameShort: 'ড.আ',
    role:  'বিষয় বিশেষজ্ঞ ও সংশ্লেষক',
    model: 'llama-3.3-70b-versatile',
    color: '#5b21b6',
    avatarClass: 'expert1-avatar',
    bubbleClass: 'bubble-expert1',
    system: `তুমি ড. আরিফ, একজন অভিজ্ঞ বিষয় বিশেষজ্ঞ ও সংশ্লেষক। তুমি সরাসরি বাংলায় কথা বলছ।
কঠোর নিয়ম:
- প্রথম পুরুষে কথা বলো।
- "ড. আরিফ বলেছেন" বা তৃতীয় পুরুষের বর্ণনা সম্পূর্ণ নিষিদ্ধ।
- প্রতিটি বক্তব্যে গভীর ধারণা, বৈজ্ঞানিক ব্যাখ্যা, এবং বাস্তব প্রাসঙ্গিকতা উল্লেখ করো।
- তথ্য উল্লেখ করো কিন্তু কোনো প্রতিষ্ঠানের নাম বা ব্যক্তির নাম ব্যবহার করো না।
- ৩-৫টি বাক্যে বিস্তারিত বলো।
- অন্য বিশেষজ্ঞদের কথায় সরাসরি সাড়া দাও।`,
  },
  expert2: {
    id:    'expert2',
    name:  'ড. নাফিসা',
    nameShort: 'ড.না',
    role:  'বিশ্লেষক ও গবেষক',
    model: 'meta-llama/llama-4-scout-17b-16e-instruct',
    color: '#0369a1',
    avatarClass: 'expert2-avatar',
    bubbleClass: 'bubble-expert2',
    system: `তুমি ড. নাফিসা, একজন তীক্ষ্ণ বিশ্লেষক ও গবেষক। তুমি সরাসরি বাংলায় কথা বলছ।
কঠোর নিয়ম:
- প্রথম পুরুষে কথা বলো।
- "ড. নাফিসা বলেছেন" বা তৃতীয় পুরুষের বর্ণনা সম্পূর্ণ নিষিদ্ধ।
- তুলনামূলক বিশ্লেষণ করো, তথ্য-ভিত্তিক যুক্তি দাও।
- ড. আরিফের বক্তব্যকে আরও বিশ্লেষণ করো বা নতুন দিক আনো।
- কোনো প্রতিষ্ঠানের নাম বা ব্যক্তির নাম ব্যবহার করো না।
- ৩-৫টি বাক্যে বিস্তারিত বলো।`,
  },
  expert3: {
    id:    'expert3',
    name:  'ড. রাকিব',
    nameShort: 'ড.রা',
    role:  'সমালোচক ও প্রশ্নকর্তা',
    model: 'llama3-70b-8192',
    color: '#b45309',
    avatarClass: 'expert3-avatar',
    bubbleClass: 'bubble-expert3',
    system: `তুমি ড. রাকিব, একজন তীব্র সমালোচক ও প্রশ্নকর্তা। তুমি সরাসরি বাংলায় কথা বলছ।
কঠোর নিয়ম:
- প্রথম পুরুষে কথা বলো।
- "ড. রাকিব বলেছেন" বা তৃতীয় পুরুষের বর্ণনা সম্পূর্ণ নিষিদ্ধ।
- বিদ্যমান বক্তব্যকে চ্যালেঞ্জ করো, বিকল্প দৃষ্টিভঙ্গি তুলে ধরো, গুরুত্বপূর্ণ প্রশ্ন করো।
- বিতর্কমূলক হও কিন্তু তথ্যভিত্তিক থাকো।
- কোনো প্রতিষ্ঠানের নাম বা ব্যক্তির নাম ব্যবহার করো না।
- ৩-৫টি বাক্যে বিস্তারিত বলো।`,
  },
};

// ── Discussion phases ─────────────────────────
const DISCUSSION_PHASES = [
  { id: 'intro',     label: 'পরিচিতি ও ভিত্তি',  rounds: 2, stance: 'discuss'   },
  { id: 'analysis',  label: 'গভীর বিশ্লেষণ',      rounds: 3, stance: 'discuss'   },
  { id: 'debate',    label: 'বিতর্ক ও খণ্ডন',     rounds: 3, stance: 'debate'    },
  { id: 'synthesis', label: 'সংশ্লেষণ',           rounds: 2, stance: 'synthesis' },
  { id: 'conclude',  label: 'উপসংহার',             rounds: 1, stance: 'synthesis' },
];

const STANCE_LABELS = {
  discuss:   { label: '💬 আলোচনা',   class: 'stance-discuss'  },
  debate:    { label: '⚔️ বিতর্ক',    class: 'stance-debate'   },
  critique:  { label: '🔍 সমালোচনা', class: 'stance-critique' },
  synthesis: { label: '🔗 সংশ্লেষণ', class: 'stance-synthesis'},
};

const TURN_ORDER = ['expert1', 'expert2', 'expert3'];

const ALL_EXPERT_PREFIXES = [
  'ড. আরিফ','Dr. Arif','ড.আরিফ',
  'ড. নাফিসা','Dr. Nafisa','ড.নাফিসা',
  'ড. রাকিব','Dr. Rakib','ড.রাকিব',
  'আরিফ','নাফিসা','রাকিব',
];

// ── State ─────────────────────────────────────
let sessionTopic       = '';
let isRunning          = false;
let isPaused           = false;
let ttsEnabled         = true;
let sessionSeconds     = 0;
let timerInterval      = null;
let currentTurnIndex   = 0;
let dialogueLog        = [];
let initialContent     = null;
let uploadedFiles      = [];
let currentPhaseIdx    = 0;
let currentPhaseRound  = 0;
let userPendingMsg     = null;
let userInterrupted    = false;
let agentVoiceMap      = { expert1: null, expert2: null, expert3: null };

const AGENT_TTS = {
  expert1: { rate: 0.85, pitch: 0.95 },
  expert2: { rate: 0.88, pitch: 1.10 },
  expert3: { rate: 0.92, pitch: 0.85 },
};

// ── DOM ───────────────────────────────────────
const uploadScreen    = document.getElementById('upload-screen');
const deeplearnScreen = document.getElementById('deeplearn-screen');
const uploadZone      = document.getElementById('uploadZone');
const fileInput       = document.getElementById('fileInput');
const uploadPreviews  = document.getElementById('uploadPreviews');
const topicInput      = document.getElementById('topicInput');
const startBtn        = document.getElementById('startBtn');
const stageTopic      = document.getElementById('stageTopic');
const stageIdle       = document.getElementById('stageIdle');
const debateStage     = document.getElementById('debateStage');
const ttsWave         = document.getElementById('ttsWave');
const ttsLabel        = document.getElementById('ttsLabel');
const ttsToggle       = document.getElementById('ttsToggle');
const chatMessages    = document.getElementById('chatMessages');
const userInput       = document.getElementById('userInput');
const sendBtn         = document.getElementById('sendBtn');
const pauseInputBtn   = document.getElementById('pauseInputBtn');
const pauseBtn        = document.getElementById('pauseBtn');
const exportBtn       = document.getElementById('exportBtn');
const resetBtn        = document.getElementById('resetBtn');
const sessionTimer    = document.getElementById('sessionTimer');
const phaseLabel      = document.getElementById('phaseLabel');

// ── Auto-fill topic from URL param (passed by classroom page) ──
(function () {
  try {
    const params = new URLSearchParams(location.search);
    const t = params.get('topic');
    if (t) topicInput.value = decodeURIComponent(t);
  } catch (e) {}
})();

// ── Upload Zone ─────────────────────────────
uploadZone.addEventListener('click', () => fileInput.click());
uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('dragover'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone.classList.remove('dragover');
  handleFiles(Array.from(e.dataTransfer.files));
});
fileInput.addEventListener('change', () => handleFiles(Array.from(fileInput.files)));

function handleFiles(files) {
  uploadedFiles = files.slice(0, 3);
  uploadPreviews.innerHTML = '';
  if (uploadedFiles.length > 0) {
    uploadPreviews.classList.remove('hidden');
    uploadedFiles.forEach(file => {
      const box = document.createElement('div');
      box.className = 'preview-file';
      box.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><span>${file.name.slice(0, 14)}...</span>`;
      uploadPreviews.appendChild(box);
    });
  } else {
    uploadPreviews.classList.add('hidden');
  }
}

async function toBase64(file) {
  return new Promise((res, rej) => {
    const r = new FileReader();
    r.onload  = () => res(r.result.split(',')[1]);
    r.onerror = rej;
    r.readAsDataURL(file);
  });
}

// ── Start ─────────────────────────────────────
startBtn.addEventListener('click', async () => {
  const topic = topicInput.value.trim();
  if (!topic && uploadedFiles.length === 0) {
    alert('অনুগ্রহ করে একটি বিষয় লিখুন অথবা ফাইল আপলোড করুন।');
    return;
  }
  
  sessionTopic = topic || uploadedFiles.map(f => f.name).join(', ');
  await switchToDeepLearn();
});

async function switchToDeepLearn() {
  uploadScreen.classList.remove('active');
  deeplearnScreen.classList.add('active');
  stageTopic.textContent = sessionTopic;
  startTimer();
  loadVoices();
  await startDiscussion();
}

// ── Timer ─────────────────────────────────────
function startTimer() {
  sessionSeconds = 0;
  timerInterval = setInterval(() => {
    if (!isPaused) sessionSeconds++;
    const m = String(Math.floor(sessionSeconds / 60)).padStart(2, '0');
    const s = String(sessionSeconds % 60).padStart(2, '0');
    sessionTimer.textContent = toBengaliNumerals(`${m}:${s}`);
  }, 1000);
}

function toBengaliNumerals(str) {
  return str.replace(/\d/g, d => '০১২৩৪৫৬৭৮৯'[d]);
}

// ── Voices ────────────────────────────────────
function loadVoices() {
  const assign = () => {
    const all   = speechSynthesis.getVoices();
    const bnAll = all.filter(v => v.lang.startsWith('bn'));
    if (bnAll.length === 0) {
      const any = all[0] || null;
      Object.keys(EXPERTS).forEach(id => { agentVoiceMap[id] = any; });
      return;
    }
    const MALE   = /Pradeep|Bashkar|Arnav|Ravi|male/i;
    const FEMALE = /Nabanita|Tanishaa|Asha|Heera|Swara|female/i;
    const males   = bnAll.filter(v =>  MALE.test(v.name));
    const females = bnAll.filter(v =>  FEMALE.test(v.name));
    const neutral = bnAll.filter(v => !MALE.test(v.name) && !FEMALE.test(v.name));
    const mPool = males.length   ? males   : [...neutral, ...females];
    const fPool = females.length ? females : [...neutral, ...males];
    agentVoiceMap.expert1 = mPool[0] || bnAll[0];
    agentVoiceMap.expert2 = fPool[0] || bnAll[0];
    agentVoiceMap.expert3 = mPool[1] || mPool[0] || bnAll[0];
  };
  assign();
  speechSynthesis.addEventListener('voiceschanged', assign);
}

// ── TTS ───────────────────────────────────────
function speak(text, expertId) {
  return new Promise(resolve => {
    if (!ttsEnabled) { resolve(); return; }
    const voice = agentVoiceMap[expertId];
    if (!voice)  { resolve(); return; }
    const tts = AGENT_TTS[expertId];
    speechSynthesis.cancel();
    const utt   = new SpeechSynthesisUtterance(text);
    utt.voice   = voice;
    utt.lang    = voice.lang;
    utt.rate    = tts.rate;
    utt.pitch   = tts.pitch;
    ttsWave.classList.add('speaking');
    ttsLabel.textContent = EXPERTS[expertId].name + ' বলছেন...';
    utt.onend   = () => { ttsWave.classList.remove('speaking'); ttsLabel.textContent = 'নীরব'; resolve(); };
    utt.onerror = () => { ttsWave.classList.remove('speaking'); ttsLabel.textContent = 'নীরব'; resolve(); };
    speechSynthesis.speak(utt);
  });
}

ttsToggle.addEventListener('click', () => {
  ttsEnabled = !ttsEnabled;
  ttsToggle.classList.toggle('muted', !ttsEnabled);
  if (!ttsEnabled) {
    speechSynthesis.cancel();
    ttsWave.classList.remove('speaking');
    ttsLabel.textContent = 'TTS বন্ধ';
  } else {
    ttsLabel.textContent = 'নীরব';
  }
});

// ── Text Cleaning ─────────────────────────────
function cleanReply(text) {
  const escaped = ALL_EXPERT_PREFIXES.map(n => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
  const prefixPat = new RegExp(
    `^[\\s]*(?:\\*{0,2})(?:\\[)?(?:${escaped})(?:\\])?(?:\\*{0,2})[\\s]*:[\\s]*`, 'i'
  );
  let s = text.trim(), prev;
  do { prev = s; s = s.replace(prefixPat, '').trim(); } while (s !== prev);
  const midPat = new RegExp(
    `(?:\\n|\\r)+(?:\\*{0,2})(?:\\[)?(?:${escaped})(?:\\])?(?:\\*{0,2})[\\s]*:`, 'i'
  );
  const cut = s.search(midPat);
  if (cut > 0) s = s.slice(0, cut).trim();
  return s;
}

// ── Phase management ──────────────────────────
function getCurrentPhase() {
  return DISCUSSION_PHASES[currentPhaseIdx] || DISCUSSION_PHASES[DISCUSSION_PHASES.length - 1];
}

function advancePhase() {
  currentPhaseRound++;
  const phase = getCurrentPhase();
  if (currentPhaseRound >= phase.rounds * 3) { // *3 because 3 experts per round
    currentPhaseIdx   = Math.min(currentPhaseIdx + 1, DISCUSSION_PHASES.length - 1);
    currentPhaseRound = 0;
    insertPhaseDivider();
    updatePhaseUI();
  }
}

function updatePhaseUI() {
  const phase = getCurrentPhase();
  phaseLabel.textContent = phase.label;
  for (let i = 1; i <= 5; i++) {
    const el = document.getElementById(`phase${i}`);
    if (!el) continue;
    el.classList.remove('done', 'active');
    if (i - 1 < currentPhaseIdx)      el.classList.add('done');
    else if (i - 1 === currentPhaseIdx) el.classList.add('active');
  }
  for (let i = 1; i <= 5; i++) {
    const el = document.getElementById(`dd${i}`);
    if (!el) continue;
    el.classList.toggle('active', i - 1 <= currentPhaseIdx);
  }
}

// ── Expert speaking indicators ────────────────
function setExpertSpeaking(expertId) {
  document.querySelectorAll('.expert-card').forEach(c => c.classList.remove('speaking'));
  document.getElementById(`card-${expertId}`)?.classList.add('speaking');
}
function clearExpertSpeaking() {
  document.querySelectorAll('.expert-card').forEach(c => c.classList.remove('speaking'));
}

// ── Chat bubbles ──────────────────────────────
let typingBubbleEl = null;

function showTyping(expertId) {
  const expert = EXPERTS[expertId];
  typingBubbleEl = document.createElement('div');
  typingBubbleEl.className = `chat-bubble typing-bubble ${expert.bubbleClass}`;
  typingBubbleEl.innerHTML = `
    <div class="bubble-meta">
      <span class="bubble-dot" style="background:${expert.color}"></span>
      ${expert.name}
    </div>
    <div class="bubble-text">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>`;
  chatMessages.appendChild(typingBubbleEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTyping() {
  if (typingBubbleEl) { typingBubbleEl.remove(); typingBubbleEl = null; }
}

function addChatBubble(expertId, text) {
  const expert = EXPERTS[expertId];
  const div = document.createElement('div');
  div.className = `chat-bubble ${expert.bubbleClass}`;
  div.innerHTML = `
    <div class="bubble-meta">
      <span class="bubble-dot" style="background:${expert.color}"></span>
      ${expert.name}
    </div>
    <div class="bubble-text">${text}</div>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addUserBubble(text) {
  const div = document.createElement('div');
  div.className = 'chat-bubble bubble-user';
  div.innerHTML = `
    <div class="bubble-meta" style="justify-content:flex-end">আপনি</div>
    <div class="bubble-text">${text}</div>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function insertPhaseDivider() {
  const phase = DISCUSSION_PHASES[currentPhaseIdx] || {};
  const div = document.createElement('div');
  div.className = 'chat-phase-divider';
  div.innerHTML = `<div class="chat-phase-label">📍 ${phase.label || ''}</div>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ── Stage display ─────────────────────────────
function showOnStage(expertId, text, stanceKey) {
  const expert = EXPERTS[expertId];
  const stance = STANCE_LABELS[stanceKey] || STANCE_LABELS.discuss;
  stageIdle.classList.add('hidden');
  debateStage.classList.remove('hidden');

  const card = document.createElement('div');
  card.className = `speaker-card ${expertId}`;
  card.innerHTML = `
    <div class="speaker-card-header">
      <div class="speaker-avatar-lg ${expert.avatarClass}">${expert.nameShort}</div>
      <div>
        <div class="speaker-name-lg" style="color:${expert.color}">${expert.name}</div>
        <div class="speaker-role-lg">${expert.role}</div>
      </div>
      <div class="speaker-stance ${stance.class}">${stance.label}</div>
    </div>
    <div class="speaker-text-lg">${text}</div>`;

  while (debateStage.children.length >= 2) {
    debateStage.removeChild(debateStage.firstChild);
  }
  debateStage.appendChild(card);
  debateStage.scrollTop = debateStage.scrollHeight;
}

// ── Build prompt ──────────────────────────────
async function buildInitialContent() {
  _config = await loadEnvConfig();
  // Index any uploaded PDFs first
  for (const file of uploadedFiles) {
    if (file.type === 'application/pdf') {
      await loadAndIndexPDF(file, msg => console.log('[PDF]', msg));
      if (!sessionTopic) sessionTopic = file.name.replace(/\.pdf$/i, '');
    }
  }

  const docCtx = getRelevantContext(sessionTopic || 'মূল বিষয়', 4000);
  const docBlock = docCtx ? `\n\nডকুমেন্ট থেকে প্রাসঙ্গিক অংশ:\n${docCtx}` : '';
  const topicLine = sessionTopic ? `বিষয়: ${sessionTopic}` : 'আপলোড করা ফাইলের বিষয়বস্তু:';
  return `${topicLine}${docBlock}\n\nএই বিষয়ের সবচেয়ে গুরুত্বপূর্ণ এবং গভীর দিকগুলো কি? বিশেষজ্ঞ পর্যায়ে আলোচনার জন্য ৩-৫টি মূল বিষয় চিহ্নিত করো।`;
}

function buildMessagesForExpert(expertId) {
  const expert = EXPERTS[expertId];
  const phase  = getCurrentPhase();

  if (dialogueLog.length === 0) {
    return [{
      role: 'user',
      content: typeof initialContent === 'string' ? initialContent : JSON.stringify(initialContent),
    }];
  }

  const transcript = dialogueLog.slice(-12)
    .map(e => `[${e.name}]: ${e.text}`)
    .join('\n\n');

  const phaseInstruction = {
    intro:     'বিষয়টির মূল ভিত্তি, ইতিহাস এবং মূল ধারণাগুলো ব্যাখ্যা করো।',
    analysis:  'বিষয়টির গভীর বিশ্লেষণ করো — কারণ, প্রভাব, প্রক্রিয়া, এবং প্রমাণ নিয়ে আলোচনা করো।',
    debate:    'বিদ্যমান বক্তব্যকে চ্যালেঞ্জ করো, বিরোধী মতামত তুলে ধরো, যুক্তিতর্ক করো।',
    synthesis: 'বিভিন্ন দৃষ্টিভঙ্গিকে একসাথে বিবেচনা করে একটি সমন্বিত বোঝাপড়া তৈরি করো।',
    conclude:  'আলোচনার উপসংহার টানো এবং ভবিষ্যতের দিকনির্দেশনা দাও।',
  }[phase.id] || '';

  const docCtx = getRelevantContext(
    `${sessionTopic} ${phaseInstruction} ${transcript.slice(-300)}`, 3000
  );
  const docBlock = docCtx ? `\nডকুমেন্ট থেকে প্রাসঙ্গিক তথ্য:\n${docCtx}\n` : '';

  return [{
    role: 'user',
    content:
      `বিষয়: ${sessionTopic}\n` +
      `বর্তমান পর্যায়: ${phase.label}\n` +
      `নির্দেশনা: ${phaseInstruction}\n` +
      docBlock +
      `\nএখন পর্যন্ত আলোচনা:\n${transcript}\n\n` +
      `এখন ${expert.name} হিসেবে বিস্তারিত ও গভীরভাবে তোমার মত দাও। ` +
      `উপরের ডকুমেন্টের তথ্যের উপর ভিত্তি করো। ` +
      `সরাসরি শুরু করো, কোনো নাম-পরিচয় ছাড়া।`,
  }];
}

// ── Groq API call ─────────────────────────────

async function openRouterChat(messages, system, maxTokens = 600, temp = 0.8) {
  for (const model of OPENROUTER_MODELS) {
    for (let i = 0; i < openRouterKeys().length; i++) {
      try {
        const res = await fetch(`${openRouterBase()}/chat/completions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${openRouterKeys()[i]}`,
            'HTTP-Referer': 'http://localhost',
            'X-Title': 'DeepLearn',
          },
          body: JSON.stringify({ model, max_tokens: maxTokens, temperature: temp,
            messages: [{ role: 'system', content: system }, ...messages] }),
        });
        if (!res.ok) { if (res.status === 429) await sleep(1000); throw new Error(`${res.status}`); }
        const d = await res.json();
        const text = d?.choices?.[0]?.message?.content || '';
        if (!text.trim()) throw new Error('Empty');
        return cleanReply(text.trim());
      } catch (e) { console.warn(`[OpenRouter] ${model} key${i+1}: ${e.message}`); }
    }
  }
  throw new Error('All OpenRouter keys failed');
}

async function callGroq(expertId, modelOverride) {
  const expert   = EXPERTS[expertId];
  const messages = buildMessagesForExpert(expertId);

  // Try OpenRouter first
  try { return await openRouterChat(messages, expert.system); } catch (e) {
    console.warn('[callGroq] OpenRouter failed, falling back to Groq:', e.message);
  }

  // Groq fallback — rotate models × keys
  const models = modelOverride ? [modelOverride] : [expert.model, ...GROQ_MODELS];
  for (const model of models) {
    for (let ki = 0; ki < groqKeys().length; ki++) {
      try {
        const res = await fetch(`${groqBase()}/chat/completions`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${groqKeys()[ki]}` },
          body: JSON.stringify({ model, max_tokens: 600, temperature: 0.8,
            messages: [{ role: 'system', content: expert.system }, ...messages] }),
        });
        if (res.status === 429) { await sleep(400); continue; }
        if (!res.ok) continue;
        const d = await res.json();
        const text = d?.choices?.[0]?.message?.content || '';
        if (!text.trim()) continue;
        return cleanReply(text.trim());
      } catch (e) { console.warn(`[Groq] ${model} key${ki+1}: ${e.message}`); }
    }
  }
  throw new Error('সব OpenRouter ও Groq কী ব্যর্থ।');
}

// ── Knowledge fetch (enrichment panel) ────────
async function fetchKnowledgeInsert(topic, phaseId) {
  if (phaseId !== 'analysis' && phaseId !== 'debate') return null;

  const prompt = `বিষয়: "${topic}"

এই বিষয়ে ইন্টারনেট থেকে পাওয়া সাম্প্রতিক গবেষণা ও তথ্যের উপর ভিত্তি করে ২-৩টি গুরুত্বপূর্ণ তথ্যবিন্দু বাংলায় দাও।
- শিক্ষামূলক প্ল্যাটফর্ম, বিজ্ঞান জার্নাল, এবং অনলাইন কোর্সের তথ্য অন্তর্ভুক্ত করো
- কোনো প্রতিষ্ঠানের নাম বা ব্যক্তির নাম উল্লেখ করো না
- শুধু JSON রিটার্ন করো: {"insight": "বাংলায় ২-৩ বাক্য", "sources": ["বিষয়ভিত্তিক উৎস ধরন ১", "উৎস ধরন ২"]}`;

  try {
    const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type':  'application/json',
        'Authorization': `Bearer ${groqKeys()[0] || ''}`,
      },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        max_tokens: 300,
        temperature: 0.5,
        response_format: { type: 'json_object' },
        messages: [{ role: 'user', content: prompt }],
      }),
    });
    const data = await res.json();
    if (!res.ok) return null;
    return JSON.parse(data.choices?.[0]?.message?.content || '{}');
  } catch (e) {
    return null;
  }
}

function showKnowledgeInsert(insight, sources) {
  if (!insight) return;
  const div = document.createElement('div');
  div.className = 'knowledge-insert';
  const chips = (sources || []).map(s => `<span class="ks-chip">${s}</span>`).join('');
  div.innerHTML = `
    <div class="knowledge-header">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      গবেষণা তথ্য
    </div>
    <div class="knowledge-body">${insight}</div>
    ${chips ? `<div class="knowledge-sources">${chips}</div>` : ''}`;

  while (debateStage.children.length >= 2) {
    debateStage.removeChild(debateStage.firstChild);
  }
  debateStage.appendChild(div);
  debateStage.scrollTop = debateStage.scrollHeight;
}

// ── Main loop ─────────────────────────────────
async function startDiscussion() {
  isRunning         = true;
  currentTurnIndex  = 0;
  currentPhaseIdx   = 0;
  currentPhaseRound = 0;
  dialogueLog       = [];
  chatMessages.innerHTML = '';
  initialContent    = await buildInitialContent();

  userInput.disabled     = false;
  sendBtn.disabled       = false;
  pauseInputBtn.disabled = false;

  insertPhaseDivider();
  updatePhaseUI();
  runLoop();
}

async function runLoop() {
  while (isRunning) {
    if (isPaused) { await sleep(400); continue; }

    if (userInterrupted && userPendingMsg) {
      await handleUserTurn();
      continue;
    }

    const expertId = TURN_ORDER[currentTurnIndex % TURN_ORDER.length];
    await runExpertTurn(expertId);
    currentTurnIndex++;
    advancePhase();
    updatePhaseUI();

    if (isRunning && !isPaused) await sleep(1000);
  }
}

async function runExpertTurn(expertId) {
  const expert = EXPERTS[expertId];
  const phase  = getCurrentPhase();

  setExpertSpeaking(expertId);
  showTyping(expertId);

  let reply = '';
  try {
    const shouldInsert = (currentTurnIndex % 9 === 4) && (phase.id === 'analysis' || phase.id === 'debate');
    if (shouldInsert && expertId === 'expert2') {
      const knowledge = await fetchKnowledgeInsert(sessionTopic, phase.id);
      if (knowledge?.insight) {
        showKnowledgeInsert(knowledge.insight, knowledge.sources);
        await sleep(2000);
      }
    }
    reply = await callGroq(expertId);
  } catch (err) {
    console.error(err);
    hideTyping();
    clearExpertSpeaking();
    await sleep(1200);
    return;
  }

  hideTyping();
  dialogueLog.push({ name: expert.name, text: reply });
  if (dialogueLog.length > 24) dialogueLog = dialogueLog.slice(-24);

  const stanceKey = expertId === 'expert3' && phase.id === 'debate' ? 'critique'
                  : phase.id === 'debate' ? 'debate'
                  : phase.id === 'synthesis' || phase.id === 'conclude' ? 'synthesis'
                  : 'discuss';

  showOnStage(expertId, reply, stanceKey);
  addChatBubble(expertId, reply);
  await speak(reply, expertId);
  clearExpertSpeaking();
}

async function handleUserTurn() {
  const msg       = userPendingMsg;
  userPendingMsg  = null;
  userInterrupted = false;
  dialogueLog.push({ name: 'পর্যবেক্ষক', text: msg });
  for (const id of TURN_ORDER) {
    if (!isRunning) break;
    await runExpertTurn(id);
    advancePhase();
    if (isRunning) await sleep(600);
  }
  currentTurnIndex = 0;
}

// ── User input ────────────────────────────────
sendBtn.addEventListener('click', submitUserMsg);
userInput.addEventListener('keydown', e => { if (e.key === 'Enter') submitUserMsg(); });

function submitUserMsg() {
  const msg = userInput.value.trim();
  if (!msg || !isRunning) return;
  userInput.value = '';
  addUserBubble(msg);
  userPendingMsg  = msg;
  userInterrupted = true;
  isPaused        = false;
  pauseBtn.textContent = 'বিরতি';
  pauseInputBtn.classList.remove('active');
}

// ── Pause ─────────────────────────────────────
pauseBtn.addEventListener('click', togglePause);
pauseInputBtn.addEventListener('click', togglePause);

function togglePause() {
  isPaused = !isPaused;
  pauseBtn.textContent = isPaused ? 'চালিয়ে যান' : 'বিরতি';
  pauseInputBtn.classList.toggle('active', isPaused);
  if (isPaused) {
    speechSynthesis.cancel();
    ttsWave.classList.remove('speaking');
    ttsLabel.textContent = 'বিরতি';
  } else {
    ttsLabel.textContent = 'নীরব';
  }
}

// ── Export ────────────────────────────────────
exportBtn.addEventListener('click', () => {
  const lines = dialogueLog.map(e => `[${e.name}]: ${e.text}`).join('\n\n');
  const blob = new Blob(
    [`গভীর শিক্ষা আলোচনা\nবিষয়: ${sessionTopic}\n\n${lines}`],
    { type: 'text/plain;charset=utf-8' }
  );
  const a = document.createElement('a');
  a.href     = URL.createObjectURL(blob);
  a.download = `deeplearn_${sessionTopic.slice(0, 20)}_${Date.now()}.txt`;
  a.click();
});

// ── Reset ─────────────────────────────────────
resetBtn.addEventListener('click', () => {
  if (!confirm('আলোচনা শেষ করতে চান?')) return;
  isRunning = false;
  isPaused  = false;
  speechSynthesis.cancel();
  clearInterval(timerInterval);
  deeplearnScreen.classList.remove('active');
  uploadScreen.classList.add('active');
  dialogueLog    = [];
  chatMessages.innerHTML = '<div class="chat-welcome">আলোচনা শুরু হলে এখানে সম্পূর্ণ বিতর্ক দেখা যাবে</div>';
  debateStage.innerHTML  = '';
  debateStage.classList.add('hidden');
  stageIdle.classList.remove('hidden');
  currentPhaseIdx   = 0;
  currentPhaseRound = 0;
  updatePhaseUI();
});

// ── Helpers ───────────────────────────────────
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }