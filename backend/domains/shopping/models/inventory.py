"""
Inventory domain models.
Inventory batches representing real purchased quantities stored in-house.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.domains.users.models import User
    from .lists import ShoppingListItem
    from .catalog import ShoppingProduct, ShoppingSupplier


class InventoryBatch(Base):
    __tablename__ = "inventory_batch"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("shopping_products.id"),
        nullable=False,
    )

    list_item_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("shopping_list_items.id"),
        nullable=True,
        index=True,
    )

    purchase_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    quantity_purchased: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    purchase_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    supplier_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("shopping_suppliers.id"),
        nullable=True,
    )

    is_on_sale: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    expiration_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
    )

    updated_by_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
    )

    purchased_by_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
    )

    deleted_by_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    updated_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    deleted_at: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    product: Mapped["ShoppingProduct"] = relationship(
        "ShoppingProduct",
        back_populates="inventory_batches",
    )

    list_item: Mapped[Optional["ShoppingListItem"]] = relationship(
        "ShoppingListItem",
        back_populates="inventory_batches",
    )

    supplier: Mapped[Optional["ShoppingSupplier"]] = relationship(
        "ShoppingSupplier",
        back_populates="inventory_batches",
    )

    purchased_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[purchased_by_user_id],
        back_populates="inventory_batches_purchased",
    )

    created_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="inventory_batches_created",
    )

    updated_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by_user_id],
        back_populates="inventory_batches_updated",
    )

    deleted_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[deleted_by_user_id],
        back_populates="inventory_batches_deleted",
    )

    def __repr__(self) -> str:
        return (
            f"<InventoryBatch id={self.id} product_id={self.product_id} "
            f"quantity_purchased={self.quantity_purchased} purchase_price={self.purchase_price}>"
        )