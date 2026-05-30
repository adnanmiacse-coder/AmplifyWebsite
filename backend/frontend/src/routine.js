import { loadEnvConfig } from './env-config.js';

let _config = {};
loadEnvConfig().then(cfg => { _config = cfg; });

const _env = (typeof import !== 'undefined' && import.meta && import.meta.env) ? import.meta.env : {};
const GROQ_API_KEY = _config.GROQ_API_KEY || _env.VITE_GROQ_API_KEY || window.GROQ_API_KEY || '';

if (!GROQ_API_KEY) {
  console.warn('Note: API keys are now loaded from server (/api/config). Set them in backend .env for proper functionality.');
}

// ── DOM refs ──
const form              = document.getElementById('routineForm');
const stepForm          = document.getElementById('step-form');
const stepLoading       = document.getElementById('step-loading');
const stepResult        = document.getElementById('step-result');
const loadingFill       = document.getElementById('loadingFill');
const loadingMsg        = document.getElementById('loadingMsg');
const routineOutput     = document.getElementById('routineOutput');
const resultMeta        = document.getElementById('resultMeta');
const btnRestart        = document.getElementById('btnRestart');
const examDateInput     = document.getElementById('examDate');
const daysRemaining     = document.getElementById('daysRemaining');
const hoursSlider       = document.getElementById('studyHours');
const hoursValue        = document.getElementById('hoursValue');
const uploadZone        = document.getElementById('uploadZone');
const uploadInput       = document.getElementById('syllabusUpload');
const uploadPreviews    = document.getElementById('uploadPreviews');
const uploadPlaceholder = document.getElementById('uploadPlaceholder');

let selectedLevel  = 'SSC';
let uploadedImages = [];

// ── Level toggle ──
document.getElementById('btnSSC').addEventListener('click', () => setLevel('SSC'));
document.getElementById('btnHSC').addEventListener('click', () => setLevel('HSC'));

function setLevel(val) {
  selectedLevel = val;
  document.getElementById('btnSSC').classList.toggle('active', val === 'SSC');
  document.getElementById('btnHSC').classList.toggle('active', val === 'HSC');
  document.getElementById('levelInput').value = val;
}

// ── Date → days remaining ──
examDateInput.addEventListener('change', () => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const exam = new Date(examDateInput.value);
  const diff = Math.ceil((exam - today) / (1000 * 60 * 60 * 24));
  if (diff > 0) {
    daysRemaining.textContent = `${diff} days remaining`;
  } else if (diff === 0) {
    daysRemaining.textContent = 'Exam is today!';
  } else {
    daysRemaining.textContent = 'Please pick a future date';
  }
});

// ── Hours slider ──
hoursSlider.addEventListener('input', () => {
  hoursValue.textContent = `${hoursSlider.value} hrs`;
});

// ── Upload zone ──
uploadZone.addEventListener('click', () => uploadInput.click());

uploadZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));

uploadZone.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadZone.classList.remove('dragover');
  handleFiles(Array.from(e.dataTransfer.files));
});

uploadInput.addEventListener('change', () => {
  handleFiles(Array.from(uploadInput.files));
});

function handleFiles(files) {
  const allowed = files.filter(f => f.type.startsWith('image/')).slice(0, 3);
  uploadedImages = allowed;
  uploadPreviews.innerHTML = '';
  if (allowed.length > 0) {
    uploadPlaceholder.style.display = 'none';
    allowed.forEach(file => {
      const img    = document.createElement('img');
      img.className = 'preview-thumb';
      img.src       = URL.createObjectURL(file);
      uploadPreviews.appendChild(img);
    });
  } else {
    uploadPlaceholder.style.display = 'flex';
  }
}

