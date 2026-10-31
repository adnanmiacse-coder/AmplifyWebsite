(function () {
  'use strict';

  // ═════════════════════════════════════════════════════════════════════════
  // 1. UNIVERSAL AI PROMPT ENFORCEMENT: NO FRACTIONAL DIGITS / USE DECIMALS
  // ═════════════════════════════════════════════════════════════════════════
  const numericFormattingInstruction =
    'CRITICAL NUMERIC FORMATTING RULE: Do not ever mention or use any fractional digits or fraction notation (such as 1/2, 3/4, or fractions). If a fractional digit or fraction appears, ensure it is converted to and written as a decimal number (for example, write 1/2 as 0.5, 3/4 as 0.75, 1/4 as 0.25; use approximate decimals for repeating values). Never output fractions or fractional digits; express all fractional values strictly as decimal numbers throughout your response.';

  // Intercept all fetch requests to AI endpoints (Groq, OpenRouter, Cerebras, Gemini, OpenAI, etc.)
  const originalFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    const url = typeof input === 'string' || input instanceof URL ? String(input) : input?.url || '';
    const body = init?.body;

    if (typeof body === 'string' && (/\/chat\/completions(?:[?#]|$)|:generateContent(?:[?#]|$)/i.test(url) || /cerebras\.ai|openrouter\.ai|api\.groq\.com|api\.openai\.com/i.test(url))) {
      try {
        const payload = JSON.parse(body);

        if (Array.isArray(payload.messages)) {
          const systemMessage = payload.messages.find((message) => message.role === 'system');
          if (systemMessage) {
            if (typeof systemMessage.content === 'string') {
              if (!systemMessage.content.includes(numericFormattingInstruction)) {
                systemMessage.content = `${systemMessage.content}\n\n${numericFormattingInstruction}`;
              }
            } else if (Array.isArray(systemMessage.content)) {
              systemMessage.content.push({ type: 'text', text: numericFormattingInstruction });
            } else {
              systemMessage.content = numericFormattingInstruction;
            }
          } else {
            payload.messages.unshift({ role: 'system', content: numericFormattingInstruction });
          }
        }

        if (/:generateContent/i.test(url) || payload.contents || payload.systemInstruction || payload.system_instruction) {
          const instructionKey = payload.system_instruction ? 'system_instruction' : 'systemInstruction';
          const instruction = payload[instructionKey];
          if (typeof instruction === 'string') {
            payload[instructionKey] = {
              parts: [{ text: instruction }, { text: numericFormattingInstruction }],
            };
          } else if (instruction && Array.isArray(instruction.parts)) {
            instruction.parts.push({ text: numericFormattingInstruction });
          } else {
            payload[instructionKey] = {
              parts: [{ text: numericFormattingInstruction }],
            };
          }
        }

        init = { ...init, body: JSON.stringify(payload) };
      } catch (error) {
        console.warn('Amplify AI response-format interceptor pass-through:', error);
      }
    }

    return originalFetch(input, init);
  };

  // ═════════════════════════════════════════════════════════════════════════
  // 2. BULLETPROOF NAVIGATION STACK & REFRESH-SAFE PRIOR PAGE ARROW
  // ═════════════════════════════════════════════════════════════════════════
  const NAV_STACK_KEY = 'amplify_nav_stack';

  function getNavStack() {
    try {
      const raw = sessionStorage.getItem(NAV_STACK_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  function saveNavStack(stack) {
    try {
      sessionStorage.setItem(NAV_STACK_KEY, JSON.stringify(stack));
    } catch {}
  }

  function normalizePath(urlStr) {
    try {
      const u = new URL(urlStr, window.location.origin);
      let p = u.pathname;
      if (p.endsWith('/') && p.length > 1) p = p.slice(0, -1);
      return p + u.search;
    } catch {
      return urlStr;
    }
  }

  function getCanonicalPage(path) {
    const clean = (path || '').split('?')[0].replace(/\/+$/, '') || '/';
    return clean;
  }

  function recordNavigationAndGetPrior() {
    const currentPath = normalizePath(window.location.pathname + window.location.search);
    const canonical = getCanonicalPage(currentPath);
    const isHomePage = canonical === '/' || canonical === '/index.html' || canonical === '/index';

    if (isHomePage) {
      saveNavStack(['/index.html']);
      return null;
    }

    let stack = getNavStack().filter((item) => typeof item === 'string' && item.length > 0);

    if (stack.length === 0) {
      let referrerPath = null;
      if (document.referrer) {
        try {
          const refUrl = new URL(document.referrer);
          if (refUrl.origin === window.location.origin) {
            referrerPath = normalizePath(refUrl.pathname + refUrl.search);
          }
        } catch {}
      }
      if (referrerPath && getCanonicalPage(referrerPath) !== canonical) {
        stack = [referrerPath, currentPath];
      } else {
        stack = ['/index.html', currentPath];
      }
    } else {
      const top = stack[stack.length - 1];
      if (getCanonicalPage(top) === canonical) {
        // REFRESH DETECTED: Top of stack matches current page. Keep prior history unchanged!
        stack[stack.length - 1] = currentPath;
      } else if (stack.length >= 2 && getCanonicalPage(stack[stack.length - 2]) === canonical) {
        // Back navigation detected
        stack.pop();
        stack[stack.length - 1] = currentPath;
      } else {
        // Forward navigation to a new subpage
        if (stack.length > 25) stack = stack.slice(-15);
        stack.push(currentPath);
      }
    }

    saveNavStack(stack);

    let prior = '/index.html';
    if (stack.length >= 2) {
      prior = stack[stack.length - 2];
    }
    return prior;
  }

  function setupBackButton() {
    const canonical = getCanonicalPage(window.location.pathname);
    const isHomePage = canonical === '/' || canonical === '/index.html' || canonical === '/index';
    if (isHomePage) return;

    const priorPage = recordNavigationAndGetPrior() || '/index.html';

    // Hook existing back elements if present on the page
    document.querySelectorAll('[data-amplify-back], .nav-back, #btnGoBack, .btn-go-back, #backToClassroom').forEach((el) => {
      if (el.tagName === 'A' && (!el.getAttribute('href') || el.getAttribute('href') === 'javascript:history.back()' || el.getAttribute('href') === '#')) {
        el.setAttribute('href', priorPage);
      }
      el.addEventListener('click', (event) => {
        event.preventDefault();
        window.location.assign(priorPage);
      });
    });

    if (document.querySelector('.amplify-platform-back')) return;

    // Create platform back arrow button
    const backBtn = document.createElement('a');
    backBtn.href = priorPage;
    backBtn.className = 'amplify-platform-back';
    backBtn.dataset.amplifyBack = '';
    backBtn.setAttribute('aria-label', 'Go back to prior page');
    backBtn.setAttribute('title', `Go back to previous page (${priorPage})`);
    backBtn.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      <span class="back-text">Back</span>
    `;

    backBtn.addEventListener('click', (event) => {
      event.preventDefault();
      // Remove current page from stack before navigation
      const stack = getNavStack();
      if (stack.length >= 2) {
        stack.pop();
        saveNavStack(stack);
      }
      window.location.assign(priorPage);
    });

    const style = document.createElement('style');
    style.textContent = `
      .amplify-platform-back {
        position: fixed;
        top: max(16px, env(safe-area-inset-top));
        left: max(16px, env(safe-area-inset-left));
        z-index: 2147483000;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border: 1px solid rgba(0, 255, 136, 0.35);
        border-radius: 999px;
        background: rgba(8, 15, 25, 0.88);
        color: #00ff88;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-decoration: none;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 12px rgba(0, 255, 136, 0.15);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        cursor: pointer;
      }
      .amplify-platform-back:hover,
      .amplify-platform-back:focus-visible {
        background: rgba(0, 255, 136, 0.15);
        border-color: #00ff88;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 255, 136, 0.35);
        outline: none;
      }
      .amplify-platform-back:active {
        transform: translateY(0);
      }
      @media (max-width: 640px) {
        .amplify-platform-back .back-text {
          display: none;
        }
        .amplify-platform-back {
          padding: 8px;
          width: 38px;
          height: 38px;
          justify-content: center;
        }
      }
    `;

    document.head.appendChild(style);
    document.body.appendChild(backBtn);
  }

// ═════════════════════════════════════════════════════════════════════════
  // 3. AMPLIFY VOICE & LANGUAGE SYSTEM (ENGLISH / BANGLA TOGGLE + TTS)
  // ═════════════════════════════════════════════════════════════════════════
  const LANG_STORAGE_KEY = 'amplify_voice_lang';
  const TARGET_PAGES_REGEX = /(?:classroom|biology|tutor|deeplearn|pdf-tutor)/i;

  const AmplifyVoice = {
    getLanguage() {
      try {
        const saved = localStorage.getItem(LANG_STORAGE_KEY);
        if (saved === 'en' || saved === 'bn') return saved;
      } catch {}
      return 'en'; // English is primary by default
    },

    setLanguage(lang) {
      if (lang !== 'en' && lang !== 'bn') lang = 'en';
      try {
        localStorage.setItem(LANG_STORAGE_KEY, lang);
      } catch {}

      // Update all toggle buttons in DOM
      document.querySelectorAll('.amplify-lang-btn').forEach((btn) => {
        const isCurrent = btn.dataset.lang === lang;
        btn.classList.toggle('active', isCurrent);
        btn.setAttribute('aria-pressed', isCurrent ? 'true' : 'false');
      });

      // Notify entire application
      window.dispatchEvent(new CustomEvent('amplify-lang-change', { detail: { lang } }));
      AmplifyVoice.showToast(lang === 'en' ? 'Voice & Response: English' : 'কণ্ঠস্বর ও রেসপন্স: বাংলা');
      return lang;
    },

    isEnglish() {
      return this.getLanguage() === 'en';
    },

    isBangla() {
      return this.getLanguage() === 'bn';
    },

    onLanguageChange(callback) {
      window.addEventListener('amplify-lang-change', (e) => callback(e.detail.lang));
    },

    // Enhanced voice discovery with ranking
    getBestVoices(targetLang) {
      const lang = targetLang || this.getLanguage();
      const all = typeof window !== 'undefined' && window.speechSynthesis ? window.speechSynthesis.getVoices() : [];

      if (lang === 'bn') {
        const bnVoices = all.filter((v) => {
          const l = (v.lang || '').toLowerCase();
          const n = (v.name || '').toLowerCase();
          return l.startsWith('bn') || l.includes('bengali') || n.includes('bangla') || n.includes('bengali') || n.includes('বাংলা');
        });

        // Sort by quality: Nabonita, Pradeep, Google, Microsoft first
        bnVoices.sort((a, b) => {
          const score = (v) => {
            const name = (v.name || '').toLowerCase();
            if (name.includes('nabonita') || name.includes('নবনীতা')) return 100;
            if (name.includes('pradeep') || name.includes('প্রদীপ')) return 95;
            if (name.includes('google')) return 90;
            if (name.includes('natural') || name.includes('online')) return 85;
            if (name.includes('microsoft')) return 80;
            if (v.lang === 'bn-BD') return 70;
            if (v.lang === 'bn-IN') return 60;
            return 10;
          };
          return score(b) - score(a);
        });

        if (bnVoices.length > 0) return bnVoices;

        // Fallback to Hindi voices if browser has no Bangla voice
        const hiVoices = all.filter((v) => (v.lang || '').startsWith('hi'));
        return hiVoices.length > 0 ? hiVoices : all;
      }

      // English ranking
      const enVoices = all.filter((v) => (v.lang || '').toLowerCase().startsWith('en'));
      enVoices.sort((a, b) => {
        const score = (v) => {
          const name = (v.name || '').toLowerCase();
          if (name.includes('google uk english female')) return 100;
          if (name.includes('google us english')) return 98;
          if (name.includes('jenny') || name.includes('guy') || name.includes('aria')) return 95;
          if (name.includes('natural')) return 92;
          if (name.includes('samantha')) return 90;
          if (name.includes('victoria') || name.includes('karen') || name.includes('daniel')) return 85;
          if (name.includes('david') || name.includes('zira') || name.includes('mark')) return 80;
          if (name.includes('google')) return 75;
          if (v.lang === 'en-US') return 70;
          if (v.lang === 'en-GB') return 68;
          return 20;
        };
        return score(b) - score(a);
      });

      return enVoices.length > 0 ? enVoices : all;
    },

    showToast(msg) {
      let toast = document.getElementById('amplify-lang-toast');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'amplify-lang-toast';
        document.body.appendChild(toast);
      }
      toast.textContent = msg;
      toast.className = 'amplify-lang-toast show';
      clearTimeout(this._toastTimer);
      this._toastTimer = setTimeout(() => {
        toast.className = 'amplify-lang-toast';
      }, 2200);
    },

    setupLanguageToggle() {
      const canonical = getCanonicalPage(window.location.pathname);
      const isTargetPage = TARGET_PAGES_REGEX.test(canonical) || TARGET_PAGES_REGEX.test(window.location.href);
      if (!isTargetPage) return;

      if (document.querySelector('.amplify-platform-lang-toggle')) return;

      const currentLang = AmplifyVoice.getLanguage();

      const toggleWrap = document.createElement('div');
      toggleWrap.className = 'amplify-platform-lang-toggle';
      toggleWrap.setAttribute('role', 'group');
      toggleWrap.setAttribute('aria-label', 'Switch AI Voice and Response Language');

      toggleWrap.innerHTML = `
        <button type="button" class="amplify-lang-btn ${currentLang === 'en' ? 'active' : ''}" data-lang="en" title="English Voice and AI Responses">
          <span class="amplify-lang-flag">🇺🇸</span>
          <span class="amplify-lang-text">EN</span>
        </button>
        <button type="button" class="amplify-lang-btn ${currentLang === 'bn' ? 'active' : ''}" data-lang="bn" title="বাংলা কণ্ঠস্বর ও AI রেসপন্স">
          <span class="amplify-lang-flag">🇧🇩</span>
          <span class="amplify-lang-text">বাং</span>
        </button>
      `;

      toggleWrap.querySelectorAll('.amplify-lang-btn').forEach((btn) => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const target = btn.dataset.lang;
          AmplifyVoice.setLanguage(target);
        });
      });

      const style = document.createElement('style');
      style.textContent = `
        .amplify-platform-lang-toggle {
          position: fixed;
          top: max(16px, env(safe-area-inset-top));
          right: max(16px, env(safe-area-inset-right));
          z-index: 2147483000;
          display: inline-flex;
          align-items: center;
          padding: 3px;
          border-radius: 999px;
          background: rgba(10, 18, 30, 0.90);
          border: 1px solid rgba(0, 212, 255, 0.35);
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.55), 0 0 14px rgba(0, 212, 255, 0.20);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          user-select: none;
        }
        .amplify-lang-btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border: none;
          background: transparent;
          color: rgba(255, 255, 255, 0.65);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Hind Siliguri", sans-serif;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.03em;
          border-radius: 999px;
          cursor: pointer;
          transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .amplify-lang-btn:hover {
          color: #ffffff;
          background: rgba(255, 255, 255, 0.08);
        }
        .amplify-lang-btn.active {
          color: #030a14;
          background: linear-gradient(135deg, #00D4FF 0%, #00FF88 100%);
          box-shadow: 0 2px 10px rgba(0, 212, 255, 0.45);
        }
        .amplify-lang-flag {
          font-size: 13px;
          line-height: 1;
        }
        .amplify-lang-toast {
          position: fixed;
          bottom: 24px;
          left: 50%;
          transform: translateX(-50%) translateY(20px);
          background: rgba(8, 16, 28, 0.94);
          color: #00FF88;
          border: 1px solid rgba(0, 255, 136, 0.35);
          padding: 8px 18px;
          border-radius: 999px;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Hind Siliguri", sans-serif;
          font-size: 13px;
          font-weight: 600;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(10px);
          pointer-events: none;
          z-index: 2147483001;
          opacity: 0;
          transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .amplify-lang-toast.show {
          opacity: 1;
          transform: translateX(-50%) translateY(0);
        }
        @media (max-width: 640px) {
          .amplify-platform-lang-toggle {
            top: max(12px, env(safe-area-inset-top));
            right: max(12px, env(safe-area-inset-right));
          }
          .amplify-lang-btn {
            padding: 5px 9px;
            font-size: 11px;
            gap: 4px;
          }
        }
      `;

      document.head.appendChild(style);
      document.body.appendChild(toggleWrap);
    }
  };

  window.AmplifyVoice = AmplifyVoice;

    // ═════════════════════════════════════════════════════════════════════════
  // 4. SAME-TAB NAVIGATION ENFORCEMENT
  // ═════════════════════════════════════════════════════════════════════════
  function isInternalUrl(urlStr) {
    if (!urlStr || urlStr.startsWith('#') || urlStr.startsWith('javascript:') || urlStr.startsWith('mailto:') || urlStr.startsWith('tel:')) {
      return false;
    }
    try {
      const u = new URL(urlStr, window.location.origin);
      if (u.origin === window.location.origin) return true;
      if (u.hostname.includes('railway.app') || u.hostname.includes('amplifywebsite')) return true;
      return false;
    } catch {
      return !urlStr.startsWith('http://') && !urlStr.startsWith('https://');
    }
  }

  // Intercept all link clicks so internal links always navigate in the same tab
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a');
    if (!link) return;
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;

    if (isInternalUrl(href)) {
      if (link.getAttribute('target') === '_blank') {
        link.removeAttribute('target');
      }
      if (!event.ctrlKey && !event.metaKey && !event.shiftKey && event.button === 0) {
        event.preventDefault();
        try {
          const u = new URL(href, window.location.origin);
          window.location.assign(u.pathname + u.search + u.hash);
        } catch {
          window.location.assign(href);
        }
      }
    }
  }, true);

  // Intercept window.open for internal pages
  const originalWindowOpen = window.open.bind(window);
  window.open = function (url, target, features) {
    if (url && typeof url === 'string' && isInternalUrl(url)) {
      window.location.assign(url);
      return window;
    }
    return originalWindowOpen(url, target, features);
  };

  function initPlatformAddons() {
    setupBackButton();
    AmplifyVoice.setupLanguageToggle();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPlatformAddons, { once: true });
  } else {
    initPlatformAddons();
  }
})();
