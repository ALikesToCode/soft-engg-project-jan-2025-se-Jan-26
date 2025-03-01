from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Authentication
    SESSION_SECRET: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

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
    LANGSMITH_TRACING:str
    LANGSMITH_ENDPOINT:str
    LANGSMITH_API_KEY:str
    LANGSMITH_PROJECT:str
    GOOGLE_API_KEY:str

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_origins_list(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")

settings = Settings()
