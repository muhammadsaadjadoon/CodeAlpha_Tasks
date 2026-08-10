from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_curve, precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from ..config import DATASET_PATH, DATA_DIR, MODEL_DIRECTORY, MODEL_VERSION
from ..database import Base, engine, db_session
from ..models import DatasetSummary, ModelPerformance
from .features import INTERNAL_CATEGORICAL, INTERNAL_NUMERIC, TARGET, clean_training_frame

SYNTHETIC_DATASET_PATH = DATA_DIR / "credit_dataset.csv"
KAGGLE_DATASET_PATH = DATA_DIR / "kaggle_credit_risk_dataset.csv"

ENGINEERED_NUMERIC = INTERNAL_NUMERIC + [
    "debt_to_income_ratio", "monthly_savings", "loan_to_income_ratio", "expense_to_income_ratio",
    "savings_rate", "existing_debt_burden", "credit_history_stability", "employment_stability",
    "payment_reliability_indicator", "previous_default_indicator",
]
FEATURE_COLUMNS = ENGINEERED_NUMERIC + INTERNAL_CATEGORICAL


def resolve_dataset_path(dataset: str | Path | None = None) -> Path:
    """Return a safe dataset path for synthetic, kaggle, env/default, or custom CSV training."""
    if dataset is None or str(dataset).strip().lower() in {"", "default", "active"}:
        return Path(DATASET_PATH)
    value = str(dataset).strip()
    key = value.lower()
    if key in {"synthetic", "included", "demo"}:
        return SYNTHETIC_DATASET_PATH
    if key in {"kaggle", "real", "credit_risk", "credit-risk"}:
        return KAGGLE_DATASET_PATH
    return Path(value)


def dataset_source(raw: pd.DataFrame, dataset_path: Path) -> str:
    cols = {c.lower().strip() for c in raw.columns}
    if {"person_age", "person_income", "loan_status"}.issubset(cols):
        return "Kaggle credit-risk dataset"
    if dataset_path.name == KAGGLE_DATASET_PATH.name:
        return "Kaggle credit-risk dataset"
    if dataset_path.name == SYNTHETIC_DATASET_PATH.name:
        return "Included synthetic credit-risk dataset"
    return f"CSV dataset: {dataset_path.name}"


