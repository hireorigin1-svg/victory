from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Victory"
    environment: str = "development"
    database_url: str = "sqlite:///./cinemind.db"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: list[str] = ["http://localhost:3000"]
    allow_public_registration: bool = True
    seed_director_email: str = "director@example.com"
    seed_director_password: str = "correct-horse-battery"
    enable_real_llm_calls: bool = False
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-5"
    upload_dir: str = "uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
