# ============================================================
# models.py — Database table definitions
# ============================================================
from sqlalchemy import (Column, Integer, String, Float,
                         ForeignKey, DateTime, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id               = Column(Integer, primary_key=True, index=True)
    email            = Column(String, unique=True, index=True, nullable=False)
    hashed_password  = Column(String, nullable=False)
    full_name        = Column(String, nullable=False)
    role             = Column(String, default="faculty")  # "faculty" or "hod"
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

    students = relationship("Student", back_populates="uploaded_by")


class Student(Base):
    __tablename__ = "students"

    id               = Column(Integer, primary_key=True, index=True)
    student_name     = Column(String, nullable=False)
    student_roll     = Column(String, nullable=True)
    uploaded_by_id   = Column(Integer, ForeignKey("users.id"))
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

    uploaded_by  = relationship("User", back_populates="students")
    predictions  = relationship("Prediction", back_populates="student")


class Prediction(Base):
    __tablename__ = "predictions"

    id               = Column(Integer, primary_key=True, index=True)
    student_id       = Column(Integer, ForeignKey("students.id"))
    checkpoint       = Column(String, nullable=False)  # "early" or "mid_semester"
    risk_probability = Column(Float, nullable=False)
    risk_tier        = Column(String, nullable=False)  # HIGH / MEDIUM / LOW
    shap_values      = Column(Text, nullable=True)     # stored as JSON string
    top_risk_drivers = Column(Text, nullable=True)     # stored as JSON string
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

    student       = relationship("Student", back_populates="predictions")
    interventions = relationship("Intervention", back_populates="prediction")


class Intervention(Base):
    __tablename__ = "interventions"

    id            = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"))
    feature       = Column(String, nullable=False)
    driver_label  = Column(String, nullable=False)
    action_text   = Column(Text, nullable=False)
    referral      = Column(String, nullable=False)
    status        = Column(String, default="pending")  # pending/in_progress/resolved
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    prediction = relationship("Prediction", back_populates="interventions")