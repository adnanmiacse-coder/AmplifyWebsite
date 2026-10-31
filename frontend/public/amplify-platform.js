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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupBackButton, { once: true });
  } else {
    setupBackButton();
  }
})();
