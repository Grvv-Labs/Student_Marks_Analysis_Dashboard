/* =============================================================
   app.js — Student Marks Analysis Dashboard
   Fetches data from FastAPI backend, renders Chart.js charts,
   drives the SPA navigation, and populates all tables.
============================================================= */

const API = '';   // same origin

// ── Chart.js global defaults ────────────────────────────────
Chart.defaults.color = '#64748b';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'Inter', sans-serif";

// ── Grade palette ───────────────────────────────────────────
const GRADE_COLORS = {
  'F (<40)':    '#f87171',
  'C (40-59)':  '#fb923c',
  'B (60-79)':  '#facc15',
  'A (80-89)':  '#34d399',
  'A+ (90-100)':'#818cf8',
};

// ── SPA Navigation ──────────────────────────────────────────
const sections = document.querySelectorAll('.section');
const navLinks  = document.querySelectorAll('.nav-link');

function showSection(id) {
  sections.forEach(s => s.classList.toggle('active', s.id === id));
  navLinks.forEach(l => l.classList.toggle('active', l.dataset.section === id));
}

navLinks.forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    showSection(link.dataset.section);
    if (window.innerWidth < 768) sidebar.classList.remove('open');
  });
});

// Hamburger
const hamburger = document.getElementById('hamburger');
const sidebar   = document.getElementById('sidebar');
hamburger.addEventListener('click', () => sidebar.classList.toggle('open'));

// ── Animated counter ────────────────────────────────────────
function animateCount(el, target, decimals = 0, duration = 900) {
  const start = performance.now();
  function step(now) {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    const val = (target * ease).toFixed(decimals);
    el.textContent = decimals > 0 ? val : Number(val).toLocaleString();
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ── Fetch helpers ────────────────────────────────────────────
async function apiFetch(endpoint) {
  const res = await fetch(API + endpoint);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

// ══════════════════════════════════════════════════════════════
//  1. Stats Cards
// ══════════════════════════════════════════════════════════════
async function loadStats() {
  try {
    const d = await apiFetch('/api/stats');
    const map = [
      ['stat-students', d.total_students, 0],
      ['stat-avg',      d.overall_avg,    1],
      ['stat-high',     d.highest_mark,   0],
      ['stat-low',      d.lowest_mark,    0],
      ['stat-records',  d.total_records,  0],
      ['stat-subjects', d.subjects_count, 0],
    ];
    map.forEach(([id, val, dec]) => {
      const el = document.querySelector(`#${id} .stat-value`);
      if (el) animateCount(el, val, dec);
    });
  } catch (err) {
    console.error('Stats error:', err);
  }
}

// ══════════════════════════════════════════════════════════════
//  2. Subject Bar Chart
// ══════════════════════════════════════════════════════════════
async function loadSubjectChart() {
  try {
    const data = await apiFetch('/api/subject-averages');
    const labels = data.map(d => d.Subject);
    const values = data.map(d => d.average);

    const gradient = (ctx) => {
      const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 320);
      g.addColorStop(0, 'rgba(99,102,241,0.9)');
      g.addColorStop(1, 'rgba(56,189,248,0.6)');
      return g;
    };

    new Chart(document.getElementById('subjectBarChart'), {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Average Marks',
          data: values,
          backgroundColor: (ctx) => gradient(ctx),
          borderRadius: 8,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.parsed.y.toFixed(1)} marks`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            min: 50,
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: '#64748b' }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#94a3b8', font: { size: 11 } }
          }
        },
        animation: { duration: 1000, easing: 'easeOutQuart' }
      }
    });
  } catch (err) {
    console.error('Subject chart error:', err);
  }
}

// ══════════════════════════════════════════════════════════════
//  3. Grade Donut Chart + Legend
// ══════════════════════════════════════════════════════════════
async function loadGradeChart() {
  try {
    const data = await apiFetch('/api/grade-distribution');
    const labels = data.map(d => d.grade);
    const values = data.map(d => d.count);
    const colors = labels.map(l => GRADE_COLORS[l] || '#64748b');
    const total  = values.reduce((a, b) => a + b, 0);

    new Chart(document.getElementById('gradeDonutChart'), {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderColor: 'rgba(0,0,0,0.3)',
          borderWidth: 2,
          hoverOffset: 12,
        }]
      },
      options: {
        cutout: '65%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.label}: ${ctx.parsed} students (${((ctx.parsed/total)*100).toFixed(1)}%)`
            }
          }
        },
        animation: { animateRotate: true, duration: 1000 }
      }
    });

    // Legend
    const legend = document.getElementById('grade-legend-table');
    const max = Math.max(...values);
    data.forEach((d, i) => {
      const pct = ((d.count / total) * 100).toFixed(1);
      const barW = Math.round((d.count / max) * 100);
      legend.innerHTML += `
        <div class="grade-row">
          <div class="grade-dot" style="background:${colors[i]}"></div>
          <div class="grade-info">
            <div class="grade-name">${d.grade}</div>
            <div class="grade-count">${d.count.toLocaleString()} students · ${pct}%</div>
          </div>
          <div class="grade-bar-wrap">
            <div class="grade-bar-fill" style="width:${barW}%;background:${colors[i]}"></div>
          </div>
        </div>`;
    });
  } catch (err) {
    console.error('Grade chart error:', err);
  }
}

