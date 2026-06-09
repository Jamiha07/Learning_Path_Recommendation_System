// ─── CONFIG ───────────────────────────────────────────────────────────────────
const API_BASE = 'http://127.0.0.1:8080';

// ─── Static data (used only for fallback display & charts) ───────────────────
const ALL_COURSES = [
  'Python Fundamentals','SQL & Databases','Machine Learning Basics','Deep Learning',
  'Data Visualization','Cloud Computing (AWS)','Docker & Kubernetes','Cybersecurity Essentials',
  'System Design','Frontend Basics (React)','Statistics & Probability','NLP & Text Analytics',
  'MLOps Pipelines','A/B Testing & Experimentation','Data Wrangling & Pandas',
  'Git & Version Control','APIs & Microservices','Time Series Analysis',
  'Reinforcement Learning','Business Intelligence & BI Tools'
];

const COURSE_ICONS = {
  'Python Fundamentals':'🐍','SQL & Databases':'🗄️','Machine Learning Basics':'🤖',
  'Deep Learning':'🧠','Data Visualization':'📊','Cloud Computing (AWS)':'☁️',
  'Docker & Kubernetes':'🐳','Cybersecurity Essentials':'🔐','System Design':'🏗️',
  'Frontend Basics (React)':'⚛️','Statistics & Probability':'📐','NLP & Text Analytics':'💬',
  'MLOps Pipelines':'⚙️','A/B Testing & Experimentation':'🔬','Data Wrangling & Pandas':'🐼',
  'Git & Version Control':'🌿','APIs & Microservices':'🔗','Time Series Analysis':'📈',
  'Reinforcement Learning':'🎯','Business Intelligence & BI Tools':'📋'
};

const COURSE_DURATION = {
  'Python Fundamentals':20,'SQL & Databases':15,'Machine Learning Basics':30,
  'Deep Learning':40,'Data Visualization':12,'Cloud Computing (AWS)':25,
  'Docker & Kubernetes':18,'Cybersecurity Essentials':22,'System Design':28,
  'Frontend Basics (React)':20,'Statistics & Probability':16,'NLP & Text Analytics':24,
  'MLOps Pipelines':20,'A/B Testing & Experimentation':10,'Data Wrangling & Pandas':14,
  'Git & Version Control':8,'APIs & Microservices':18,'Time Series Analysis':20,
  'Reinforcement Learning':35,'Business Intelligence & BI Tools':15
};

// ─── Slider updater ───────────────────────────────────────────────────────────
function updateSlider(name, val) {
  document.getElementById('sv-' + name).textContent = parseFloat(val).toFixed(1);
  updateRadar();
}

// ─── Live Radar Chart ─────────────────────────────────────────────────────────
function updateRadar() {
  const skills = getSkills();
  const r      = [skills.python, skills.math, skills.sql, skills.ml, skills.cloud, skills.python];
  const theta  = ['Python', 'Math/Stats', 'SQL', 'ML Knowledge', 'Cloud Infra', 'Python'];
  Plotly.react('radar-chart', [{
    type: 'scatterpolar', r, theta, fill: 'toself',
    fillcolor: 'rgba(200,255,0,0.15)',
    line: { color: '#c8ff00', width: 2 },
    marker: { color: '#c8ff00', size: 6 }
  }], {
    paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
    font: { color: 'rgba(240,240,240,0.7)', family: 'DM Sans' },
    polar: {
      bgcolor: 'transparent',
      radialaxis: { visible: true, range: [0, 10], gridcolor: 'rgba(255,255,255,0.08)',
                    tickfont: { color: 'rgba(240,240,240,0.4)', size: 10 } },
      angularaxis: { gridcolor: 'rgba(255,255,255,0.08)',
                     tickfont: { color: 'rgba(240,240,240,0.6)', size: 11 } }
    },
    margin: { t: 20, b: 20, l: 40, r: 40 }, showlegend: false
  }, { responsive: true });
}

function getSkills() {
  return {
    python: parseFloat(document.getElementById('sl-python').value),
    math:   parseFloat(document.getElementById('sl-math').value),
    sql:    parseFloat(document.getElementById('sl-sql').value),
    ml:     parseFloat(document.getElementById('sl-ml').value),
    cloud:  parseFloat(document.getElementById('sl-cloud').value),
  };
}

