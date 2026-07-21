"""
Bootstrap dell'ambiente applicativo.

Responsabilità:
- determinare APP_ENV
- caricare in memoria il file .env corrispondente, se presente
- non sovrascrivere mai variabili già presenti nell'ambiente reale

Questo modulo NON espone configurazione tipizzata dell'applicazione.
Per quella usare esclusivamente `backend.core.settings`.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

VALID_ENVS: Final[tuple[str, ...]] = ("dev", "test", "prod")
DEFAULT_ENV: Final[str] = "dev"
BACKEND_DIR: Final[Path] = Path(__file__).resolve().parent.parent


def _normalize_app_env(value: str | None) -> str:
    if value is None:
        return DEFAULT_ENV
    return value.strip().lower().strip("\"'")


def select_app_env() -> str:
    """Restituisce l'ambiente applicativo valido, con fallback a DEFAULT_ENV."""
    raw = _normalize_app_env(os.environ.get("APP_ENV", DEFAULT_ENV))
    if raw not in VALID_ENVS:
        logger.warning(
            "APP_ENV=%r non valido; valori ammessi: %s. Uso default=%r.",
            raw,
            ", ".join(VALID_ENVS),
            DEFAULT_ENV,
        )
        return DEFAULT_ENV
    return raw


def get_env_file(app_env: str | None = None) -> Path:
    """Restituisce il path del file .env relativo all'ambiente richiesto."""
    resolved_env = _normalize_app_env(app_env) if app_env is not None else select_app_env()
    if resolved_env not in VALID_ENVS:
        resolved_env = DEFAULT_ENV
    return BACKEND_DIR / f".env.{resolved_env}"


def load_environment() -> tuple[str, Path | None]:
    app_env = select_app_env()
    env_file = get_env_file(app_env)

    if env_file.is_file():
        load_dotenv(dotenv_path=env_file, override=False)
        logger.info("Ambiente attivo: %s | env file: %s", app_env, env_file.name)
        return app_env, env_file

    logger.warning(
        "Ambiente attivo: %s | file %s non trovato in %s. Uso solo variabili d'ambiente già presenti.",
        app_env,
        env_file.name,
        BACKEND_DIR,
    )
    return app_env, None


APP_ENV, ENV_FILE = load_environment()

__all__ = [
    "APP_ENV",
    "ENV_FILE",
    "VALID_ENVS",
    "DEFAULT_ENV",
    "BACKEND_DIR",
    "select_app_env",
    "get_env_file",
    "load_environment",
]