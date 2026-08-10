from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

from .data import ARTIFACT_DIR, FEATURES, TARGET, build_dataset_files


RANDOM_STATE = 42


def _preprocessor(scale: bool) -> ColumnTransformer:
    steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale:
        steps.append(("scaler", StandardScaler()))
    return ColumnTransformer([("features", Pipeline(steps), FEATURES)], remainder="drop")


def model_candidates() -> dict[str, tuple[Pipeline, dict]]:
    return {
        "Logistic Regression": (
            Pipeline(
                [
                    ("prep", _preprocessor(scale=True)),
                    (
                        "model",
                        LogisticRegression(
                            max_iter=5000,
                            class_weight="balanced",
                            random_state=RANDOM_STATE,
                        ),
                    ),
                ]
            ),
            {
                "model__C": np.logspace(-2, 1.2, 14),
                "model__solver": ["lbfgs", "liblinear"],
            },
        ),
        "SVM": (
            Pipeline(
                [
                    ("prep", _preprocessor(scale=True)),
                    (
                        "model",
                        SVC(
                            probability=True,
                            class_weight="balanced",
                            random_state=RANDOM_STATE,
                        ),
                    ),
                ]
            ),
            {
                "model__C": np.logspace(-1, 1.1, 12),
                "model__gamma": ["scale", "auto", 0.01, 0.03, 0.1],
                "model__kernel": ["rbf"],
            },
        ),
        "Random Forest": (
            Pipeline(
                [
                    ("prep", _preprocessor(scale=False)),
                    (
                        "model",
                        RandomForestClassifier(
                            n_estimators=500,
                            class_weight="balanced_subsample",
                            random_state=RANDOM_STATE,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
            {
                "model__max_depth": [None, 4, 6, 8, 12],
                "model__min_samples_leaf": [1, 2, 3, 5, 8],
                "model__max_features": ["sqrt", "log2", 0.7],
                "model__n_estimators": [300, 500, 700],
            },
        ),
        "XGBoost": (
            Pipeline(
                [
                    ("prep", _preprocessor(scale=False)),
                    (
                        "model",
                        XGBClassifier(
                            objective="binary:logistic",
                            eval_metric="logloss",
                            tree_method="hist",
                            random_state=RANDOM_STATE,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
            {
                "model__n_estimators": [180, 260, 360, 480],
                "model__max_depth": [2, 3, 4, 5],
                "model__learning_rate": [0.02, 0.04, 0.06, 0.1],
                "model__subsample": [0.75, 0.85, 1.0],
                "model__colsample_bytree": [0.7, 0.85, 1.0],
                "model__min_child_weight": [1, 3, 5],
                "model__reg_lambda": [1.0, 2.0, 5.0],
            },
        ),
    }


def _evaluate(model, X_test: pd.DataFrame, y_test: pd.Series, threshold: float = 0.5) -> dict:
    probability = model.predict_proba(X_test)[:, 1]
    prediction = (probability >= threshold).astype(int)
    return {
        "roc_auc": round(float(roc_auc_score(y_test, probability)), 4),
        "accuracy": round(float(accuracy_score(y_test, prediction)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(y_test, prediction)), 4),
        "precision": round(float(precision_score(y_test, prediction, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, prediction, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, prediction, zero_division=0)), 4),
        "brier": round(float(brier_score_loss(y_test, probability)), 4),
        "confusion_matrix": confusion_matrix(y_test, prediction).tolist(),
        "classification_report": classification_report(y_test, prediction, output_dict=True, zero_division=0),
    }


def _reference_values(X: pd.DataFrame) -> dict[str, float]:
    categorical = {"sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"}
    refs: dict[str, float] = {}
    for feature in FEATURES:
        series = X[feature].dropna()
        if feature in categorical:
            refs[feature] = float(series.mode().iloc[0])
        else:
            refs[feature] = float(series.median())
    return refs


def train(mode: str = "full") -> dict:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    data, dataset_report = build_dataset_files()
    X = data[FEATURES].copy()
    y = data[TARGET].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    fitted: dict[str, Pipeline] = {}
    reports: dict[str, dict] = {}

    for name, (estimator, search_space) in model_candidates().items():
        print(f"\n==> Training {name}")
        if mode == "full":
            search = RandomizedSearchCV(
                estimator,
                param_distributions=search_space,
                n_iter=10 if name != "SVM" else 8,
                scoring="roc_auc",
                n_jobs=-1,
                cv=cv,
                random_state=RANDOM_STATE,
                refit=True,
                verbose=0,
            )
            search.fit(X_train, y_train)
            best_model = search.best_estimator_
            best_params = search.best_params_
            cv_auc = float(search.best_score_)
        else:
            best_model = estimator.fit(X_train, y_train)
            best_params = {"mode": "fast-defaults"}
            cv_auc = float(cross_val_score(estimator, X_train, y_train, cv=cv, scoring="roc_auc", n_jobs=-1).mean())

        fitted[name] = best_model
        reports[name] = {
            "cv_roc_auc": round(cv_auc, 4),
            "best_params": best_params,
            "holdout": _evaluate(best_model, X_test, y_test),
        }
        print(f"    CV ROC-AUC: {cv_auc:.4f} | Holdout ROC-AUC: {reports[name]['holdout']['roc_auc']:.4f}")

    selected_name = max(reports, key=lambda key: reports[key]["cv_roc_auc"])
    selected_base = clone(fitted[selected_name])
    print(f"\n==> Selected by cross-validated ROC-AUC: {selected_name}")

    # Probability calibration improves the meaning of probability-like output.
    calibrated = CalibratedClassifierCV(selected_base, method="sigmoid", cv=5)
    calibrated.fit(X_train, y_train)
    calibrated_metrics = _evaluate(calibrated, X_test, y_test)

    threshold = 0.5
    bundle = {
        "model": calibrated,
        "model_name": f"{selected_name} + sigmoid calibration",
        "selected_base_model": selected_name,
        "features": FEATURES,
        "feature_reference": _reference_values(X_train),
        "threshold": threshold,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": int(len(data)),
        "random_state": RANDOM_STATE,
    }
    joblib.dump(bundle, ARTIFACT_DIR / "model_bundle.joblib", compress=3)

    report = {
        "project": "HeartTrack",
        "training_mode": mode,
        "trained_at_utc": bundle["trained_at_utc"],
        "selection_rule": "HeartTrack selects the model with the best average ROC-AUC across five cross-validation runs. The test set is kept separate for final evaluation.",
        "selected_model": bundle["model_name"],
        "selected_base_model": selected_name,
        "threshold": threshold,
        "calibrated_holdout": calibrated_metrics,
        "models": reports,
        "split": {
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
            "test_fraction": 0.20,
            "stratified": True,
            "random_state": RANDOM_STATE,
        },
        "dataset": dataset_report,
        "runtime": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "xgboost": xgboost.__version__,
        },
        "cautions": [
            "HeartTrack is not a diagnostic tool, and its predictions have not been clinically validated.",
            "The UCI heart-disease records are historical and contain missing values.",
            "The 0.5 decision threshold and on-screen risk levels are model settings, not clinical categories.",
        ],
    }
    (ARTIFACT_DIR / "metrics.json").write_text(json.dumps(report, indent=2, default=float), encoding="utf-8")
    print(f"\nSaved model: {ARTIFACT_DIR / 'model_bundle.joblib'}")
    print(f"Saved metrics: {ARTIFACT_DIR / 'metrics.json'}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Train HeartTrack classification models.")
    parser.add_argument("--mode", choices=["fast", "full"], default="full")
    args = parser.parse_args()
    train(args.mode)


if __name__ == "__main__":
    main()
