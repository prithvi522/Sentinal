from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SentinelAI OS"
    environment: str = "development"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    # Default to a local SQLite DB for easy local development; override with DATABASE_URL for production/docker
    database_url: str = "sqlite:///./dev.db"
    jwt_secret: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
    frontend_origin: str = "http://localhost:5173"

    chatgpt_api_key: str | None = None
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    virustotal_api_key: str | None = None
    threatfox_api_key: str | None = None
    abuseipdb_api_key: str | None = None
    shodan_api_key: str | None = None
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    simulation_interval_seconds: int = 8
    # Maximum upload size for code scans (bytes). Set to null/None to disable limit.
    max_upload_size_bytes: int | None = 50 * 1024 * 1024  # 50 MB

    # Resolve the backend/.env file relative to this config file so env vars are loaded
    # reliably even when the process CWD is elsewhere.
    _env_path = Path(__file__).resolve().parents[2] / ".env"
    model_config = SettingsConfigDict(
        env_file=str(_env_path), env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
