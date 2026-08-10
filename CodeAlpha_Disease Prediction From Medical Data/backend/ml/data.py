from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"

FEATURES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]
TARGET = "target"
COLUMNS = FEATURES + ["num"]

SOURCES = {
    "Cleveland": "processed.cleveland.data",
    "Hungarian": "processed.hungarian.data",
    "Switzerland": "processed.switzerland.data",
    "VA Long Beach": "processed.va.data",
}


def _read_source(site: str, filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename
    frame = pd.read_csv(path, names=COLUMNS, na_values="?", dtype=str)
    for column in COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["source_site"] = site
    return frame


def load_combined_dataset() -> pd.DataFrame:
    frames = [_read_source(site, filename) for site, filename in SOURCES.items()]
    data = pd.concat(frames, ignore_index=True)

    # UCI target is 0 for no disease and 1-4 for presence. This project follows
    # the classic binary formulation documented by the dataset authors.
    data[TARGET] = (data["num"] > 0).astype(int)
    data = data.drop(columns=["num"])

    # Some legacy sites encode unavailable cholesterol / resting BP as zero.
    # Treat physiologically impossible zero values as missing before imputation.
    for column in ["trestbps", "chol", "thalach"]:
        data.loc[data[column] <= 0, column] = np.nan

    return data


def build_dataset_files() -> tuple[pd.DataFrame, dict]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    data = load_combined_dataset()

    csv_path = PROCESSED_DIR / "hearttrack_uci_combined.csv"
    data.to_csv(csv_path, index=False)

    report = {
        "dataset_name": "UCI Heart Disease — combined processed cohorts",
        "rows": int(len(data)),
        "features": len(FEATURES),
        "target": TARGET,
        "positive_rate": round(float(data[TARGET].mean()), 4),
        "source_counts": data["source_site"].value_counts().to_dict(),
        "missing_values": {key: int(value) for key, value in data[FEATURES].isna().sum().to_dict().items()},
        "feature_names": FEATURES,
        "notes": [
            "The target indicates whether heart disease was recorded in the source data.",
            "Source location is kept for reporting only and is not used to calculate risk.",
            "Missing numeric values are filled with the median during model training.",
            "Zero values for cholesterol, resting blood pressure, and maximum heart rate are treated as missing before training.",
        ],
    }
    (ARTIFACT_DIR / "dataset_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return data, report


if __name__ == "__main__":
    frame, report = build_dataset_files()
    print(f"Built {len(frame)} rows at {PROCESSED_DIR / 'hearttrack_uci_combined.csv'}")
    print(json.dumps(report, indent=2))
