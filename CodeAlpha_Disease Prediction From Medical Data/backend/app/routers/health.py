from fastapi import APIRouter

from ..model_service import model_is_ready
from ..schemas import HealthResponse


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", model_ready=model_is_ready(), service="HeartTrack API")
