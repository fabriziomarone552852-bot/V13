"""
Canonical product and supplier entities.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.domains.catalogs.models import ConfigCode
    from backend.domains.users.models import User
    from .inventory import InventoryBatch
    from .lists import ShoppingListItem


class ShoppingProduct(Base):
    """Canonical product entity used by shopping items and inventory batches."""

    __tablename__ = "shopping_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name_normalized: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    created_by_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    updated_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="shopping_products_created",
    )
    updated_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by_user_id],
        back_populates="shopping_products_updated",
    )

    list_items: Mapped[List["ShoppingListItem"]] = relationship(
        "ShoppingListItem",
        back_populates="product",
        lazy="selectin",
    )
    inventory_batches: Mapped[List["InventoryBatch"]] = relationship(
        "InventoryBatch",
        back_populates="product",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ShoppingProduct id={self.id} name_normalized={self.name_normalized!r}>"


class ShoppingSupplier(Base):
    """Supplier used for inventory purchases."""

    __tablename__ = "shopping_suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_normalized: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    status_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_codes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    created_by_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    updated_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped["ConfigCode"] = relationship(
        "ConfigCode",
        foreign_keys=[status_id],
    )

    created_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="shopping_suppliers_created",
    )
    updated_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by_user_id],
        back_populates="shopping_suppliers_updated",
    )

    inventory_batches: Mapped[List["InventoryBatch"]] = relationship(
        "InventoryBatch",
        back_populates="supplier",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ShoppingSupplier id={self.id} name={self.name!r}>"