"""
Monthly entries domain schemas.
Pydantic models for monthly feelings and monthly values.
"""
from __future__ import annotations

from typing import Optional

from pydantic import Field, field_validator

from backend.core.schemas import ORMBaseModel, StrictBaseModel


class MonthlyFeelingBase(StrictBaseModel):
    feel_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("feel_name")
    @classmethod
    def normalize_feel_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("feel_name non può essere vuoto.")
        return value


class MonthlyFeelingCreate(MonthlyFeelingBase):
    pass


class MonthlyFeelingUpdate(StrictBaseModel):
    feel_name: Optional[str] = Field(default=None, min_length=1, max_length=100)

    @field_validator("feel_name")
    @classmethod
    def normalize_feel_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("feel_name non può essere vuoto.")
        return value


class MonthlyFeelingResponse(ORMBaseModel):
    id: int
    feel_name: str


class MonthlyEntryBase(StrictBaseModel):
    year: int = Field(..., ge=1)
    month: int = Field(..., ge=1, le=12)
    feel_type: int
    feel_value: int = Field(..., ge=0, le=10)


class MonthlyEntryCreate(MonthlyEntryBase):
    pass


class MonthlyEntryUpdate(StrictBaseModel):
    feel_value: int = Field(..., ge=0, le=10)


class MonthlyEntryResponse(ORMBaseModel):
    id: int
    user_id: int
    year: int
    month: int
    feel_type: int
    feel_value: int
    feel_name: Optional[str] = None
