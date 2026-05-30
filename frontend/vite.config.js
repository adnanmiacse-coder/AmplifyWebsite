import { defineConfig } from 'vite';

// Determine backend URL based on environment
const backendUrl = process.env.VITE_BACKEND_URL || 'http://localhost:8000';

export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: backendUrl,
        changeOrigin: true,
      },
      '/turn': {
        target: backendUrl,
        changeOrigin: true,
      },
      '/generate': {
        target: backendUrl,
        changeOrigin: true,
      },
      '/videos': {
        target: backendUrl,
        changeOrigin: true,
      },
    },
  },
});

