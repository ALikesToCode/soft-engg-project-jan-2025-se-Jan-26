from pydantic_settings import BaseSettings
from typing import List
from datetime import timedelta
import os
from pathlib import Path

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://localhost:5432"

    # Authentication
    SESSION_SECRET: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # JWT Settings
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Redis Settings
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:5173"

    # API
    API_PREFIX: str = "/api/v1"

    # Application
    APP_NAME: str = "SE Team 26 API"
    APP_DESCRIPTION: str = "Backend API for SE Team 26 Project"
    APP_VERSION: str = "1.0.0"

    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENV: str = "development"

    # LLM
    LANGSMITH_TRACING: str
    LANGSMITH_ENDPOINT: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str
    GOOGLE_API_KEY: str

    # S3 Storage Settings
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_ENDPOINT_URL: str = ""
    S3_BUCKET_NAME: str = ""
    S3_REGION: str = ""

    # Monitoring Settings
    MONITORING_METRICS_HISTORY_SIZE: int = 1000
    MONITORING_HEALTH_CHECK_INTERVAL: int = 60  # seconds
    MONITORING_METRICS_COLLECTION_INTERVAL: int = 30  # seconds
    
    # Service URLs
    API_HEALTH_URL: str = "http://localhost:8000/health"
    
    # Alert Thresholds
    ALERT_THRESHOLD_CPU: float = 80.0
    ALERT_THRESHOLD_MEMORY: float = 85.0
    ALERT_THRESHOLD_DISK: float = 90.0
    ALERT_THRESHOLD_RESPONSE_TIME: float = 2000.0
    ALERT_THRESHOLD_ERROR_RATE: float = 5.0
    ALERT_THRESHOLD_OPEN_FILES: int = 1000
    ALERT_THRESHOLD_PROCESS_COUNT: int = 500

    # Logflare Settings
    USE_LOGFLARE: bool = False
    LOGFLARE_SOURCE_ID: str
    LOGFLARE_API_KEY: str           
    LOGFLARE_BATCH_SIZE: int
    LOGFLARE_LOG_LEVEL: str 

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_origins_list(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")

settings = Settings()
