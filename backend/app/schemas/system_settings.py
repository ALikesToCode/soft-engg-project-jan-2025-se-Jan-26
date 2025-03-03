from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class AuthSettings(BaseModel):
    jwt_expiry: int = Field(24, description="JWT token expiry in hours")
    oauth_provider: str = Field("google", description="OAuth provider")
    mfa_enabled: bool = Field(False, description="Enable Multi-Factor Authentication")


class NotificationSettings(BaseModel):
    email_frequency: str = Field("immediate", description="Default email frequency")
    smtp_server: str = Field("smtp.example.com", description="SMTP server address")


class ApiSettings(BaseModel):
    rate_limit: int = Field(100, description="API rate limit (requests/minute)")
    data_retention_days: int = Field(30, description="Data retention period in days")


class Integration(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., description="Integration name")
    type: str = Field(..., description="Integration type")
    endpoint: str = Field(..., description="API endpoint")
    api_key: str = Field(..., description="API key")
    status: str = Field("inactive", description="Integration status")


class IntegrationCreate(BaseModel):
    name: str = Field(..., description="Integration name")
    type: str = Field(..., description="Integration type")
    endpoint: str = Field(..., description="API endpoint")
    api_key: str = Field(..., description="API key")
    status: str = Field("inactive", description="Integration status")


class IntegrationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    status: Optional[str] = None


class SystemSettings(BaseModel):
    auth: AuthSettings = Field(default_factory=AuthSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    integrations: List[Integration] = Field(default_factory=list) 