from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    theme: Mapped[str] = mapped_column(String(16), default="system")
    avatar_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    avatar_mime: Mapped[str | None] = mapped_column(String(48), nullable=True)
    avatar_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def has_avatar(self) -> bool:
        return bool(self.avatar_data and self.avatar_mime)
    sessions: Mapped[list["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    analyses: Mapped[list["AnalysisRecord"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user: Mapped[User] = relationship(back_populates="sessions")


class AnalysisRecord(Base):
    """Server-side analysis metadata. Raw audio is never persisted."""

    __tablename__ = "analysis_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    primary_emotion: Mapped[str] = mapped_column(String(48), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    distribution_json: Mapped[str] = mapped_column(Text)
    valence: Mapped[float] = mapped_column(Float)
    arousal: Mapped[float] = mapped_column(Float)
    duration_seconds: Mapped[float] = mapped_column(Float)
    sample_rate: Mapped[int] = mapped_column(Integer)
    model_version: Mapped[str] = mapped_column(String(180))
    source_type: Mapped[str] = mapped_column(String(24), default="upload", index=True)
    source_name: Mapped[str] = mapped_column(String(180), default="Voice sample")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    user: Mapped[User] = relationship(back_populates="analyses")
