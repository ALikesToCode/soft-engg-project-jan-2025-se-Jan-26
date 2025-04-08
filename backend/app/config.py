from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
from datetime import timedelta
import os
from pathlib import Path
import json
import logging

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://localhost:5432"
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"

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
    REDIS_USERNAME: str = "default"
    REDIS_PASSWORD: str = ""

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

    # Environment and base settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "True").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS: List[str] = json.loads(os.getenv("CORS_ORIGINS", '["*"]'))
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Authentication settings
    PASSWORD_SALT: str = os.getenv("PASSWORD_SALT", "your-password-salt-please-change-in-production")
    
    # LLM services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE: Optional[str] = os.getenv("OPENAI_API_BASE")
    OPENAI_API_TYPE: Optional[str] = os.getenv("OPENAI_API_TYPE")
    OPENAI_API_VERSION: Optional[str] = os.getenv("OPENAI_API_VERSION")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # File uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "52428800"))  # 50MB default
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt", ".jpg", ".jpeg", ".png", ".mp4"]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Admin user
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_DEFAULT_PASSWORD: str = os.getenv("ADMIN_DEFAULT_PASSWORD", "Admin123!")
    
    # Vector database settings
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "qdrant")
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "faq_embeddings")
    
    # Redis cache settings
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "True").lower() == "true"
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
    CACHE_EXPIRY_SECONDS: int = int(os.getenv("CACHE_EXPIRY_SECONDS", "300"))  # 5 minutes
    
    # Performance settings
    DEFAULT_PAGINATION_LIMIT: int = int(os.getenv("DEFAULT_PAGINATION_LIMIT", "100"))
    MAX_PAGINATION_LIMIT: int = int(os.getenv("MAX_PAGINATION_LIMIT", "1000"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
    
    # Email settings
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[str] = os.getenv("EMAILS_FROM_EMAIL")

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")

settings = Settings()

# Configure logging
logging_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=logging_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