// ── Convert images to base64 ──
async function toBase64(file) {
  return new Promise((resolve, reject) => {
    const reader  = new FileReader();
    reader.onload  = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// ── Loading animation ──
const loadingMessages = [
  'Analyzing your syllabus and exam timeline...',
  'Calculating subject weights and priorities...',
  'Distributing study sessions across days...',
  'Scheduling revision and mock test slots...',
  'Finalizing your personalized routine...',
];

function animateLoading() {
  let progress = 0;
  let msgIndex  = 0;
  const interval = setInterval(() => {
    progress = Math.min(progress + Math.random() * 14, 92);
    loadingFill.style.width = `${progress}%`;
    if (msgIndex < loadingMessages.length - 1) {
      msgIndex++;
      loadingMsg.textContent = loadingMessages[msgIndex];
    }
  }, 900);
  return interval;
}

// ── Show / hide steps ──
function showStep(id) {
  [stepForm, stepLoading, stepResult].forEach(el => el.classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');
}

// ── Form submit ──
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const examDate = examDateInput.value;
  const subjects = document.getElementById('subjects').value.trim();
  const hours    = hoursSlider.value;
  const today    = new Date();
  today.setHours(0, 0, 0, 0);
  const exam     = new Date(examDate);
  const daysLeft = Math.ceil((exam - today) / (1000 * 60 * 60 * 24));

  if (daysLeft <= 0) {
    alert('Please select a future exam date.');
    return;
  }

  showStep('step-loading');
  const loadingInterval = animateLoading();

  const messageContent = [];

  for (const img of uploadedImages) {
    const b64 = await toBase64(img);
    messageContent.push({
      type: 'image_url',
      image_url: { url: `data:${img.type};base64,${b64}` }
    });
  }

  const displayDays = Math.min(daysLeft, 60);

  messageContent.push({
    type: 'text',
    text: `You are an expert academic planner for Bangladeshi students.

Create a detailed day-by-day exam preparation routine for the following student:

- Level: ${selectedLevel}
- Subjects: ${subjects}
- Days until exam: ${daysLeft} (show ${displayDays} days in the plan)
- Available study hours per day: ${hours} hours
${uploadedImages.length > 0 ? '- Syllabus images are attached — use the topics visible in them to plan specific chapters per day.' : ''}

Rules:
1. Return ONLY valid JSON. No markdown, no backticks, no explanation.
2. The JSON must be an array of day objects.
3. Each day object has: "day" (number), "date" (YYYY-MM-DD starting from today+1), "sessions" (array).
4. Each session has: "time" (e.g. "8:00 AM - 9:30 AM"), "subject" (string), "detail" (what to study specifically), "tag" (one of: study, revision, break, mock).
5. Include short breaks (15-30 min) as sessions with tag "break".
6. In the last 20% of days, increase revision and mock sessions.
7. Spread subjects evenly — do not repeat the same subject more than twice in one day.
8. Today's date is ${new Date().toISOString().split('T')[0]}.

Return only the JSON array.`
  });

  try {
    if (!GROQ_API_KEY) {
      throw new Error('Missing Groq API key. Set VITE_GROQ_API_KEY in frontend/.env.');
    }

    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GROQ_API_KEY}`
      },
      body: JSON.stringify({
        model: 'meta-llama/llama-4-scout-17b-16e-instruct',
        max_tokens: 8000,
        temperature: 0.4,
        messages: [{ role: 'user', content: messageContent }]
      })
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(`Groq API error ${response.status}: ${data.error?.message || JSON.stringify(data)}`);
    }

    clearInterval(loadingInterval);
    loadingFill.style.width = '100%';
    await new Promise(r => setTimeout(r, 400));

    const raw   = data.choices?.[0]?.message?.content || '';
    const clean = raw.replace(/```json|```/g, '').trim();
    const days  = JSON.parse(clean);

    renderRoutine(days, { level: selectedLevel, subjects, daysLeft, hours, examDate });
    showStep('step-result');

  } catch (err) {
    clearInterval(loadingInterval);
    console.error(err);
    alert(`Something went wrong generating your routine. ${err.message || 'Please check your API key and try again.'}`);
    showStep('step-form');
  }
});

// ── Render routine ──
function renderRoutine(days, meta) {
  localStorage.setItem('amplify_routine', JSON.stringify(days));

  resultMeta.innerHTML = `
    <span class="meta-chip">📚 ${meta.level}</span>
    <span class="meta-chip">📅 ${meta.daysLeft} days to exam</span>
    <span class="meta-chip">⏱ ${meta.hours} hrs/day</span>
    <span class="meta-chip">🎯 ${meta.subjects}</span>
  `;

  routineOutput.innerHTML = days.map((day, i) => {
    const sessions = day.sessions.map(s => `
      <div class="session-row">
        <span class="session-time">${s.time}</span>
        <div>
          <div class="session-subject">${s.subject}</div>
          <div class="session-detail">${s.detail}</div>
        </div>
        <span class="session-tag tag-${s.tag}">${s.tag}</span>
      </div>
    `).join('');

    return `
      <div class="routine-day ${i === 0 ? 'open' : ''}" id="day-${i}">
        <div class="routine-day-header" onclick="toggleDay(${i})">
          <div>
            <h3>Day ${day.day}</h3>
            <span class="day-date">${formatDate(day.date)}</span>
          </div>
          <span class="day-toggle">▼</span>
        </div>
        <div class="routine-day-body">
          ${sessions}
        </div>
      </div>
    `;
  }).join('');
}

// ── Toggle day accordion ──
window.toggleDay = function(i) {
  document.getElementById(`day-${i}`).classList.toggle('open');
};

// ── Format date ──
function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' });
}

// ── Restart ──
btnRestart.addEventListener('click', () => {
  form.reset();
  uploadedImages = [];
  uploadPreviews.innerHTML   = '';
  uploadPlaceholder.style.display = 'flex';
  hoursValue.textContent     = '6 hrs';
  daysRemaining.textContent  = '';
  setLevel('SSC');
  showStep('step-form');
});

// ── Navbar scroll ──
window.addEventListener('scroll', () => {
  const header = document.getElementById('header');
  if (header) header.classList.toggle('scrolled', window.scrollY > 50);
});