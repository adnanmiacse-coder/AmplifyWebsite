const OPPORTUNITIES_APIS = ['/api/opportunities', '/ai/api/opportunities'];
const OPPORTUNITY_TYPES = new Set(['job', 'scholarship', 'fellowship', 'research', 'grant']);

const DEFAULT_OPPORTUNITIES = [
  {
    title: 'Chevening Scholarships',
    desc: 'UK government global scholarship programme offering full financial support for one-year master’s degrees at any UK university.',
    link: 'https://www.chevening.org/scholarships/',
    source: 'UK Foreign & Commonwealth Office',
    type: 'Scholarship',
    region: '🇬🇧 UK',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'Fulbright Foreign Student Program',
    desc: 'Fully funded graduate study, master’s and PhD programs at leading universities across the United States.',
    link: 'https://foreign.fulbrightonline.org/',
    source: 'US Department of State',
    type: 'Scholarship',
    region: '🇺🇸 USA',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'DAAD Research Grants - Doctoral Programmes',
    desc: 'Doctoral candidates and young academics can conduct research or complete PhDs at state-recognized universities in Germany.',
    link: 'https://www.daad.de/en/',
    source: 'German Academic Exchange (DAAD)',
    type: 'Research',
    region: '🇪🇺 EU',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'Gates Cambridge Scholarship',
    desc: 'Full-cost awards for outstanding applicants from countries outside the UK to pursue a full-time postgraduate degree at Cambridge.',
    link: 'https://www.gatescambridge.org/',
    source: 'University of Cambridge',
    type: 'Fellowship',
    region: '🇬🇧 UK',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'Erasmus Mundus Joint Master Degrees (EMJM)',
    desc: 'High-level integrated international study programmes with full EU-funded scholarships covering tuition, travel, and monthly allowance.',
    link: 'https://erasmus-plus.ec.europa.eu/opportunities/individuals/students/erasmus-mundus-joint-masters',
    source: 'European Commission',
    type: 'Scholarship',
    region: '🇪🇺 EU',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'JSPS Postdoctoral Fellowships for Research in Japan',
    desc: 'Fellowships providing opportunities for overseas researchers to conduct cooperative research with host researchers in Japan.',
    link: 'https://www.jsps.go.jp/english/e-fellow/',
    source: 'Japan Society for the Promotion of Science',
    type: 'Research',
    region: '🇯🇵 Japan',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'Swiss Government Excellence Scholarships',
    desc: 'Postgraduate scholarships for foreign scholars and researchers at Swiss public universities and federal institutes of technology.',
    link: 'https://www.sbfi.admin.ch/sbfi/en/home/education/scholarships-and-grants/swiss-government-excellence-scholarships.html',
    source: 'Federal Commission for Scholarships (FCS)',
    type: 'Fellowship',
    region: '🇪🇺 EU',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'Australia Awards Scholarships',
    desc: 'Long-term development awards administered by the Department of Foreign Affairs and Trade for study in Australian universities.',
    link: 'https://www.dfat.gov.au/people-to-people/australia-awards',
    source: 'Australian Government DFAT',
    type: 'Scholarship',
    region: '🇦🇺 Australia',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'MEXT Japanese Government Scholarships',
    desc: 'Full scholarships for undergraduate, research, and masters/doctoral studies at top Japanese universities funded by MEXT.',
    link: 'https://www.studyinjapan.go.jp/en/planning/scholarship/mext-scholarships/',
    source: 'Ministry of Education Japan (MEXT)',
    type: 'Scholarship',
    region: '🇯🇵 Japan',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'Rhodes Scholarship at Oxford',
    desc: 'The oldest graduate scholarship in the world, supporting exceptional students from across the globe to study at Oxford University.',
    link: 'https://www.rhodeshouse.ox.ac.uk/scholarships/the-rhodes-scholarship/',
    source: 'Rhodes Trust',
    type: 'Fellowship',
    region: '🇬🇧 UK',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'Commonwealth Scholarships',
    desc: 'Funded by the UK Foreign, Commonwealth & Development Office for master’s and PhD studies to contribute to sustainable development.',
    link: 'https://cscuk.fcdo.gov.uk/scholarships/',
    source: 'Commonwealth Scholarship Commission',
    type: 'Scholarship',
    region: '🇬🇧 UK',
    date: '',
    deadlineStatus: 'unknown'
  },
  {
    title: 'Swedish Institute Scholarships for Global Professionals',
    desc: 'Fully funded scholarship for full-time master’s studies in Sweden covering tuition, living expenses, insurance, and travel grant.',
    link: 'https://si.se/en/apply/scholarships/swedish-institute-scholarships-for-global-professionals/',
    source: 'Swedish Institute (SI)',
    type: 'Scholarship',
    region: '🇪🇺 EU',
    date: '',
    deadlineStatus: 'unknown'
  }
];

