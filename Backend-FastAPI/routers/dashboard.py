# ============================================================
# routers/dashboard.py — HOD and faculty dashboard summary
# ============================================================
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Student, Prediction, Intervention
from auth import get_current_faculty, get_current_hod

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    db          : Session = Depends(get_db),
    current_user = Depends(get_current_faculty)
):
    """
    Returns risk counts and intervention stats for the
    currently logged-in faculty member's uploaded students.
    Powers the main dashboard view in React.
    """
    # Get all students belonging to this faculty member
    student_ids = [
        s.id for s in
        db.query(Student.id)
        .filter(Student.uploaded_by_id == current_user.id)
        .all()
    ]

    if not student_ids:
        return {
            'total_students'       : 0,
            'high_risk_count'      : 0,
            'medium_risk_count'    : 0,
            'low_risk_count'       : 0,
            'at_risk_count'        : 0,
            'interventions_pending': 0,
            'interventions_resolved': 0,
            'early_checkpoint_count': 0,
            'mid_checkpoint_count' : 0
        }

    # Get latest prediction per student
    predictions = (
        db.query(Prediction)
        .filter(Prediction.student_id.in_(student_ids))
        .all()
    )

    # Keep only the most recent prediction per student
    latest_per_student = {}
    for pred in predictions:
        sid = pred.student_id
        if sid not in latest_per_student:
            latest_per_student[sid] = pred
        elif pred.created_at > latest_per_student[sid].created_at:
            latest_per_student[sid] = pred

    latest_preds = list(latest_per_student.values())

    high_count   = sum(1 for p in latest_preds if p.risk_tier == 'HIGH')
    medium_count = sum(1 for p in latest_preds if p.risk_tier == 'MEDIUM')
    low_count    = sum(1 for p in latest_preds if p.risk_tier == 'LOW')
    at_risk      = sum(1 for p in latest_preds if p.risk_tier in ['HIGH', 'MEDIUM'])

    early_count  = sum(1 for p in latest_preds if p.checkpoint == 'early')
    mid_count    = sum(1 for p in latest_preds if p.checkpoint == 'mid_semester')

    # Intervention stats across all predictions
    pred_ids = [p.id for p in predictions]
    interventions = (
        db.query(Intervention)
        .filter(Intervention.prediction_id.in_(pred_ids))
        .all()
    )

    pending_count  = sum(1 for i in interventions if i.status == 'pending')
    resolved_count = sum(1 for i in interventions if i.status == 'resolved')
    progress_count = sum(1 for i in interventions if i.status == 'in_progress')

    return {
        'total_students'          : len(student_ids),
        'high_risk_count'         : high_count,
        'medium_risk_count'       : medium_count,
        'low_risk_count'          : low_count,
        'at_risk_count'           : at_risk,
        'early_checkpoint_count'  : early_count,
        'mid_checkpoint_count'    : mid_count,
        'interventions_pending'   : pending_count,
        'interventions_in_progress': progress_count,
        'interventions_resolved'  : resolved_count,
    }


@router.get("/hod")
def get_hod_summary(
    db          : Session = Depends(get_db),
    current_user = Depends(get_current_hod)   # HOD only
):
    """
    School-wide view — only accessible by HOD role.
    Shows counts across ALL faculty uploads, not just one teacher.
    """
    total_students = db.query(func.count(Student.id)).scalar()

    predictions = db.query(Prediction).all()

    latest_per_student = {}
    for pred in predictions:
        sid = pred.student_id
        if sid not in latest_per_student:
            latest_per_student[sid] = pred
        elif pred.created_at > latest_per_student[sid].created_at:
            latest_per_student[sid] = pred

    latest_preds = list(latest_per_student.values())

    return {
        'total_students'    : total_students,
        'high_risk_count'   : sum(1 for p in latest_preds if p.risk_tier == 'HIGH'),
        'medium_risk_count' : sum(1 for p in latest_preds if p.risk_tier == 'MEDIUM'),
        'low_risk_count'    : sum(1 for p in latest_preds if p.risk_tier == 'LOW'),
        'at_risk_count'     : sum(1 for p in latest_preds
                                  if p.risk_tier in ['HIGH', 'MEDIUM']),
    }