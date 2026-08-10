import json
import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session
from app.config import settings
from app.db import get_db
from app.dependencies import current_user
from app.models import AnalysisRecord, User
from app.schemas import AnalysisHistoryPage, AnalysisResponse, EmotionScore, ModelStatusResponse
from app.services.audio import AudioValidationError, load_and_normalize
from app.services.inference import ModelUnavailableError, inference_service

router = APIRouter(prefix="/api/analysis", tags=["analysis"])
ALLOWED_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp4",
    "audio/x-m4a",
    "audio/webm",
    "audio/ogg",
    "audio/flac",
    "application/octet-stream",
}


def record_to_response(record: AnalysisRecord) -> AnalysisResponse:
    distribution_data = json.loads(record.distribution_json)
    return AnalysisResponse(
        id=record.id,
        primary_emotion=record.primary_emotion,
        confidence=record.confidence,
        distribution=[EmotionScore(**item) for item in distribution_data],
        valence=record.valence,
        arousal=record.arousal,
        duration_seconds=record.duration_seconds,
        sample_rate=record.sample_rate,
        model_version=record.model_version,
        source_type=record.source_type,
        source_name=record.source_name,
        created_at=record.created_at,
    )


@router.get("/model-status", response_model=ModelStatusResponse)
def model_status(_: User = Depends(current_user)):
    return inference_service.status()


@router.post("/voice", response_model=AnalysisResponse)
async def analyze_voice(
    audio: UploadFile = File(...),
    source_type: str = Form(default="upload"),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    content_type = (audio.content_type or "application/octet-stream").split(";")[0].strip().lower()
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Choose a WAV, MP3, M4A, WebM, OGG, or FLAC audio file.")
    if source_type not in {"recording", "upload"}:
        raise HTTPException(status_code=422, detail="Unsupported audio source.")

    max_bytes = settings.max_audio_mb * 1024 * 1024
    original_name = Path(audio.filename or ("Live recording.wav" if source_type == "recording" else "Voice sample")).name
    suffix = Path(original_name).suffix or (".wav" if source_type == "recording" else ".bin")
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
            temp_path = Path(handle.name)
            total = 0
            while chunk := await audio.read(1024 * 1024):
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(status_code=413, detail=f"Audio must be smaller than {settings.max_audio_mb} MB.")
                handle.write(chunk)

        signal, sample_rate, duration = load_and_normalize(temp_path)
        prediction = inference_service.predict(signal, sample_rate)
        distribution = [
            EmotionScore(label=label, probability=prob)
            for label, prob in sorted(prediction.probabilities.items(), key=lambda item: item[1], reverse=True)
        ]
        record = AnalysisRecord(
            user_id=user.id,
            primary_emotion=prediction.primary_emotion,
            confidence=prediction.confidence,
            distribution_json=json.dumps([item.model_dump() for item in distribution]),
            valence=prediction.valence,
            arousal=prediction.arousal,
            duration_seconds=duration,
            sample_rate=sample_rate,
            model_version=prediction.model_version,
            source_type=source_type,
            source_name="Live microphone" if source_type == "recording" else original_name[:180],
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record_to_response(record)
    except AudioValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ModelUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    finally:
        await audio.close()
        if temp_path and temp_path.exists():
            try:
                os.remove(temp_path)
            except OSError:
                pass


@router.get("/history", response_model=AnalysisHistoryPage)
def history(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    total = db.scalar(select(func.count(AnalysisRecord.id)).where(AnalysisRecord.user_id == user.id)) or 0
    records = db.scalars(
        select(AnalysisRecord)
        .where(AnalysisRecord.user_id == user.id)
        .order_by(AnalysisRecord.created_at.desc(), AnalysisRecord.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return AnalysisHistoryPage(items=[record_to_response(record) for record in records], total=total)


@router.delete("/history/{record_id}", status_code=204)
def delete_history_item(
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    record = db.scalar(
        select(AnalysisRecord).where(AnalysisRecord.id == record_id, AnalysisRecord.user_id == user.id)
    )
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    db.delete(record)
    db.commit()


@router.delete("/history", status_code=204)
def clear_history(db: Session = Depends(get_db), user: User = Depends(current_user)):
    db.execute(delete(AnalysisRecord).where(AnalysisRecord.user_id == user.id))
    db.commit()
