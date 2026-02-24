"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration – values come from env vars or `.env` file."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    OPENAI_API_KEY: str | None = None
    DEFAULT_WORD_COUNT: int = 1500
    DEFAULT_LANGUAGE: str = "en"
    MAX_REVISIONS: int = 2
    APP_ENV: str = "dev"
    SERP_PROVIDER: str = "mock"

    @field_validator("DEFAULT_WORD_COUNT")
    @classmethod
    def _word_count_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("DEFAULT_WORD_COUNT must be > 0")
        return v

    @field_validator("MAX_REVISIONS")
    @classmethod
    def _max_revisions_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("MAX_REVISIONS must be >= 0")
        return v

    @model_validator(mode="after")
    def _require_api_key_outside_dev(self) -> Settings:
        if self.APP_ENV != "dev" and not self.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when APP_ENV is not 'dev'"
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()
