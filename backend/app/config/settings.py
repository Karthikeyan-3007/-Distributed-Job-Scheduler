"""
Centralized, environment-driven configuration.

Nothing in the application should hardcode a secret, URL, timeout, or limit.
Everything flows through this single Settings object, which is injected
wherever needed. This keeps configuration testable and swappable per
environment (dev / test / staging / prod) without touching code.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://scheduler:scheduler@localhost:5432/scheduler"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Auth
    JWT_SECRET_KEY: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Worker / Scheduler tuning
    WORKER_POLL_INTERVAL_SECONDS: float = 2.0
    WORKER_HEARTBEAT_INTERVAL_SECONDS: float = 5.0
    WORKER_HEARTBEAT_TIMEOUT_SECONDS: float = 20.0
    SCHEDULER_TICK_SECONDS: float = 1.0

    # App
    APP_NAME: str = "Distributed Job Scheduler"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
