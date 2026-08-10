from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from ..config import settings
from ..deps import get_current_user, get_db
from ..models import Session as LoginSession, User
from ..schemas import LoginIn, RegisterIn, UserOut
from ..security import expiry, hash_password, hash_session_token, new_session_token, verify_password

router=APIRouter(prefix="/api/auth", tags=["auth"])

def set_cookie(response: Response, token: str):
    response.set_cookie(settings.session_cookie_name, token, httponly=True, secure=settings.cookie_secure, samesite="lax", path="/")

@router.post("/register", response_model=UserOut)
def register(payload:RegisterIn,response:Response,db:Session=Depends(get_db)):
    email=payload.email.lower().strip()
    if db.scalar(select(User).where(User.email==email)):
        raise HTTPException(status_code=409,detail="An account with this email already exists.")
    user=User(email=email,full_name=payload.full_name.strip(),password_hash=hash_password(payload.password),theme="system")
    db.add(user); db.flush()
    token=new_session_token(); db.add(LoginSession(user_id=user.id,token_hash=hash_session_token(token),expires_at=expiry(settings.session_ttl_hours)))
    db.commit(); db.refresh(user); set_cookie(response,token); return user

@router.post("/login",response_model=UserOut)
def login(payload:LoginIn,response:Response,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==payload.email.lower().strip()))
    if not user or not verify_password(payload.password,user.password_hash):
        raise HTTPException(status_code=401,detail="Incorrect email or password.")
    token=new_session_token(); db.add(LoginSession(user_id=user.id,token_hash=hash_session_token(token),expires_at=expiry(settings.session_ttl_hours))); db.commit(); set_cookie(response,token); return user

@router.post("/logout",status_code=204)
def logout(request:Request,response:Response,db:Session=Depends(get_db)):
    token=request.cookies.get(settings.session_cookie_name)
    if token: db.execute(delete(LoginSession).where(LoginSession.token_hash==hash_session_token(token))); db.commit()
    response.delete_cookie(settings.session_cookie_name,path="/")

@router.get("/me",response_model=UserOut)
def me(user:User=Depends(get_current_user)): return user
