"""
CyberShield XDR — Application Settings
Uses Pydantic BaseSettings for type-safe environment variable loading.
All secrets are sourced from environment variables, never hardcoded.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_env: str = "development"
    app_name: str = "CyberShield XDR"
    app_version: str = "1.0.0"
    secret_key: str
    debug: bool = False

    # --- Database ---
    database_url: str
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "cybershield"
    postgres_user: str
    postgres_password: str

    # --- Redis ---
    redis_url: str
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: Optional[str] = None

    # --- JWT ---
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # --- CORS ---
    allowed_origins: List[str] = ["http://localhost:5173"]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # --- Rate Limiting ---
    rate_limit_per_minute: int = 60
    auth_rate_limit_per_minute: int = 10

    # --- File Upload ---
    max_upload_size_mb: int = 50
    upload_dir: str = "/app/uploads"
    allowed_extensions: str = "exe,dll,pdf,doc,docx,zip,tar,gz,js,py,sh,bat,ps1"

    @property
    def allowed_extensions_set(self) -> set:
        return {ext.strip().lower() for ext in self.allowed_extensions.split(",")}

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    # --- Threat Intelligence ---
    abuseipdb_api_key: Optional[str] = None
    virustotal_api_key: Optional[str] = None
    alienvault_otx_api_key: Optional[str] = None

    # --- OpenAI ---
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"

    # --- Email ---
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: str = "noreply@cybershield.com"

    # --- Slack / Discord ---
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None

    # --- OpenSearch ---
    opensearch_host: str = "opensearch"
    opensearch_port: int = 9200
    opensearch_user: str = "admin"
    opensearch_password: Optional[str] = None

    # --- Celery ---
    celery_broker_url: str
    celery_result_backend: str

    # --- Security ---
    bcrypt_rounds: int = 12
    bcrypt_pepper: str = "default_insecure_pepper_override_in_prod"
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Returns cached Settings instance.
    Use as FastAPI dependency: settings = Depends(get_settings)
    """
    return Settings()
