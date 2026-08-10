from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import current_user
from app.models import User
from app.schemas import ProfileRequest, ThemeRequest, UserOut

router = APIRouter(prefix="/api/profile", tags=["profile"])

MAX_AVATAR_BYTES = 2 * 1024 * 1024
AVATAR_TYPES = {
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/webp": (b"RIFF",),
}


def _detect_avatar_mime(content: bytes) -> str | None:
    if content.startswith(AVATAR_TYPES["image/jpeg"][0]):
        return "image/jpeg"
    if content.startswith(AVATAR_TYPES["image/png"][0]):
        return "image/png"
    if len(content) >= 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return "image/webp"
    return None


def _save_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("", response_model=UserOut)
def update_profile(
    payload: ProfileRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    user.full_name = payload.full_name.strip()
    return _save_user(db, user)


@router.patch("/theme", response_model=UserOut)
def update_theme(
    payload: ThemeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    user.theme = payload.theme
    return _save_user(db, user)


@router.put("/avatar", response_model=UserOut)
async def upload_avatar(
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    try:
        content = await avatar.read(MAX_AVATAR_BYTES + 1)
    finally:
        await avatar.close()

    if not content:
        raise HTTPException(status_code=422, detail="Choose a non-empty profile image.")
    if len(content) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=413, detail="Profile image must be 2 MB or smaller.")

    detected_mime = _detect_avatar_mime(content)
    if detected_mime is None:
        raise HTTPException(status_code=415, detail="Choose a JPEG, PNG, or WebP profile image.")

    user.avatar_data = content
    user.avatar_mime = detected_mime
    user.avatar_updated_at = datetime.now(timezone.utc)
    return _save_user(db, user)


@router.get("/avatar")
def get_avatar(user: User = Depends(current_user)):
    if not user.avatar_data or not user.avatar_mime:
        raise HTTPException(status_code=404, detail="No profile image has been uploaded.")

    return Response(
        content=user.avatar_data,
        media_type=user.avatar_mime,
        headers={
            "Cache-Control": "no-store, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "Content-Disposition": "inline",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.delete("/avatar", response_model=UserOut)
def delete_avatar(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    user.avatar_data = None
    user.avatar_mime = None
    user.avatar_updated_at = datetime.now(timezone.utc)
    return _save_user(db, user)
