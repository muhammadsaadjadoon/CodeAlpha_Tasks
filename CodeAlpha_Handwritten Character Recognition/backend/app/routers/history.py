import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session
from ..deps import get_current_user, get_db
from ..models import RecognitionRecord, User
from ..schemas import HistoryPage, RecognitionOut

router=APIRouter(prefix="/api/recognition",tags=["history"])

def out(r):
    return RecognitionOut(id=r.id,primary_label=r.primary_label,confidence=r.confidence,distribution=json.loads(r.distribution_json),model_role=r.model_role,model_version=r.model_version,source_type=r.source_type,source_name=r.source_name,foreground_ratio=r.foreground_ratio,processed_preview=None,created_at=r.created_at)

@router.get("/history",response_model=HistoryPage)
def history(limit:int=50,offset:int=0,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    limit=max(1,min(limit,100)); offset=max(0,offset)
    total=db.scalar(select(func.count()).select_from(RecognitionRecord).where(RecognitionRecord.user_id==user.id)) or 0
    rows=db.scalars(select(RecognitionRecord).where(RecognitionRecord.user_id==user.id).order_by(RecognitionRecord.created_at.desc()).limit(limit).offset(offset)).all()
    return HistoryPage(items=[out(r) for r in rows],total=total)

@router.delete("/history/{record_id}",status_code=204)
def remove(record_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    row=db.get(RecognitionRecord,record_id)
    if not row or row.user_id!=user.id: raise HTTPException(status_code=404,detail="Record not found.")
    db.delete(row); db.commit()

@router.delete("/history",status_code=204)
def clear(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    db.execute(delete(RecognitionRecord).where(RecognitionRecord.user_id==user.id)); db.commit()
