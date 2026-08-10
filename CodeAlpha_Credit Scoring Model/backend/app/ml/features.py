from __future__ import annotations

import math
from typing import Any
import numpy as np
import pandas as pd

INTERNAL_NUMERIC = [
    "age", "annual_income", "monthly_income", "employment_duration", "existing_debt",
    "monthly_expenses", "savings", "loan_amount", "loan_term", "existing_loans",
    "credit_history_length", "previous_defaults", "late_payments", "credit_utilization",
    "outstanding_credit_balance",
]
INTERNAL_CATEGORICAL = ["gender", "employment_status", "loan_purpose", "payment_behaviour"]
TARGET = "target"

COLUMN_ALIASES = {
    "age": ["age", "person_age"],
    "gender": ["gender", "person_gender"],
    "annual_income": ["annual_income", "income", "person_income"],
    "monthly_income": ["monthly_income"],
    "employment_status": ["employment_status", "person_home_ownership", "employment", "home_ownership"],
    "employment_duration": ["employment_duration", "employment_length", "employment_length_years", "person_emp_length"],
    "existing_debt": ["existing_debt", "existing_loan_balance", "debt"],
    "monthly_expenses": ["monthly_expenses", "expenses"],
    "savings": ["savings", "savings_balance"],
    "loan_amount": ["loan_amount", "requested_loan_amount", "loan_amnt"],
    "loan_purpose": ["loan_purpose", "purpose", "loan_intent"],
    "loan_term": ["loan_term", "term"],
    "credit_history_length": ["credit_history_length", "credit_history_length_years", "cb_person_cred_hist_length"],
    "previous_defaults": ["previous_defaults", "num_derogatory_marks", "previous_default", "cb_person_default_on_file"],
    "existing_loans": ["existing_loans", "num_credit_lines"],
    "late_payments": ["late_payments", "num_late_payments_12m"],
    "payment_behaviour": ["payment_behaviour", "payment_history", "loan_grade"],
    "credit_utilization": ["credit_utilization", "revolving_utilization", "loan_percent_income"],
    "outstanding_credit_balance": ["outstanding_credit_balance", "existing_loan_balance", "loan_amnt"],
    TARGET: ["target", "creditworthy", "loan_status", "good_credit", "risk"],
}

DEFAULTS = {
    "age": 35, "annual_income": 60000, "monthly_income": 5000, "employment_duration": 4,
    "existing_debt": 12000, "monthly_expenses": 2800, "savings": 8000, "loan_amount": 15000,
    "loan_term": 36, "existing_loans": 2, "credit_history_length": 6, "previous_defaults": 0,
    "late_payments": 0, "credit_utilization": 0.35, "outstanding_credit_balance": 8000,
    "gender": "not_specified", "employment_status": "employed", "loan_purpose": "personal",
    "payment_behaviour": "consistent",
}

YES_VALUES = {"1", "true", "yes", "y", "good", "creditworthy", "low", "recommended", "no default", "n"}
NO_VALUES = {"0", "false", "no", "bad", "high", "not_creditworthy", "default", "defaulted"}


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        value = float(value)
        if math.isnan(value) or math.isinf(value):
            return float(default)
        return value
    except Exception:
        return float(default)


def safe_div(numerator: Any, denominator: Any) -> float:
    n = safe_float(numerator)
    d = safe_float(denominator)
    if abs(d) < 1e-9:
        return 0.0
    return float(n / d)


def normalize_flag_series(series: pd.Series) -> pd.Series:
    def convert(v: Any) -> float:
        if isinstance(v, str):
            s = v.strip().lower()
            if s in {"y", "yes", "true", "default", "defaulted", "1"}:
                return 1.0
            if s in {"n", "no", "false", "no default", "0"}:
                return 0.0
        return safe_float(v, 0)
    return series.apply(convert)


def normalize_bool_target(series: pd.Series, source_name: str | None = None) -> pd.Series:
    """Normalize targets so 1 always means creditworthy/good credit.

    Kaggle's common credit-risk column `loan_status` usually stores 1 as default/risky
    and 0 as non-default. That specific source is inverted here so the rest of Credora
    keeps one consistent meaning: probability = chance of good creditworthiness.
    """
    source = (source_name or "").lower().strip()

    def standard(v: Any) -> int:
        if isinstance(v, str):
            s = v.strip().lower()
            if s in YES_VALUES:
                return 1
            if s in NO_VALUES:
                return 0
        return 1 if safe_float(v) >= 0.5 else 0

    def loan_status(v: Any) -> int:
        if isinstance(v, str):
            s = v.strip().lower()
            if s in {"1", "default", "defaulted", "bad", "high", "yes", "y"}:
                return 0
            if s in {"0", "non_default", "non-default", "good", "low", "no", "n"}:
                return 1
        return 0 if safe_float(v) >= 0.5 else 1

    converter = loan_status if source == "loan_status" else standard
    return series.apply(converter).astype(int)


def _lower_columns(df: pd.DataFrame) -> dict[str, str]:
    return {c.lower().strip().replace(" ", "_"): c for c in df.columns}


