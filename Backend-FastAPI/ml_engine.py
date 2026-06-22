# ============================================================
# ml_engine.py — Load both models, predict, SHAP, intervene
# ============================================================
# This file loads both checkpoints ONCE when the server starts
# (not on every request — that would be too slow).
# When a CSV is uploaded, it picks the right model based on
# whether G1 is present in the data, then runs the full
# predict → SHAP → intervention pipeline.

import os
import json
import joblib
import numpy as np
import pandas as pd
import shap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR   = os.path.join(BASE_DIR, "ml_models")


# ============================================================
# STEP 1 — Load both model pairs at startup
# ============================================================

def _load(filename):
    return joblib.load(os.path.join(ML_DIR, filename))

def _load_json(filename):
    with open(os.path.join(ML_DIR, filename)) as f:
        return json.load(f)

# Early checkpoint (no grades needed)
model_early    = _load("failsafe_model_early.pkl")
scaler_early   = _load("failsafe_scaler_early.pkl")
features_early = _load_json("feature_names_early.json")

# Mid-semester checkpoint (G1 required)
model_mid      = _load("failsafe_model_mid.pkl")
scaler_mid     = _load("failsafe_scaler_mid.pkl")
features_mid   = _load_json("feature_names_mid.json")

# Config (thresholds + metadata for both)
config = _load_json("model_config_two_tier.json")

# SHAP explainers — built once, reused for every request
explainer_early = shap.TreeExplainer(model_early)
explainer_mid   = shap.TreeExplainer(model_mid)

print("ML Engine: both checkpoints loaded successfully.")


# ============================================================
# STEP 2 — Intervention map
# ============================================================

INTERVENTION_MAP = {
    'G1': {
        'label'       : 'Below-expected first-period grade',
        'intervention': 'This is the strongest signal — treat as primary concern. '
                       'Schedule a one-on-one review of first-period coursework to '
                       'identify specific weak topics. Arrange targeted subject tutoring '
                       'before the next assessment.',
        'referral'    : 'Subject teacher (priority review)'
    },
    'failures': {
        'label'       : 'History of past failures',
        'intervention': 'Enrol in academic recovery programme. Assign a peer mentor '
                       'who excelled in previously failed subjects. Schedule weekly '
                       '1-on-1 check-in with subject teacher.',
        'referral'    : 'Academic counsellor'
    },
    'absences': {
        'label'       : 'High absenteeism',
        'intervention': 'Contact parent/guardian to discuss attendance pattern. '
                       'Create an attendance contract with clear targets. '
                       'Investigate root cause: transport, health, or motivation.',
        'referral'    : 'Pastoral care / school counsellor'
    },
    'goout': {
        'label'       : 'Frequent social outings affecting study time',
        'intervention': 'Discuss time management and study-life balance. '
                       'Introduce structured weekly study schedule. '
                       'Consider study group to make study more social.',
        'referral'    : 'Student mentor'
    },
    'studytime': {
        'label'       : 'Insufficient study time',
        'intervention': 'Provide study timetable template. '
                       'Offer supervised study hall sessions after school.',
        'referral'    : 'Academic support centre'
    },
    'schoolsup': {
        'label'       : 'Not receiving school academic support',
        'intervention': 'Immediately enrol in school support programme. '
                       'Arrange extra tuition in weakest subjects.',
        'referral'    : 'Subject teacher + academic support team'
    },
    'famsup': {
        'label'       : 'Limited family academic support at home',
        'intervention': 'Schedule parent meeting. Provide take-home study guides. '
                       'Consider after-school homework club.',
        'referral'    : 'Family liaison officer'
    },
    'famrel': {
        'label'       : 'Poor family relationship quality',
        'intervention': 'Refer to school counsellor for wellbeing check. '
                       'Ensure student has a trusted adult contact at school.',
        'referral'    : 'School counsellor / welfare officer'
    },
    'Dalc': {
        'label'       : 'Daily alcohol consumption concern',
        'intervention': 'Confidential welfare check by school counsellor. '
                       'Referral to substance awareness programme if appropriate.',
        'referral'    : 'School counsellor (confidential)'
    },
    'Walc': {
        'label'       : 'Weekend alcohol consumption concern',
        'intervention': 'Wellbeing conversation with trusted staff member. '
                       'Peer support group or mentoring programme.',
        'referral'    : 'Wellbeing coordinator'
    },
    'health': {
        'label'       : 'Health concerns affecting attendance',
        'intervention': 'Check if student needs reasonable adjustments. '
                       'Liaise with school nurse. Create flexible catch-up plan.',
        'referral'    : 'School nurse / medical officer'
    },
    'romantic': {
        'label'       : 'Romantic relationship impacting focus',
        'intervention': 'Pastoral check-in to ensure wellbeing. '
                       'Reinforce academic goals and long-term aspirations.',
        'referral'    : 'Form tutor / pastoral lead'
    },
    'internet': {
        'label'       : 'No internet access at home',
        'intervention': 'Provide school device loan. '
                       'Give access to library computer lab outside hours.',
        'referral'    : 'IT / resources coordinator'
    },
    'higher': {
        'label'       : 'Student does not aspire to higher education',
        'intervention': 'Career guidance session to explore vocational pathways. '
                       'Connect with alumni or industry mentors.',
        'referral'    : 'Careers advisor'
    },
    'Fedu': {
        'label'       : 'Low father education background',
        'intervention': 'Increase school-side academic scaffolding. '
                       'Provide structured guidance family may not be able to give.',
        'referral'    : 'Academic support team'
    },
    'Medu': {
        'label'       : 'Low mother education background',
        'intervention': 'Increase school-side academic scaffolding. '
                       'Communicate with parents in accessible language.',
        'referral'    : 'Academic support team'
    },
    'freetime': {
        'label'       : 'Excessive free time (low structure)',
        'intervention': 'Encourage structured extracurricular activities. '
                       'Introduce goal-setting session with tutor.',
        'referral'    : 'Student activities coordinator'
    },
    'traveltime': {
        'label'       : 'Long travel time to school',
        'intervention': 'Explore transport support options. '
                       'Allow online resource access for missed early sessions.',
        'referral'    : 'School administration'
    },
    'support_index': {
        'label'       : 'Low overall support index',
        'intervention': 'Holistic case review — coordinate academic support, '
                       'family liaison, and careers guidance together.',
        'referral'    : 'Pastoral lead (coordinating case manager)'
    },
    'risk_behavior': {
        'label'       : 'Elevated lifestyle risk score',
        'intervention': 'Confidential wellbeing conversation covering lifestyle balance.',
        'referral'    : 'School counsellor'
    },
    'engagement': {
        'label'       : 'Low engagement score',
        'intervention': 'Structured study plan with regular teacher check-ins. '
                       'Investigate whether disengagement stems from difficulty or circumstance.',
        'referral'    : 'Form tutor + subject teacher'
    },
}


