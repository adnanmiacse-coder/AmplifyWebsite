import { defineConfig } from 'vite';

// Local dev: proxy API requests to Laravel to avoid CORS.
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'https://amplifywebsite-production.up.railway.app',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});

