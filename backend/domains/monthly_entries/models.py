"""
Monthly entries domain models.
Gestione dei feeling mensili per utente.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.domains.users.models import User


class MonthlyFeeling(Base):
    """Lookup table per i tipi di feeling mensili."""

    __tablename__ = "monthly_feeling"

    __table_args__ = (
        Index("idx_monthly_feeling_name", "feel_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feel_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    entries: Mapped[List["MonthlyEntry"]] = relationship(
        "MonthlyEntry",
        back_populates="feeling",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<MonthlyFeeling id={self.id} feel_name={self.feel_name!r}>"


class MonthlyEntry(Base):
    """Monthly value for a feeling and a user."""

    __tablename__ = "monthly_entries"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "year",
            "month",
            "feel_type",
            name="uq_monthly_entries_user_year_month_feel_type",
        ),
        Index("idx_monthly_entries_user_year_month", "user_id", "year", "month"),
        Index("idx_monthly_entries_feel_type", "feel_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    feel_type: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("monthly_feeling.id", ondelete="RESTRICT"),
        nullable=False,
    )
    feel_value: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship("User")
    feeling: Mapped["MonthlyFeeling"] = relationship(
        "MonthlyFeeling",
        back_populates="entries",
    )

    def __repr__(self) -> str:
        return (
            f"<MonthlyEntry id={self.id} user_id={self.user_id} "
            f"year={self.year} month={self.month} feel_type={self.feel_type} "
            f"feel_value={self.feel_value}>"
        )
