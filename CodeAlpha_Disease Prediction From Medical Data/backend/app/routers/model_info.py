import json

from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import get_current_user
from ..config import Settings, get_settings
from ..schemas import UserResponse


router = APIRouter(prefix="/models", tags=["Model Lab"])


@router.get("/report")
def model_report(
    _: UserResponse = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    if not settings.metrics_path.exists():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model performance details are temporarily unavailable.")
    return json.loads(settings.metrics_path.read_text(encoding="utf-8"))


@router.get("/dataset")
def dataset_report(
    _: UserResponse = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    if not settings.dataset_report_path.exists():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Training data details are temporarily unavailable.")
    return json.loads(settings.dataset_report_path.read_text(encoding="utf-8"))
