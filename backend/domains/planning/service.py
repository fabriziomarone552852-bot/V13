"""Service del dominio Planning (daily entries) — regole di business."""
from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.domains.planning import repository as repo
from backend.domains.planning import schemas
from backend.domains.planning.models import DailyEntry
from backend.domains.users.models import User

_NOT_FOUND = "Daily entry non trovata."
_GOAL_DUP = "Esiste già un obiettivo per questa data."


def list_entries(
    db: Session,
    current_user: User,
    data_riferimento: Optional[date] = None,
    tipo: Optional[str] = None,
) -> List[DailyEntry]:
    return repo.list_for_user(db, current_user.id, data_riferimento, tipo)


def get_entry(db: Session, current_user: User, entry_id: int) -> DailyEntry:
    entry = repo.get_owned(db, entry_id, current_user.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
    return entry


def create_entry(db: Session, current_user: User, payload: schemas.DailyEntryCreate) -> DailyEntry:
    if payload.tipo == "Obiettivo" and repo.goal_exists(
        db, current_user.id, payload.data_riferimento
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_GOAL_DUP)

    new_entry = DailyEntry(
        user_id=current_user.id,
        data_riferimento=payload.data_riferimento,
        tipo=payload.tipo,
        testo=payload.testo,
        immagine_url=payload.immagine_url,
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
        payload.data_riferimento if payload.data_riferimento is not None else entry.data_riferimento
    )

    if new_tipo == "Obiettivo" and repo.goal_exists(
        db, current_user.id, new_data_riferimento, exclude_id=entry.id
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_GOAL_DUP)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    return repo.save(db, entry)


def delete_entry(db: Session, current_user: User, entry_id: int) -> None:
    entry = repo.get_owned(db, entry_id, current_user.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
    repo.delete(db, entry)
