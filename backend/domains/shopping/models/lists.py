"""
Shopping lists and list items.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.domains.catalogs.models import ConfigCode
    from backend.domains.users.models import User
    from .catalog import ShoppingProduct
    from .groups import ShoppingGroup
    from .inventory import InventoryBatch


class ShoppingList(Base):
    """Shopping list optionally linked to a group."""

    __tablename__ = "shopping_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    owner_id: Mapped[int] = mapped_column(
        "user_id",  # Mappato sulla colonna reale "user_id"
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("shopping_groups.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    visibility_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_codes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_codes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="shopping_lists",
        foreign_keys=[owner_id],
    )
    group: Mapped[Optional["ShoppingGroup"]] = relationship(
        "ShoppingGroup",
        back_populates="shopping_lists",
        foreign_keys=[group_id],
    )
    visibility: Mapped["ConfigCode"] = relationship(
        "ConfigCode",
        foreign_keys=[visibility_id],
    )
    status: Mapped["ConfigCode"] = relationship(
        "ConfigCode",
        foreign_keys=[status_id],
    )

    items: Mapped[List["ShoppingListItem"]] = relationship(
        "ShoppingListItem",
        back_populates="shopping_list",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ShoppingList id={self.id} name={self.name!r}>"


class ShoppingListItem(Base):
    """Item inside a shopping list."""

    __tablename__ = "shopping_list_items"
    
    # Questo allinea il modello all'indice unico parziale presente nel DB
    __table_args__ = (
        Index(
            "ux_shopping_list_items_open_name",
            "shopping_list_id",
            "name_normalized",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND is_purchased = false"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    shopping_list_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shopping_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shopping_products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name_normalized: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    unit_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("config_codes.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_purchased: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
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
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    shopping_list: Mapped["ShoppingList"] = relationship(
        "ShoppingList",
        back_populates="items",
    )
    product: Mapped["ShoppingProduct"] = relationship(
        "ShoppingProduct",
        back_populates="list_items",
    )
    unit: Mapped[Optional["ConfigCode"]] = relationship(
        "ConfigCode",
        foreign_keys=[unit_id],
    )

    created_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="shopping_items_created",
    )
    updated_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by_user_id],
        back_populates="shopping_items_updated",
    )

    inventory_batches: Mapped[List["InventoryBatch"]] = relationship(
        "InventoryBatch",
        back_populates="list_item",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<ShoppingListItem id={self.id} shopping_list_id={self.shopping_list_id} "
            f"product_id={self.product_id} purchased={self.is_purchased}>"
        )