function normalizeOpportunities(items) {
  if (!Array.isArray(items)) return [];

  const seen = new Set();
  return items.reduce((validItems, item) => {
    if (!item || typeof item !== 'object') return validItems;

    const title = typeof item.title === 'string' ? item.title.trim() : '';
    const desc = typeof item.desc === 'string' ? item.desc.trim() : '';
    const source = typeof item.source === 'string' ? item.source.trim() : '';
    const type = typeof item.type === 'string' ? item.type.trim() : '';
    const region = typeof item.region === 'string' && item.region.trim()
      ? item.region.trim()
      : 'Not listed';
    const link = typeof item.link === 'string' ? item.link.trim() : '';

    let url;
    try {
      url = new URL(link);
    } catch {
      return validItems;
    }
    if (
      !title ||
      !desc ||
      !source ||
      !OPPORTUNITY_TYPES.has(type.toLowerCase()) ||
      !['http:', 'https:'].includes(url.protocol) ||
      url.username ||
      url.password
    ) {
      return validItems;
    }

    const date = typeof item.date === 'string' ? item.date.trim() : '';
    const requestedDeadlineStatus = typeof item.deadlineStatus === 'string'
      ? item.deadlineStatus.toLowerCase()
      : 'unknown';
    let deadlineStatus = ['rolling', 'confirmed'].includes(requestedDeadlineStatus)
      ? requestedDeadlineStatus
      : 'unknown';

    const deadlineTimestamp = Date.parse(`${date}T00:00:00Z`);
    if (
      deadlineStatus === 'confirmed' &&
      (
        !/^\d{4}-\d{2}-\d{2}$/.test(date) ||
        Number.isNaN(deadlineTimestamp) ||
        new Date(deadlineTimestamp).toISOString().slice(0, 10) !== date
      )
    ) {
      deadlineStatus = 'unknown';
    }
    if (
      deadlineStatus === 'confirmed' &&
      Date.parse(`${date}T23:59:59Z`) < Date.now()
    ) {
      return validItems;
    }

    const key = `${url.origin}${url.pathname.replace(/\/+$/, '')}`.toLowerCase();
    if (seen.has(key)) return validItems;
    seen.add(key);
    validItems.push({
      title,
      desc,
      source,
      type,
      region,
      link: url.href,
      date: deadlineStatus === 'confirmed' ? date : '',
      deadlineStatus
    });
    return validItems;
  }, []);
}

let allOpportunities = normalizeOpportunities(DEFAULT_OPPORTUNITIES);
let activeFilter = 'ALL';
let opportunityFeedStatus = 'loading';

function isCurrentLangBn() {
  const htmlLang = document.documentElement.lang;
  return htmlLang === 'bn' || localStorage.getItem('amplify_language') === 'bn';
}

function updateStatusText(count, status = opportunityFeedStatus) {
  const statusEl = document.getElementById('oppStatus');
  const countEl = document.getElementById('oppCount');
  const isBn = isCurrentLangBn();

  if (statusEl) {
    statusEl.textContent = status === 'loading'
      ? (isBn ? 'সুযোগ খোঁজা হচ্ছে...' : 'Loading public opportunities...')
      : status === 'live'
        ? (isBn ? 'লাইভ ফিড থেকে সুযোগ দেখানো হচ্ছে' : 'Showing opportunities from live feeds')
        : (isBn ? 'লাইভ ফিড অনুপলব্ধ — সংরক্ষিত সুযোগ দেখানো হচ্ছে; আবেদনের সময়সীমা যাচাই করুন' : 'Live feeds unavailable — showing saved programs; verify current deadlines');
  }
  if (countEl) {
    countEl.textContent = isBn ? `${count}টি পাওয়া গেছে` : `${count} opportunities`;
  }
}

