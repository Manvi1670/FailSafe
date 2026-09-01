<div align="center">

# 🛡️ FAILSAFE
### Early Student Risk Detection & Personalised Intervention System

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML%20Engine-F7931E?style=for-the-badge)](https://xgboost.readthedocs.io/)
[![React](https://img.shields.io/badge/React-Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![SHAP](https://img.shields.io/badge/SHAP-Explainability-FF6B6B?style=for-the-badge)](https://shap.readthedocs.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

<br/>

> **FAILSAFE** predicts which students are heading toward academic failure before the semester ends, using attendance, behaviour, and family data rather than final grades. Every prediction is explained with SHAP and automatically converted into a personalised, educator-ready intervention plan.

<br/>

**[Live Demo](https://fail-safe-gamma.vercel.app/)** · **[GitHub Repo](https://github.com/Manvi1670/FailSafe)**

| Role | Email | Password |
|:---:|:---:|:---:|
| Faculty | faculty@failsafe.com | faculty123 |
| HOD | hod@failsafe.com | hod123 |

> The backend may take ~30 seconds to wake up on first load (Render free tier).

</div>

---

## The Problem

In educational institutions, student failure often goes undetected until end-of-semester results, leaving no room for meaningful intervention. Faculty lack a proactive, data-driven tool to identify at-risk students early and understand the root causes behind their struggles.

Academic advisors are left asking:
- Which students are heading toward failure right now, before any grades exist?
- Why exactly is this specific student at risk?
- What concrete action should I take, and who should I refer them to?

**FAILSAFE answers all three.**

---

## Why FAILSAFE is Different

| Capability | Typical Student Risk Project | FAILSAFE |
|---|---|---|
| **Prediction timing** | Uses final grades (too late) | Predicts from week one, no grades needed |
| **Explainability** | None or global feature importance only | Per-student SHAP value decomposition |
| **Actionability** | Risk score only | 20+ mapped interventions with referral contacts |
| **Transparency** | Black box | Every prediction shows which features drove the score |
| **Architecture** | Jupyter notebook | Full-stack: FastAPI + PostgreSQL + React |
| **Roles** | Single user | Faculty view + HOD school-wide view |
| **Intervention tracking** | None | Pending to In Progress to Resolved workflow |

---

## System Architecture

```
Faculty uploads student CSV
         |
         v
FastAPI /predict/upload
         |
         |-- Detect checkpoint
         |     |-- G1 column present? -> Mid-semester model (AUC 0.944)
         |     `-- No G1? -> Early model (AUC 0.742)
         |
         |-- Preprocess + encode features
         |     (binary map, get_dummies,
         |      support_index, risk_behavior, engagement)
         |
         |-- StandardScaler -> XGBoost binary classifier
         |     -> risk_probability per student (0-100%)
         |     -> risk_tier: HIGH / MEDIUM / LOW
         |
         |-- SHAP TreeExplainer
         |     -> per-student feature importance
         |     -> top risk drivers + protective factors
         |
         |-- Intervention Engine
         |     -> maps each SHAP driver to specific action + referral
         |
         `-- Save to PostgreSQL
               (students, predictions, SHAP values, interventions)
         |
         v
React Dashboard
         |-- Faculty Dashboard  -> risk stats + student table + filters
         |-- Upload Page        -> drag-and-drop CSV + live result card
         |-- Student Detail     -> SHAP bar chart + intervention plan + status dropdowns
         `-- HOD Dashboard      -> school-wide donut chart + risk breakdown
```

---

## Features

### Machine Learning
- Two-tier XGBoost classifier: early model (no grades) and mid-semester model (uses G1), auto-selected based on uploaded data
- SHAP TreeExplainer for per-student feature importance
- Class imbalance handling via dynamic scale_pos_weight
- GridSearchCV hyperparameter tuning with 5-fold cross-validation
- Engineered composite features: support_index, risk_behavior, engagement

### Explainability
- Per-student SHAP waterfall showing base risk to each feature contribution to final score
- Risk-increasing features (red) and protective factors (green) both shown
- Human-readable labels: failures becomes "History of past failures", G1 becomes "Below-expected first-period grade"
- G1 dominance quantified: mid-semester model has G1 carrying 64.6% of model attention

### Intervention Engine
- 20+ feature-mapped interventions covering academic, lifestyle, family, wellbeing, and logistical domains
- Each intervention has specific action text and a named referral contact
- Protective factors identified and flagged to preserve
- Faculty mark each action as Pending, In Progress, or Resolved

### REST API (FastAPI)
- JWT authentication with Faculty and HOD roles
- POST /predict/upload accepts CSV and returns full intelligence report
- Auto-detects separator (semicolon or comma) for CSV flexibility
- Interactive docs at /docs

### React Dashboard
- Faculty Dashboard: risk stat cards, sortable student table, risk tier filter, visual risk score bars
- Upload Page: drag-and-drop CSV with animated progress bar and live result card
- Student Detail Page: SHAP bar chart, risk summary, intervention plan with status dropdowns
- HOD Dashboard: CSS conic-gradient donut chart, risk breakdown bars, school-wide view

---

## Tech Stack

### Machine Learning
| Component | Technology |
|---|---|
| Model | XGBoost (binary:logistic) |
| Explainability | SHAP (TreeExplainer) |
| Data Processing | Pandas, NumPy |
| Preprocessing | Scikit-learn (StandardScaler, GridSearchCV) |
| Visualisation | Matplotlib, Seaborn |
| Persistence | Joblib (.pkl) |

### Backend
| Component | Technology |
|---|---|
| API Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Auth | JWT (python-jose) + Passlib/bcrypt |
| Server | Uvicorn (ASGI) |

### Frontend
| Component | Technology |
|---|---|
| Framework | React (Vite) |
| Routing | React Router DOM |
| HTTP Client | Axios |
| Styling | CSS Modules (plain CSS, no framework) |
| Forms | React Hook Form |

### Deployment
| Component | Platform |
|---|---|
| Frontend | Vercel |
| Backend | Render |
| Database | Neon (serverless PostgreSQL) |

---

## Dataset and Feature Engineering

**Source:** UCI Machine Learning Repository, Student Performance Dataset
**Citation:** P. Cortez and A. Silva. "Using Data Mining to Predict Secondary School Student Performance." 2008.

| Property | Detail |
|---|---|
| Subject | Mathematics (student-mat.csv) |
| Total Records | 395 students |
| Input Features | 30 attributes |
| Target Variable | Binary: at_risk = 1 if G3 < 10 (fail), else 0 |
| At-risk rate | 32.9% (130 students) |

### Feature Categories

| Category | Features |
|---|---|
| Academic Behaviour | studytime, failures, absences |
| Social and Lifestyle | goout, Dalc, Walc, romantic, freetime |
| Support Network | schoolsup, famsup, higher, internet |
| Family Context | Medu, Fedu, Mjob, Fjob, famrel, Pstatus, guardian |
| Logistical | traveltime, health, nursery, activities, paid |

### Engineered Composite Features

```python
# Combines school support + family support + higher education aspiration
support_index = schoolsup + famsup + higher

# Combines daily alcohol + weekend alcohol + social going-out frequency
risk_behavior = Dalc + Walc + goout

# Study time offset by absence penalty
engagement = studytime - (absences / 10)
```

---

## Two-Tier Model Design

The core architectural insight of FAILSAFE: instead of one model, two checkpoints are trained from the same data.

| Checkpoint | Features | ROC-AUC | CV F1 | When to use |
|---|---|---|---|---|
| Early | Behaviour and background only, no grades | 0.742 | 0.350 | Week 1 of semester |
| Mid-semester | All features plus G1 | 0.944 | 0.723 | After first grading period |

The system auto-detects which to use: if the uploaded CSV contains a G1 column, the mid-semester model runs. Otherwise the early model runs.

**G1 dominance analysis:** In the mid-semester model, G1 carries 64.6% of the model's attention. The remaining 35.4% is spread across failures, absences, famrel, schoolsup, and goout, proving the model is not simply thresholding a single grade. It uses context to catch students whose grade does not yet reflect a developing problem.

---

## Model Performance

### Early Model (no grades)

| Metric | Value |
|---|---|
| ROC-AUC | 0.742 |
| CV F1 Score | 0.350 |
| Precision (at-risk) | 0.64 |
| Recall (at-risk) | 0.62 |
| Accuracy | 0.76 |
| Threshold | 0.52 |

### Mid-Semester Model (includes G1)

| Metric | Value |
|---|---|
| ROC-AUC | 0.944 |
| CV F1 Score | 0.723 |
| Threshold | 0.50 |
| G1 SHAP share | 64.6% |
| Remaining features | 35.4% across 42 behavioural signals |

### Risk Tiers

| Tier | Threshold | Educator Action |
|---|---|---|
| HIGH | >= 75% | Immediate action required |
| MEDIUM | 50-74% | Intervention within 2 weeks |
| LOW | < 50% | Monitor over next month |

---

## SHAP Explainability

FAILSAFE uses SHAP (SHapley Additive exPlanations) to provide per-student explanations for every prediction.

**Real example: Student 128 (88.8% risk, correctly flagged)**

| Feature | SHAP Impact | Meaning |
|---|---|---|
| G1 | +1.484 | Below-expected first-period grade, strongest signal |
| failures | +0.291 | History of past class failures |
| absences | +0.087 | High absenteeism |
| Fjob_other | -0.024 | Father job category, protective factor |

The waterfall chart shows the journey from base risk (average student: 1.2%) to final predicted risk (88.8%), with each feature contribution visible and labelled.

---

## Intervention Engine

The intervention engine maps every SHAP risk driver to a specific, educator-ready action with a named referral contact.

**Example output for Student 128:**

```
Rank 1 | G1: Below-expected first-period grade
Action: This is the strongest signal. Schedule a one-on-one review of
        first-period coursework to identify specific weak topics. Arrange
        targeted subject tutoring before the next assessment.
Refer:  Subject teacher (priority review)

Rank 2 | failures: History of past failures
Action: Enrol in academic recovery programme. Assign a peer mentor who
        excelled in previously failed subjects. Schedule weekly 1-on-1
        check-in with subject teacher.
Refer:  Academic counsellor

Rank 3 | absences: High absenteeism
Action: Contact parent/guardian to discuss attendance pattern. Create an
        attendance contract with clear targets. Investigate root cause:
        transport, health, or motivation.
Refer:  Pastoral care / school counsellor
```

Faculty mark each intervention as Pending, In Progress, or Resolved, giving HODs a real-time view of intervention coverage.

---

## API Reference

**Base URL:** http://localhost:8000
**Docs:** http://localhost:8000/docs

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /auth/register | No | Create faculty or HOD account |
| POST | /auth/login | No | Returns JWT access token |
| GET | /auth/me | Yes | Current logged-in user profile |
| POST | /predict/upload | Yes | Upload CSV, run full ML pipeline, save to DB |
| GET | /students/ | Yes | List all students with risk scores and filters |
| GET | /students/{id} | Yes | Student detail plus SHAP values and interventions |
| GET | /dashboard/summary | Yes | Faculty risk counts and intervention stats |
| GET | /dashboard/hod | HOD | School-wide risk summary across all faculty |
| PATCH | /interventions/{id} | Yes | Update intervention status |
| GET | /interventions/{id} | Yes | Get single intervention detail |

---

## Frontend Pages

| Page | Route | Description |
|---|---|---|
| Login | /login | JWT auth, role-based redirect |
| Register | /register | Create faculty or HOD account |
| Dashboard | /dashboard | Risk stat cards, student table with tier filter and risk bars |
| Upload | /upload | Drag-and-drop CSV, checkpoint info, animated progress, result card |
| Student Detail | /students/:id | SHAP bar chart, risk summary, intervention plan with status dropdowns |
| HOD Dashboard | /hod | Donut chart, risk breakdown bars, action-required alerts |

---

## Project Structure

```
FailSafe/
|
|-- Machine_Learning/
|   |-- dataprocessing.ipynb          # Data cleaning, encoding, feature engineering
|   |-- model_training.ipynb          # XGBoost training, GridSearch, evaluation
|   |-- shap_two_tier.ipynb           # SHAP analysis for both checkpoints
|   |-- student-mat.csv               # UCI Mathematics dataset
|   |-- X_early.csv / y_early.csv     # Early model feature set
|   |-- X_mid.csv / y_mid.csv         # Mid-semester feature set
|   |-- feature_names_early.json
|   |-- feature_names_mid.json
|   |-- model_config_two_tier.json    # Thresholds + ROC-AUC metadata
|   |-- intervention_report_early.csv
|   |-- intervention_report_mid.csv
|   `-- *.png                         # SHAP charts, confusion matrices, ROC curves
|
|-- Backend-FastAPI/
|   |-- main.py                       # FastAPI app entry point + CORS
|   |-- database.py                   # PostgreSQL connection (SQLAlchemy)
|   |-- models.py                     # DB tables: User, Student, Prediction, Intervention
|   |-- schemas.py                    # Pydantic V2 request/response shapes
|   |-- auth.py                       # JWT auth, password hashing, role guards
|   |-- ml_engine.py                  # Loads both models, predict + SHAP + interventions
|   |-- create_tables.py              # One-time DB table creation
|   |-- requirements.txt
|   |-- ml_models/
|   |   |-- failsafe_model_early.pkl
|   |   |-- failsafe_scaler_early.pkl
|   |   |-- failsafe_model_mid.pkl
|   |   |-- failsafe_scaler_mid.pkl
|   |   |-- feature_names_early.json
|   |   |-- feature_names_mid.json
|   |   `-- model_config_two_tier.json
|   `-- routers/
|       |-- auth_router.py
|       |-- predict.py
|       |-- students.py
|       |-- dashboard.py
|       `-- interventions.py
|
`-- failsafe-frontend/
    |-- src/
    |   |-- main.jsx
    |   |-- App.jsx
    |   |-- index.css
    |   |-- api/
    |   |   `-- axios.js              # Axios instance + JWT interceptor
    |   |-- context/
    |   |   `-- AuthContext.jsx       # Global auth state
    |   |-- components/
    |   |   |-- Navbar.jsx
    |   |   `-- ProtectedRoute.jsx
    |   `-- pages/
    |       |-- Login.jsx / Login.module.css
    |       |-- Register.jsx / Register.module.css
    |       |-- Dashboard.jsx / Dashboard.module.css
    |       |-- Upload.jsx / Upload.module.css
    |       |-- StudentDetail.jsx / StudentDetail.module.css
    |       `-- HodDashboard.jsx / HodDashboard.module.css
    |-- package.json
    `-- vite.config.js
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 16

### 1. Clone the Repository

```bash
git clone https://github.com/Manvi1670/FailSafe.git
cd FailSafe
```

### 2. Set Up the Backend

```bash
cd Backend-FastAPI
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `.env` inside Backend-FastAPI/:

```
DATABASE_URL=postgresql://failsafe_user:yourpassword@localhost:5432/failsafe_db
SECRET_KEY=enter_your_secret_key_here
ALGORITHM=HS256    
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Create database tables (run once):

```bash
python create_tables.py
```

Start the backend:

```bash
uvicorn main:app --reload
```

### 3. Set Up the Frontend

```bash
cd ../failsafe-frontend
npm install
npm run dev
```

App at http://localhost:5173

### 4. Running Every Time

**Terminal 1 (Backend):**
```bash
cd Backend-FastAPI
venv\Scripts\activate
uvicorn main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd failsafe-frontend
npm run dev
```

Then open http://localhost:5173/login

---

## Author

**Manvitha Bheemavarapu** — [github.com/Manvi1670](https://github.com/Manvi1670)

---


<div align="center">

**FAILSAFE v1.0** · Python · FastAPI · XGBoost · SHAP · React · PostgreSQL

</div>
