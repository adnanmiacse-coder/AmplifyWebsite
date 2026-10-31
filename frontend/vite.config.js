import { defineConfig } from 'vite';
import { existsSync, readdirSync } from 'node:fs';
import { dirname, extname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Determine backend URL based on environment
const backendUrl = process.env.VITE_BACKEND_URL || 'http://localhost:8000';
const frontendRoot = dirname(fileURLToPath(import.meta.url));
const htmlEntries = [
  ...readdirSync(frontendRoot, { withFileTypes: true })
    .filter((entry) => entry.isFile() && extname(entry.name) === '.html')
    .map((entry) => join(frontendRoot, entry.name)),
  ...readdirSync(join(frontendRoot, 'teacher'), { withFileTypes: true })
    .filter((entry) => entry.isFile() && extname(entry.name) === '.html')
    .map((entry) => join(frontendRoot, 'teacher', entry.name)),
];

export default defineConfig({
  plugins: [
    {
      name: 'amplify-html-fallback',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          const url = (req.url || '').split('?')[0];
          if (!url.includes('.') && url !== '/') {
            const cleanPath = url.replace(/^\/+/, '');
            const candidate = join(frontendRoot, `${cleanPath}.html`);
            const teacherCandidate = join(frontendRoot, 'teacher', `${cleanPath.replace(/^teacher\/+/, '')}.html`);
            if (existsSync(candidate)) {
              req.url = req.url.replace(url, `/${cleanPath}.html`);
            } else if (existsSync(teacherCandidate)) {
              req.url = req.url.replace(url, `/teacher/${cleanPath.replace(/^teacher\/+/, '')}.html`);
            }
          }
          next();
        });
      },
    },
    {
      name: 'amplify-platform-script',
      transformIndexHtml() {
        return [{
          tag: 'script',
          attrs: { src: '/amplify-platform.js' },
          injectTo: 'head-prepend',
        }];
      },
    },
  ],
  build: {
    rollupOptions: {
      input: htmlEntries,
    },
  },
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
