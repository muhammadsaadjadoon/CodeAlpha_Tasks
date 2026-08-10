from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from .config import ACCESS_TOKEN_EXPIRE_MINUTES
from .models import SessionToken, User

ITERATIONS = 390_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(db: Session, user: User) -> str:
    raw = secrets.token_urlsafe(36)
    db.add(SessionToken(
        user_id=user.id,
        token_hash=token_digest(raw),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    ))
    db.commit()
    return raw


def get_user_by_token(db: Session, token: str | None) -> User | None:
    if not token:
        return None
    session = db.query(SessionToken).filter(SessionToken.token_hash == token_digest(token)).first()
    if not session:
        return None
    expires = session.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        return None
    return db.get(User, session.user_id)


def destroy_session(db: Session, token: str | None) -> None:
    if not token:
        return
    session = db.query(SessionToken).filter(SessionToken.token_hash == token_digest(token)).first()
    if session:
        db.delete(session)
        db.commit()