// ─── Get Recommendations from SVD Backend ────────────────────────────────────
async function getRecommendations() {
  const btn     = document.getElementById('rec-btn');
  const btnText = document.getElementById('btn-text');
  const spinner = document.getElementById('btn-spinner');

  btn.classList.add('loading');
  btnText.style.display = 'none';
  spinner.style.display = 'block';

  const skills   = getSkills();
  const engagement = parseFloat(document.getElementById('sl-eng').value);
  const dept     = document.getElementById('inp-dept').value;
  const internId = document.getElementById('inp-intern-id').value.trim();

  try {
    let recs, internData;

    // If intern ID matches dataset format (INT_XXXX), try fetching directly
    if (/^INT_\d+$/.test(internId)) {
      const res = await fetch(`${API_BASE}/api/intern/${internId}`);
      if (res.ok) {
        internData = await res.json();
        recs = internData.recommendations;
        // Sync sliders to real intern's data
        syncSliders(internData);
      }
    }

    // Otherwise (custom/new intern) POST with slider values
    if (!recs) {
      const res = await fetch(`${API_BASE}/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intern_id: internId, department: dept,
          python_skill: skills.python, math_stat: skills.math,
          sql_score: skills.sql, ml_knowledge: skills.ml,
          cloud_infra: skills.cloud, engagement
        })
      });
      const data = await res.json();
      recs = data.recommendations;
    }

    // Ensure icons & durations are set
    recs = recs.map(r => ({
      ...r,
      icon: r.icon || COURSE_ICONS[r.course] || '📚',
      duration_hours: r.duration_hours || COURSE_DURATION[r.course] || 15
    }));

    showBackendStatus(true);
    displayResults(internId, dept, recs);

  } catch (err) {
    console.warn('Backend not reachable:', err);
    showBackendStatus(false);
    showError();
  }

  btn.classList.remove('loading');
  btnText.style.display = 'inline';
  spinner.style.display = 'none';
}

// ─── Sync sliders when a real intern is loaded ────────────────────────────────
function syncSliders(data) {
  const map = {
    python: data.python_skill, math: data.math_stat,
    sql: data.sql_score, ml: data.ml_knowledge,
    cloud: data.cloud_infra, eng: data.engagement
  };
  Object.entries(map).forEach(([k, v]) => {
    const sl = document.getElementById('sl-' + k);
    if (sl && v !== undefined) {
      sl.value = v;
      updateSlider(k, v);
    }
  });
}

// ─── Backend status indicator ─────────────────────────────────────────────────
function showBackendStatus(ok) {
  const el = document.getElementById('backend-status');
  if (!el) return;
  el.textContent = ok ? '🟢 SVD Model Active' : '🔴 Backend Offline';
  el.style.color = ok ? 'var(--neon-lime)' : 'var(--hot-pink)';
}

function showError() {
  document.getElementById('empty-state').style.display = 'block';
  document.getElementById('empty-state').innerHTML = `
    <div class="icon">⚠️</div>
    <h3>Backend not running</h3>
    <p>Start the Flask server: <code style="background:rgba(255,255,255,0.1);padding:2px 8px;border-radius:4px;">cd backend && python app.py</code></p>
  `;
  document.getElementById('rec-results').style.display = 'none';
}

// ─── Display Results ──────────────────────────────────────────────────────────
function displayResults(internId, dept, recs) {
  document.getElementById('empty-state').style.display = 'none';
  document.getElementById('rec-results').style.display = 'block';
  document.getElementById('rec-subtitle').textContent =
    `SVD Matrix Factorization — Top 3 recommendations for ${internId} · ${dept}`;

  const maxScore = Math.max(...recs.map(r => r.score));

  const cardsEl = document.getElementById('rec-cards');
  cardsEl.innerHTML = '';
  recs.forEach(r => {
    const pct = ((r.score / maxScore) * 100).toFixed(1);
    cardsEl.innerHTML += `
      <div class="rec-card">
        <div class="rec-rank">⭐ Recommendation #${r.rank}</div>
        <div class="rec-icon">${r.icon || COURSE_ICONS[r.course] || '📚'}</div>
        <div class="rec-title">${r.course}</div>
        <div class="rec-score-bar"><div class="rec-score-fill" style="width:${pct}%"></div></div>
        <div style="font-size:0.78rem;color:var(--text-muted);">SVD Score: <strong style="color:var(--neon-lime)">${r.score}</strong></div>
        <div class="rec-meta">
          <span class="rec-tag">⏱ ${r.duration_hours || COURSE_DURATION[r.course] || 15}h</span>
          <span class="rec-tag cyan">🧠 SVD Model</span>
        </div>
        <div class="rec-explanation">${r.explanation || ''}</div>
      </div>`;
  });

  // Learning timeline
  const pathEl = document.getElementById('learning-path');
  pathEl.innerHTML = '';
  let week = 1;
  recs.forEach((r, i) => {
    const dur = r.duration_hours || COURSE_DURATION[r.course] || 15;
    pathEl.innerHTML += `
      <div class="path-step" data-num="${i+1}" style="animation-delay:${i*0.15}s">
        <div class="step-icon">${r.icon || COURSE_ICONS[r.course] || '📚'}</div>
        <div class="step-info">
          <div class="step-title">${r.course}</div>
          <div class="step-meta">Week ${week}–${week + Math.ceil(dur/8)} &nbsp;·&nbsp; ~${dur}h &nbsp;·&nbsp; SVD score ${r.score}</div>
        </div>
      </div>`;
    week += Math.ceil(dur / 8) + 1;
  });
}

// ─── Randomize Profile ────────────────────────────────────────────────────────
function randomizeProfile() {
  ['python','math','sql','ml','cloud','eng'].forEach(k => {
    const val = (Math.random() * 8 + 1.5).toFixed(1);
    const sl  = document.getElementById('sl-' + k);
    if (sl) { sl.value = val; updateSlider(k, val); }
  });
}

// ─── Analytics Charts ─────────────────────────────────────────────────────────
async function renderAnalytics() {
  const dark = {
    paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
    font: { color: 'rgba(240,240,240,0.6)', family: 'DM Sans', size: 11 },
    margin: { t: 15, b: 60, l: 55, r: 15 }
  };

  let analyticsData = null;
  try {
    const res = await fetch(`${API_BASE}/api/analytics`);
    analyticsData = await res.json();
  } catch (e) {
    console.warn('Analytics API not reachable, using static data');
  }

  // Model performance bar
  const svdNdcg      = analyticsData?.model_metrics?.svd_ndcg      ?? 87.24;
  const baselineNdcg = analyticsData?.model_metrics?.baseline_ndcg ?? 26.22;
  Plotly.newPlot('chart-ndcg', [{
    type: 'bar',
    x: ['Baseline\n(Popularity)', 'SVD Matrix\nFactorization'],
    y: [baselineNdcg, svdNdcg],
    marker: { color: ['rgba(255,45,120,0.7)', 'rgba(200,255,0,0.8)'],
              line: { color: ['#ff2d78', '#c8ff00'], width: 2 } },
    text: [`${baselineNdcg}%`, `${svdNdcg}%`], textposition: 'outside',
    textfont: { color: ['#ff2d78', '#c8ff00'], size: 13, family: 'Syne' }
  }], {
    ...dark, yaxis: { range: [0, 105], gridcolor: 'rgba(255,255,255,0.06)', ticksuffix: '%' }
  }, { responsive: true });

  // Course popularity
  const popData = analyticsData?.course_popularity ?? {
    'SQL & Databases':139,'Data Visualization':84,'Python Fundamentals':83,
    'Machine Learning Basics':75,'Git & Version Control':71,'Deep Learning':68,
    'Cloud Computing (AWS)':62,'APIs & Microservices':58,'Docker & Kubernetes':55,'Cybersecurity Essentials':50
  };
  const popCourses = Object.keys(popData).slice(0, 10).reverse();
  const popCounts  = popCourses.map(c => popData[c]);
  Plotly.newPlot('chart-popular', [{
    type: 'bar', orientation: 'h',
    y: popCourses, x: popCounts,
    marker: { color: popCounts.map((_, i) => `hsla(${60 + i * 15},100%,60%,0.75)`) }
  }], { ...dark, xaxis: { gridcolor: 'rgba(255,255,255,0.06)' }, margin: { t:15,b:40,l:190,r:15 } },
  { responsive: true });

  // Skill distribution
  const skillNames = ['Python', 'Math/Stats', 'SQL', 'ML Knowledge', 'Cloud'];
  const means = analyticsData
    ? Object.values(analyticsData.skill_means)
    : [6.2, 5.4, 5.9, 4.8, 4.2];
  const stds = analyticsData
    ? Object.values(analyticsData.skill_stds)
    : [1.8, 2.1, 1.9, 2.3, 2.4];
  Plotly.newPlot('chart-skills', [
    { type: 'bar', name: 'Mean', x: skillNames, y: means, marker: { color: 'rgba(200,255,0,0.75)' } },
    { type: 'bar', name: 'Std Dev', x: skillNames, y: stds, marker: { color: 'rgba(0,245,255,0.5)' } }
  ], {
    ...dark, barmode: 'group',
    legend: { font: { color: 'rgba(240,240,240,0.6)' }, bgcolor: 'transparent' },
    yaxis: { gridcolor: 'rgba(255,255,255,0.06)', range: [0, 11] }
  }, { responsive: true });

  // Dept heatmap
  const depts    = ['DS','SWE','PM','DevOps','Cyber','MLE','Front','Back','DE','Cloud'];
  const courses5 = ['Python','SQL','ML','Cloud','Viz'];
  const z = [
    [1,1,2,0,4],[0,1,0,1,1],[0,1,0,0,1],[1,1,0,1,0],
    [1,1,0,1,0],[1,1,1,1,0],[1,0,0,0,1],[1,1,0,1,0],
    [1,1,0,1,1],[1,1,0,1,0]
  ];
  Plotly.newPlot('chart-heatmap', [{
    type: 'heatmap', x: courses5, y: depts, z,
    colorscale: [['0','#0d0520'],['0.3','rgba(0,245,255,0.4)'],['1','#c8ff00']],
    showscale: false
  }], { ...dark, margin: { t:15,b:40,l:60,r:15 } }, { responsive: true });

  // Engagement trend
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const eng = analyticsData?.monthly_engagement?.length >= 12
    ? analyticsData.monthly_engagement.slice(0,12)
    : [6.1,6.4,5.9,7.2,7.8,8.1,7.5,8.3,7.9,8.6,8.2,8.9];
  Plotly.newPlot('chart-engagement', [{
    type: 'scatter', mode: 'lines+markers', x: months, y: eng,
    line: { color: '#c8ff00', width: 3, shape: 'spline' },
    marker: { color: '#c8ff00', size: 7 },
    fill: 'tozeroy', fillcolor: 'rgba(200,255,0,0.07)'
  }], {
    ...dark,
    yaxis: { range: [4, 10], gridcolor: 'rgba(255,255,255,0.06)' },
    xaxis: { gridcolor: 'rgba(255,255,255,0.06)' }
  }, { responsive: true });

  // Dept distribution
  const deptData = analyticsData?.dept_counts ?? {
    'Data Science':112,'Software Engineering':108,'ML Engineering':105,
    'Data Engineering':104,'DevOps':98,'Cybersecurity':96,
    'Cloud Infrastructure':95,'Backend Dev':94,'Frontend Dev':97,'Product Management':91
  };
  Plotly.newPlot('chart-dept', [{
    type: 'bar',
    x: Object.keys(deptData), y: Object.values(deptData),
    marker: { color: Object.values(deptData).map((_, i) => `hsla(${160 + i * 18},90%,55%,0.75)`) },
    text: Object.values(deptData), textposition: 'outside',
    textfont: { color: 'rgba(240,240,240,0.7)', size: 11 }
  }], {
    ...dark,
    xaxis: { tickangle: -35, gridcolor: 'rgba(255,255,255,0.06)' },
    yaxis: { gridcolor: 'rgba(255,255,255,0.06)' },
    margin: { t:20,b:110,l:50,r:15 }
  }, { responsive: true });

  // SVD info donut
  Plotly.newPlot('chart-formula', [{
    type: 'pie',
    labels: ['Completed Course Signals', 'Ground Truth Labels', 'SVD Latent Factors'],
    values: [45, 35, 20],
    hole: 0.55,
    marker: {
      colors: ['rgba(200,255,0,0.85)', 'rgba(0,245,255,0.75)', 'rgba(255,45,120,0.75)'],
      line: { color: '#0d0520', width: 3 }
    },
    textfont: { color: 'rgba(240,240,240,0.9)', size: 11 },
    textinfo: 'label+percent'
  }], {
    paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
    font: { color: 'rgba(240,240,240,0.6)', family: 'DM Sans' },
    showlegend: false, margin: { t:15,b:15,l:15,r:15 }
  }, { responsive: true });
}

// ─── Page Navigation ──────────────────────────────────────────────────────────
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  event.target.classList.add('active');
  if (name === 'analytics') renderAnalytics();
}

// ─── Particle Background ──────────────────────────────────────────────────────
(function initParticles() {
  const canvas = document.getElementById('particles');
  const ctx    = canvas.getContext('2d');
  let W, H;
  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  resize();
  window.addEventListener('resize', resize);
  const particles = Array.from({ length: 60 }, () => ({
    x: Math.random() * window.innerWidth, y: Math.random() * window.innerHeight,
    vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3,
    r: Math.random() * 2 + 0.5, alpha: Math.random() * 0.3 + 0.05,
    color: Math.random() > 0.6 ? '200,255,0' : '0,245,255'
  }));
  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.color},${p.alpha})`; ctx.fill();
    });
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const d = Math.hypot(particles[i].x - particles[j].x, particles[i].y - particles[j].y);
        if (d < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(200,255,0,${0.06 * (1 - d / 120)})`;
          ctx.lineWidth = 0.5; ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
})();

// ─── Init ─────────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', async () => {
  updateRadar();

  // Check if backend is alive
  try {
    const res = await fetch(`${API_BASE}/api/model_info`);
    const info = await res.json();
    showBackendStatus(true);
    // Update hero stats with real model metrics
    const ndcgEl = document.querySelector('.hero-stat:nth-child(2) .num');
    if (ndcgEl) ndcgEl.textContent = `${info.svd_ndcg}%`;
  } catch {
    showBackendStatus(false);
  }
});
