"""Configuration management for the data pipeline monitor"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    app_name: str = "Data Pipeline Monitor"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    api_port: int = int(os.getenv("API_PORT", 8000))

    # Database Configuration
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/pipeline_monitor"
    )

    # LLM Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4")

    # Monitoring Configuration
    anomaly_threshold: float = float(os.getenv("ANOMALY_THRESHOLD", 0.8))
    check_interval_seconds: int = int(os.getenv("CHECK_INTERVAL_SECONDS", 300))

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