def find_source_column(df: pd.DataFrame, internal: str) -> str | None:
    lower = _lower_columns(df)
    for alias in COLUMN_ALIASES.get(internal, []):
        if alias.lower() in lower:
            return lower[alias.lower()]
    return None


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for internal in COLUMN_ALIASES:
        source = find_source_column(df, internal)
        if source:
            out[internal] = df[source]
    return out


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    lowered = {k.lower().strip().replace(" ", "_"): v for k, v in record.items()}
    mapped: dict[str, Any] = {}
    for internal, aliases in COLUMN_ALIASES.items():
        if internal == TARGET:
            continue
        value = None
        for alias in aliases:
            if alias in lowered:
                value = lowered[alias]
                break
        if value is None:
            value = lowered.get(internal, DEFAULTS.get(internal))
        mapped[internal] = value
    if not mapped.get("monthly_income"):
        mapped["monthly_income"] = safe_float(mapped.get("annual_income"), 0) / 12
    return mapped


def engineer_features_from_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    for col in INTERNAL_NUMERIC:
        if col not in data:
            data[col] = np.nan
        if col == "previous_defaults":
            data[col] = normalize_flag_series(data[col])
        else:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    annual_for_derivation = data["annual_income"].where(data["annual_income"].notna() & (data["annual_income"] > 0), np.nan)
    monthly = data["monthly_income"]
    data["monthly_income"] = monthly.where(monthly.notna() & (monthly > 0), annual_for_derivation / 12).fillna(0)
    data["monthly_expenses"] = data["monthly_expenses"].where(
        data["monthly_expenses"].notna() & (data["monthly_expenses"] >= 0),
        data["monthly_income"] * 0.55,
    )
    data["existing_debt"] = data["existing_debt"].where(data["existing_debt"].notna(), data["outstanding_credit_balance"].fillna(0))
    data["savings"] = data["savings"].where(data["savings"].notna(), data["monthly_income"] * 2)
    data["loan_term"] = data["loan_term"].fillna(DEFAULTS["loan_term"])
    data["existing_loans"] = data["existing_loans"].fillna(DEFAULTS["existing_loans"])
    data["late_payments"] = data["late_payments"].fillna(DEFAULTS["late_payments"])
    data["credit_utilization"] = data["credit_utilization"].fillna(DEFAULTS["credit_utilization"])

    for col in INTERNAL_NUMERIC:
        data[col] = data[col].fillna(DEFAULTS[col]).clip(lower=0)

    for col in INTERNAL_CATEGORICAL:
        if col not in data:
            data[col] = DEFAULTS[col]
        data[col] = data[col].fillna(DEFAULTS[col]).astype(str).str.lower().str.strip().replace({"": DEFAULTS[col]})

    data["debt_to_income_ratio"] = (data["existing_debt"] / data["annual_income"].replace(0, np.nan)).replace([np.inf, -np.inf], np.nan).fillna(0)
    data["monthly_savings"] = data["monthly_income"] - data["monthly_expenses"]
    data["loan_to_income_ratio"] = (data["loan_amount"] / data["annual_income"].replace(0, np.nan)).replace([np.inf, -np.inf], np.nan).fillna(0)
    data["expense_to_income_ratio"] = (data["monthly_expenses"] / data["monthly_income"].replace(0, np.nan)).replace([np.inf, -np.inf], np.nan).fillna(0)
    data["savings_rate"] = (data["monthly_savings"] / data["monthly_income"].replace(0, np.nan)).replace([np.inf, -np.inf], np.nan).fillna(0)
    data["existing_debt_burden"] = (data["existing_debt"] + data["outstanding_credit_balance"]) / data["annual_income"].replace(0, np.nan)
    data["existing_debt_burden"] = data["existing_debt_burden"].replace([np.inf, -np.inf], np.nan).fillna(0)
    data["credit_history_stability"] = np.minimum(data["credit_history_length"] / 15, 1)
    data["employment_stability"] = np.minimum(data["employment_duration"] / 8, 1)
    data["payment_reliability_indicator"] = 1 - np.minimum((data["late_payments"] + data["previous_defaults"] * 3) / 12, 1)
    data["previous_default_indicator"] = (data["previous_defaults"] > 0).astype(int)
    return data


def engineer_features(record: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_record(record)
    df = engineer_features_from_frame(pd.DataFrame([normalized]))
    return df.iloc[0].to_dict()


def clean_training_frame(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    target_source = find_source_column(raw, TARGET)
    mapped = map_columns(raw)
    if TARGET not in mapped:
        raise ValueError("Dataset needs a target column such as target, creditworthy, loan_status, or good_credit.")
    duplicate_rows = int(mapped.duplicated().sum())
    missing_values = {col: int(mapped[col].isna().sum()) for col in mapped.columns}
    mapped = mapped.drop_duplicates().copy()
    mapped[TARGET] = normalize_bool_target(mapped[TARGET], target_source)
    engineered = engineer_features_from_frame(mapped.drop(columns=[TARGET]))
    engineered[TARGET] = mapped[TARGET].values
    summary = {
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "clean_records": int(len(engineered)),
        "target_distribution": {str(k): int(v) for k, v in engineered[TARGET].value_counts().to_dict().items()},
        "target_source": target_source or TARGET,
    }
    return engineered, summary
