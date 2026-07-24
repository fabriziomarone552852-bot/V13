"""
Policy condivisa per la validazione delle password.

Centralizza i vincoli usati dagli schemi Pydantic e dai servizi di dominio,
così l'applicazione mantiene una definizione unica della policy password.
"""
from __future__ import annotations

from backend.core.settings import get_settings

settings = get_settings()

PASSWORD_MIN_LENGTH: int = settings.password_min_length
PASSWORD_MAX_LENGTH: int = settings.password_max_length

__all__ = [
    "PASSWORD_MIN_LENGTH",
    "PASSWORD_MAX_LENGTH",
]