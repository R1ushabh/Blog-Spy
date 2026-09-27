import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Competitor Blog Spy & Real-Time Content Monitoring System"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "supersecretkey_change_in_production_987654321"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database URL: default to SQLite WAL mode for local dev, can be switched to PostgreSQL
    DATABASE_URL: str = "sqlite:///./competitor_spy.db"
    
    # Worker & Concurrency settings
    MAX_WORKERS: int = 10
    MAX_CONCURRENT_REQUESTS: int = 20
    REQUEST_TIMEOUT: int = 15
    DEFAULT_MONITOR_INTERVAL: int = 60  # seconds
    RETRY_LIMIT: int = 3
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"]
    
    # Optional SMTP
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "alerts@competitorspy.local"
    
    # Playwright fallback flag
    PLAYWRIGHT_ENABLED: bool = False
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