def generate_credit_dataset(path: Path = SYNTHETIC_DATASET_PATH, n: int = 2600) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    age = rng.integers(21, 69, n)
    annual_income = np.clip(rng.normal(62000, 26000, n), 12000, 260000)
    monthly_income = annual_income / 12
    employment_duration = np.clip(rng.normal(5.5, 4.0, n), 0, 35)
    existing_debt = np.clip(rng.normal(13000, 12000, n), 0, 150000)
    monthly_expenses = np.clip(monthly_income * rng.uniform(0.35, 0.92, n), 500, 18000)
    savings = np.clip(rng.exponential(8000, n), 0, 250000)
    loan_amount = np.clip(rng.normal(17000, 11000, n), 500, 120000)
    loan_term = rng.choice([12, 24, 36, 48, 60, 72], n, p=[.08,.14,.36,.18,.18,.06])
    existing_loans = np.clip(rng.poisson(2.2, n), 0, 12)
    credit_history_length = np.clip(age - rng.integers(18, 25, n) + rng.normal(0, 2, n), 0, 45)
    previous_defaults = np.clip(rng.poisson(.22, n), 0, 5)
    late_payments = np.clip(rng.poisson(.7, n), 0, 10)
    credit_utilization = np.clip(rng.beta(2.2, 3.2, n), 0, 1)
    outstanding_credit_balance = np.clip(existing_debt * rng.uniform(.2, .9, n), 0, 120000)
    gender = rng.choice(["female", "male", "not_specified"], n, p=[.46,.48,.06])
    employment_status = rng.choice(["employed", "self_employed", "contract", "student", "unemployed", "retired"], n, p=[.56,.18,.1,.07,.06,.03])
    loan_purpose = rng.choice(["debt_consolidation", "home", "auto", "business", "education", "medical", "personal"], n, p=[.28,.14,.18,.13,.1,.07,.1])
    payment_behaviour = rng.choice(["consistent", "minor_delays", "irregular", "poor"], n, p=[.58,.23,.13,.06])
    dti = existing_debt / np.maximum(annual_income, 1)
    lti = loan_amount / np.maximum(annual_income, 1)
    savings_rate = (monthly_income - monthly_expenses) / np.maximum(monthly_income, 1)
    z = (1.15 - 2.8*dti - 2.0*lti - 2.4*credit_utilization - .55*late_payments - 1.1*previous_defaults
         + 0.000018*annual_income + .055*employment_duration + .04*credit_history_length + 0.00001*savings
         + .55*savings_rate + .25*(payment_behaviour == "consistent") - .5*(payment_behaviour == "poor")
         - .25*(employment_status == "unemployed") + rng.normal(0, .8, n))
    prob = 1/(1+np.exp(-z))
    target = (rng.random(n) < prob).astype(int)
    df = pd.DataFrame({
        "age": age, "gender": gender, "annual_income": annual_income.round(2), "monthly_income": monthly_income.round(2),
        "employment_status": employment_status, "employment_duration": employment_duration.round(1),
        "existing_debt": existing_debt.round(2), "monthly_expenses": monthly_expenses.round(2), "savings": savings.round(2),
        "loan_amount": loan_amount.round(2), "loan_purpose": loan_purpose, "loan_term": loan_term, "existing_loans": existing_loans,
        "credit_history_length": credit_history_length.round(1), "previous_defaults": previous_defaults, "late_payments": late_payments,
        "payment_behaviour": payment_behaviour, "credit_utilization": credit_utilization.round(3),
        "outstanding_credit_balance": outstanding_credit_balance.round(2), "target": target,
    })
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def _pipeline(model):
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    categorical = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    prep = ColumnTransformer([
        ("num", numeric, ENGINEERED_NUMERIC),
        ("cat", categorical, INTERNAL_CATEGORICAL),
    ])
    return Pipeline([("preprocess", prep), ("model", model)])


def _importance(pipe: Pipeline) -> list[dict[str, float | str]]:
    prep = pipe.named_steps["preprocess"]
    names = list(prep.get_feature_names_out())
    model = pipe.named_steps["model"]
    if hasattr(model, "feature_importances_"):
        vals = np.abs(model.feature_importances_)
    elif hasattr(model, "coef_"):
        vals = np.abs(model.coef_[0])
    else:
        vals = np.zeros(len(names))
    if vals.sum() > 0:
        vals = vals / vals.sum()
    pairs = sorted(zip(names, vals), key=lambda x: -x[1])[:12]
    return [{"feature": str(k).replace("num__", "").replace("cat__", ""), "importance": round(float(v), 5)} for k, v in pairs]


