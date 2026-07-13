"""
Categories domain models.
Tabella dizionario per le categorie e tabella ponte per le personalizzazioni utente.
"""
from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.domains.users.models import User


class CategoryGenre(IntEnum):
    """Category type enumeration."""
    TASKS = 1
    EVENTS = 2
    COMMON = 3
    MOOD = 4


class Category(Base):
    """Dizionario globale delle categorie (univoche per nome)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

    # Relazione verso la tabella ponte
    user_links: Mapped[List["UserCategory"]] = relationship(
        "UserCategory", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"


class UserCategory(Base):
    """Tabella ponte: associa un utente a una categoria del dizionario con preferenze."""

    __tablename__ = "user_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    colore: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    genre: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Un utente non può collegarsi due volte alla stessa identica categoria del dizionario
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", name="uq_user_category"),
    )

    # Relazioni
    user: Mapped["User"] = relationship("User")
    category: Mapped["Category"] = relationship("Category", back_populates="user_links")

    def __repr__(self) -> str:
        return f"<UserCategory id={self.id} user_id={self.user_id} category_id={self.category_id} genre={self.genre}>"