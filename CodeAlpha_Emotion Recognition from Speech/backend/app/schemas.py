from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ThemeRequest(BaseModel):
    theme: Literal["system", "light", "dark"]


class ProfileRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    theme: str
    has_avatar: bool = False
    avatar_updated_at: datetime | None = None


class EmotionScore(BaseModel):
    label: str
    probability: float


class AnalysisResponse(BaseModel):
    id: int
    primary_emotion: str
    confidence: float
    distribution: list[EmotionScore]
    valence: float
    arousal: float
    duration_seconds: float
    sample_rate: int
    model_version: str
    source_type: str
    source_name: str
    created_at: datetime
    privacy: str = "Audio is processed transiently and removed immediately after analysis. Only result metadata is retained in your private history."


class AnalysisHistoryPage(BaseModel):
    items: list[AnalysisResponse]
    total: int


class ModelStatusResponse(BaseModel):
    ready: bool
    state: Literal["ready", "available", "loading", "unavailable", "error"]
    model_version: str
    source: str
    device: str
    message: str
