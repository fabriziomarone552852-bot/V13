"""
Schemas for canonical shopping products and suppliers.
"""
from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator
from backend.core.schemas import ORMBaseModel, StrictBaseModel

class ShoppingProductCreate(StrictBaseModel):
    name: str = Field(..., min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Il nome del prodotto non può essere vuoto.")
        return value

class ShoppingProductUpdate(StrictBaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Il nome del prodotto non può essere vuoto.")
        return value

class ShoppingProductResponse(ORMBaseModel):
    id: int
    name_normalized: str
    created_by_user_id: int
    updated_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

class ShoppingSupplierCreate(StrictBaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    status_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Il nome del fornitore non può essere vuoto.")
        return value

class ShoppingSupplierUpdate(StrictBaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Il nome del fornitore non può essere vuoto.")
        return value

class ShoppingSupplierResponse(ORMBaseModel):
    id: int
    name: str
    name_normalized: str
    status_id: int
    created_by_user_id: int
    updated_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
