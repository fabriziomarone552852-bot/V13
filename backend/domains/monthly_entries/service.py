"""
Monthly entries service.
Regole di business e validazioni.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.domains.monthly_entries import repository as repo
from backend.domains.monthly_entries import schemas
from backend.domains.monthly_entries.models import MonthlyEntry, MonthlyFeeling
from backend.domains.users.models import User


def _validate_monthly_year_month(year: int, month: int) -> None:
    if year < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="year non valido.")
    if month < 1 or month > 12:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="month deve essere compreso tra 1 e 12.")


def _validate_feel_value(value: int) -> None:
    if value < 0 or value > 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="feel_value deve essere compreso tra 0 e 10.")


def _get_feeling_or_404(db: Session, feeling_id: int) -> MonthlyFeeling:
    feeling = repo.get_feeling(db, feeling_id)
    if not feeling:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feeling non trovato.")
    return feeling


def _get_entry_or_404(db: Session, entry_id: int, user_id: int) -> MonthlyEntry:
    entry = repo.get_entry(db, entry_id, user_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry mensile non trovata.")
    return entry


# -------------------- Feelings --------------------

def list_feelings(db: Session) -> List[MonthlyFeeling]:
    return repo.list_feelings(db)


def create_feeling(db: Session, feeling_in: schemas.MonthlyFeelingCreate) -> MonthlyFeeling:
    existing = repo.get_feeling_by_name(db, feeling_in.feel_name)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="feel_name già esistente.")

    feeling = MonthlyFeeling(feel_name=feeling_in.feel_name)
    return repo.create_feeling(db, feeling)


def update_feeling(db: Session, feeling_id: int, feeling_in: schemas.MonthlyFeelingUpdate) -> MonthlyFeeling:
    feeling = _get_feeling_or_404(db, feeling_id)

    if feeling_in.feel_name is not None:
        duplicate = repo.get_feeling_by_name(db, feeling_in.feel_name)
        if duplicate and duplicate.id != feeling.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="feel_name già esistente.")
        feeling.feel_name = feeling_in.feel_name

    return repo.update_feeling(db, feeling)


def delete_feeling(db: Session, feeling_id: int) -> None:
    feeling = _get_feeling_or_404(db, feeling_id)
    repo.delete_feeling(db, feeling)


# -------------------- Entries --------------------

def list_entries(
    db: Session,
    current_user: User,
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> List[MonthlyEntry]:
    if year is not None and year < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="year non valido.")
    if month is not None and (month < 1 or month > 12):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="month deve essere compreso tra 1 e 12.")

    return repo.list_entries(db, current_user.id, year, month)


def create_entry(db: Session, current_user: User, entry_in: schemas.MonthlyEntryCreate) -> MonthlyEntry:
    _validate_monthly_year_month(entry_in.year, entry_in.month)
    _validate_feel_value(entry_in.feel_value)
    _get_feeling_or_404(db, entry_in.feel_type)

    existing = repo.get_entry_by_key(
        db,
        current_user.id,
        entry_in.year,
        entry_in.month,
        entry_in.feel_type,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esiste già un valore per questo feeling in questo mese.",
        )

    entry = MonthlyEntry(
        user_id=current_user.id,
        year=entry_in.year,
        month=entry_in.month,
        feel_type=entry_in.feel_type,
        feel_value=entry_in.feel_value,
    )

    try:
        return repo.create_entry(db, entry)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esiste già un valore per questo feeling in questo mese.",
        )


def update_entry(db: Session, current_user: User, entry_id: int, entry_in: schemas.MonthlyEntryUpdate) -> MonthlyEntry:
    _validate_feel_value(entry_in.feel_value)

    entry = _get_entry_or_404(db, entry_id, current_user.id)
    entry.feel_value = entry_in.feel_value
    return repo.update_entry(db, entry)


def delete_entry(db: Session, current_user: User, entry_id: int) -> None:
    entry = _get_entry_or_404(db, entry_id, current_user.id)
    repo.delete_entry(db, entry)