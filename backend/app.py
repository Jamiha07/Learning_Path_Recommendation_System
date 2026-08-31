import os, pickle, json
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Load trained SVD model ────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH         = os.path.join(BASE_DIR, '..', 'model', 'svd_model.pkl')
META_PATH          = os.path.join(BASE_DIR, '..', 'model', 'model_metadata.json')
CONTENT_MODEL_PATH = os.path.join(BASE_DIR, '..', 'model', 'content_model.pkl')
CONTENT_META_PATH  = os.path.join(BASE_DIR, '..', 'model', 'content_model_metadata.json')
DATA_PATH          = os.path.join(BASE_DIR, '..', 'data', 'intern_learning_path_dataset_v2.xlsx')

with open(MODEL_PATH, 'rb') as f:
    svd_model = pickle.load(f)

with open(META_PATH, 'r') as f:
    metadata = json.load(f)

# Content-based model: trained on intern FEATURES (skills, dept, engagement)
# rather than intern IDs, so it can score any profile, known or brand new.
with open(CONTENT_MODEL_PATH, 'rb') as f:
    content_model = pickle.load(f)

with open(CONTENT_META_PATH, 'r') as f:
    content_metadata = json.load(f)

CONTENT_FEATURE_COLUMNS = content_metadata['feature_columns']
CONTENT_DEPARTMENTS     = content_metadata['departments']

df = pd.read_excel(DATA_PATH, sheet_name='Intern Dataset')

ALL_COURSES = metadata['all_courses']

# ── Build set of known user IDs from the trained model ───────
KNOWN_USERS = {
    svd_model.trainset.to_raw_uid(u)
    for u in svd_model.trainset.all_users()
}
print(f"✅ Known users in model: {len(KNOWN_USERS)}")

COURSE_ICONS = {
    'Python Fundamentals':'🐍','SQL & Databases':'🗄️','Machine Learning Basics':'🤖',
    'Deep Learning':'🧠','Data Visualization':'📊','Cloud Computing (AWS)':'☁️',
    'Docker & Kubernetes':'🐳','Cybersecurity Essentials':'🔐','System Design':'🏗️',
    'Frontend Basics (React)':'⚛️','Statistics & Probability':'📐','NLP & Text Analytics':'💬',
    'MLOps Pipelines':'⚙️','A/B Testing & Experimentation':'🔬','Data Wrangling & Pandas':'🐼',
    'Git & Version Control':'🌿','APIs & Microservices':'🔗','Time Series Analysis':'📈',
    'Reinforcement Learning':'🎯','Business Intelligence & BI Tools':'📋'
}

COURSE_DURATION = {
    'Python Fundamentals':20,'SQL & Databases':15,'Machine Learning Basics':30,
    'Deep Learning':40,'Data Visualization':12,'Cloud Computing (AWS)':25,
    'Docker & Kubernetes':18,'Cybersecurity Essentials':22,'System Design':28,
    'Frontend Basics (React)':20,'Statistics & Probability':16,'NLP & Text Analytics':24,
    'MLOps Pipelines':20,'A/B Testing & Experimentation':10,'Data Wrangling & Pandas':14,
    'Git & Version Control':8,'APIs & Microservices':18,'Time Series Analysis':20,
    'Reinforcement Learning':35,'Business Intelligence & BI Tools':15
}

print(f"✅ SVD model loaded | NDCG@3: {metadata['svd_ndcg']}%")
print(f"✅ Content model loaded | held-out NDCG@3: {content_metadata['ndcg_at_3']}%")


# ── Content-based scoring for interns NOT in the SVD training set ─────
# Unlike SVD (one latent vector per known intern_id), this model was trained
# on the actual feature values (skills, department, engagement), so it can
# score a profile it has never seen before — it's a real prediction, not a
# hand-picked formula.
def content_based_score(course, dept, python_skill, math_stat,
                        sql_score, ml_knowledge, cloud_infra, engagement):
    row = {
        'python_skill_score': python_skill,
        'math_stat_score':    math_stat,
        'sql_score':          sql_score,
        'ml_knowledge_score': ml_knowledge,
        'cloud_infra_score':  cloud_infra,
        'engagement_score':   engagement,
    }
    for d in CONTENT_DEPARTMENTS:
        row[f'dept_{d}'] = 1.0 if dept == d else 0.0
    for c in ALL_COURSES:
        row[f'course_{c}'] = 1.0 if course == c else 0.0

    features = pd.DataFrame([row]).reindex(columns=CONTENT_FEATURE_COLUMNS, fill_value=0.0)
    score = float(content_model.predict(features)[0])
    return round(score, 4)


# ── Main prediction function ──────────────────────────────────
def svd_predict_new(intern_id, dept, python_skill, math_stat,
                    sql_score, ml_knowledge, cloud_infra,
                    engagement, completed_courses):

    is_known = intern_id in KNOWN_USERS
    print(f"   is_known_user: {is_known}")

    model_used = 'SVD Matrix Factorization' if is_known else 'Content-Based (Random Forest)'

    scores = []
    for c in ALL_COURSES:
        if c in completed_courses:
            continue

        if is_known:
            # Known intern — use full SVD prediction
            pred  = svd_model.predict(intern_id, c)
            score = round(pred.est, 4)
        else:
            # Unknown/new intern — real prediction from the content-based model
            score = content_based_score(
                c, dept, python_skill, math_stat,
                sql_score, ml_knowledge, cloud_infra, engagement
            )

        scores.append({
            'course':         c,
            'score':          score,
            'icon':           COURSE_ICONS.get(c, '📚'),
            'duration_hours': COURSE_DURATION.get(c, 15)
        })

    scores.sort(key=lambda x: x['score'], reverse=True)
    top3 = scores[:3]
    for i, s in enumerate(top3):
        s['rank'] = i + 1
        s['explanation'] = (
            f"Score: {s['score']} | "
            f"Dept: {dept} | "
            f"Engagement: {engagement}/10"
        )
    return top3, model_used


