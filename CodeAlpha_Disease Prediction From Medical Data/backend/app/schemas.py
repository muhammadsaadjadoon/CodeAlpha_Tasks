from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

    @field_validator("full_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Full name is required")
        return cleaned

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        if not any(ch.isupper() for ch in value):
            raise ValueError("Password must contain an uppercase letter")
        if not any(ch.islower() for ch in value):
            raise ValueError("Password must contain a lowercase letter")
        if not any(ch.isdigit() for ch in value):
            raise ValueError("Password must contain a number")
        return value


class ProfileUpdateRequest(BaseModel):
    display_name: str = Field(min_length=2, max_length=80)
    email: EmailStr

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Display name is required")
        return cleaned


class UserResponse(BaseModel):
    email: EmailStr
    display_name: str


class LoginResponse(BaseModel):
    user: UserResponse
    message: str = "Signed in successfully"


class RegisterResponse(BaseModel):
    user: UserResponse
    message: str = "Account created successfully"


class HeartAssessment(BaseModel):
    age: int = Field(ge=18, le=100)
    sex: int = Field(ge=0, le=1, description="Sex category used by the trained model: 0=female, 1=male")
    cp: int = Field(ge=1, le=4, description="Chest pain category used by the trained model")
    trestbps: float = Field(ge=70, le=250)
    chol: float = Field(ge=80, le=700)
    fbs: int = Field(ge=0, le=1)
    restecg: int = Field(ge=0, le=2)
    thalach: float = Field(ge=50, le=250)
    exang: int = Field(ge=0, le=1)
    oldpeak: float = Field(ge=-2.5, le=10)
    slope: int = Field(ge=1, le=3)
    ca: int = Field(ge=0, le=3)
    thal: int = Field(ge=3, le=7)

    @field_validator("thal")
    @classmethod
    def validate_thal(cls, value: int) -> int:
        if value not in {3, 6, 7}:
            raise ValueError("Select a valid thallium stress-test result")
        return value


class FeatureInfluence(BaseModel):
    feature: str
    label: str
    direction: Literal["higher", "lower", "neutral"]
    impact: float
    value: float
    reference: float


class PredictionResponse(BaseModel):
    probability: float
    percent: float
    predicted_class: int
    risk_level: Literal["Low", "Moderate", "High", "Very High"]
    model_name: str
    threshold: float
    influences: list[FeatureInfluence]
    disclaimer: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_ready: bool
    service: str
