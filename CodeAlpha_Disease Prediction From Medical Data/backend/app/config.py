from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "HeartTrack API"
    app_env: str = "development"
    frontend_origin: str = "http://localhost:5173"
    secret_key: str = "change-me-before-production-use-at-least-32-bytes"
    demo_email: str = "demo@hearttrack.ai"
    demo_password: str = "HeartTrack@2026"
    cookie_secure: bool = False
    session_minutes: int = 60
    model_bundle_path: Path = BASE_DIR / "ml" / "artifacts" / "model_bundle.joblib"
    metrics_path: Path = BASE_DIR / "ml" / "artifacts" / "metrics.json"
    dataset_report_path: Path = BASE_DIR / "ml" / "artifacts" / "dataset_report.json"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="HEARTTRACK_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
