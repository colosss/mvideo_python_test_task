from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    WEB_API_BASE_URL: str = "http://localhost:8000"
    FETCH_INTERVAL_SECOND: float=Field(default=10.0, gt=0)
    EXPORT_BATCH_LIMIT: int=Field(default=500, ge=1, le=1000)
    EXPORT_FILE_PATH: str="/data/http_logs.jsonl"
    EXPORT_STATE_PATH: str="/data/http_logs.state.json"
    EXPORT_LOCK_PATH: str="/data/http_logs.lock"
    BACKGROUND_HTTP_TIMEOUT_SECONDS: float=Field(default=10.0, gt=0)

@lru_cache
def get_settings()->Settings:
    return Settings()

settings=get_settings()