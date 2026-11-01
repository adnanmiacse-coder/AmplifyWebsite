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
          if (url === '/api/opportunities') {
            res.setHeader('Content-Type', 'application/json');
            res.setHeader('Cache-Control', 'no-cache');
            const items = [
              {
                title: 'Chevening Scholarships 2025/2026',
                desc: 'UK government global scholarship programme offering full financial support for one-year master’s degrees at any UK university.',
                link: 'https://www.chevening.org/scholarships/',
                source: 'UK Foreign & Commonwealth Office',
                type: 'Scholarship',
                region: '🇬🇧 UK',
                date: 'Applications Open'
              },
              {
                title: 'Fulbright Foreign Student Program',
                desc: 'Fully funded graduate study, master’s and PhD programs at leading universities across the United States.',
                link: 'https://foreign.fulbrightonline.org/',
                source: 'US Department of State',
                type: 'Scholarship',
                region: '🇺🇸 USA',
                date: 'Annual Cycle'
              },
              {
                title: 'DAAD Research Grants - Doctoral Programmes',
                desc: 'Doctoral candidates and young academics can conduct research or complete PhDs at state-recognized universities in Germany.',
                link: 'https://www.daad.de/en/',
                source: 'German Academic Exchange (DAAD)',
                type: 'Research',
                region: '🇪🇺 EU',
                date: 'Rolling Deadlines'
              },
              {
                title: 'Gates Cambridge Scholarship',
                desc: 'Full-cost awards for outstanding applicants from countries outside the UK to pursue a full-time postgraduate degree at Cambridge.',
                link: 'https://www.gatescambridge.org/',
                source: 'University of Cambridge',
                type: 'Fellowship',
                region: '🇬🇧 UK',
                date: 'Prestigious'
              },
              {
                title: 'Erasmus Mundus Joint Master Degrees (EMJM)',
                desc: 'High-level integrated international study programmes with full EU-funded scholarships covering tuition, travel, and monthly allowance.',
                link: 'https://erasmus-plus.ec.europa.eu/opportunities/individuals/students/erasmus-mundus-joint-masters',
                source: 'European Commission',
                type: 'Scholarship',
                region: '🇪🇺 EU',
                date: 'Multiple Fields'
              },
              {
                title: 'JSPS Postdoctoral Fellowships for Research in Japan',
                desc: 'Fellowships providing opportunities for overseas researchers to conduct cooperative research with host researchers in Japan.',
                link: 'https://www.jsps.go.jp/english/e-fellow/',
                source: 'Japan Society for the Promotion of Science',
                type: 'Research',
                region: '🇯🇵 Japan',
                date: 'Global Applicants'
              },
              {
                title: 'Swiss Government Excellence Scholarships',
                desc: 'Postgraduate scholarships for foreign scholars and researchers at Swiss public universities and federal institutes of technology.',
                link: 'https://www.sbfi.admin.ch/sbfi/en/home/education/scholarships-and-grants/swiss-government-excellence-scholarships.html',
                source: 'Federal Commission for Scholarships (FCS)',
                type: 'Fellowship',
                region: '🇪🇺 EU',
                date: 'Research/PhD'
              },
              {
                title: 'Australia Awards Scholarships',
                desc: 'Long-term development awards administered by the Department of Foreign Affairs and Trade for study in Australian universities.',
                link: 'https://www.dfat.gov.au/people-to-people/australia-awards',
                source: 'Australian Government DFAT',
                type: 'Scholarship',
                region: '🇦🇺 Australia',
                date: 'Full Funding'
              },
              {
                title: 'MEXT Japanese Government Scholarships',
                desc: 'Full scholarships for undergraduate, research, and masters/doctoral studies at top Japanese universities funded by MEXT.',
                link: 'https://www.studyinjapan.go.jp/en/planning/scholarship/mext-scholarships/',
                source: 'Ministry of Education Japan (MEXT)',
                type: 'Scholarship',
                region: '🇯🇵 Japan',
                date: 'Embassy Track'
              },
              {
                title: 'Rhodes Scholarship at Oxford',
                desc: 'The oldest graduate scholarship in the world, supporting exceptional students from across the globe to study at Oxford University.',
                link: 'https://www.rhodeshouse.ox.ac.uk/scholarships/the-rhodes-scholarship/',
                source: 'Rhodes Trust',
                type: 'Fellowship',
                region: '🇬🇧 UK',
                date: 'Postgraduate'
              },
              {
                title: 'Commonwealth Scholarships',
                desc: 'Funded by the UK Foreign, Commonwealth & Development Office for master’s and PhD studies to contribute to sustainable development.',
                link: 'https://cscuk.fcdo.gov.uk/scholarships/',
                source: 'Commonwealth Scholarship Commission',
                type: 'Scholarship',
                region: '🇬🇧 UK',
                date: 'Annual Cycle'
              },
              {
                title: 'Swedish Institute Scholarships for Global Professionals',
                desc: 'Fully funded scholarship for full-time master’s studies in Sweden covering tuition, living expenses, insurance, and travel grant.',
                link: 'https://si.se/en/apply/scholarships/swedish-institute-scholarships-for-global-professionals/',
                source: 'Swedish Institute (SI)',
                type: 'Scholarship',
                region: '🇪🇺 EU',
                date: 'Global Professionals'
              }
            ];
            res.end(JSON.stringify({ status: 'ok', count: items.length, items }));
            return;
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
