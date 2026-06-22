# ============================================================
# schemas.py — Pydantic request/response shapes (Pydantic V2)
# ============================================================
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
from datetime import datetime


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "faculty"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Interventions ----------
class InterventionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    feature: str
    driver_label: str
    action_text: str
    referral: str
    status: str

class InterventionStatusUpdate(BaseModel):
    status: str   # "pending" / "in_progress" / "resolved"


# ---------- Predictions ----------
class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    checkpoint: str
    risk_probability: float
    risk_tier: str
    top_risk_drivers: List[str]
    created_at: datetime
    interventions: List[InterventionOut] = []


# ---------- Students ----------
class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_name: str
    student_roll: Optional[str]
    predictions: List[PredictionOut] = []


# ---------- Dashboard ----------
class DashboardSummary(BaseModel):
    total_students: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    interventions_pending: int
    interventions_resolved: int