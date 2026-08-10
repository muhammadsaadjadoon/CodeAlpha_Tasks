from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(24), default="English")
    theme: Mapped[str] = mapped_column(String(24), default="dark")
    default_model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    prediction_threshold: Mapped[float] = mapped_column(Float, default=0.55)
    auto_save: Mapped[bool] = mapped_column(Boolean, default=True)
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    assessment_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    applicants: Mapped[list["Applicant"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class SessionToken(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    user: Mapped[User] = relationship()

class Applicant(Base):
    __tablename__ = "applicants"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    full_name: Mapped[str] = mapped_column(String(180), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employment_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    employment_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    annual_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    existing_debt: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_expenses: Mapped[float | None] = mapped_column(Float, nullable=True)
    savings: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    user: Mapped[User] = relationship(back_populates="applicants")
    assessments: Mapped[list["Assessment"]] = relationship(back_populates="applicant", cascade="all, delete-orphan")
    __table_args__ = (Index("ix_applicant_user_email", "user_id", "email"),)

class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assessment_reference: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    model_name: Mapped[str] = mapped_column(String(80), nullable=False)
    model_version: Mapped[str] = mapped_column(String(40), nullable=False)
    input_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    engineered_features: Mapped[str] = mapped_column(Text, nullable=False)
    prediction: Mapped[int] = mapped_column(Integer, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    credit_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    recommendation: Mapped[str] = mapped_column(String(80), nullable=False)
    positive_factors: Mapped[str] = mapped_column(Text, nullable=False)
    risk_factors: Mapped[str] = mapped_column(Text, nullable=False)
    improvement_recommendations: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    applicant: Mapped[Applicant] = relationship(back_populates="assessments")

class ModelPerformance(Base):
    __tablename__ = "model_performances"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(80), index=True)
    model_version: Mapped[str] = mapped_column(String(40), index=True)
    accuracy: Mapped[float] = mapped_column(Float)
    precision: Mapped[float] = mapped_column(Float)
    recall: Mapped[float] = mapped_column(Float)
    f1_score: Mapped[float] = mapped_column(Float)
    roc_auc: Mapped[float] = mapped_column(Float)
    confusion_matrix: Mapped[str] = mapped_column(Text)
    roc_curve_data: Mapped[str] = mapped_column(Text)
    precision_recall_curve_data: Mapped[str] = mapped_column(Text)
    feature_importance: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    training_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    dataset_records: Mapped[int] = mapped_column(Integer)
    feature_count: Mapped[int] = mapped_column(Integer)
    training_duration: Mapped[float] = mapped_column(Float, default=0)

class DatasetSummary(Base):
    __tablename__ = "dataset_summaries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_name: Mapped[str] = mapped_column(String(160))
    source: Mapped[str] = mapped_column(String(255))
    total_records: Mapped[int] = mapped_column(Integer)
    feature_count: Mapped[int] = mapped_column(Integer)
    missing_values: Mapped[str] = mapped_column(Text)
    duplicate_rows: Mapped[int] = mapped_column(Integer)
    clean_records: Mapped[int] = mapped_column(Integer)
    target_distribution: Mapped[str] = mapped_column(Text)
    numerical_summary: Mapped[str] = mapped_column(Text)
    categorical_summary: Mapped[str] = mapped_column(Text)
    correlation_data: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
