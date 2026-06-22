# ============================================================
# routers/interventions.py — Update intervention status
# ============================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Intervention, Prediction, Student
from schemas import InterventionStatusUpdate
from auth import get_current_faculty

router = APIRouter(prefix="/interventions", tags=["Interventions"])


@router.patch("/{intervention_id}")
def update_intervention_status(
    intervention_id : int,
    update          : InterventionStatusUpdate,
    db              : Session = Depends(get_db),
    current_user     = Depends(get_current_faculty)
):
    """
    Updates the status of one intervention.
    Faculty mark interventions as they act on them:
      pending -> in_progress -> resolved
    This is what the HOD dashboard tracks over time.
    """
    allowed_statuses = ['pending', 'in_progress', 'resolved']
    if update.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of: {allowed_statuses}"
        )

    # Verify this intervention belongs to current user's student
    intervention = (
        db.query(Intervention)
        .join(Prediction)
        .join(Student)
        .filter(
            Intervention.id == intervention_id,
            Student.uploaded_by_id == current_user.id
        )
        .first()
    )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )

    intervention.status = update.status
    db.commit()
    db.refresh(intervention)

    return {
        'intervention_id': intervention.id,
        'feature'        : intervention.feature,
        'driver_label'   : intervention.driver_label,
        'status'         : intervention.status,
        'message'        : f"Status updated to '{update.status}'"
    }


@router.get("/{intervention_id}")
def get_intervention(
    intervention_id: int,
    db             : Session = Depends(get_db),
    current_user    = Depends(get_current_faculty)
):
    """Returns a single intervention's full details."""
    intervention = (
        db.query(Intervention)
        .join(Prediction)
        .join(Student)
        .filter(
            Intervention.id == intervention_id,
            Student.uploaded_by_id == current_user.id
        )
        .first()
    )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )

    return {
        'intervention_id': intervention.id,
        'prediction_id'  : intervention.prediction_id,
        'feature'        : intervention.feature,
        'driver_label'   : intervention.driver_label,
        'action_text'    : intervention.action_text,
        'referral'       : intervention.referral,
        'status'         : intervention.status,
        'created_at'     : intervention.created_at.isoformat()
    }