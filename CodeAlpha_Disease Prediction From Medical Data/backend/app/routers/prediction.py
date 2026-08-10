from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import get_current_user
from ..model_service import HeartModelService, ModelNotReadyError, get_model_service
from ..schemas import HeartAssessment, PredictionResponse, UserResponse


router = APIRouter(prefix="/prediction", tags=["Prediction"])


@router.post("/heart", response_model=PredictionResponse)
def predict_heart_risk(
    assessment: HeartAssessment,
    _: UserResponse = Depends(get_current_user),
):
    try:
        service: HeartModelService = get_model_service()
    except ModelNotReadyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return service.predict(assessment)
