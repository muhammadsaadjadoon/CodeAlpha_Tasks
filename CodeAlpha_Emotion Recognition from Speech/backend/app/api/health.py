from fastapi import APIRouter
from app.services.inference import inference_service

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok", "model_ready": inference_service.model is not None, "model_version": inference_service.version}


@router.get("/model/info")
def model_info():
    return {
        "name": "INFLECT Speech Emotion Intelligence",
        "architecture": "Wav2Vec2 audio classification champion",
        "labels": ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"],
        "version": inference_service.version,
        "ready": inference_service.model is not None,
        "privacy": "Audio is processed transiently and is not retained after inference.",
    }
