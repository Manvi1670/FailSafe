# ============================================================
# routers/students.py — Student list and detail endpoints
# ============================================================
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from database import get_db
from models import Student, Prediction, Intervention
from auth import get_current_user

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/")
def get_all_students(
    risk_tier : Optional[str] = None,
    checkpoint: Optional[str] = None,
    db        : Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Returns all students uploaded by the current user,
    with their latest prediction and risk tier.
    Supports optional filtering by risk_tier and checkpoint.
    """
    query = (
        db.query(Student)
        .options(joinedload(Student.predictions)
                 .joinedload(Prediction.interventions))
        .filter(Student.uploaded_by_id == current_user.id)
    )

    students = query.all()

    results = []
    for student in students:
        if not student.predictions:
            continue

        # Get the most recent prediction
        latest = sorted(student.predictions,
                        key=lambda p: p.created_at, reverse=True)[0]

        # Apply filters if provided
        if risk_tier and latest.risk_tier != risk_tier.upper():
            continue
        if checkpoint and latest.checkpoint != checkpoint:
            continue

        results.append({
            'student_id'            : student.id,
            'student_name'          : student.student_name,
            'student_roll'          : student.student_roll,
            'checkpoint'            : latest.checkpoint,
            'risk_probability'      : latest.risk_probability,
            'risk_tier'             : latest.risk_tier,
            'top_risk_drivers'      : json.loads(latest.top_risk_drivers or '[]'),
            'interventions_total'   : len(latest.interventions),
            'interventions_pending' : sum(1 for i in latest.interventions
                                         if i.status == 'pending'),
            'interventions_resolved': sum(1 for i in latest.interventions
                                         if i.status == 'resolved'),
            'created_at'            : latest.created_at.isoformat()
        })

    # Sort by risk probability descending (highest risk first)
    results.sort(key=lambda x: x['risk_probability'], reverse=True)

    return {
        'total'   : len(results),
        'students': results
    }


@router.get("/{student_id}")
def get_student_detail(
    student_id  : int,
    db          : Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Returns full detail for one student:
    - All predictions (early + mid-semester if both exist)
    - SHAP values for each prediction
    - All interventions with current status
    """
    student = (
        db.query(Student)
        .options(joinedload(Student.predictions)
                 .joinedload(Prediction.interventions))
        .filter(Student.id == student_id,
                Student.uploaded_by_id == current_user.id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found"
        )

    predictions_out = []
    for pred in sorted(student.predictions,
                       key=lambda p: p.created_at, reverse=True):

        # Parse SHAP values from stored JSON string
        shap_dict = json.loads(pred.shap_values or '{}')

        # Get top 10 SHAP features sorted by absolute impact
        shap_sorted = sorted(shap_dict.items(),
                             key=lambda x: abs(x[1]), reverse=True)[:10]

        interventions_out = [{
            'intervention_id': iv.id,
            'feature'        : iv.feature,
            'driver_label'   : iv.driver_label,
            'action_text'    : iv.action_text,
            'referral'       : iv.referral,
            'status'         : iv.status,
            'created_at'     : iv.created_at.isoformat()
        } for iv in pred.interventions]

        predictions_out.append({
            'prediction_id'   : pred.id,
            'checkpoint'      : pred.checkpoint,
            'risk_probability': pred.risk_probability,
            'risk_percentage' : f"{pred.risk_probability * 100:.1f}%",
            'risk_tier'       : pred.risk_tier,
            'top_risk_drivers': json.loads(pred.top_risk_drivers or '[]'),
            'top_shap_values' : [{'feature': f, 'shap': round(v, 4)}
                                  for f, v in shap_sorted],
            'interventions'   : interventions_out,
            'created_at'      : pred.created_at.isoformat()
        })

    return {
        'student_id'  : student.id,
        'student_name': student.student_name,
        'student_roll': student.student_roll,
        'predictions' : predictions_out
    }