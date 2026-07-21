"""
Configurazione tipizzata e centralizzata dell'applicazione.

Unica fonte di verità per le impostazioni runtime.
Il bootstrap dell'ambiente viene eseguito da `backend.core.env`.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

import backend.core.env as _env

DEV_FALLBACK_SECRET = "dev-insecure-default-key-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        hide_input_in_errors=True,
    )

    app_env: Literal["dev", "test", "prod"] = "dev"

    @field_validator("app_env", mode="before")
    @classmethod
    def normalize_app_env(cls, value: str | None) -> str:
        if value is None:
            return "dev"
        if isinstance(value, str):
            return value.strip().lower().strip("\"'")
        return value

    database_url: str = Field(..., min_length=1)
    db_pool_size: int = Field(10, ge=1)
    db_max_overflow: int = Field(20, ge=0)
    db_pool_recycle: int = Field(1800, ge=0)
    db_pool_timeout: int = Field(30, ge=1)

    secret_key: SecretStr = Field(
        default=SecretStr(DEV_FALLBACK_SECRET),
        min_length=16,
    )
    algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = Field(60, ge=1)
    refresh_token_expire_days: int = Field(7, ge=1)

    default_max_subtask_depth: int = Field(3, ge=0)
    default_habit_log_lookback_days: int = Field(30, ge=1)
    default_completed_task_lookback_days: int = Field(90, ge=1)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("DATABASE_URL non può essere vuota.")
        return normalized

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: SecretStr, info) -> SecretStr:
        app_env = info.data.get("app_env", "dev")
        secret = value.get_secret_value()

        if app_env != "dev" and secret == DEV_FALLBACK_SECRET:
            raise ValueError(
                "SECRET_KEY deve essere valorizzata esplicitamente negli ambienti non-dev."
            )

        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings", "DEV_FALLBACK_SECRET"]