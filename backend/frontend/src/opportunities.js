const OPPORTUNITIES_API = '/api/opportunities';

const DEFAULT_OPPORTUNITIES = [
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

let allOpportunities = [...DEFAULT_OPPORTUNITIES];
let activeFilter = 'ALL';

function isCurrentLangBn() {
  const htmlLang = document.documentElement.lang;
  return htmlLang === 'bn' || localStorage.getItem('amplify_language') === 'bn';
}

function updateStatusText(count, isLive = true) {
  const statusEl = document.getElementById('oppStatus');
  const countEl  = document.getElementById('oppCount');
  const isBn = isCurrentLangBn();

  if (statusEl) {
    if (isLive) {
      statusEl.textContent = isBn ? 'সরাসরি সুযোগ প্রদর্শিত হচ্ছে' : 'Showing opportunities from live feed';
    } else {
      statusEl.textContent = isBn ? 'আন্তর্জাতিক সুযোগসমূহ প্রদর্শিত হচ্ছে' : 'Showing verified opportunities';
    }
  }

  if (countEl) {
    countEl.textContent = isBn ? `${count}টি পাওয়া গেছে` : `${count} verified opportunities`;
  }
}

async function loadOpportunities() {
  const grid = document.getElementById('oppGrid');
  if (!grid) return;

  // Render immediately so user sees verified results with 0 delay
  renderOpportunities();
  updateStatusText(allOpportunities.length, false);

  // Try fetching API silently
  try {
    const res = await fetch(OPPORTUNITIES_API, { 
      cache: 'no-store',
      headers: { 'Accept': 'application/json' }
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.items) && data.items.length > 0) {
        allOpportunities = data.items;
        renderOpportunities();
        updateStatusText(allOpportunities.length, true);
      }
    }
  } catch (err) {
    // Graceful fallback to verified built-in dataset
  }
}

function setOppFilter(type, btn) {
  activeFilter = type;
  document.querySelectorAll('.opp-filter-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderOpportunities();
}

function renderOpportunities() {
  const searchInput = document.getElementById('oppSearch');
  const query = (searchInput?.value || '').trim().toLowerCase();

  const filtered = allOpportunities.filter(o => {
    const typeOk = activeFilter === 'ALL' || o.type.toLowerCase() === activeFilter.toLowerCase();
    const searchOk = !query || 
      o.title.toLowerCase().includes(query) || 
      (o.source && o.source.toLowerCase().includes(query)) || 
      (o.region && o.region.toLowerCase().includes(query)) ||
      (o.desc && o.desc.toLowerCase().includes(query));
    return typeOk && searchOk;
  });

  const grid = document.getElementById('oppGrid');
  if (!grid) return;

  if (filtered.length === 0) {
    const isBn = isCurrentLangBn();
    grid.innerHTML = `<div class="opp-no-results">${isBn ? 'কোনো সুযোগ পাওয়া যায়নি। অন্য ফিল্টার ব্যবহার করে দেখুন।' : 'No opportunities found. Try a different filter or search term.'}</div>`;
    return;
  }

  const typeClass = { 
    scholarship: 'opp-type-scholarship', 
    research: 'opp-type-research', 
    fellowship: 'opp-type-fellowship' 
  };

  const isBn = isCurrentLangBn();
  const viewText = isBn ? 'বিস্তারিত দেখুন →' : 'View Details →';

  grid.innerHTML = filtered.map(o => {
    const tLower = (o.type || 'Scholarship').toLowerCase();
    const badgeClass = typeClass[tLower] || 'opp-type-scholarship';
    const typeLabel = isBn ? (tLower === 'research' ? 'গবেষণা' : tLower === 'fellowship' ? 'ফেলোশিপ' : 'বৃত্তি') : o.type;

    return `
      <div class="card opp-card">
        <span class="opp-card-type ${badgeClass}">${typeLabel}</span>
        <div class="opp-card-title">${o.title}</div>
        <div class="opp-card-source">${o.source} ${o.date ? '· ' + o.date : ''}</div>
        <div class="opp-card-desc">${o.desc}</div>
        <div class="opp-card-footer">
          <span class="opp-card-region">${o.region || '🌍 International'}</span>
          <a href="${o.link}" target="_blank" rel="noopener noreferrer" class="opp-card-link">${viewText}</a>
        </div>
      </div>
    `;
  }).join('');
}

window.setOppFilter        = setOppFilter;
window.renderOpportunities = renderOpportunities;
window.loadOpportunities   = loadOpportunities;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadOpportunities);
} else {
  loadOpportunities();
}

window.addEventListener('amplify-lang-change', () => {
  renderOpportunities();
  updateStatusText(allOpportunities.length, true);
});
