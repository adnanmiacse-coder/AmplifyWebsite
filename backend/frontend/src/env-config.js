/**
 * Server-side environment configuration loader
 * Fetches API keys and config from backend endpoint instead of exposing them client-side
 * This keeps keys secure and prevents accidental commits to version control
 */

let _configCache = null;
let _configPromise = null;

/**
 * Fetch environment config from server
 * Caches result to avoid multiple requests
 */
export async function loadEnvConfig() {
  // Return cached config if available
  if (_configCache) {
    return _configCache;
  }

  // Return existing promise to avoid duplicate requests
  if (_configPromise) {
    return _configPromise;
  }

  // Fetch from server
  _configPromise = (async () => {
    const BACKEND_URL = (typeof window !== 'undefined' && window.AMPLIFY_ENV?.BACKEND_URL)
      || ((typeof import !== 'undefined' && import.meta && import.meta.env)
        ? import.meta.env.VITE_BACKEND_URL || ''
        : '');
    const apiUrl = BACKEND_URL ? `${BACKEND_URL.replace(/\/$/, '')}/api/config` : '/api/config';

    try {
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });

      if (!response.ok) {
        console.warn(`[EnvConfig] Failed to load config: ${response.status}`);
        return getDefaultConfig();
      }

      const data = await response.json();
      _configCache = data;
      return data;
    } catch (error) {
      console.warn('[EnvConfig] Error fetching config:', error.message);
      return getDefaultConfig();
    } finally {
      _configPromise = null;
    }
  })();

  return _configPromise;
}

/**
 * Get default (empty) config for fallback
 */
function getDefaultConfig() {
  return {
    GROQ_API_KEY: '',
    GROQ_API_BASE_URL: 'https://api.groq.com/openai/v1',
    CEREBRAS_API_KEY: '',
    CEREBRAS_API_BASE: 'https://api.cerebras.ai/v1',
    OPENROUTER_KEYS: [],
    OPENROUTER_BASE: 'https://openrouter.ai/api/v1',
    GEMINI_KEY: '',
    GEMINI_MODEL: 'gemini-2.0-flash-lite',
    GEMINI_BASE: 'https://generativelanguage.googleapis.com/v1beta/models',
  };
}

/**
 * Get a single config value (waits for load if not cached)
 */
export async function getConfig(key) {
  const config = await loadEnvConfig();
  return config[key] || '';
}

/**
 * Parse environment list (comma or newline separated values)
 */
export function parseEnvList(value) {
  if (!value) return [];
  const trimmed = String(value).trim();
  if (!trimmed) return [];
  try {
    const parsed = JSON.parse(trimmed);
    if (Array.isArray(parsed)) {
      return parsed.map(item => String(item).trim()).filter(Boolean);
    }
  } catch (e) {}
  return trimmed.split(/[\r\n,]+/).map(item => item.trim()).filter(Boolean);
}

// Initialize config load on module import (non-blocking)
if (typeof window !== 'undefined') {
  loadEnvConfig().catch(err => {
    console.warn('[EnvConfig] Background load error:', err.message);
  });
}
