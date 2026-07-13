"""
Schemas for shopping lists and items.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from typing import List, Optional

from pydantic import Field, computed_field, field_validator

from backend.core.schemas import ORMBaseModel, StrictBaseModel
from .inventory import InventoryBatchResponse


def _truncate_2_decimals(value: object) -> Decimal:
    dec = Decimal(str(value))
    return dec.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


class ShoppingListCreate(StrictBaseModel):
    group_id: Optional[int] = None
    visibility_id: int
    status_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Il nome della lista non può essere vuoto.")
        return value


class ShoppingListUpdate(StrictBaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    visibility_id: Optional[int] = None
    status_id: Optional[int] = None
    group_id: Optional[int] = None
    closed_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Il nome della lista non può essere vuoto.")
        return value


class ShoppingListItemCreate(StrictBaseModel):
    shopping_list_id: int
    product_name: str = Field(..., min_length=1, max_length=255)
    quantity: Optional[Decimal] = Field(
        default=None,
        max_digits=12,
        decimal_places=2,
        ge=Decimal("0"),
    )
    unit_id: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Il nome del prodotto non può essere vuoto.")
        return value

    @field_validator("quantity", mode="before")
    @classmethod
    def truncate_quantity(cls, value: object) -> object:
        if value is None or value == "":
            return value
        return _truncate_2_decimals(value)


class ShoppingListItemUpdate(StrictBaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity: Optional[Decimal] = Field(
        default=None,
        max_digits=12,
        decimal_places=2,
        ge=Decimal("0"),
    )
    unit_id: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Il nome del prodotto non può essere vuoto.")
        return value

    @field_validator("quantity", mode="before")
    @classmethod
    def truncate_quantity(cls, value: object) -> object:
        if value is None or value == "":
            return value
        return _truncate_2_decimals(value)


class _ShoppingProductLiteResponse(ORMBaseModel):
    id: int
    name_normalized: str


class _ShoppingUnitLiteResponse(ORMBaseModel):
    id: int
    code_name: str


class ShoppingListItemResponse(ORMBaseModel):
    id: int
    shopping_list_id: int
    product_id: int
    name_normalized: str
    quantity: Optional[Decimal] = None
    unit_id: Optional[int] = None
    notes: Optional[str] = None
    is_purchased: bool
    created_by_user_id: int
    updated_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    inventory_batches: List[InventoryBatchResponse] = Field(default_factory=list)

    # Relazioni ORM rese disponibili al modello Pydantic
    # ma escluse dalla serializzazione pubblica.
    product: Optional[_ShoppingProductLiteResponse] = Field(
        default=None,
        exclude=True,
    )
    unit: Optional[_ShoppingUnitLiteResponse] = Field(
        default=None,
        exclude=True,
    )

    @computed_field
    @property
    def product_name(self) -> str:
        return self.product.name_normalized if self.product else self.name_normalized

    @computed_field
    @property
    def unit_name(self) -> Optional[str]:
        return self.unit.code_name if self.unit else None


class ShoppingListResponse(ORMBaseModel):
    id: int
    owner_id: int
    group_id: Optional[int] = None
    visibility_id: int
    status_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    items: List[ShoppingListItemResponse] = Field(default_factory=list)


_ShoppingProductLiteResponse.model_rebuild()
_ShoppingUnitLiteResponse.model_rebuild()
ShoppingListItemResponse.model_rebuild()
ShoppingListResponse.model_rebuild()
