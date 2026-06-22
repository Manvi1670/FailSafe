# ============================================================
# routers/predict.py — CSV upload + full ML pipeline endpoint
# ============================================================
import io
import json
import pandas as pd

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from database import get_db
from models import Student, Prediction, Intervention
from auth import get_current_faculty
from ml_engine import run_prediction_pipeline

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_and_predict(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_faculty)
):
    """
    Accepts a CSV file upload from a faculty member.
    Runs the full ML pipeline on every student in the file:
      1. Preprocess + encode
      2. Detect checkpoint (early or mid-semester)
      3. Predict risk probability
      4. Compute SHAP values
      5. Generate intervention plans
      6. Save everything to PostgreSQL
      7. Return results as JSON
    """

    # --- Validate file type ---
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted"
        )

    # --- Read CSV into a dataframe ---
    contents = await file.read()
    try:
        # Try semicolon first (UCI dataset format), fall back to comma
        try:
            df_raw = pd.read_csv(io.BytesIO(contents), sep=";")
            if df_raw.shape[1] < 5:
                df_raw = pd.read_csv(io.BytesIO(contents), sep=",")
        except Exception:
            df_raw = pd.read_csv(io.BytesIO(contents), sep=",")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse CSV: {str(e)}"
        )

    if df_raw.empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded CSV is empty"
        )

    # --- Run the full ML pipeline ---
    try:
        results = run_prediction_pipeline(df_raw)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction pipeline failed: {str(e)}"
        )

    # --- Save results to PostgreSQL ---
    saved_students = []

    for result in results:

        # 1. Create student record
        student = Student(
            student_name   = result['student_name'],
            student_roll   = result['student_roll'],
            uploaded_by_id = current_user.id
        )
        db.add(student)
        db.flush()   # get student.id without committing yet

        # 2. Create prediction record
        prediction = Prediction(
            student_id       = student.id,
            checkpoint       = result['checkpoint'],
            risk_probability = result['risk_probability'],
            risk_tier        = result['risk_tier'],
            shap_values      = result['shap_values'],
            top_risk_drivers = json.dumps(result['top_risk_drivers'])
        )
        db.add(prediction)
        db.flush()   # get prediction.id

        # 3. Create intervention records
        for iv in result['interventions']:
            intervention = Intervention(
                prediction_id = prediction.id,
                feature       = iv['feature'],
                driver_label  = iv['driver_label'],
                action_text   = iv['action'],
                referral      = iv['referral'],
                status        = 'pending'
            )
            db.add(intervention)

        # 4. Build response object for this student
        saved_students.append({
            'student_id'      : student.id,
            'student_name'    : result['student_name'],
            'student_roll'    : result['student_roll'],
            'checkpoint'      : result['checkpoint'],
            'risk_probability': result['risk_probability'],
            'risk_percentage' : result['risk_percentage'],
            'risk_tier'       : result['risk_tier'],
            'urgency'         : result['urgency'],
            'is_at_risk'      : result['is_at_risk'],
            'top_risk_drivers': result['top_risk_drivers'],
            'interventions'   : result['interventions'],
            'protective_factors': result['protective_factors'],
            'summary'         : result['summary']
        })

    # Commit everything at once — all students or none
    db.commit()

    # --- Return summary response ---
    at_risk_count = sum(1 for s in saved_students if s['is_at_risk'])
    high_count    = sum(1 for s in saved_students if s['risk_tier'] == 'HIGH')
    medium_count  = sum(1 for s in saved_students if s['risk_tier'] == 'MEDIUM')
    low_count     = sum(1 for s in saved_students if s['risk_tier'] == 'LOW')

    return {
        "message"        : f"Processed {len(saved_students)} students successfully",
        "checkpoint_used": saved_students[0]['checkpoint'] if saved_students else None,
        "total_students" : len(saved_students),
        "at_risk_count"  : at_risk_count,
        "high_risk"      : high_count,
        "medium_risk"    : medium_count,
        "low_risk"       : low_count,
        "students"       : saved_students
    }