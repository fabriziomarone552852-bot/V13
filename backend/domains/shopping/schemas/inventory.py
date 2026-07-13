"""
Inventory domain schemas.
Pydantic models for inventory batches.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_DOWN
from typing import Optional

from pydantic import Field, field_validator

from backend.core.schemas import ORMBaseModel, StrictBaseModel


def _truncate_2_decimals(value: object) -> Decimal:
    dec = Decimal(str(value))
    return dec.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


class InventoryBatchBase(StrictBaseModel):
    product_id: int
    list_item_id: Optional[int] = None
    supplier_id: Optional[int] = None

    purchase_date: date
    expiration_date: Optional[date] = None

    quantity_purchased: Decimal = Field(
        ...,
        max_digits=12,
        decimal_places=2,
        gt=Decimal("0"),
    )

    purchase_price: Decimal = Field(
        ...,
        max_digits=12,
        decimal_places=2,
        ge=Decimal("0"),
    )

    is_on_sale: bool = False
    purchased_by_user_id: Optional[int] = None

    @field_validator("quantity_purchased", "purchase_price", mode="before")
    @classmethod
    def truncate_decimals(cls, value: object) -> object:
        if value is None or value == "":
            return value
        return _truncate_2_decimals(value)


class InventoryBatchCreate(InventoryBatchBase):
    pass


class InventoryBatchUpdate(StrictBaseModel):
    product_id: Optional[int] = None
    list_item_id: Optional[int] = None
    supplier_id: Optional[int] = None

    purchase_date: Optional[date] = None
    expiration_date: Optional[date] = None

    quantity_purchased: Optional[Decimal] = Field(
        default=None,
        max_digits=12,
        decimal_places=2,
        gt=Decimal("0"),
    )

    purchase_price: Optional[Decimal] = Field(
        default=None,
        max_digits=12,
        decimal_places=2,
        ge=Decimal("0"),
    )

    is_on_sale: Optional[bool] = None
    purchased_by_user_id: Optional[int] = None

    @field_validator("quantity_purchased", "purchase_price", mode="before")
    @classmethod
    def truncate_decimals(cls, value: object) -> object:
        if value is None or value == "":
            return value
        return _truncate_2_decimals(value)


class InventoryBatchResponse(ORMBaseModel):
    id: int
    product_id: int
    list_item_id: Optional[int] = None
    supplier_id: Optional[int] = None

    purchase_date: date
    expiration_date: Optional[date] = None

    quantity_purchased: Decimal
    purchase_price: Decimal

    is_on_sale: bool
    purchased_by_user_id: Optional[int] = None

    created_by_user_id: Optional[int] = None
    updated_by_user_id: Optional[int] = None
    deleted_by_user_id: Optional[int] = None

    created_at: date
    updated_at: date
    deleted_at: Optional[date] = None


class SupplierPriceSummary(ORMBaseModel):
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    avg_price: Optional[Decimal] = None
    latest_price: Optional[Decimal] = None
    latest_purchase_date: Optional[date] = None


class PriceHistoryPoint(ORMBaseModel):
    purchase_date: date
    purchase_price: Decimal
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    is_on_sale: bool = False