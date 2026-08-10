from fastapi import APIRouter, Depends
from ..deps import get_current_user
from ..models import User
from ..services.model_runtime import runtime
router=APIRouter(prefix="/api/model",tags=["model"])
@router.get("/status")
def status(user:User=Depends(get_current_user)): return runtime.status()
@router.get("/metrics")
def metrics(user:User=Depends(get_current_user)): return runtime.metrics()
