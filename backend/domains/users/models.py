"""
Users domain models.
User authentication and profile management.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.domains.audit.models import SharedActivityLog
    from backend.domains.categories.models import UserCategory
    from backend.domains.countdowns.models import Countdown
    from backend.domains.events.models import Event
    from backend.domains.habits.models import Habit
    from backend.domains.notifications.models import Notification
    from backend.domains.planning.models import DailyEntry
    from backend.domains.shopping.models import (
        InventoryBatch,
        ShoppingGroup,
        ShoppingGroupMember,
        ShoppingList,
        ShoppingListItem,
        ShoppingProduct,
        ShoppingSupplier,
    )
    from backend.domains.tasks.models import Task


class User(Base):
    """User account and authentication."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    max_subtask_depth_user: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=3,
        server_default=text("3"),
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    must_change_password: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    deleted_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    deleted_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[deleted_by_user_id],
        remote_side="User.id",
        back_populates="deleted_users",
    )
    deleted_users: Mapped[List["User"]] = relationship(
        "User",
        foreign_keys="User.deleted_by_user_id",
        back_populates="deleted_by_user",
    )

    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_categories: Mapped[List["UserCategory"]] = relationship(
        "UserCategory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    shopping_groups: Mapped[List["ShoppingGroup"]] = relationship(
        "ShoppingGroup",
        foreign_keys="ShoppingGroup.owner_id",
        back_populates="owner",
    )
    shopping_group_memberships: Mapped[List["ShoppingGroupMember"]] = relationship(
        "ShoppingGroupMember",
        foreign_keys="ShoppingGroupMember.user_id",
        back_populates="user",
    )
    shopping_groups_added_members: Mapped[List["ShoppingGroupMember"]] = relationship(
        "ShoppingGroupMember",
        foreign_keys="ShoppingGroupMember.added_by_user_id",
        back_populates="added_by_user",
    )

    shopping_lists: Mapped[List["ShoppingList"]] = relationship(
        "ShoppingList",
        foreign_keys="ShoppingList.owner_id",
        back_populates="owner",
    )

    shopping_items_created: Mapped[List["ShoppingListItem"]] = relationship(
        "ShoppingListItem",
        foreign_keys="ShoppingListItem.created_by_user_id",
        back_populates="created_by_user",
    )
    shopping_items_updated: Mapped[List["ShoppingListItem"]] = relationship(
        "ShoppingListItem",
        foreign_keys="ShoppingListItem.updated_by_user_id",
        back_populates="updated_by_user",
    )

    inventory_batches_purchased: Mapped[List["InventoryBatch"]] = relationship(
        "InventoryBatch",
        foreign_keys="InventoryBatch.purchased_by_user_id",
        back_populates="purchased_by_user",
    )
    inventory_batches_created: Mapped[List["InventoryBatch"]] = relationship(
        "InventoryBatch",
        foreign_keys="InventoryBatch.created_by_user_id",
        back_populates="created_by_user",
    )
    inventory_batches_updated: Mapped[List["InventoryBatch"]] = relationship(
        "InventoryBatch",
        foreign_keys="InventoryBatch.updated_by_user_id",
        back_populates="updated_by_user",
    )
    inventory_batches_deleted: Mapped[List["InventoryBatch"]] = relationship(
        "InventoryBatch",
        foreign_keys="InventoryBatch.deleted_by_user_id",
        back_populates="deleted_by_user",
    )

    shopping_products_created: Mapped[List["ShoppingProduct"]] = relationship(
        "ShoppingProduct",
        foreign_keys="ShoppingProduct.created_by_user_id",
        back_populates="created_by_user",
    )
    shopping_products_updated: Mapped[List["ShoppingProduct"]] = relationship(
        "ShoppingProduct",
        foreign_keys="ShoppingProduct.updated_by_user_id",
        back_populates="updated_by_user",
    )

    shopping_suppliers_created: Mapped[List["ShoppingSupplier"]] = relationship(
        "ShoppingSupplier",
        foreign_keys="ShoppingSupplier.created_by_user_id",
        back_populates="created_by_user",
    )
    shopping_suppliers_updated: Mapped[List["ShoppingSupplier"]] = relationship(
        "ShoppingSupplier",
        foreign_keys="ShoppingSupplier.updated_by_user_id",
        back_populates="updated_by_user",
    )

    shared_logs: Mapped[List["SharedActivityLog"]] = relationship(
        "SharedActivityLog",
        back_populates="performed_by_user",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    daily_entries: Mapped[List["DailyEntry"]] = relationship(
        "DailyEntry",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    countdowns: Mapped[List["Countdown"]] = relationship(
        "Countdown",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    habits: Mapped[List["Habit"]] = relationship(
        "Habit",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} username={self.username!r} email={self.email!r} "
            f"deleted_at={self.deleted_at!r} "
            f"max_subtask_depth_user={self.max_subtask_depth_user}>"
        )