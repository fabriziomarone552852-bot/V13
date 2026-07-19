"""
Service del dominio Planning (daily entries).
Business rules e validazioni applicative.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.domains.planning import repository as repo
from backend.domains.planning import schemas
from backend.domains.planning.models import DailyEntry
from backend.domains.users.models import User

_NOT_FOUND = "Daily entry non trovata."
_DAILY_GOAL_DUP = "Esiste già un obiettivo giornaliero per questa data."
_WEEKLY_GOAL_DUP = "Esiste già un obiettivo settimanale per questa data."
_MONTHLY_GOAL_DUP = "Esiste già un obiettivo mensile per questa data."


def _validate_unique_entry_type(
    db: Session,
    user_id: int,
    data_riferimento: date,
    tipo: str,
    exclude_id: Optional[int] = None,
) -> None:
    duplicate_messages = {
        "OD": _DAILY_GOAL_DUP,
        "OW": _WEEKLY_GOAL_DUP,
        "OM": _MONTHLY_GOAL_DUP,
    }

    if tipo not in duplicate_messages:
        return

    exists = repo.entry_exists_by_type(
        db=db,
        user_id=user_id,
        data_riferimento=data_riferimento,
        tipo=tipo,
        exclude_id=exclude_id,
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=duplicate_messages[tipo],
        )


def list_entries(
    db: Session,
    user: User,
    data_riferimento: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    tipo: Optional[str] = None,
) -> list[DailyEntry]:
    return repo.list_for_user(
        db=db,
        user_id=user.id,
        data_riferimento=data_riferimento,
        start_date=start_date,
        end_date=end_date,
        tipo=tipo,
    )


def get_entry(db: Session, current_user: User, entry_id: int) -> DailyEntry:
    entry = repo.get_owned(db, entry_id, current_user.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
    return entry


def create_entry(db: Session, current_user: User, payload: schemas.DailyEntryCreate) -> DailyEntry:
    _validate_unique_entry_type(
        db=db,
        user_id=current_user.id,
        data_riferimento=payload.data_riferimento,
        tipo=payload.tipo,
    )

    new_entry = DailyEntry(
        user_id=current_user.id,
        data_riferimento=payload.data_riferimento,
        tipo=payload.tipo,
        testo=payload.testo,
        completato=payload.completato,
        category_id=payload.category_id,
    )
    return repo.add(db, new_entry)


def update_entry(
    db: Session,
    current_user: User,
    entry_id: int,
    payload: schemas.DailyEntryUpdate,
) -> DailyEntry:
    entry = repo.get_owned(db, entry_id, current_user.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)

    new_tipo = payload.tipo if payload.tipo is not None else entry.tipo
    new_data_riferimento = (
        payload.data_riferimento
        if payload.data_riferimento is not None
        else entry.data_riferimento
    )

    _validate_unique_entry_type(
        db=db,
        user_id=current_user.id,
        data_riferimento=new_data_riferimento,
        tipo=new_tipo,
        exclude_id=entry.id,
    )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    return repo.save(db, entry)


def delete_entry(db: Session, current_user: User, entry_id: int) -> None:
    entry = repo.get_owned(db, entry_id, current_user.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
    repo.delete(db, entry)