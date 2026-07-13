"""
Common helpers per i services Shopping.
"""

from datetime import date, datetime, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _today() -> date:
    return date.today()


def _normalize_name(value: str) -> str:
    return value.strip().lower()