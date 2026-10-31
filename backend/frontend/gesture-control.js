/* AMPLIFY · HOLO GESTURE LINK v2
   Drop-in replacement for the old "Hand Gesture Control" <script> block.
   Keep the MediaPipe <script src=".../hands.js"> tag above it. */
(function () {
'use strict';

/* Let the voiceover module move the camera too (it reads window.targetDistance / targetSpherical,
   but those are `let` globals, so they were never visible there). */
try {
  Object.defineProperty(window, 'targetDistance',  { get: () => targetDistance,  set: v => { targetDistance = v; },  configurable: true });
  Object.defineProperty(window, 'targetSpherical', { get: () => targetSpherical, set: v => { targetSpherical = v; }, configurable: true });
} catch (e) {}

/* ── tuning knobs ── */
const GAIN_THETA = 6, GAIN_PHI = 4;   // palm → rotation sensitivity
const DWELL_MS   = 700;               // hold time for command gestures
const INERTIA    = 2.6;               // higher = spin stops sooner
const cl = (v, a, b) => Math.max(a, Math.min(b, v));

/* ── styles ── */
const st = document.createElement('style');
st.textContent = `
.gl-pip{position:absolute;top:16px;left:16px;width:208px;height:156px;border-radius:14px;overflow:hidden;border:1px solid rgba(74,240,196,.45);background:#000;z-index:9;display:none;box-shadow:0 0 28px rgba(74,240,196,.25)}
.gl-pip video{width:100%;height:100%;object-fit:cover;transform:scaleX(-1);opacity:.8}
.gl-pip::after{content:'';position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(74,240,196,.08) 0 1px,transparent 1px 3px);pointer-events:none}
.gl-fx{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:7;display:none}
.gl-chip{position:absolute;top:14px;left:50%;transform:translateX(-50%);z-index:9;display:none;font:500 11px var(--mono);letter-spacing:2px;color:var(--acc);background:rgba(5,8,15,.82);border:1px solid var(--border2);border-radius:999px;padding:6px 16px;backdrop-filter:blur(10px);white-space:nowrap;transition:background .2s,box-shadow .2s}
.gl-chip.flash{background:rgba(74,240,196,.28);box-shadow:0 0 26px rgba(74,240,196,.65)}
.gl-sheet{position:absolute;top:180px;left:16px;width:208px;z-index:9;display:none;background:rgba(9,14,26,.88);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:14px;padding:12px 14px;font:10px var(--mono);color:var(--txt2)}
.gl-sheet b{color:var(--acc);font-weight:500;letter-spacing:2px;font-size:9px;display:block;margin:8px 0 6px}
.gl-sheet b:first-child{margin-top:0}
.gl-sheet div{display:flex;justify-content:space-between;gap:8px;margin-bottom:4px}
.gl-sheet span{color:var(--txt)}
@media(max-width:768px){.gl-sheet{display:none!important}}`;
document.head.appendChild(st);

/* ── DOM ── */
const cw = document.querySelector('.canvas-wrap');
const pip = document.createElement('div'); pip.className = 'gl-pip';
const vid = document.createElement('video'); vid.autoplay = vid.muted = vid.playsInline = true; pip.appendChild(vid);
const fxC = document.createElement('canvas'); fxC.className = 'gl-fx';
const chipEl = document.createElement('div'); chipEl.className = 'gl-chip';
const sheet = document.createElement('div'); sheet.className = 'gl-sheet';
sheet.innerHTML = `<b>CONTINUOUS</b>
<div>🖐 Palm move<span>Rotate</span></div><div>✊ Fist move<span>Pan</span></div>
<div>🤏 Pinch + push/pull<span>Zoom</span></div><div>🙌 Two hands<span>Zoom + dial</span></div>
<b>HOLD 0.7s</b>
<div>👍 Thumbs up<span>AI voice</span></div><div>☝ Point<span>Auto-rotate</span></div>
<div>✌ Victory<span>Reset view</span></div><div>3 fingers<span>Wireframe</span></div>
<div>🤘 Rock<span>Next model</span></div><div>🤙 Shaka<span>Prev model</span></div>`;
cw.append(pip, fxC, chipEl, sheet);
const g = fxC.getContext('2d');

const btn = document.createElement('button');
btn.className = 'ctrl-btn'; btn.innerHTML = '✋ Gesture'; btn.title = 'Holo gesture control (G)';
document.querySelector('.viewer-controls').appendChild(btn);

/* ── One-Euro filter: heavy smoothing at rest, low lag when moving fast ── */
class OneEuro {
  constructor(mc = .8, b = 8, dc = 1) { this.mc = mc; this.b = b; this.dc = dc; this.reset(); }
  a(c, dt) { const r = 2 * Math.PI * c * dt; return r / (r + 1); }
  f(v, t) {
    if (this.x === null) { this.x = v; this.t = t; return v; }
    const dt = Math.max((t - this.t) / 1000, 1e-3); this.t = t;
    this.dx += this.a(this.dc, dt) * ((v - this.x) / dt - this.dx);
    this.x += this.a(this.mc + this.b * Math.abs(this.dx), dt) * (v - this.x);
    return this.x;
  }
  reset() { this.x = null; this.dx = 0; this.t = 0; }
}
const F  = [new OneEuro(), new OneEuro(), new OneEuro(1, 4, 1)];          // x, y, hand size
const F2 = [new OneEuro(), new OneEuro(), new OneEuro(), new OneEuro()];  // two-hand centres

/* ── state ── */
const S = { on: false, hands: null, stream: null, pose: null, cand: null, candN: 0, mode: null,
  px: 0, py: 0, vx: 0, vy: 0, t: 0, size0: 0, z0: 0, d0: 0, ang: 0,
  dwP: null, dwT: 0, prog: 0, latched: null, lastSeen: 0, lm: null, lm2: null, flashUntil: 0 };
let sk = [], sk2 = [], trail = [];

const LBL = { palm: 'PALM · ROTATE', fist: 'FIST · PAN', pinch: 'PINCH · PUSH / PULL TO ZOOM',
  victory: 'HOLD · RESET VIEW', point: 'HOLD · AUTO-ROTATE', thumbs: 'HOLD · AI VOICE',
  three: 'HOLD · WIREFRAME', rock: 'HOLD · NEXT MODEL', shaka: 'HOLD · PREVIOUS MODEL' };
const step = d => selectModel((window._currentModelData.idx + d + MODELS.length) % MODELS.length);
const CMDS = {
  victory: { label: 'VIEW RESET',      run: () => resetCamera() },
  point:   { label: 'AUTO-ROTATE',     run: () => toggleAutoRotate() },
  thumbs:  { label: 'AI VOICE TOGGLE', run: () => window.toggleVoiceover && window.toggleVoiceover() },
  three:   { label: 'WIREFRAME',       run: () => toggleWireframe() },
  rock:    { label: 'NEXT MODEL',      run: () => step(1) },
  shaka:   { label: 'PREVIOUS MODEL',  run: () => step(-1) },
};

let _chip = '';
function setChip(t) { if (performance.now() < S.flashUntil || t === _chip) return; _chip = t; chipEl.textContent = '◉ ' + t; }
let ac;
function blip(f = 880) {
  try {
    ac = ac || new (window.AudioContext || window.webkitAudioContext)();
    const o = ac.createOscillator(), v = ac.createGain(), n = ac.currentTime;
    o.frequency.setValueAtTime(f, n); o.frequency.exponentialRampToValueAtTime(f * 1.8, n + .12);
    v.gain.setValueAtTime(.06, n); v.gain.exponentialRampToValueAtTime(.001, n + .18);
    o.connect(v).connect(ac.destination); o.start(); o.stop(n + .2);
  } catch (e) {}
}
function fire(c) {
  try { c.run(); } catch (e) { console.error(e); }
  S.flashUntil = 0; _chip = ''; setChip('✓ ' + c.label); S.flashUntil = performance.now() + 900;
  chipEl.classList.add('flash'); setTimeout(() => chipEl.classList.remove('flash'), 600); blip();
}

/* ── hand analysis (rotation-invariant, normalised by hand size) ── */
const D = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
function analyse(lm) {
  const size = D(lm[0], lm[9]) || 1e-3;
  const ext = (t, p) => D(lm[t], lm[0]) > D(lm[p], lm[0]) * 1.12;
  const f = [ext(8, 6), ext(12, 10), ext(16, 14), ext(20, 18)];
  const cx = (lm[0].x + lm[5].x + lm[9].x + lm[13].x + lm[17].x) / 5;
  const cy = (lm[0].y + lm[5].y + lm[9].y + lm[13].y + lm[17].y) / 5;
  const thumbExt = D(lm[4], lm[17]) > D(lm[3], lm[17]) * 1.1 && D(lm[4], lm[5]) > size * .35;
  return { size, f, n: f.filter(Boolean).length, cx, cy, thumbExt,
    thumbUp: thumbExt && lm[4].y < lm[3].y - size * .15 && lm[4].y < lm[5].y,
    pinchR: D(lm[4], lm[8]) / size, idxOut: D(lm[8], { x: cx, y: cy }) / size };
}
function classify(a, prev) {
  const [i, m, r, p] = a.f, n = a.n;
  if (a.pinchR < (prev === 'pinch' ? .42 : .3) && a.idxOut > .65) return 'pinch';
  if (n === 4) return 'palm';
  if (n === 0) return a.thumbUp ? 'thumbs' : 'fist';
  if (i && n === 1) return 'point';
  if (i && m && n === 2) return 'victory';
  if (i && m && r && n === 3) return 'three';
  if (i && p && n === 2) return 'rock';
  if (p && n === 1 && a.thumbExt) return 'shaka';
  return null;
}
function stable(raw) {            // debounce: a pose must persist for a few frames
  if (raw === S.cand) S.candN++; else { S.cand = raw; S.candN = 1; }
  if (S.candN >= (raw ? 3 : 2)) S.pose = S.cand;
  return S.pose;
}

/* ── per-frame logic ── */
function single(lm, t) {
  const a = analyse(lm), x = F[0].f(1 - a.cx, t), y = F[1].f(a.cy, t), sz = F[2].f(a.size, t);
  S.lm = lm; S.lm2 = null;
  const pose = stable(classify(a, S.pose));
  const mode = { palm: 'rotate', fist: 'pan', pinch: 'zoom' }[pose] || null;
  if (mode !== S.mode) {
    if (mode !== null) S.vx = S.vy = 0;          // keep momentum only when releasing a rotate
    S.mode = mode; S.px = x; S.py = y; S.size0 = sz; S.z0 = targetDistance;
  }
  const dt = cl((t - S.t) / 1000, .008, .1); S.t = t;
  let dx = x - S.px, dy = y - S.py; S.px = x; S.py = y;
  if (Math.abs(dx) < .0008) dx = 0; if (Math.abs(dy) < .0008) dy = 0;

  if (mode === 'rotate') {                       // the model follows your palm
    targetSpherical.theta -= dx * GAIN_THETA;
    targetSpherical.phi = cl(targetSpherical.phi - dy * GAIN_PHI, .1, Math.PI - .1);
    S.vx = cl(S.vx + (dx / dt - S.vx) * .4, -2.5, 2.5); S.vy = cl(S.vy + (dy / dt - S.vy) * .4, -2.5, 2.5);
  } else if (mode === 'pan') {
    const ps = targetDistance * 1.1;
    targetPan.x = cl(targetPan.x - dx * ps, -3, 3); targetPan.y = cl(targetPan.y + dy * ps, -3, 3);
  } else if (mode === 'zoom') {                  // hand towards camera = zoom in
    targetDistance = cl(S.z0 / Math.pow(sz / S.size0, 1.8), .3, 20);
  }

  const cmd = CMDS[pose];                        // hold-to-confirm commands
  if (cmd && S.latched !== pose) {
    if (S.dwP !== pose) { S.dwP = pose; S.dwT = t; }
    S.prog = (t - S.dwT) / DWELL_MS;
    if (S.prog >= 1) { fire(cmd); S.latched = pose; S.prog = 0; }
  } else { S.dwP = null; S.prog = 0; if (pose !== S.latched) S.latched = null; }
  setChip(pose ? LBL[pose] : 'TRACKING…');
}

function dual(L, t) {                            // two hands: spread = zoom, turn = dial rotate
  const c = L.slice(0, 2).map(l => { const a = analyse(l); return { x: 1 - a.cx, y: a.cy }; });
  const ax = F2[0].f(c[0].x, t), ay = F2[1].f(c[0].y, t), bx = F2[2].f(c[1].x, t), by = F2[3].f(c[1].y, t);
  const d = Math.max(Math.hypot(ax - bx, ay - by), .05), ang = Math.atan2(by - ay, bx - ax);
  if (S.mode !== 'dual') { S.mode = 'dual'; S.d0 = d; S.z0 = targetDistance; S.ang = ang; S.vx = S.vy = 0; S.dwP = null; S.prog = 0; S.pose = null; }
  targetDistance = cl(S.z0 * Math.pow(S.d0 / d, 1.2), .3, 20);
  let da = ang - S.ang; if (da > Math.PI) da -= 2 * Math.PI; if (da < -Math.PI) da += 2 * Math.PI;
  S.ang = ang; targetSpherical.theta -= da * 1.3;
  S.lm = L[0]; S.lm2 = L[1]; setChip('DUAL LINK · SPREAD TO ZOOM · TURN TO DIAL');
}

function lose() {
  if (S.mode === 'dual' || (S.mode && S.mode !== 'rotate')) S.vx = S.vy = 0;
  S.mode = null; S.pose = S.cand = null; S.dwP = null; S.prog = 0; S.latched = null; S.lm = S.lm2 = null;
  F.concat(F2).forEach(f => f.reset()); setChip('SEARCHING FOR HAND…');
}
function onResults(res) {
  const t = performance.now(), L = res.multiHandLandmarks || [];
  if (!L.length) { if (t - S.lastSeen > 200 && (S.lm || S.mode)) lose(); return; }
  S.lastSeen = t;
  if (L.length >= 2) return dual(L, t);
  if (S.mode === 'dual') { S.mode = null; F.forEach(f => f.reset()); }
  single(L[0], t);
}

/* ── render loop: hologram overlay + inertia (runs at display rate) ── */
const BONES = [[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]];
const TIPS = [4, 8, 12, 16, 20];
function holo(lm, store, now, primary) {
  lm.forEach((p, i) => { const s = store[i] || (store[i] = { x: p.x, y: p.y }); s.x += (p.x - s.x) * .5; s.y += (p.y - s.y) * .5; });
  const c = { x: 0, y: 0 }; [0, 5, 9, 13, 17].forEach(i => { c.x += store[i].x / 5; c.y += store[i].y / 5; });
  const W = fxC.width, H = fxC.height, k = H * 1.25;
  const rx = (.5 + ((1 - c.x) - .5) * 1.2) * W, ry = (.5 + (c.y - .5) * 1.2) * H;
  const P = store.map(s => [rx + (c.x - s.x) * k * 1.333, ry + (s.y - c.y) * k]);
  g.save(); g.strokeStyle = g.fillStyle = '#4af0c4'; g.shadowColor = '#4af0c4'; g.shadowBlur = 14; g.lineWidth = 1.4; g.globalAlpha = .55;
  BONES.forEach(([a, b]) => { g.beginPath(); g.moveTo(...P[a]); g.lineTo(...P[b]); g.stroke(); });
  P.forEach((p, i) => { g.beginPath(); g.arc(p[0], p[1], TIPS.includes(i) ? 4 : 2, 0, 7); g.fill(); });
  g.globalAlpha = .9; g.lineWidth = 1.6; g.setLineDash([6, 8]); g.lineDashOffset = -now / 40;
  g.beginPath(); g.arc(rx, ry, 52, 0, 7); g.stroke(); g.setLineDash([]);
  if (primary) {
    if (S.prog > 0) { g.strokeStyle = g.shadowColor = '#f0c44a'; g.lineWidth = 4; g.beginPath(); g.arc(rx, ry, 62, -Math.PI / 2, -Math.PI / 2 + Math.min(S.prog, 1) * 2 * Math.PI); g.stroke(); }
    trail.push(P[8]); if (trail.length > 24) trail.shift();
  }
  g.restore();
  return [rx, ry];
}
function loop(now) {
  if (!S.on) return;
  requestAnimationFrame(loop);
  const dt = Math.min((now - (S.lt || now)) / 1000, .05); S.lt = now;
  if (S.mode === null && (Math.abs(S.vx) > .02 || Math.abs(S.vy) > .02)) {   // flick-to-spin inertia
    targetSpherical.theta -= S.vx * GAIN_THETA * dt;
    targetSpherical.phi = cl(targetSpherical.phi - S.vy * GAIN_PHI * dt, .1, Math.PI - .1);
    const kd = Math.exp(-dt * INERTIA); S.vx *= kd; S.vy *= kd;
  }
  const w = cw.clientWidth, h = cw.clientHeight;
  if (fxC.width !== w || fxC.height !== h) { fxC.width = w; fxC.height = h; }
  g.clearRect(0, 0, w, h);
  if (!S.lm) { trail.shift(); sk = []; sk2 = []; return; }
  const c1 = holo(S.lm, sk, now, true);
  if (S.lm2) {
    const c2 = holo(S.lm2, sk2, now, false);
    g.save(); g.strokeStyle = '#5b8fff'; g.shadowColor = '#5b8fff'; g.shadowBlur = 12; g.lineWidth = 1.5; g.setLineDash([4, 6]);
    g.beginPath(); g.moveTo(...c1); g.lineTo(...c2); g.stroke(); g.restore();
  } else sk2 = [];
  g.save(); g.lineCap = 'round'; g.shadowColor = '#4af0c4'; g.shadowBlur = 10;
  for (let i = 1; i < trail.length; i++) {
    g.strokeStyle = `rgba(74,240,196,${i / trail.length * .6})`; g.lineWidth = i / trail.length * 3;
    g.beginPath(); g.moveTo(...trail[i - 1]); g.lineTo(...trail[i]); g.stroke();
  }
  g.restore();
}

/* ── lifecycle ── */
async function pump() {
  if (!S.on || !S.hands) return;
  try { await S.hands.send({ image: vid }); } catch (e) {}
  requestAnimationFrame(pump);
}
async function start() {
  S.on = true; btn.classList.add('active'); btn.innerHTML = '✋ Gesture ON';
  [pip, fxC, chipEl, sheet].forEach(e => e.style.display = 'block');
  _chip = ''; setChip('CALIBRATING OPTICS…');
  try {
    S.stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' } });
    vid.srcObject = S.stream; await vid.play();
    S.hands = new Hands({ locateFile: f => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${f}` });
    S.hands.setOptions({ maxNumHands: 2, modelComplexity: 1, minDetectionConfidence: .65, minTrackingConfidence: .6 });
    S.hands.onResults(onResults); await S.hands.initialize();
    if (!S.on) return;
    setChip('LINK ESTABLISHED · SHOW YOUR HAND'); requestAnimationFrame(loop); pump();
  } catch (e) { console.error('Gesture cam:', e); setChip('CAMERA ERROR · CHECK PERMISSIONS'); }
}
function stop() {
  S.on = false; btn.classList.remove('active'); btn.innerHTML = '✋ Gesture';
  [pip, fxC, chipEl, sheet].forEach(e => e.style.display = 'none');
  if (S.stream) S.stream.getTracks().forEach(t => t.stop());
  try { S.hands && S.hands.close(); } catch (e) {}
  S.hands = S.stream = null; S.mode = S.pose = null; S.vx = S.vy = 0; S.lm = S.lm2 = null; trail = [];
}
btn.onclick = () => (S.on ? stop() : start());
window.addEventListener('keydown', e => { if ((e.key === 'g' || e.key === 'G') && !/input|textarea/i.test(e.target.tagName)) btn.onclick(); });
})();