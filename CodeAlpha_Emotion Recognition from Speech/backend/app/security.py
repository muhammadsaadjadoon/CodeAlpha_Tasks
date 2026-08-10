import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from sqlalchemy import delete, select
from sqlalchemy.orm import Session as DbSession
from app.config import settings
from app.models import Session, User

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    return password_hash.verify(password, stored_hash)


def _token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(db: DbSession, user: User) -> str:
    token = secrets.token_urlsafe(48)
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.session_ttl_hours)
    db.add(Session(user_id=user.id, token_hash=_token_digest(token), expires_at=expires))
    db.commit()
    return token


def revoke_session(db: DbSession, token: str | None) -> None:
    if token:
        db.execute(delete(Session).where(Session.token_hash == _token_digest(token)))
        db.commit()


def get_user_by_session(db: DbSession, token: str | None) -> User | None:
    if not token:
        return None
    now = datetime.now(timezone.utc)
    stmt = select(Session).where(Session.token_hash == _token_digest(token), Session.expires_at > now)
    session = db.scalar(stmt)
    return session.user if session else None
