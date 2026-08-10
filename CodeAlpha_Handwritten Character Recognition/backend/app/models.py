from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

def utcnow(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    theme: Mapped[str] = mapped_column(String(16), default="system")
    avatar_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    avatar_mime: Mapped[str | None] = mapped_column(String(64), nullable=True)
    avatar_version: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    sessions: Mapped[list["Session"]] = relationship(cascade="all, delete-orphan")
    records: Mapped[list["RecognitionRecord"]] = relationship(cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class RecognitionRecord(Base):
    __tablename__ = "recognition_records"
    __table_args__ = (Index("ix_recognition_user_created", "user_id", "created_at"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    primary_label: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float)
    distribution_json: Mapped[str] = mapped_column(Text)
    model_role: Mapped[str] = mapped_column(String(32))
    model_version: Mapped[str] = mapped_column(String(120))
    source_type: Mapped[str] = mapped_column(String(32))
    source_name: Mapped[str] = mapped_column(String(255))
    foreground_ratio: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
