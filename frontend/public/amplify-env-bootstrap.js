/**
 * Environment bootstrap for static HTML pages
 * Loads API config from server and makes it available to inline scripts
 * Include this in a <script> tag before other scripts that use window.AMPLIFY_ENV
 */

(async function initAmplifyEnv() {
  try {
    const response = await fetch('/api/config', {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    if (response.ok) {
      const config = await response.json();
      window.AMPLIFY_ENV = window.AMPLIFY_ENV || {};
      window.AMPLIFY_ENV.GROQ_KEY = config.GROQ_API_KEY || '';
      window.AMPLIFY_ENV.GROQ_BASE = config.GROQ_API_BASE_URL || 'https://api.groq.com/openai/v1';
      window.AMPLIFY_ENV.CEREBRAS_KEY = config.CEREBRAS_API_KEY || '';
      window.AMPLIFY_ENV.CEREBRAS_BASE = config.CEREBRAS_API_BASE || 'https://api.cerebras.ai/v1';
      console.log('[AmplifyEnv] Config loaded from server');
    } else {
      console.warn('[AmplifyEnv] Failed to load config:', response.status);
    }
  } catch (error) {
    console.warn('[AmplifyEnv] Error:', error.message);
  }
})();
