"""
Categories domain schemas.
Pydantic models for API request/response validation.
"""
from __future__ import annotations

from enum import IntEnum
from typing import Optional

from pydantic import Field, field_validator

from backend.core.schemas import ORMBaseModel, StrictBaseModel


class CategoryGenre(IntEnum):
    """Category type enumeration."""
    TASKS = 1
    EVENTS = 2
    COMMON = 3
    MOOD = 4


def _normalize_name(value: str) -> str:
    normalized = " ".join(value.strip().lower().split())
    if not normalized:
        raise ValueError("Il nome della categoria non può essere vuoto.")
    return normalized


def _validate_hex_color(value: Optional[str]) -> Optional[str]:
    if value is None:
        return value

    if len(value) != 7 or not value.startswith("#"):
        raise ValueError("Il colore deve essere un codice HEX nel formato #RRGGBB.")

    hex_digits = value[1:]
    is_valid_hex = all(char in "0123456789abcdefABCDEF" for char in hex_digits)
    if not is_valid_hex:
        raise ValueError("Il colore deve essere un codice HEX valido.")

    return value.upper()


class CategoryBase(StrictBaseModel):
    """Base schema for user-scoped categories."""

    name: str = Field(..., min_length=1, max_length=50)
    colore: Optional[str] = Field(
        None,
        max_length=7,
        description="Codice colore HEX, es: #FF5733",
    )
    genre: CategoryGenre = Field(
        CategoryGenre.COMMON,
        description="1=solo tasks, 2=solo events, 3=comune, 4=mood",
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _normalize_name(value)

    @field_validator("colore")
    @classmethod
    def validate_hex_color(cls, value: Optional[str]) -> Optional[str]:
        return _validate_hex_color(value)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(StrictBaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    colore: Optional[str] = Field(
        None,
        max_length=7,
        description="Codice colore HEX, es: #FF5733",
    )
    genre: Optional[CategoryGenre] = Field(
        None,
        description="1=solo tasks, 2=solo events, 3=comune, 4=mood",
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _normalize_name(value)

    @field_validator("colore")
    @classmethod
    def validate_hex_color(cls, value: Optional[str]) -> Optional[str]:
        return _validate_hex_color(value)


class CategoryResponse(ORMBaseModel):
    id: int
    name: str
    colore: Optional[str] = None
    user_id: int
    genre: CategoryGenre