import os
from typing import List, Optional
from pydantic import BaseSettings, Field, AnyUrl, validator

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """
    # --- API ---
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")

    # --- Database ---
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # --- Monitoring Integrations ---
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: Optional[str] = Field(default="us-east-1", env="AWS_REGION")
    PROMETHEUS_URL: Optional[AnyUrl] = Field(default=None, env="PROMETHEUS_URL")

    # --- Resource Discovery ---
    ENABLE_AWS_DISCOVERY: bool = Field(default=True, env="ENABLE_AWS_DISCOVERY")
    ENABLE_PROMETHEUS_DISCOVERY: bool = Field(default=True, env="ENABLE_PROMETHEUS_DISCOVERY")

    # --- Alerting (Email) ---
    ALERT_EMAIL_FROM: str = Field(default="alerts@example.com", env="ALERT_EMAIL_FROM")
    ALERT_EMAIL_RECIPIENTS: List[str] = Field(default=[], env="ALERT_EMAIL_RECIPIENTS")
    SMTP_SERVER: str = Field(default="smtp.example.com", env="SMTP_SERVER")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")

    # --- Alerting (Messaging) ---
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    TEAMS_WEBHOOK_URL: Optional[str] = Field(default=None, env="TEAMS_WEBHOOK_URL")

    # --- Security ---
    SECRET_KEY: str = Field(default="supersecretkey", env="SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @validator("ALERT_EMAIL_RECIPIENTS", pre=True)
    def parse_email_recipients(cls, v):
        if isinstance(v, str):
            return [email.strip() for email in v.split(",") if email.strip()]
        return v

# Singleton settings instance
settings = Settings()

# --- Exports ---
__all__ = ["settings", "Settings"]