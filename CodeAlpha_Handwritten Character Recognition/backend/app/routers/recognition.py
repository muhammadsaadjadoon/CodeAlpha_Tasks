import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..config import settings
from ..deps import get_current_user, get_db
from ..models import RecognitionRecord, User
from ..schemas import RecognitionOut
from ..services.image_preprocessing import preprocess_character
from ..services.model_runtime import runtime

router=APIRouter(prefix="/api/recognition",tags=["recognition"])

@router.post("/character",response_model=RecognitionOut)
async def recognize(image:UploadFile=File(...),mode:str=Form("auto"),source_type:str=Form("upload"),source_name:str=Form("handwriting.png"),user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    raw=await image.read()
    if not raw: raise HTTPException(status_code=400,detail="No image data received.")
    if len(raw)>settings.max_image_bytes: raise HTTPException(status_code=413,detail="Image is too large.")
    try: processed=preprocess_character(raw)
    except ValueError as exc: raise HTTPException(status_code=400,detail=str(exc))
    role="digit" if mode=="digits" else "character"
    try: prediction=runtime.predict(processed,role)
    except RuntimeError as exc: raise HTTPException(status_code=503,detail=str(exc))
    record=RecognitionRecord(user_id=user.id,primary_label=prediction["primary_label"],confidence=prediction["confidence"],distribution_json=json.dumps(prediction["distribution"]),model_role=role,model_version=prediction["model_version"],source_type=source_type[:32],source_name=source_name[:255],foreground_ratio=processed.foreground_ratio)
    db.add(record); db.commit(); db.refresh(record)
    return RecognitionOut(id=record.id,primary_label=record.primary_label,confidence=record.confidence,distribution=prediction["distribution"],model_role=record.model_role,model_version=record.model_version,source_type=record.source_type,source_name=record.source_name,foreground_ratio=record.foreground_ratio,processed_preview=processed.preview_data_url,created_at=record.created_at)
