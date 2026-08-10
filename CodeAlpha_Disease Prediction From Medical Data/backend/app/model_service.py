from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .config import get_settings
from .schemas import FeatureInfluence, HeartAssessment, PredictionResponse


FEATURE_LABELS = {
    "age": "Age",
    "sex": "Sex",
    "cp": "Chest pain type",
    "trestbps": "Resting blood pressure",
    "chol": "Serum cholesterol",
    "fbs": "Fasting blood sugar",
    "restecg": "Resting ECG",
    "thalach": "Maximum heart rate",
    "exang": "Exercise-induced angina",
    "oldpeak": "ST depression",
    "slope": "ST slope",
    "ca": "Major vessels",
    "thal": "Thalassemia category",
}


class ModelNotReadyError(RuntimeError):
    pass


class HeartModelService:
    def __init__(self, bundle_path: Path):
        if not bundle_path.exists():
            raise ModelNotReadyError(
                "The prediction model is not ready yet. Please try again after it has been set up."
            )
        self.bundle = joblib.load(bundle_path)
        self.model = self.bundle["model"]
        self.features = self.bundle["features"]
        self.references = self.bundle["feature_reference"]
        self.model_name = self.bundle["model_name"]
        self.threshold = float(self.bundle.get("threshold", 0.5))

    def _probability(self, frame: pd.DataFrame) -> float:
        return float(self.model.predict_proba(frame[self.features])[:, 1][0])

    def _local_influences(self, row: dict[str, float], base_prob: float) -> list[FeatureInfluence]:
        influences: list[FeatureInfluence] = []
        for feature in self.features:
            reference = float(self.references[feature])
            counterfactual = row.copy()
            counterfactual[feature] = reference
            ref_prob = self._probability(pd.DataFrame([counterfactual]))
            impact = base_prob - ref_prob
            if impact > 0.008:
                direction = "higher"
            elif impact < -0.008:
                direction = "lower"
            else:
                direction = "neutral"
            influences.append(
                FeatureInfluence(
                    feature=feature,
                    label=FEATURE_LABELS.get(feature, feature),
                    direction=direction,
                    impact=round(float(impact), 4),
                    value=float(row[feature]),
                    reference=round(reference, 3),
                )
            )
        influences.sort(key=lambda item: abs(item.impact), reverse=True)
        return influences[:6]

    @staticmethod
    def _risk_level(probability: float) -> str:
        if probability < 0.30:
            return "Low"
        if probability < 0.60:
            return "Moderate"
        if probability < 0.80:
            return "High"
        return "Very High"

    def predict(self, assessment: HeartAssessment) -> PredictionResponse:
        row = assessment.model_dump()
        frame = pd.DataFrame([row], columns=self.features)
        probability = self._probability(frame)
        predicted_class = int(probability >= self.threshold)
        return PredictionResponse(
            probability=round(probability, 6),
            percent=round(probability * 100, 1),
            predicted_class=predicted_class,
            risk_level=self._risk_level(probability),
            model_name=self.model_name,
            threshold=round(self.threshold, 3),
            influences=self._local_influences(row, probability),
            disclaimer=(
                "This estimate is for informational use only and is not a diagnosis. "
                "If you have health concerns, speak with a qualified healthcare professional."
            ),
        )


@lru_cache
def get_model_service() -> HeartModelService:
    return HeartModelService(get_settings().model_bundle_path)


def model_is_ready() -> bool:
    try:
        get_model_service()
        return True
    except ModelNotReadyError:
        return False
