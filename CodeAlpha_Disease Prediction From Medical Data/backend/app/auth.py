from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Annotated

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Cookie, Depends, HTTPException, Response, status

from .config import Settings, get_settings
from .schemas import UserResponse


COOKIE_NAME = "ht_session"
ALGORITHM = "HS256"
_password_hasher = PasswordHasher()
_registry_lock = Lock()
_registered_users: dict[str, dict[str, str]] = {}
_demo_hash_cache: dict[str, str] = {}


def _demo_password_hash(settings: Settings) -> str:
    cached = _demo_hash_cache.get(settings.demo_password)
    if cached:
        return cached
    password_hash = _password_hasher.hash(settings.demo_password)
    _demo_hash_cache[settings.demo_password] = password_hash
    return password_hash


def register_runtime_user(full_name: str, email: str, password: str, settings: Settings) -> UserResponse | None:
    normalized_email = email.strip().lower()
    if normalized_email == settings.demo_email.lower():
        return None
    with _registry_lock:
        if normalized_email in _registered_users:
            return None
        _registered_users[normalized_email] = {
            "display_name": full_name.strip(),
            "password_hash": _password_hasher.hash(password),
        }
    return UserResponse(email=normalized_email, display_name=full_name.strip())


def authenticate_user(email: str, password: str, settings: Settings) -> UserResponse | None:
    normalized_email = email.strip().lower()
    if normalized_email == settings.demo_email.lower():
        try:
            _password_hasher.verify(_demo_password_hash(settings), password)
        except VerifyMismatchError:
            return None
        return UserResponse(email=settings.demo_email, display_name="HeartTrack Analyst")

    record = _registered_users.get(normalized_email)
    if record is None:
        return None
    try:
        _password_hasher.verify(record["password_hash"], password)
    except VerifyMismatchError:
        return None
    return UserResponse(email=normalized_email, display_name=record["display_name"])


def update_runtime_user_profile(
    current_user: UserResponse,
    display_name: str,
    email: str,
    settings: Settings,
) -> UserResponse | None:
    current_email = str(current_user.email).strip().lower()
    normalized_email = email.strip().lower()
    cleaned_name = " ".join(display_name.split())
    demo_email = settings.demo_email.lower()

    with _registry_lock:
        # The built-in demo identity is reserved for the demo account itself.
        if normalized_email == demo_email and current_email != demo_email:
            return None
        if normalized_email != current_email and normalized_email in _registered_users:
            return None

        if current_email == demo_email:
            # Keep the original demo login available. If the demo user chooses a new
            # email, create a runtime account carrying the same demo password.
            if normalized_email != demo_email:
                _registered_users[normalized_email] = {
                    "display_name": cleaned_name,
                    "password_hash": _demo_password_hash(settings),
                }
        else:
            record = _registered_users.get(current_email)
            if record is not None:
                record = {**record, "display_name": cleaned_name}
                if normalized_email != current_email:
                    _registered_users.pop(current_email, None)
                    _registered_users[normalized_email] = record
                else:
                    _registered_users[current_email] = record

    return UserResponse(email=normalized_email, display_name=cleaned_name)


def issue_session_cookie(response: Response, user: UserResponse, settings: Settings) -> None:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.email),
        "name": user.display_name,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.session_minutes)).timestamp()),
        "aud": "hearttrack-web",
        "iss": "hearttrack-api",
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=settings.session_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )


def get_current_user(
    session: Annotated[str | None, Cookie(alias=COOKIE_NAME)] = None,
    settings: Settings = Depends(get_settings),
) -> UserResponse:
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in to continue.")
    try:
        payload = jwt.decode(
            session,
            settings.secret_key,
            algorithms=[ALGORITHM],
            audience="hearttrack-web",
            issuer="hearttrack-api",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session has expired. Please sign in again.") from exc
    return UserResponse(email=payload["sub"], display_name=payload.get("name", "HeartTrack Analyst"))
