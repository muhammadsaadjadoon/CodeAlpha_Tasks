from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from PIL import Image
from sqlalchemy import delete
from sqlalchemy.orm import Session

from ..config import settings
from ..deps import get_current_user, get_db
from ..models import Session as LoginSession, User
from ..schemas import PasswordChangeIn, ProfileNameIn, ThemeIn, UserOut
from ..security import hash_password, hash_session_token, verify_password

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.patch("/theme", response_model=UserOut)
def update_theme(
    payload: ThemeIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.theme = payload.theme
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/name", response_model=UserOut)
def update_name(
    payload: ProfileNameIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    clean_name = " ".join(payload.full_name.strip().split())
    if len(clean_name) < 2:
        raise HTTPException(status_code=422, detail="Username must contain at least 2 characters.")

    user.full_name = clean_name
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/password", status_code=204)
def update_password(
    payload: PasswordChangeIn,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    if verify_password(payload.new_password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Choose a new password that is different from your current password.",
        )

    user.password_hash = hash_password(payload.new_password)
    db.add(user)

    # Keep the current browser session, but invalidate every other active session
    # after a password change.
    current_token = request.cookies.get(settings.session_cookie_name)
    delete_statement = delete(LoginSession).where(LoginSession.user_id == user.id)
    if current_token:
        delete_statement = delete_statement.where(
            LoginSession.token_hash != hash_session_token(current_token)
        )
    db.execute(delete_statement)
    db.commit()
    return Response(status_code=204)


@router.post("/avatar", response_model=UserOut)
async def upload_avatar(
    avatar: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    raw = await avatar.read()
    if len(raw) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Profile image must be 2 MB or smaller.")

    try:
        image = Image.open(BytesIO(raw))
        image.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid profile image.")

    if avatar.content_type not in {"image/png", "image/jpeg", "image/webp"}:
        raise HTTPException(status_code=400, detail="Use PNG, JPEG, or WebP.")

    user.avatar_bytes = raw
    user.avatar_mime = avatar.content_type
    user.avatar_version = (user.avatar_version or 0) + 1
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/avatar", response_model=UserOut)
def delete_avatar(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.avatar_bytes = None
    user.avatar_mime = None
    user.avatar_version = (user.avatar_version or 0) + 1
    db.commit()
    db.refresh(user)
    return user


@router.get("/avatar")
def avatar(user: User = Depends(get_current_user)):
    if not user.avatar_bytes:
        raise HTTPException(status_code=404, detail="No profile image.")

    return Response(
        content=user.avatar_bytes,
        media_type=user.avatar_mime or "image/png",
        headers={"Cache-Control": "no-store"},
    )
