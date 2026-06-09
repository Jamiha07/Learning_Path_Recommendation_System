import os, pickle, json
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Load trained SVD model ────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'model', 'svd_model.pkl')
META_PATH  = os.path.join(BASE_DIR, '..', 'model', 'model_metadata.json')
DATA_PATH  = os.path.join(BASE_DIR, '..', 'data', 'intern_learning_path_dataset_v2.xlsx')

with open(MODEL_PATH, 'rb') as f:
    svd_model = pickle.load(f)

with open(META_PATH, 'r') as f:
    metadata = json.load(f)

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

# ── Department → relevant courses ────────────────────────────
DEPT_COURSES = {
    'Data Science':        ['Python Fundamentals','Machine Learning Basics','Deep Learning',
                            'Statistics & Probability','Data Visualization','NLP & Text Analytics',
                            'Data Wrangling & Pandas','Time Series Analysis','MLOps Pipelines',
                            'A/B Testing & Experimentation'],
    'Software Engineering':['Python Fundamentals','System Design','APIs & Microservices',
                            'Docker & Kubernetes','Git & Version Control','Frontend Basics (React)',
                            'SQL & Databases','Cloud Computing (AWS)'],
    'Cloud & DevOps':      ['Cloud Computing (AWS)','Docker & Kubernetes','MLOps Pipelines',
                            'APIs & Microservices','System Design','Git & Version Control',
                            'Cybersecurity Essentials'],
    'Cybersecurity':       ['Cybersecurity Essentials','System Design','Cloud Computing (AWS)',
                            'APIs & Microservices','SQL & Databases','Docker & Kubernetes'],
    'Data Engineering':    ['SQL & Databases','Data Wrangling & Pandas','Cloud Computing (AWS)',
                            'Python Fundamentals','APIs & Microservices','MLOps Pipelines',
                            'Time Series Analysis'],
    'Business Analytics':  ['Business Intelligence & BI Tools','Data Visualization','SQL & Databases',
                            'Statistics & Probability','A/B Testing & Experimentation',
                            'Data Wrangling & Pandas'],
    'Machine Learning':    ['Machine Learning Basics','Deep Learning','MLOps Pipelines',
                            'NLP & Text Analytics','Reinforcement Learning','Statistics & Probability',
                            'Time Series Analysis','Python Fundamentals'],
    'Frontend':            ['Frontend Basics (React)','APIs & Microservices','Git & Version Control',
                            'System Design','Docker & Kubernetes'],
    'Research':            ['Statistics & Probability','Machine Learning Basics','Deep Learning',
                            'Reinforcement Learning','NLP & Text Analytics','Time Series Analysis'],
    'Product':             ['A/B Testing & Experimentation','Business Intelligence & BI Tools',
                            'Data Visualization','SQL & Databases','APIs & Microservices'],
}

# ── Skill → courses it boosts ─────────────────────────────────
SKILL_COURSES = {
    'python': ['Python Fundamentals','Machine Learning Basics','Deep Learning',
               'Data Wrangling & Pandas','MLOps Pipelines','NLP & Text Analytics',
               'Time Series Analysis','Reinforcement Learning'],
    'math':   ['Statistics & Probability','Machine Learning Basics','Deep Learning',
               'Time Series Analysis','Reinforcement Learning','A/B Testing & Experimentation'],
    'sql':    ['SQL & Databases','Data Wrangling & Pandas',
               'Business Intelligence & BI Tools','Data Visualization'],
    'ml':     ['Machine Learning Basics','Deep Learning','MLOps Pipelines',
               'NLP & Text Analytics','Reinforcement Learning','Time Series Analysis'],
    'cloud':  ['Cloud Computing (AWS)','Docker & Kubernetes','MLOps Pipelines',
               'APIs & Microservices','Cybersecurity Essentials'],
}

print(f"✅ SVD model loaded | NDCG@3: {metadata['svd_ndcg']}%")


# ── Skill-based scoring for unknown interns ───────────────────
def skill_based_score(course, dept, python_skill, math_stat,
                      sql_score, ml_knowledge, cloud_infra, engagement):
    """
    Pure skill+dept scoring used when the user is NOT in the training set.
    Scores range 1-10 so they're on the same scale as SVD predictions.
    """
    dept_relevant = set(DEPT_COURSES.get(dept, []))
    skill_map = {
        'python': python_skill,
        'math':   math_stat,
        'sql':    sql_score,
        'ml':     ml_knowledge,
        'cloud':  cloud_infra,
    }

    # 1. Department affinity (0 or 1)
    dept_score = 1.0 if course in dept_relevant else 0.0

    # 2. Skill gap bonus — low skill in a relevant area = higher priority
    gap_total  = 0.0
    gap_count  = 0
    for skill_key, skill_val in skill_map.items():
        if course in SKILL_COURSES.get(skill_key, []):
            gap_total += (10.0 - skill_val) / 9.0
            gap_count += 1
    gap_bonus = (gap_total / gap_count) if gap_count > 0 else 0.0

    # 3. Engagement modifier (-0.1 to +0.1)
    eng_mod = (engagement - 5.0) * 0.02

    # Weighted blend → scale to 1-10
    raw   = 0.5 * dept_score + 0.4 * gap_bonus + 0.1 * (engagement / 10.0)
    score = 1.0 + raw * 9.0 + eng_mod
    return round(score, 4)


# ── Main prediction function ──────────────────────────────────
def svd_predict_new(intern_id, dept, python_skill, math_stat,
                    sql_score, ml_knowledge, cloud_infra,
                    engagement, completed_courses):

    is_known = intern_id in KNOWN_USERS
    print(f"   is_known_user: {is_known}")

    scores = []
    for c in ALL_COURSES:
        if c in completed_courses:
            continue

        if is_known:
            # Known intern — use full SVD prediction
            pred  = svd_model.predict(intern_id, c)
            score = round(pred.est, 4)
        else:
            # Unknown intern — use skill+dept scoring
            score = skill_based_score(
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
    return top3


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

    recs = svd_predict_new(
        intern_id, dept, python_skill, math_stat,
        sql_score, ml_knowledge, cloud_infra,
        engagement, completed
    )

    print(f"📤 TOP 3: {[r['course'] for r in recs]}")

    return jsonify({
        'intern_id':       intern_id,
        'department':      dept,
        'model':           'SVD Matrix Factorization',
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
    return jsonify(metadata)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
