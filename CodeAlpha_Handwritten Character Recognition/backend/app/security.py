from datetime import datetime, timedelta, timezone
import hashlib, secrets
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(password: str, password_hash: str) -> bool:
    try: return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError: return False

def new_session_token() -> str:
    return secrets.token_urlsafe(48)

def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def expiry(hours: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=hours)
