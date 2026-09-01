from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    whisper_model: str = "small"
    whisper_model_path: str | None = None
    whisper_compute_type: str = "int8"
    max_upload_size_bytes: int = 25 * 1024 * 1024
    log_level: str = "INFO"
    ui_password: SecretStr


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