# ============================================================
# STEP 3 — Preprocessing helper
# ============================================================

def preprocess_uploaded_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the same encoding steps used during training to
    a freshly uploaded CSV. Returns a clean, numeric dataframe.
    """
    df = df.copy()
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()

    # Binary yes/no
    binary_cols = ['schoolsup', 'famsup', 'paid', 'activities',
                   'nursery', 'higher', 'internet', 'romantic']
    for col in binary_cols:
        if col in df.columns:
            df[col] = df[col].map({'yes': 1, 'no': 0})

    # Engineered features
    if all(c in df.columns for c in ['schoolsup', 'famsup', 'higher']):
        df['support_index'] = df['schoolsup'] + df['famsup'] + df['higher']
    if all(c in df.columns for c in ['Dalc', 'Walc', 'goout']):
        df['risk_behavior'] = df['Dalc'] + df['Walc'] + df['goout']
    if all(c in df.columns for c in ['studytime', 'absences']):
        df['engagement'] = df['studytime'] - (df['absences'] / 10)

    # One-hot encode
    multi_cols = ['school', 'sex', 'address', 'famsize', 'Pstatus',
                  'Mjob', 'Fjob', 'reason', 'guardian']
    existing_multi = [c for c in multi_cols if c in df.columns]
    df = pd.get_dummies(df, columns=existing_multi, drop_first=True)

    return df


# ============================================================
# STEP 4 — Detect checkpoint from uploaded data
# ============================================================

def detect_checkpoint(df: pd.DataFrame) -> str:
    """
    If G1 is present in the uploaded CSV, use the mid-semester
    model. Otherwise use the early model.
    """
    if 'G1' in df.columns:
        return "mid_semester"
    return "early"


# ============================================================
# STEP 5 — Align columns to match training feature set
# ============================================================

def align_features(df: pd.DataFrame, feature_names: list) -> pd.DataFrame:
    """
    After preprocessing, the uploaded data may have different
    one-hot columns than what the model was trained on
    (e.g. an upload with only GP students won't have school_MS).
    This adds missing columns as 0 and drops any extra ones,
    so the shape always matches exactly what the model expects.
    """
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0
    return df[feature_names]


# ============================================================
# STEP 6 — Core prediction pipeline
# ============================================================

def run_prediction_pipeline(df_raw: pd.DataFrame) -> list:
    """
    Takes a raw uploaded dataframe (straight from CSV),
    runs the full pipeline, and returns a list of per-student
    result dicts ready to be saved to the database and returned
    as JSON to the frontend.
    """
    # Keep student name/roll if provided, remove before model
    student_names = df_raw.get('student_name',
                    pd.Series(['Student ' + str(i)
                               for i in range(len(df_raw))])).tolist()
    student_rolls = df_raw.get('student_roll',
                    pd.Series([None] * len(df_raw))).tolist()

    # Detect which checkpoint to use
    checkpoint = detect_checkpoint(df_raw)

    if checkpoint == "mid_semester":
        model, scaler, features = model_mid, scaler_mid, features_mid
        explainer = explainer_mid
        threshold = config['mid_semester']['threshold']
    else:
        model, scaler, features = model_early, scaler_early, features_early
        explainer = explainer_early
        threshold = config['early']['threshold']

    # Drop columns that aren't features
    drop_cols = ['student_name', 'student_roll', 'G2', 'G3', 'at_risk']
    df_proc = preprocess_uploaded_csv(df_raw)
    for col in drop_cols:
        if col in df_proc.columns:
            df_proc = df_proc.drop(columns=[col])
    if checkpoint == "early" and 'G1' in df_proc.columns:
        df_proc = df_proc.drop(columns=['G1'])

    # Align to exact training feature set
    df_aligned = align_features(df_proc, features)

    # Scale
    X_scaled = scaler.transform(df_aligned)

    # Predict
    y_prob = model.predict_proba(X_scaled)[:, 1]

    # SHAP
    shap_values = explainer.shap_values(X_scaled)

    # Build per-student results
    results = []
    for i in range(len(df_raw)):
        prob      = float(y_prob[i])
        is_at_risk = prob >= threshold

        # Risk tier
        if prob >= 0.75:
            risk_tier, urgency = "HIGH", "Immediate action required"
        elif prob >= 0.50:
            risk_tier, urgency = "MEDIUM", "Intervention recommended within 2 weeks"
        else:
            risk_tier, urgency = "LOW", "Monitor over next month"

        # SHAP for this student
        student_shap = shap_values[i]
        pairs = sorted(zip(features, student_shap),
                       key=lambda x: abs(x[1]), reverse=True)
        risk_factors  = [(n, float(v)) for n, v in pairs if v >  0.01]
        protective    = [(n, float(v)) for n, v in pairs if v < -0.01]

        # Interventions
        interventions = []
        for feat_name, shap_val in risk_factors[:5]:
            key = feat_name
            if key not in INTERVENTION_MAP:
                base = feat_name.split('_')[0]
                key  = base if base in INTERVENTION_MAP else None
            if key:
                entry = INTERVENTION_MAP[key]
                interventions.append({
                    'feature'     : feat_name,
                    'driver_label': entry['label'],
                    'shap_impact' : round(shap_val, 4),
                    'action'      : entry['intervention'],
                    'referral'    : entry['referral'],
                    'status'      : 'pending'
                })

        # Protective factors
        protective_notes = [
            {'feature': n,
             'note': f"Protective factor (impact: {v:.3f}). Preserve it."}
            for n, v in protective[:3]
        ]

        results.append({
            'student_name'    : student_names[i],
            'student_roll'    : student_rolls[i],
            'checkpoint'      : checkpoint,
            'risk_probability': round(prob, 4),
            'risk_percentage' : f"{prob*100:.1f}%",
            'risk_tier'       : risk_tier,
            'urgency'         : urgency,
            'is_at_risk'      : is_at_risk,
            'top_risk_drivers': [f[0] for f in risk_factors[:5]],
            'shap_values'     : json.dumps({f: float(v)
                                            for f, v in zip(features, student_shap)}),
            'interventions'   : interventions,
            'protective_factors': protective_notes,
            'summary'         : f"[{checkpoint}] {risk_tier} risk ({prob*100:.1f}%). "
                               f"Primary concern: {risk_factors[0][0] if risk_factors else 'N/A'}. "
                               f"{urgency}."
        })

    return results