from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

Theme = Literal["system", "light", "dark"]

class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class ThemeIn(BaseModel):
    theme: Theme


class ProfileNameIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)

class PasswordChangeIn(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str
    theme: Theme
    avatar_version: int

class ScoreOut(BaseModel):
    label: str
    probability: float

class RecognitionOut(BaseModel):
    id: int
    primary_label: str
    confidence: float
    distribution: list[ScoreOut]
    model_role: str
    model_version: str
    source_type: str
    source_name: str
    foreground_ratio: float
    processed_preview: str | None = None
    created_at: datetime

class HistoryPage(BaseModel):
    items: list[RecognitionOut]
    total: int
