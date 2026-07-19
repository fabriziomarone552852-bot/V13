"""
Planning domain schemas.
Pydantic models for daily planning entries and calendar pixels.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import Field, field_validator

from backend.core.schemas import ORMBaseModel, StrictBaseModel

VALID_DAILY_ENTRY_TYPES = {
    "PX",
    "OD",
    "PD",
    "N1",
    "N2",
    "N3",
    "N4",
    "OW",
    "PW",
    "OM",
    "PM",
    "EP",
    "EN",
}


class DailyEntryBase(StrictBaseModel):
    """Base schema for planning entries."""

    data_riferimento: date
    tipo: str = Field(..., min_length=2, max_length=2)
    testo: Optional[str] = None
    completato: bool = False
    category_id: Optional[int] = Field(
        default=None,
        description="ID della categoria collegata (user_categories.id).",
    )

    @field_validator("tipo")
    @classmethod
    def validate_tipo(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_DAILY_ENTRY_TYPES:
            allowed = ", ".join(sorted(VALID_DAILY_ENTRY_TYPES))
            raise ValueError(f"Tipo non valido. Deve essere uno tra: {allowed}")
        return normalized

    @field_validator("testo")
    @classmethod
    def normalize_testo(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class DailyEntryCreate(DailyEntryBase):
    """Schema for entry creation."""


class DailyEntryUpdate(StrictBaseModel):
    """Schema for partial update."""

    data_riferimento: Optional[date] = None
    tipo: Optional[str] = Field(default=None, min_length=2, max_length=2)
    testo: Optional[str] = None
    completato: Optional[bool] = None
    category_id: Optional[int] = None

    @field_validator("tipo")
    @classmethod
    def validate_tipo(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().upper()
        if normalized not in VALID_DAILY_ENTRY_TYPES:
            allowed = ", ".join(sorted(VALID_DAILY_ENTRY_TYPES))
            raise ValueError(f"Tipo non valido. Deve essere uno tra: {allowed}")
        return normalized

    @field_validator("testo")
    @classmethod
    def normalize_testo(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class DailyEntryResponse(ORMBaseModel):
    """Read response for frontend consumption."""

    id: int
    user_id: int
    data_riferimento: date
    tipo: str
    testo: Optional[str]
    completato: bool
    category_id: Optional[int]