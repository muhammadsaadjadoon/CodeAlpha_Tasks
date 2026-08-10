from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field, field_validator

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: str
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def email_ok(cls, value):
        return validate_email_text(value)

class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def email_ok(cls, value):
        return validate_email_text(value)

def validate_email_text(value: str | None) -> str | None:
    if value is None or value == "":
        return value
    if "@" not in value or "." not in value.split("@")[-1]:
        raise ValueError("Please enter a valid email address.")
    return value.lower().strip()


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    profile_image: str | None = None
    preferred_language: str
    theme: str
    default_model: str | None = None
    prediction_threshold: float
    auto_save: bool
    email_notifications: bool
    assessment_alerts: bool
    created_at: str

class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    email: str | None = None

    @field_validator("email")
    @classmethod
    def email_ok(cls, value):
        return validate_email_text(value)
    preferred_language: str | None = None
    theme: str | None = None
    default_model: str | None = None
    prediction_threshold: float | None = Field(default=None, ge=0.05, le=0.95)
    auto_save: bool | None = None
    email_notifications: bool | None = None
    assessment_alerts: bool | None = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

class ApplicantBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=180)
    email: str | None = None

    @field_validator("email")
    @classmethod
    def email_ok(cls, value):
        return validate_email_text(value)
    phone: str | None = Field(default=None, max_length=80)
    age: int | None = Field(default=None, ge=18, le=100)
    gender: str | None = None
    employment_status: str | None = None
    employment_duration: float | None = Field(default=None, ge=0, le=60)
    annual_income: float | None = Field(default=None, ge=0)
    monthly_income: float | None = Field(default=None, ge=0)
    existing_debt: float | None = Field(default=None, ge=0)
    monthly_expenses: float | None = Field(default=None, ge=0)
    savings: float | None = Field(default=None, ge=0)

class ApplicantCreate(ApplicantBase):
    pass

class ApplicantUpdate(ApplicantBase):
    full_name: str | None = Field(default=None, min_length=2, max_length=180)

class ApplicantOut(ApplicantBase):
    id: int
    latest_credit_score: int | None = None
    current_risk_level: str | None = None
    latest_recommendation: str | None = None
    last_assessment: str | None = None
    created_at: str

class ScoringRequest(ApplicantBase):
    loan_amount: float = Field(ge=0)
    loan_purpose: str = Field(default="personal")
    loan_term: int = Field(default=36, ge=1, le=360)
    existing_loans: int = Field(default=0, ge=0, le=100)
    credit_history_length: float = Field(default=0, ge=0, le=80)
    previous_defaults: int = Field(default=0, ge=0, le=20)
    late_payments: int = Field(default=0, ge=0, le=100)
    payment_behaviour: str = Field(default="consistent")
    credit_utilization: float = Field(default=0.3, ge=0, le=1)
    outstanding_credit_balance: float = Field(default=0, ge=0)

    @field_validator("monthly_income")
    @classmethod
    def monthly_income_optional(cls, value):
        return value

class PredictionOut(BaseModel):
    model_name: str
    model_version: str
    prediction: int
    probability: float
    confidence: float
    credit_score: int
    risk_level: str
    recommendation: str
    engineered_features: dict[str, Any]
    positive_factors: list[str]
    risk_factors: list[str]
    improvement_recommendations: list[str]
    assessment_id: int | None = None
    applicant_id: int | None = None
    assessment_reference: str | None = None

class ListResponse(BaseModel):
    items: list[Any]
    total: int
    page: int = 1
    page_size: int = 20
