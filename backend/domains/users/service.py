"""Service del dominio Users — regole di business per le impostazioni utente."""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.deps import get_password_hash, verify_password
from backend.domains.users import repository as repo
from backend.domains.users import schemas
from backend.domains.users.models import User


def update_settings(
    db: Session,
    current_user: User,
    settings_in: schemas.UserSettingsUpdate,
) -> User:
    if current_user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    data = settings_in.model_dump(exclude_unset=True)

    if "email" in data:
        new_email = data["email"].strip().lower()
        if new_email != current_user.email.lower():
            if repo.email_in_use(db, new_email):
                raise HTTPException(status_code=400, detail="Email già in uso")
            current_user.email = new_email

    if "new_password" in data:
        if not verify_password(data["current_password"], current_user.password_hash):
            raise HTTPException(status_code=400, detail="Password corrente non corretta")

        current_user.password_hash = get_password_hash(data["new_password"])
        current_user.must_change_password = False

    if "max_subtask_depth_user" in data:
        current_user.max_subtask_depth_user = data["max_subtask_depth_user"]

    return repo.save(db, current_user)


def soft_delete_user(
    db: Session,
    current_user: User,
    deleted_by_user_id: int | None = None,
) -> User:
    if current_user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    return repo.soft_delete_user(
        db=db,
        user=current_user,
        deleted_by_user_id=deleted_by_user_id,
    )


def restore_user(
    db: Session,
    user_id: int,
) -> User:
    user = repo.get_by_id_including_deleted(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    if user.deleted_at is None:
        return user

    try:
        return repo.restore_user(db, user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Impossibile ripristinare l'utente per conflitto sui dati univoci. "
                "Verificare username ed email."
            ),
        )