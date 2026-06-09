# PathForge ⚡ — AI Learning Path Recommendation System

> A personalized course recommendation engine for interns, built with Hybrid Collaborative Filtering and a full-stack deployable web interface.

---

## 📌 About the Project

PathForge recommends personalized learning paths for interns based on their department, skill levels, and engagement. It uses a **Hybrid Scoring Engine** that combines department affinity, skill gap analysis, and engagement to rank the most relevant courses for each intern.

Built as part of an ML internship task at **Internee.pk**.

---

## 🧠 How the Algorithm Works

```
Score = 0.6 × dept_affinity + 0.3 × gap_bonus + 0.1 × engagement_modifier

gap_bonus           = 1 - |skill_value - 5.5| / 5.5
engagement_modifier = (engagement_score - 5) × 0.02
```

The model is evaluated using **NDCG@3** (Normalized Discounted Cumulative Gain):

| Model | NDCG@3 |
|---|---|
| Baseline (Popularity) | 26.22% |
| PathForge (Hybrid) | **84.32%** |
| Lift | **+58.10%** |

---

## 📁 Folder Structure

```
PathForge/
├── frontend/
│   ├── index.html        ← Page structure
│   ├── style.css         ← Styling & theme
│   └── app.js            ← Logic, charts, scoring
│
├── backend/
│   ├── app.py            ← Flask REST API
│   └── requirements.txt  ← Python dependencies
│
├── data/
│   ├── intern_learning_path_dataset_v2.xlsx
│   ├── intern_dataset.csv
│   ├── feature_summary.csv
│   └── ml_design_notes.csv
│
├── notebook/
│   └── Learning_Path_Recommendation_System.ipynb
│
└── README.md
```

---

## 🚀 Getting Started

### Option A — Frontend Only (no setup needed)
Just open `frontend/index.html` in your browser. The app runs in demo mode — the full scoring engine is built into the JavaScript.

### Option B — Full Stack

**1. Install dependencies and start the backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend runs at `http://localhost:5000`

**2. Open the frontend:**
Open `frontend/index.html` in your browser.

**3. Connect frontend to backend:**
In `frontend/app.js`, update line 2:
```js
const DEMO_MODE = false;
```

---

## 🌐 Deployment

**Backend** — Deploy to [Render](https://render.com) or [Railway](https://railway.app):
```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

**Frontend** — Deploy to [Netlify](https://netlify.com) or [Vercel](https://vercel.com):
Drag and drop the `frontend/` folder.

After deploying the backend, update `API_BASE` in `app.js` to your live backend URL.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| ML / Data | NumPy, Pandas |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Plotly.js 2.35 |
| Fonts | Syne, DM Sans (Google Fonts) |
| Production Server | Gunicorn |

---

## 📊 Dataset

- **1000 intern profiles** across 10 departments
- **27 features** per intern including skill scores, learning style, engagement, completed courses, and ground-truth recommendations
- **20 curated courses** across Data Science, Engineering, Cloud, Security, and more
- Source: Synthetic dataset generated for internship task purposes

---

## ✨ Features

- 🎯 Real-time personalized course recommendations
- 📡 Live radar chart updating as you adjust skill sliders
- 📊 6 analytics charts — model comparison, course popularity, skill distributions, dept heatmap, engagement trend, formula breakdown
- 🗺️ Learning timeline with week-by-week progression estimate
- 🎲 Randomize profile button for exploration
- 🌌 Animated particle network background
- 📱 Fully responsive design

---

## 👩‍💻 Author

**Jamiha**  
Internee.pk — ML Engineering Internship
