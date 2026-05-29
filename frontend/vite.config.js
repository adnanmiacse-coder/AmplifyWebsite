import { defineConfig } from 'vite';

// Local dev: proxy API requests to Laravel to avoid CORS.
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});

