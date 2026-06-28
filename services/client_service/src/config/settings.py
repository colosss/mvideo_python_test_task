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
    CLIENT_WORKERS: int= Field(default=4, ge=1)
    CLIENT_MAX_DELAY_MS: int=Field(default=1000, ge=0)
    CLIENT_REQUEST_PER_WORKER: int=Field(default=0, ge=0)
    CLIENT_LOG_FILE: str="/var/log/client_service/sent_logs.json"
    CLIENT_HTTP_TIMEOUT_SECONDS: float=Field(default=5.0, gt=0)
    
@lru_cache
def get_settings()->Settings:
    return Settings()

settings=get_settings()