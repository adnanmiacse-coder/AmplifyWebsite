import https from 'node:https';
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
          if (url.startsWith('/research/gifs')) {
            try {
              const parsed = new URL(req.url, 'http://localhost');
              const q = (parsed.searchParams.get('q') || '').trim().slice(0, 200);
              if (!q) {
                res.setHeader('Content-Type', 'application/json');
                res.end(JSON.stringify({ query: '', results: [] }));
                return;
              }
              const wikiUrl = 'https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=' + encodeURIComponent('filemime:image/gif ' + q + ' animation') + '&gsrnamespace=6&gsrlimit=10&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=640&format=json';
              
              
              const wReq = https.get(wikiUrl, {
                headers: { 'User-Agent': 'Amplify/1.0 (educational GIF references; https://amplifywebsite.edu)' }
              }, (wRes) => {
                let rawData = '';
                wRes.on('data', chunk => rawData += chunk);
                wRes.on('end', () => {
                  try {
                    const parsedData = JSON.parse(rawData);
                    const pages = parsedData?.query?.pages || {};
                    const results = [];
                    const seen = new Set();
                    for (const pid of Object.keys(pages)) {
                      const p = pages[pid];
                      const title = p.title || '';
                      if (!title.toLowerCase().endsWith('.gif')) continue;
                      const cleanTitle = title.startsWith('File:') ? title.slice(5) : title;
                      const ii = p.imageinfo?.[0];
                      if (!ii) continue;
                      const imgUrl = ii.thumburl || ii.url || '';
                      const fileUrl = ii.descriptionurl || '';
                      if (!imgUrl.startsWith('https://upload.wikimedia.org/') && !imgUrl.startsWith('https://thumb.wikimedia.org/')) continue;
                      if (!fileUrl.startsWith('https://commons.wikimedia.org/')) continue;
                      if (seen.has(imgUrl)) continue;
                      seen.add(imgUrl);
                      const meta = ii.extmetadata || {};
                      const rawArtist = meta.Artist?.value || '';
                      const artist = rawArtist.replace(/<[^>]+>/g, '').trim() || 'Wikimedia Commons contributor';
                      const rawLicense = meta.LicenseShortName?.value || meta.License?.value || '';
                      const license = rawLicense.replace(/<[^>]+>/g, '').trim() || 'Wikimedia Commons';
                      results.push({
                        title: cleanTitle,
                        image_url: imgUrl,
                        file_url: fileUrl,
                        artist: artist,
                        license: license
                      });
                      if (results.length >= 5) break;
                    }
                    res.setHeader('Content-Type', 'application/json');
                    res.end(JSON.stringify({ query: q, results }));
                  } catch (err) {
                    res.setHeader('Content-Type', 'application/json');
                    res.end(JSON.stringify({ query: q, results: [] }));
                  }
                });
              });
              wReq.on('error', () => {
                res.setHeader('Content-Type', 'application/json');
                res.end(JSON.stringify({ query: q, results: [] }));
              });
              return;
            } catch (err) {
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ query: '', results: [] }));
              return;
            }
          }
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
      '/research': {
        target: backendUrl,
        changeOrigin: true,
      },
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
