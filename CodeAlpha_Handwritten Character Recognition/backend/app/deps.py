from datetime import datetime, timezone
from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import settings
from .db import SessionLocal
from .models import Session as LoginSession, User
from .security import hash_session_token

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    token_hash = hash_session_token(token)
    login = db.scalar(select(LoginSession).where(LoginSession.token_hash == token_hash))
    expires = login.expires_at if login and login.expires_at.tzinfo else (login.expires_at.replace(tzinfo=timezone.utc) if login else None)
    if not login or (expires is not None and expires < datetime.now(timezone.utc)):
        if login:
            db.delete(login); db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired.")
    user = db.get(User, login.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not found.")
    return user
