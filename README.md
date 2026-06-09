# PathForge ⚡ — AI Learning Path Recommendation System
 
> A personalized course recommendation engine for interns, powered by **SVD Matrix Factorization** and a full-stack web interface with real-time analytics.
 
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-REST%20API-black?style=flat-square&logo=flask)
![scikit-surprise](https://img.shields.io/badge/scikit--surprise-SVD-orange?style=flat-square)
![Plotly](https://img.shields.io/badge/Plotly.js-Charts-3F4F75?style=flat-square&logo=plotly)
![NDCG](https://img.shields.io/badge/NDCG%403-87.24%25-brightgreen?style=flat-square)
 
---


 <img width="1600" height="755" alt="image" src="https://github.com/user-attachments/assets/89547aa0-a637-4552-b9f3-85de29545ada" />
<img width="1600" height="772" alt="image" src="https://github.com/user-attachments/assets/2857e134-2ee6-4a3d-bc2b-ebdbe6162e43" />
<img width="1600" height="764" alt="image" src="https://github.com/user-attachments/assets/3e7841f7-e202-461f-8684-264aa0ccccb3" />
<img width="1600" height="770" alt="image" src="https://github.com/user-attachments/assets/7f9a1fbf-8d90-4a37-81af-0f0f6b72add9" />
<img width="1600" height="770" alt="image" src="https://github.com/user-attachments/assets/b7116adf-33f3-4446-b941-329c1e7f801f" />

## 📌 What is PathForge?
 
PathForge recommends the **top 3 personalized learning courses** for each intern based on their department, skill levels, and engagement score. It uses a trained **SVD (Singular Value Decomposition) Matrix Factorization** model — the same family of algorithms behind Netflix-style recommendation systems — trained on over 7,000 intern-course interactions.
 
The system handles two types of users:
- **Known Interns** (`INT_1000`–`INT_1999`): Gets predictions directly from the SVD model using learned latent factors.
- **New / Custom Interns**: Falls back to a skill-gap + department affinity scoring formula so anyone can still get a meaningful recommendation.
Built as part of an ML internship project at **Internee.pk**.
 
---
 
## 🧠 How It Works
 
PathForge uses **Collaborative Filtering via SVD**, implemented with `scikit-surprise`. The model decomposes an intern-course interaction matrix into latent factors that capture hidden patterns — which types of interns tend to benefit from which courses — and uses those factors to score unseen courses for each intern.
 
```
Interaction Matrix ≈ U × Σ × Vᵀ
 
U  = intern latent factors   (1000 interns × 50 factors)
Vᵀ = course latent factors   (50 factors × 20 courses)
```
 
For interns not in the training set, a rule-based fallback scores courses using department relevance, skill gaps, and engagement:
 
```
Score = 0.5 × dept_affinity + 0.4 × gap_bonus + 0.1 × (engagement / 10)
gap_bonus = (10 - skill_value) / 9.0   ← low skill = higher priority
```
 
The Flask backend loads the pre-trained `.pkl` model at startup and serves predictions via a REST API. The frontend calls this API, renders the results, and falls back gracefully if the backend is offline.
 
### 📈 Model Performance
 
| Metric | Value |
|---|---|
| NDCG@3 — SVD Model | **87.24%** |
| NDCG@3 — Baseline (Popularity) | 26.22% |
| Lift over Baseline | **+61.01%** |
| RMSE | 1.3648 |
| MAE | 1.2056 |
| Training Interactions | 7,055 |
| Latent Factors | 50 |
| Training Epochs | 30 |
 
---
 
## ✨ Features
 
### 🎯 Recommend Page
- Load any known Intern ID to auto-populate their real skill profile from the dataset
- Manually configure skills via 5 sliders (Python, Math/Stats, SQL, ML Knowledge, Cloud/Infra), department, and engagement score
- Live **Skill Radar Chart** — updates in real time as you drag the sliders
- Top 3 course recommendations with scores, icons, and SVD tags
- **Learning Timeline** — week-by-week progression plan estimated from the model's top picks
- 🎲 Randomize Profile button for quick exploration
- Backend status indicator (🟢 SVD Active / 🔴 Offline)
### 📊 Analytics Page
Six interactive Plotly.js charts, all powered live by the Flask backend:
- SVD vs. Baseline model comparison (NDCG@3 bar chart)
- Top 10 most recommended courses
- Skill score distributions (mean + std per skill)
- Department × Course heatmap
- Monthly engagement trend across the intern cohort
- Department distribution pie chart
### ℹ️ About Page
- Visual breakdown of the SVD decomposition formula
- All model hyperparameters and evaluation metrics at a glance
- Full tech stack reference
### 🌌 UI & Design
- Animated particle network canvas background
- Neon lime / electric cyan / hot pink on deep-violet dark theme
- Fully responsive and mobile-friendly
- Syne + DM Sans typography (Google Fonts)
---
 
## 🛠️ Tech Stack
 
| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python 3.8+, Flask | REST API serving predictions and analytics |
| ML Model | scikit-surprise (SVD) | Collaborative filtering on intern-course interactions |
| Data | Pandas, NumPy, openpyxl | Dataset loading, processing, and feature scoring |
| Production | Gunicorn | WSGI server for deployment |
| Frontend | HTML5, CSS3, Vanilla JS | Single-page app with three tabs |
| Charts | Plotly.js 2.35 | All interactive analytics visualizations |
| Fonts | Syne, DM Sans | Typography via Google Fonts |
 
---
 
## 📊 Dataset
 
- **1,000 intern profiles** across 10 departments with 27 features each — skill scores, learning style, engagement, completed courses, and ground-truth recommendations
- **20 curated courses** spanning Data Science, Engineering, Cloud, Security, Analytics, and more
- **7,055 training interactions** used to fit the SVD model
- Synthetic dataset generated for internship task purposes
**Departments:** Data Science · Software Engineering · Cloud & DevOps · Cybersecurity · Data Engineering · Business Analytics · Machine Learning · Frontend · Research · Product
 
---
 
## 🚀 Getting Started
 
### Option A — Frontend Only (no setup needed)
 
Open `frontend/index.html` in your browser. The app runs in demo mode with JS-based scoring — no Python or backend required.
 
### Option B — Full Stack (SVD model active)
 
```bash
# Install dependencies and start the backend
cd backend
pip install -r requirements.txt
python app.py
# Backend runs at http://127.0.0.1:8080
```
 
Then open `frontend/index.html`. The app auto-detects the backend and switches to live SVD predictions.
 
---
 
## 🌐 Deployment
 
**Backend** — Deploy to [Render](https://render.com) or [Railway](https://railway.app):
```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```
 
**Frontend** — Drag the `frontend/` folder to [Netlify](https://netlify.com) or connect via Git on [Vercel](https://vercel.com). Then update `API_BASE` in `app.js` to your live backend URL.
 
---
 
## 📓 Notebook
 
`notebook/Learning_Path_Recommendation_System.ipynb` contains the full ML pipeline — data exploration, interaction matrix construction, SVD training with `scikit-surprise`, NDCG@3 evaluation against the popularity baseline, and model export to `model/svd_model.pkl`.
 
---
 
## 👩‍💻 Author
 
**Jamiha** — ML Engineering Internship ·