// ══════════════════════════════════════════════════════════════
//  4. Top Students Table
// ══════════════════════════════════════════════════════════════
async function loadTopStudents() {
  try {
    const data = await apiFetch('/api/top-students?limit=10');
    const tbody = document.getElementById('top-tbody');
    const maxTotal = data[0]?.total_marks || 1;

    tbody.innerHTML = data.map(s => {
      let rankClass = s.rank <= 3 ? `rank-${s.rank}` : 'rank-other';
      const barW = Math.round((s.total_marks / maxTotal) * 100);
      return `<tr>
        <td><span class="rank-badge ${rankClass}">${s.rank}</span></td>
        <td>${s.Student_ID}</td>
        <td><strong>${s.Student_Name}</strong></td>
        <td>${s.subjects_taken}</td>
        <td>${s.total_marks.toLocaleString()}</td>
        <td>${s.avg_marks.toFixed(1)}</td>
        <td>
          <div class="mini-bar-wrap">
            <div class="mini-bar-fill" style="width:${barW}%"></div>
          </div>
        </td>
      </tr>`;
    }).join('');
  } catch (err) {
    console.error('Top students error:', err);
  }
}

// ══════════════════════════════════════════════════════════════
//  5. Class Performance Chart
// ══════════════════════════════════════════════════════════════
async function loadClassChart() {
  try {
    const data = await apiFetch('/api/class-performance');
    const labels = data.map(d => d.Class);
    const values = data.map(d => d.average);

    const colorMap = ['#6366f1','#38bdf8','#34d399','#fb923c','#a78bfa','#f87171','#facc15','#818cf8'];

    new Chart(document.getElementById('classBarChart'), {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Average Marks',
          data: values,
          backgroundColor: labels.map((_, i) => colorMap[i % colorMap.length]),
          borderRadius: 8,
          borderSkipped: false,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.parsed.x.toFixed(1)} marks`
            }
          }
        },
        scales: {
          x: {
            beginAtZero: false,
            min: 50,
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: '#64748b' }
          },
          y: {
            grid: { display: false },
            ticks: { color: '#94a3b8', font: { size: 11 } }
          }
        },
        animation: { duration: 1000, easing: 'easeOutQuart' }
      }
    });
  } catch (err) {
    console.error('Class chart error:', err);
  }
}

// ══════════════════════════════════════════════════════════════
//  6. Student Explorer (search + pagination)
// ══════════════════════════════════════════════════════════════
let explorerPage = 1;
let explorerSearch = '';
let explorerTotal = 0;
const PER_PAGE = 20;

function perfClass(avg) {
  if (avg >= 85) return ['perf-excellent', '🌟 Excellent'];
  if (avg >= 70) return ['perf-good',      '👍 Good'];
  if (avg >= 50) return ['perf-average',   '📊 Average'];
  return               ['perf-poor',       '⚠️ Needs Work'];
}

async function loadExplorer() {
  try {
    const url = `/api/students?search=${encodeURIComponent(explorerSearch)}&page=${explorerPage}&per_page=${PER_PAGE}`;
    const d = await apiFetch(url);
    explorerTotal = d.total;

    document.getElementById('explorer-count').textContent =
      `${d.total.toLocaleString()} student${d.total !== 1 ? 's' : ''} found`;

    const tbody = document.getElementById('explorer-tbody');
    tbody.innerHTML = d.students.map(s => {
      const [cls, label] = perfClass(s.avg_marks);
      return `<tr>
        <td>${s.Student_ID}</td>
        <td>${s.Student_Name}</td>
        <td>${s.Class}</td>
        <td>${s.total_marks.toLocaleString()}</td>
        <td>${s.avg_marks.toFixed(1)}</td>
        <td><span class="perf-pill ${cls}">${label}</span></td>
      </tr>`;
    }).join('') || `<tr><td colspan="6" style="text-align:center;padding:24px;color:var(--muted)">No results found</td></tr>`;

    renderPagination(d.total, d.page);
  } catch (err) {
    console.error('Explorer error:', err);
  }
}

function renderPagination(total, current) {
  const pages = Math.ceil(total / PER_PAGE);
  const container = document.getElementById('pagination');
  if (pages <= 1) { container.innerHTML = ''; return; }

  let html = `<button class="page-btn" onclick="goPage(${current-1})" ${current===1?'disabled':''}>‹ Prev</button>`;

  // sliding window
  const delta = 2;
  const range = [];
  for (let i = Math.max(1, current - delta); i <= Math.min(pages, current + delta); i++) range.push(i);
  if (range[0] > 1) { html += `<button class="page-btn" onclick="goPage(1)">1</button>`; if (range[0] > 2) html += `<span style="color:var(--muted);padding:0 4px">…</span>`; }
  range.forEach(p => {
    html += `<button class="page-btn ${p===current?'active':''}" onclick="goPage(${p})">${p}</button>`;
  });
  if (range[range.length-1] < pages) { if (range[range.length-1] < pages-1) html += `<span style="color:var(--muted);padding:0 4px">…</span>`; html += `<button class="page-btn" onclick="goPage(${pages})">${pages}</button>`; }

  html += `<button class="page-btn" onclick="goPage(${current+1})" ${current===pages?'disabled':''}>Next ›</button>`;
  container.innerHTML = html;
}

window.goPage = function(p) {
  if (p < 1) return;
  explorerPage = p;
  loadExplorer();
};

// Debounced search
let searchTimer;
document.getElementById('search-input').addEventListener('input', e => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    explorerSearch = e.target.value.trim();
    explorerPage = 1;
    loadExplorer();
  }, 350);
});

// ══════════════════════════════════════════════════════════════
//  Bootstrap
// ══════════════════════════════════════════════════════════════
async function init() {
  await Promise.all([
    loadStats(),
    loadSubjectChart(),
    loadGradeChart(),
    loadTopStudents(),
    loadClassChart(),
    loadExplorer(),
  ]);
}

init();
