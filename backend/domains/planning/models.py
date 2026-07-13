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
    from backend.domains.users.models import User
    from backend.domains.categories.models import UserCategory


class DailyEntry(Base):
    """Modello unificato per annotazioni, priorità, focus e Pixel del calendario."""

    __tablename__ = "daily_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data_riferimento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Tipi: OW, OM, OD, PM, PD, PW, EP, EN, N1, N2, N3, N4, e ora PX (Pixel)
    tipo: Mapped[str] = mapped_column(String(2), nullable=False)
    
    testo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completato: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # --- NUOVO: Collegamento alla tabella ponte Categorie (UserCategory) ---
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("user_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relazioni
    user: Mapped["User"] = relationship("User")
    # Relazione fortemente tipizzata, nessun uso di "Any"
    category: Mapped[Optional["UserCategory"]] = relationship("UserCategory")

    __table_args__ = (
        UniqueConstraint("user_id", "data_riferimento", "tipo", name="uq_user_date_type"),
    )

    def __repr__(self) -> str:
        return f"<DailyEntry id={self.id} type={self.tipo} date={self.data_riferimento}>"