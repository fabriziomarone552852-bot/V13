"""
Planning domain models.
Daily entries for goals, priorities, notes, and calendar pixels.
"""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.domains.categories.models import UserCategory
    from backend.domains.users.models import User


class DailyEntry(Base):
    """Unified planning entry for daily, weekly, monthly and pixel records."""

    __tablename__ = "daily_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    data_riferimento: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # PX, OD, PD, N1, N2, N3, N4, OW, PW, OM, PM, EP, EN
    tipo: Mapped[str] = mapped_column(String(2), nullable=False)

    testo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completato: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("user_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="daily_entries",
    )

    category: Mapped[Optional["UserCategory"]] = relationship(
        "UserCategory",
        back_populates="daily_entries",
    )

    def __repr__(self) -> str:
        return (
            f"<DailyEntry id={self.id} user_id={self.user_id} "
            f"tipo={self.tipo} data_riferimento={self.data_riferimento}>"
        )