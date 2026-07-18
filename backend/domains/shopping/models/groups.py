"""
ORM models for ShoppingGroup and ShoppingGroupMember.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.domains.config import ConfigCode
    from backend.domains.users.models import User
    from .lists import ShoppingList


class ShoppingGroup(Base):
    __tablename__ = "shopping_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    owner_id: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_codes.id", ondelete="RESTRICT"),
        nullable=False,
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
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    owner: Mapped["User"] = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="shopping_groups",
    )
    status: Mapped["ConfigCode"] = relationship(
        "ConfigCode",
        foreign_keys=[status_id],
    )

    members: Mapped[List["ShoppingGroupMember"]] = relationship(
        "ShoppingGroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    shopping_lists: Mapped[List["ShoppingList"]] = relationship(
        "ShoppingList",
        back_populates="group",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ShoppingGroup id={self.id} name={self.name!r} owner_id={self.owner_id!r}>"


class ShoppingGroupMember(Base):
    __tablename__ = "shopping_group_members"

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="ux_shopping_group_members_group_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shopping_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_codes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    added_by_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
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
    removed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    group: Mapped["ShoppingGroup"] = relationship(
        "ShoppingGroup",
        back_populates="members",
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="shopping_group_memberships",
    )
    role: Mapped["ConfigCode"] = relationship(
        "ConfigCode",
        foreign_keys=[role_id],
    )
    added_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[added_by_user_id],
        back_populates="shopping_groups_added_members",
    )

    def __repr__(self) -> str:
        return (
            f"<ShoppingGroupMember id={self.id!r} group_id={self.group_id!r} "
            f"user_id={self.user_id!r} role_id={self.role_id!r}>"
        )