def train_models(dataset_path: Path | str | None = DATASET_PATH) -> dict:
    Base.metadata.create_all(bind=engine)
    start = time.time()
    dataset_path = resolve_dataset_path(dataset_path)
    if not dataset_path.exists():
        if dataset_path == SYNTHETIC_DATASET_PATH or dataset_path == DATASET_PATH:
            raw = generate_credit_dataset(dataset_path)
        else:
            raise FileNotFoundError(f"Dataset file was not found: {dataset_path}")
    else:
        raw = pd.read_csv(dataset_path)
    df, clean_summary = clean_training_frame(raw)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.22, random_state=42, stratify=y)
    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=1400, class_weight="balanced", random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=7, min_samples_leaf=25, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=180, max_depth=11, min_samples_leaf=6, class_weight="balanced", random_state=42, n_jobs=-1),
    }
    perf_rows = []
    artifacts = {}
    for name, model in candidates.items():
        pipe = _pipeline(model)
        pipe.fit(X_train, y_train)
        prob = pipe.predict_proba(X_test)[:, 1]
        pred = (prob >= .5).astype(int)
        cm = confusion_matrix(y_test, pred, labels=[0,1])
        fpr, tpr, _ = roc_curve(y_test, prob)
        precision_curve, recall_curve, _ = precision_recall_curve(y_test, prob)
        down = lambda arr: np.asarray(arr)[np.linspace(0, len(arr)-1, min(60, len(arr))).astype(int)].round(4).tolist()
        row = {
            "model_name": name,
            "model_version": MODEL_VERSION,
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
            "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, pred, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, prob)), 4),
            "confusion_matrix": {"true_negative": int(cm[0,0]), "false_positive": int(cm[0,1]), "false_negative": int(cm[1,0]), "true_positive": int(cm[1,1])},
            "roc_curve_data": [{"fpr": a, "tpr": b} for a, b in zip(down(fpr), down(tpr))],
            "precision_recall_curve_data": [{"precision": a, "recall": b} for a, b in zip(down(precision_curve), down(recall_curve))],
            "feature_importance": _importance(pipe),
            "dataset_records": int(len(df)),
            "feature_count": int(len(FEATURE_COLUMNS)),
            "training_duration": round(time.time()-start, 3),
        }
        perf_rows.append(row)
        file_name = name.lower().replace(" ", "_") + ".joblib"
        joblib.dump({"pipeline": pipe, "feature_columns": FEATURE_COLUMNS, "version": MODEL_VERSION, "model_name": name, "dataset_name": dataset_path.name}, MODEL_DIRECTORY / file_name)
        artifacts[name] = file_name
    best = sorted(perf_rows, key=lambda r: (r["roc_auc"], r["f1_score"], r["recall"], r["precision"], r["accuracy"]), reverse=True)[0]
    joblib.dump({"active_model": best["model_name"], "artifact": artifacts[best["model_name"]], "version": MODEL_VERSION, "dataset_name": dataset_path.name}, MODEL_DIRECTORY / "active_model.joblib")
    numeric_summary = df[ENGINEERED_NUMERIC].describe().round(3).to_dict()
    categorical_summary = {col: {str(k): int(v) for k, v in df[col].value_counts().head(10).to_dict().items()} for col in INTERNAL_CATEGORICAL}
    corr = df[ENGINEERED_NUMERIC + [TARGET]].corr(numeric_only=True).round(3).fillna(0)
    corr_data = [{"x": x, "y": y_col, "value": float(corr.loc[y_col, x])} for y_col in corr.index for x in corr.columns]
    with db_session() as db:
        db.query(ModelPerformance).delete()
        for row in perf_rows:
            db.add(ModelPerformance(
                model_name=row["model_name"], model_version=row["model_version"], accuracy=row["accuracy"], precision=row["precision"], recall=row["recall"], f1_score=row["f1_score"], roc_auc=row["roc_auc"],
                confusion_matrix=json.dumps(row["confusion_matrix"]), roc_curve_data=json.dumps(row["roc_curve_data"]), precision_recall_curve_data=json.dumps(row["precision_recall_curve_data"]),
                feature_importance=json.dumps(row["feature_importance"]), is_active=row["model_name"] == best["model_name"], dataset_records=row["dataset_records"], feature_count=row["feature_count"], training_duration=row["training_duration"],
            ))
        db.query(DatasetSummary).delete()
        db.add(DatasetSummary(
            dataset_name=dataset_path.name, source=dataset_source(raw, dataset_path),
            total_records=int(len(raw)), feature_count=int(len(FEATURE_COLUMNS)), missing_values=json.dumps(clean_summary["missing_values"]),
            duplicate_rows=clean_summary["duplicate_rows"], clean_records=clean_summary["clean_records"], target_distribution=json.dumps(clean_summary["target_distribution"]),
            numerical_summary=json.dumps(numeric_summary), categorical_summary=json.dumps(categorical_summary), correlation_data=json.dumps(corr_data),
        ))
    return {"active_model": best["model_name"], "dataset_name": dataset_path.name, "dataset_source": dataset_source(raw, dataset_path), "models": perf_rows, "dataset_records": int(len(df)), "artifact_dir": str(MODEL_DIRECTORY)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Credora credit-risk models.")
    parser.add_argument("--dataset", default="active", help="Use active/default, synthetic, kaggle, or a custom CSV path.")
    args = parser.parse_args()
    print(json.dumps(train_models(resolve_dataset_path(args.dataset)), indent=2))


if __name__ == "__main__":
    main()
