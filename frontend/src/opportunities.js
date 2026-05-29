const RSS_SOURCES = [
  {
    url: 'https://opportunitydesk.org/feed/',
    label: 'Opportunity Desk',
    type: 'Scholarship'
  },
  {
    url: 'https://www.scholars4dev.com/feed/',
    label: 'Scholars4Dev',
    type: 'Scholarship'
  },
  {
    url: 'https://afterschoolafrica.com/feed/',
    label: 'After School Africa',
    type: 'Fellowship'
  },
  {
    url: 'https://www.findaphd.com/rss/scholarships.aspx',
    label: 'FindAPhD',
    type: 'Research'
  }
];

const RSS2JSON = 'https://api.rss2json.com/v1/api.json?api_key=k8cpzmwvb19t7zr8pxebcmmtfwppsnmvuwdppzjm&rss_url=';

let allOpportunities = [];
let activeFilter = 'ALL';

function guessType(title, sourceType) {
  const t = title.toLowerCase();
  if (t.includes('research') || t.includes('phd') || t.includes('postdoc')) return 'Research';
  if (t.includes('fellowship') || t.includes('fellow')) return 'Fellowship';
  if (t.includes('scholarship') || t.includes('grant') || t.includes('award')) return 'Scholarship';
  return sourceType;
}

function guessRegion(title, desc) {
  const text = (title + ' ' + desc).toLowerCase();
  if (text.includes('usa') || text.includes('united states') || text.includes('america')) return '🇺🇸 USA';
  if (text.includes('uk') || text.includes('united kingdom') || text.includes('britain') || text.includes('england')) return '🇬🇧 UK';
  if (text.includes('europe') || text.includes('germany') || text.includes('france') || text.includes('eu ')) return '🇪🇺 EU';
  if (text.includes('japan')) return '🇯🇵 Japan';
  if (text.includes('korea')) return '🇰🇷 Korea';
  if (text.includes('canada')) return '🇨🇦 Canada';
  if (text.includes('australia')) return '🇦🇺 Australia';
  return '🌍 International';
}

async function fetchSource(source) {
  try {
    const res  = await fetch(`${RSS2JSON}${encodeURIComponent(source.url)}&count=6`);
    const data = await res.json();
    if (data.status !== 'ok') return [];

    return data.items.map(item => ({
      title:  item.title,
      desc:   item.description.replace(/<[^>]+>/g, '').slice(0, 160) + '...',
      link:   item.link,
      date:   item.pubDate?.slice(0, 10) || '',
      source: source.label,
      type:   guessType(item.title, source.type),
      region: guessRegion(item.title, item.description || '')
    }));
  } catch {
    return [];
  }
}

async function loadOpportunities() {
  document.getElementById('oppStatus').textContent = 'Fetching live opportunities...';
  document.getElementById('oppCount').textContent  = '';
  document.getElementById('oppGrid').innerHTML = `
    <div class="card opp-skeleton"></div>
    <div class="card opp-skeleton"></div>
    <div class="card opp-skeleton"></div>
  `;

  const results = await Promise.all(RSS_SOURCES.map(fetchSource));
  allOpportunities = results.flat();

  const count = allOpportunities.length;
  document.getElementById('oppStatus').textContent = count > 0
    ? `Showing live opportunities from ${RSS_SOURCES.length} sources`
    : 'Could not load feeds — showing cached data';
  document.getElementById('oppCount').textContent = `${count} found`;

  // Fallback static data if all feeds fail
  if (count === 0) {
    allOpportunities = getFallbackData();
  }

  renderOpportunities();

  // Auto-refresh every 30 minutes
  setTimeout(loadOpportunities, 30 * 60 * 1000);
}

function setOppFilter(type, btn) {
  activeFilter = type;
  document.querySelectorAll('.opp-filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderOpportunities();
}

function renderOpportunities() {
  const query    = (document.getElementById('oppSearch')?.value || '').toLowerCase();
  const filtered = allOpportunities.filter(o => {
    const typeOk   = activeFilter === 'ALL' || o.type === activeFilter;
    const searchOk = !query || o.title.toLowerCase().includes(query) || o.source.toLowerCase().includes(query) || o.region.toLowerCase().includes(query);
    return typeOk && searchOk;
  });

  const grid = document.getElementById('oppGrid');

  if (filtered.length === 0) {
    grid.innerHTML = '<div class="opp-no-results">No opportunities found. Try a different filter.</div>';
    return;
  }

  const typeClass = { Scholarship: 'opp-type-scholarship', Research: 'opp-type-research', Fellowship: 'opp-type-fellowship' };

  grid.innerHTML = filtered.slice(0, 9).map(o => `
    <div class="card">
      <span class="opp-card-type ${typeClass[o.type] || 'opp-type-scholarship'}">${o.type}</span>
      <div class="opp-card-title">${o.title}</div>
      <div class="opp-card-source">${o.source} ${o.date ? '· ' + o.date : ''}</div>
      <div class="opp-card-desc">${o.desc}</div>
      <div class="opp-card-footer">
        <span class="opp-card-region">${o.region}</span>
        <a href="${o.link}" target="_blank" class="opp-card-link">View →</a>
      </div>
    </div>
  `).join('');
}

function getFallbackData() {
  return [
    { title: 'Chevening Scholarships 2025', desc: 'UK government scholarship for future leaders. Full funding for one-year masters degree at any UK university.', link: 'https://www.chevening.org', source: 'Chevening', type: 'Scholarship', region: '🇬🇧 UK', date: '' },
    { title: 'Fulbright Foreign Student Program', desc: 'Graduate study, advanced research, and teaching opportunities in the United States.', link: 'https://foreign.fulbrightonline.org', source: 'Fulbright', type: 'Scholarship', region: '🇺🇸 USA', date: '' },
    { title: 'DAAD Research Grants', desc: 'Research grants for doctoral candidates and young researchers to conduct research in Germany.', link: 'https://www.daad.de', source: 'DAAD', type: 'Research', region: '🇪🇺 EU', date: '' },
    { title: 'Gates Cambridge Scholarship', desc: 'Prestigious international scholarship at the University of Cambridge for outstanding postgraduate students.', link: 'https://www.gatescambridge.org', source: 'Gates Cambridge', type: 'Fellowship', region: '🇬🇧 UK', date: '' },
    { title: 'JSPS Postdoctoral Fellowship', desc: 'Opportunities for young foreign researchers to conduct research at Japanese universities.', link: 'https://www.jsps.go.jp', source: 'JSPS', type: 'Research', region: '🇯🇵 Japan', date: '' },
    { title: 'Erasmus Mundus Joint Masters', desc: 'Highly integrated international study programmes with monthly stipend across European universities.', link: 'https://eacea.ec.europa.eu/erasmus', source: 'EU Commission', type: 'Scholarship', region: '🇪🇺 EU', date: '' },
  ];
}

window.setOppFilter    = setOppFilter;
window.renderOpportunities = renderOpportunities;
window.loadOpportunities   = loadOpportunities;

window.addEventListener('load', loadOpportunities);