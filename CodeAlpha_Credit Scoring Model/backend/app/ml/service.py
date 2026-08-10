from __future__ import annotations

import json
import math
from pathlib import Path
from functools import lru_cache
import joblib
import pandas as pd
from ..config import MODEL_DIRECTORY, MODEL_VERSION, SCORE_MAX, SCORE_MIN
from .features import engineer_features
from .train import FEATURE_COLUMNS, train_models


def score_from_probability(probability: float) -> int:
    score = SCORE_MIN + probability * (SCORE_MAX - SCORE_MIN)
    return int(max(SCORE_MIN, min(SCORE_MAX, round(score))))


def risk_level(score: int) -> str:
    if score >= 750:
        return "Low Risk"
    if score >= 670:
        return "Moderate Risk"
    if score >= 580:
        return "Elevated Risk"
    return "High Risk"


def recommendation(probability: float, score: int) -> str:
    if probability >= .72 and score >= 700:
        return "Recommended"
    if probability >= .48 and score >= 580:
        return "Review Required"
    return "Not Recommended"


def confidence(probability: float) -> float:
    return round(float(max(probability, 1 - probability)), 4)

@lru_cache(maxsize=1)
def load_active_artifact() -> dict:
    active_path = MODEL_DIRECTORY / "active_model.joblib"
    if not active_path.exists():
        train_models()
    meta = joblib.load(active_path)
    artifact_path = MODEL_DIRECTORY / meta["artifact"]
    if not artifact_path.exists():
        train_models()
        meta = joblib.load(active_path)
        artifact_path = MODEL_DIRECTORY / meta["artifact"]
    artifact = joblib.load(artifact_path)
    return artifact


def reset_model_cache() -> None:
    load_active_artifact.cache_clear()


def _business_factors(features: dict) -> tuple[list[str], list[str], list[str]]:
    positives, risks, improvements = [], [], []
    dti = float(features.get("debt_to_income_ratio") or 0)
    savings_rate = float(features.get("savings_rate") or 0)
    emp = float(features.get("employment_stability") or 0)
    pay = float(features.get("payment_reliability_indicator") or 0)
    util = float(features.get("credit_utilization") or 0)
    history = float(features.get("credit_history_stability") or 0)
    previous_defaults = float(features.get("previous_default_indicator") or 0)
    lti = float(features.get("loan_to_income_ratio") or 0)
    if dti <= .28: positives.append("Healthy debt-to-income position")
    else:
        risks.append("Elevated debt burden compared with annual income")
        improvements.append("Reduce outstanding debt before requesting more credit")
    if savings_rate >= .18: positives.append("Strong monthly savings capacity")
    elif savings_rate < .05:
        risks.append("Limited monthly savings buffer")
        improvements.append("Improve monthly cash surplus through lower expenses or higher savings")
    if emp >= .65: positives.append("Stable employment history")
    else:
        risks.append("Short or unstable employment history")
        improvements.append("Build a longer verified employment record")
    if pay >= .85: positives.append("Reliable payment behaviour")
    else:
        risks.append("Payment history indicates missed or delayed obligations")
        improvements.append("Improve payment consistency for the next several cycles")
    if util <= .30: positives.append("Low credit utilization")
    elif util > .60:
        risks.append("High credit utilization")
        improvements.append("Lower revolving utilization below 30% where possible")
    if history >= .6: positives.append("Established credit history")
    else:
        risks.append("Limited credit history depth")
        improvements.append("Maintain older accounts responsibly to strengthen history")
    if previous_defaults:
        risks.append("Previous default indicator present")
        improvements.append("Resolve default records and maintain consistent repayment evidence")
    if lti > .45:
        risks.append("Requested loan amount is high relative to income")
        improvements.append("Consider a lower loan amount or longer verified income record")
    if not positives:
        positives.append("Profile contains enough data for a complete analytical review")
    if not risks:
        risks.append("No major risk signals detected by the current business rules")
    if not improvements:
        improvements.append("Maintain current credit discipline and monitor debt exposure")
    return positives[:5], risks[:5], improvements[:5]


def predict_credit(payload: dict) -> dict:
    artifact = load_active_artifact()
    model = artifact["pipeline"]
    engineered = engineer_features(payload)
    X = pd.DataFrame([{col: engineered.get(col, 0) for col in FEATURE_COLUMNS}])
    probability = float(model.predict_proba(X)[0, 1])
    pred = int(probability >= .5)
    score = score_from_probability(probability)
    positives, risks, improvements = _business_factors(engineered)
    return {
        "model_name": artifact.get("model_name", "Active Model"),
        "model_version": artifact.get("version", MODEL_VERSION),
        "prediction": pred,
        "probability": round(probability, 4),
        "confidence": confidence(probability),
        "credit_score": score,
        "risk_level": risk_level(score),
        "recommendation": recommendation(probability, score),
        "engineered_features": {k: (round(v, 5) if isinstance(v, float) and math.isfinite(v) else v) for k, v in engineered.items()},
        "positive_factors": positives,
        "risk_factors": risks,
        "improvement_recommendations": improvements,
    }
