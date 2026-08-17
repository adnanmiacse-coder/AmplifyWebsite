// ── Auto-inject favicon globally ──
(function() {
  if (!document.querySelector('link[rel="icon"]')) {
    const link = document.createElement('link');
    link.rel = 'icon';
    link.type = 'image/svg+xml';
    link.href = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%23020B16'/><text x='50%25' y='54%25' dominant-baseline='middle' text-anchor='middle' font-size='18' fill='%2300B7FF'>A</text></svg>";
    document.head.appendChild(link);
  }
})();


/**
 * Environment bootstrap for static HTML pages
 * Loads API config from server and makes it available to inline scripts
 * Include this in a <script> tag before other scripts that use window.AMPLIFY_ENV
 */

(async function initAmplifyEnv() {
  try {
    const origin = window.location?.origin || '';
    const host = window.location?.hostname || '';
    const configured = window.AMPLIFY_ENV?.BACKEND_URL || '';
    let base = '';
    if (configured) {
      try {
        const parsed = new URL(String(configured), origin);
        const isLocalHost = host === 'localhost' || host === '127.0.0.1';
        if (isLocalHost || parsed.origin === origin) {
          base = parsed.origin.replace(/\/$/, '');
        }
      } catch {}
    }
    const response = await fetch(base ? `${base}/api/config` : '/api/config', {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    if (response.ok) {
      const config = await response.json();
      const groqKeys = Array.isArray(config.GROQ_KEYS) && config.GROQ_KEYS.length
        ? config.GROQ_KEYS
        : (config.GROQ_API_KEY ? [config.GROQ_API_KEY] : []);
      const openRouterKeys = config.OPENROUTER_KEYS || config.OPENROUTER_API_KEYS || [];

      window.AMPLIFY_ENV = window.AMPLIFY_ENV || {};
      window.AMPLIFY_ENV.GROQ_KEYS = groqKeys;
      window.AMPLIFY_ENV.GROQ_KEY = config.GROQ_API_KEY || groqKeys[0] || '';
      window.AMPLIFY_ENV.GROQ_BASE = config.GROQ_API_BASE_URL || 'https://api.groq.com/openai/v1';
      window.AMPLIFY_ENV.OPENROUTER_KEYS = openRouterKeys;
      window.AMPLIFY_ENV.OPENROUTER_BASE = config.OPENROUTER_BASE || 'https://openrouter.ai/api/v1';
      window.AMPLIFY_ENV.CEREBRAS_KEY = config.CEREBRAS_API_KEY || '';
      window.AMPLIFY_ENV.CEREBRAS_BASE = config.CEREBRAS_API_BASE || 'https://api.cerebras.ai/v1';
      window.AMPLIFY_ENV.GEMINI_KEY = config.GEMINI_KEY || '';
      window.AMPLIFY_ENV.GEMINI_MODEL = config.GEMINI_MODEL || 'gemini-2.0-flash-lite';
      window.AMPLIFY_ENV.GEMINI_BASE = config.GEMINI_BASE || 'https://generativelanguage.googleapis.com/v1beta/models';
      window.AMPLIFY_ENV.AZURE_SPEECH_KEY = config.AZURE_SPEECH_KEY || '';
      window.AMPLIFY_ENV.AZURE_SPEECH_REGION = config.AZURE_SPEECH_REGION || '';
      console.log('[AmplifyEnv] Config loaded from server');
    } else {
      console.warn('[AmplifyEnv] Failed to load config:', response.status);
    }
  } catch (error) {
    console.warn('[AmplifyEnv] Error:', error.message);
  }
})();
