"""
Monthly entries repository.
Solo accesso ai dati, nessuna regola di business.
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from backend.domains.monthly_entries.models import MonthlyEntry, MonthlyFeeling


# -------------------- Feelings --------------------

def list_feelings(db: Session) -> List[MonthlyFeeling]:
    return (
        db.query(MonthlyFeeling)
        .order_by(MonthlyFeeling.feel_name.asc(), MonthlyFeeling.id.asc())
        .all()
    )


def get_feeling(db: Session, feeling_id: int) -> Optional[MonthlyFeeling]:
    return (
        db.query(MonthlyFeeling)
        .filter(MonthlyFeeling.id == feeling_id)
        .first()
    )


def get_feeling_by_name(db: Session, feel_name: str) -> Optional[MonthlyFeeling]:
    return (
        db.query(MonthlyFeeling)
        .filter(MonthlyFeeling.feel_name == feel_name)
        .first()
    )


def create_feeling(db: Session, feeling: MonthlyFeeling) -> MonthlyFeeling:
    db.add(feeling)
    db.commit()
    db.refresh(feeling)
    return feeling


def update_feeling(db: Session, feeling: MonthlyFeeling) -> MonthlyFeeling:
    db.commit()
    db.refresh(feeling)
    return feeling


def delete_feeling(db: Session, feeling: MonthlyFeeling) -> None:
    db.delete(feeling)
    db.commit()


# -------------------- Entries --------------------

def list_entries(
    db: Session,
    user_id: int,
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> List[MonthlyEntry]:
    query = (
        db.query(MonthlyEntry)
        .options(joinedload(MonthlyEntry.feeling))
        .filter(MonthlyEntry.user_id == user_id)
    )
    if year is not None:
        query = query.filter(MonthlyEntry.year == year)
    if month is not None:
        query = query.filter(MonthlyEntry.month == month)

    return (
        query.order_by(
            MonthlyEntry.year.desc(),
            MonthlyEntry.month.desc(),
            MonthlyEntry.feel_type.asc(),
            MonthlyEntry.id.desc(),
        )
        .all()
    )


def get_entry(db: Session, entry_id: int, user_id: int) -> Optional[MonthlyEntry]:
    return (
        db.query(MonthlyEntry)
        .options(joinedload(MonthlyEntry.feeling))
        .filter(
            MonthlyEntry.id == entry_id,
            MonthlyEntry.user_id == user_id,
        )
        .first()
    )


def get_entry_by_key(
    db: Session,
    user_id: int,
    year: int,
    month: int,
    feel_type: int,
) -> Optional[MonthlyEntry]:
    return (
        db.query(MonthlyEntry)
        .options(joinedload(MonthlyEntry.feeling))
        .filter(
            MonthlyEntry.user_id == user_id,
            MonthlyEntry.year == year,
            MonthlyEntry.month == month,
            MonthlyEntry.feel_type == feel_type,
        )
        .first()
    )


def create_entry(db: Session, entry: MonthlyEntry) -> MonthlyEntry:
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_entry(db: Session, entry: MonthlyEntry) -> MonthlyEntry:
    db.commit()
    db.refresh(entry)
    return entry


def delete_entry(db: Session, entry: MonthlyEntry) -> None:
    db.delete(entry)
    db.commit()