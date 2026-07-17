"""
Categories domain models.
Categorie completamente user-scoped: ogni utente gestisce le proprie categorie
con nome personalizzato e metadati locali.
"""
from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.domains.users.models import User
    from backend.domains.tasks.models import Task


class CategoryGenre(IntEnum):
    """Category type enumeration."""
    TASKS = 1
    EVENTS = 2
    COMMON = 3
    MOOD = 4


class UserCategory(Base):
    """Categoria utente-specifica con nome personalizzato e preferenze locali."""

    __tablename__ = "user_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    colore: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)

    genre: Mapped[int] = mapped_column(
        Integer,
        default=CategoryGenre.COMMON,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "category_name", name="uq_user_category_name"),
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_categories",
    )

    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="category",
        passive_deletes=True,
    )

    @validates("category_name")
    def validate_category_name(self, key: str, value: str) -> str:
        normalized = " ".join(value.strip().lower().split())
        if not normalized:
            raise ValueError("category_name cannot be empty")
        return normalized

    def __repr__(self) -> str:
        return (
            f"<UserCategory id={self.id} user_id={self.user_id} "
            f"category_name={self.category_name!r} genre={self.genre}>"
        )