async function loadOpportunities() {
  const grid = document.getElementById('oppGrid');
  if (!grid) return;

  renderOpportunities();
  opportunityFeedStatus = 'loading';
  updateStatusText(allOpportunities.length);

  try {
    let data;
    let opportunities;
    let lastError;
    for (const endpoint of OPPORTUNITIES_APIS) {
      try {
        const response = await fetch(endpoint, {
          cache: 'no-store',
          headers: { Accept: 'application/json' }
        });
        if (!response.ok) throw new Error(`Opportunity feed returned ${response.status}`);
        if (!response.headers.get('content-type')?.includes('application/json')) {
          throw new Error('Opportunity endpoint did not return JSON');
        }

        data = await response.json();
        opportunities = normalizeOpportunities(data.items);
        if (opportunities.length === 0) {
          throw new Error('Opportunity feed contained no valid listings');
        }
        break;
      } catch (error) {
        lastError = error;
      }
    }
    if (!opportunities) throw lastError || new Error('No opportunity endpoint responded');

    allOpportunities = opportunities;
    opportunityFeedStatus = data.status === 'fallback' ? 'fallback' : 'live';
    renderOpportunities();
    updateStatusText(allOpportunities.length);
  } catch (error) {
    console.warn('Unable to load live opportunities; keeping saved fallback data.', error);
    opportunityFeedStatus = 'fallback';
    updateStatusText(allOpportunities.length);
  }
}

function setOppFilter(type, btn) {
  activeFilter = type;
  document.querySelectorAll('.opp-filter-btn').forEach(button => button.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderOpportunities();
}

function createTextElement(tagName, className, text) {
  const element = document.createElement(tagName);
  element.className = className;
  element.textContent = text;
  return element;
}

function getDeadlineLabel(opportunity, isBn) {
  if (opportunity.deadlineStatus === 'rolling') {
    return isBn ? 'আবেদন চলমান' : 'Rolling deadline';
  }
  if (opportunity.deadlineStatus === 'confirmed' && opportunity.date) {
    return isBn ? `শেষ তারিখ: ${opportunity.date}` : `Deadline: ${opportunity.date}`;
  }
  return isBn ? 'আবেদনের শেষ তারিখ উল্লেখ নেই' : 'Deadline not listed';
}

function renderOpportunities() {
  const grid = document.getElementById('oppGrid');
  if (!grid) return;

  const query = (document.getElementById('oppSearch')?.value || '').trim().toLowerCase();
  const filtered = allOpportunities.filter(opportunity => {
    const typeMatches = activeFilter === 'ALL' ||
      opportunity.type.toLowerCase() === activeFilter.toLowerCase();
    const searchMatches = !query || [
      opportunity.title,
      opportunity.source,
      opportunity.region,
      opportunity.desc
    ].some(value => value.toLowerCase().includes(query));
    return typeMatches && searchMatches;
  });

  if (filtered.length === 0) {
    const isBn = isCurrentLangBn();
    grid.replaceChildren(createTextElement(
      'div',
      'opp-no-results',
      isBn ? 'কোনো সুযোগ পাওয়া যায়নি। অন্য ফিল্টার ব্যবহার করে দেখুন।' : 'No opportunities found. Try a different filter or search term.'
    ));
    return;
  }

  const typeClass = {
    job: 'opp-type-job',
    scholarship: 'opp-type-scholarship',
    research: 'opp-type-research',
    fellowship: 'opp-type-fellowship',
    grant: 'opp-type-scholarship'
  };
  const typeLabelBn = {
    job: 'চাকরি',
    scholarship: 'বৃত্তি',
    research: 'গবেষণা',
    fellowship: 'ফেলোশিপ',
    grant: 'অনুদান'
  };
  const isBn = isCurrentLangBn();
  const viewText = isBn ? 'বিস্তারিত দেখুন →' : 'View Details →';
  const cards = filtered.map(opportunity => {
    const card = document.createElement('article');
    card.className = 'card opp-card';

    card.append(
      createTextElement(
        'span',
        `opp-card-type ${typeClass[opportunity.type.toLowerCase()]}`,
        isBn ? typeLabelBn[opportunity.type.toLowerCase()] : opportunity.type
      ),
      createTextElement('div', 'opp-card-title', opportunity.title),
      createTextElement(
        'div',
        'opp-card-source',
        `${isBn ? 'উৎস' : 'Source'}: ${opportunity.source} · ${getDeadlineLabel(opportunity, isBn)}`
      ),
      createTextElement('div', 'opp-card-desc', opportunity.desc)
    );

    const footer = document.createElement('div');
    footer.className = 'opp-card-footer';
    footer.appendChild(createTextElement('span', 'opp-card-region', opportunity.region));

    const link = document.createElement('a');
    link.href = opportunity.link;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.className = 'opp-card-link';
    link.textContent = viewText;
    footer.appendChild(link);
    card.appendChild(footer);
    return card;
  });
  grid.replaceChildren(...cards);
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
  updateStatusText(allOpportunities.length);
});
