from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), env_file_encoding="utf-8", extra="ignore")
    app_name: str = "WriteLens"
    app_env: str = "development"
    app_secret: str = "development-only-change-me"
    database_url: str = "sqlite:///./backend/writelens.db"
    session_cookie_name: str = "writelens_session"
    session_ttl_hours: int = 168
    cookie_secure: bool = False
    max_image_bytes: int = 10 * 1024 * 1024
    model_registry_path: str = "./models/registry.json"
    frontend_origin: str = "http://localhost:5173"

settings = Settings()
