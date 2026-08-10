from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.db import get_db
from app.models import User
from app.security import get_user_by_session


def current_user(
    db: Session = Depends(get_db),
    token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
) -> User:
    user = get_user_by_session(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    return user
