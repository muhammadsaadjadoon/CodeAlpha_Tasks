from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "INFLECT"
    secret_key: str = "change-me"
    frontend_origin: str = "http://localhost:5173"
    database_url: str = "sqlite:///./inflect.db"
    session_cookie_name: str = "inflect_session"
    session_ttl_hours: int = 168
    cookie_secure: bool = False
    max_audio_mb: int = 20
    model_dir: Path = Path("../models/champion")
    model_device: str = "auto"
    allow_remote_baseline: bool = False
    remote_baseline_model: str = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
    trusted_hosts: str = "localhost,127.0.0.1"

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    @property
    def trusted_host_list(self) -> list[str]:
        return [item.strip() for item in self.trusted_hosts.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
