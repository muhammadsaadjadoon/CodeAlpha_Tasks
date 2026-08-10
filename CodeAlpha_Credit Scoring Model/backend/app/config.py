from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'credora.db'}")
SECRET_KEY = os.getenv("SECRET_KEY", "credora-local-development-secret")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
MODEL_DIRECTORY = Path(os.getenv("MODEL_DIRECTORY", str(BASE_DIR / "artifacts")))
MODEL_DIRECTORY.mkdir(exist_ok=True)
DATASET_PATH = Path(os.getenv("DATASET_PATH", str(DATA_DIR / "credit_dataset.csv")))
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]

SCORE_MIN = 300
SCORE_MAX = 850
RISK_THRESHOLDS = {
    "low": (750, 850),
    "moderate": (670, 749),
    "elevated": (580, 669),
    "high": (300, 579),
}
MODEL_VERSION = "2026.07.18"