# ── Routes ────────────────────────────────────────────────────

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data         = request.json
    intern_id    = data.get('intern_id', 'NEW_INTERN')
    dept         = data.get('department', 'Data Science')
    python_skill = float(data.get('python_skill', 5))
    math_stat    = float(data.get('math_stat', 5))
    sql_score    = float(data.get('sql_score', 5))
    ml_knowledge = float(data.get('ml_knowledge', 5))
    cloud_infra  = float(data.get('cloud_infra', 5))
    engagement   = float(data.get('engagement', 5))
    completed    = data.get('completed_courses', [])

    print(f"\n📥 REQUEST: id={intern_id} dept={dept} py={python_skill} "
          f"math={math_stat} sql={sql_score} ml={ml_knowledge} "
          f"cloud={cloud_infra} eng={engagement}")

    recs, model_used = svd_predict_new(
        intern_id, dept, python_skill, math_stat,
        sql_score, ml_knowledge, cloud_infra,
        engagement, completed
    )

    print(f"📤 TOP 3: {[r['course'] for r in recs]}")

    return jsonify({
        'intern_id':       intern_id,
        'department':      dept,
        'model':           model_used,
        'recommendations': recs
    })


@app.route('/api/intern/<intern_id>', methods=['GET'])
def get_intern(intern_id):
    row = df[df['intern_id'] == intern_id]
    if row.empty:
        return jsonify({'error': f'{intern_id} not found'}), 404
    r = row.iloc[0]

    completed = (str(r['completed_courses']).split(', ')
                 if pd.notna(r['completed_courses']) and r['completed_courses'] != 'nan'
                 else [])

    scores = []
    for c in ALL_COURSES:
        if c not in completed:
            pred = svd_model.predict(intern_id, c)
            scores.append({'course': c, 'score': round(pred.est, 4),
                           'icon': COURSE_ICONS.get(c, '📚'),
                           'duration_hours': COURSE_DURATION.get(c, 15)})
    scores.sort(key=lambda x: x['score'], reverse=True)
    top3 = scores[:3]
    for i, s in enumerate(top3):
        s['rank'] = i + 1
        s['explanation'] = (
            f"SVD score: {s['score']} | "
            f"Dept: {r['department']} | "
            f"Engagement: {r['engagement_score']}/10"
        )

    return jsonify({
        'intern_id':        intern_id,
        'department':       r['department'],
        'python_skill':     r['python_skill_score'],
        'math_stat':        r['math_stat_score'],
        'sql_score':        r['sql_score'],
        'ml_knowledge':     r['ml_knowledge_score'],
        'cloud_infra':      r['cloud_infra_score'],
        'engagement':       r['engagement_score'],
        'completed_courses':completed,
        'model':            'SVD Matrix Factorization',
        'recommendations':  top3
    })


@app.route('/api/analytics', methods=['GET'])
def analytics():
    course_counts = pd.concat([
        df['recommended_course_1'], df['recommended_course_2'], df['recommended_course_3']
    ]).dropna().value_counts().head(10)

    dept_counts = df['department'].value_counts().to_dict()

    skill_means = {
        'Python':       round(df['python_skill_score'].mean(), 2),
        'Math/Stats':   round(df['math_stat_score'].mean(), 2),
        'SQL':          round(df['sql_score'].mean(), 2),
        'ML Knowledge': round(df['ml_knowledge_score'].mean(), 2),
        'Cloud':        round(df['cloud_infra_score'].mean(), 2),
    }
    skill_stds = {
        'Python':       round(df['python_skill_score'].std(), 2),
        'Math/Stats':   round(df['math_stat_score'].std(), 2),
        'SQL':          round(df['sql_score'].std(), 2),
        'ML Knowledge': round(df['ml_knowledge_score'].std(), 2),
        'Cloud':        round(df['cloud_infra_score'].std(), 2),
    }

    monthly_eng = [round(x, 2) for x in
                   df.groupby(df['days_since_joining'] // 30)['engagement_score']
                   .mean().head(12).tolist()]

    return jsonify({
        'model_metrics':      metadata,
        'course_popularity':  course_counts.to_dict(),
        'dept_counts':        dept_counts,
        'skill_means':        skill_means,
        'skill_stds':         skill_stds,
        'monthly_engagement': monthly_eng,
        'total_interns':      len(df),
        'total_courses':      len(ALL_COURSES),
    })


@app.route('/api/departments', methods=['GET'])
def departments():
    return jsonify({'departments': df['department'].unique().tolist()})


@app.route('/api/courses', methods=['GET'])
def courses():
    return jsonify({'courses': ALL_COURSES})


@app.route('/api/model_info', methods=['GET'])
def model_info():
    # Keep original flat keys (svd_ndcg, rmse, ...) so the existing frontend
    # keeps working, and add the content model's metrics alongside them.
    return jsonify({**metadata, 'content_model': content_metadata})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
