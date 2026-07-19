"""Service del dominio Tasks — regole di business (gerarchia, profondità, categoria)."""
from datetime import datetime, timezone
from typing import Sequence, Union

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.core import deps
from backend.domains.categories import repository as categories_repo
from backend.domains.categories.models import CategoryGenre
from backend.domains.tasks import repository as repo
from backend.domains.tasks import schemas
from backend.domains.tasks.models import Task
from backend.domains.users.models import User


_COMPLETED_LOOKBACK_DAYS = 90


def populate_category_name(
    obj: Union[Task, Sequence[Task], None],
) -> Union[Task, Sequence[Task], None]:
    """Copia il nome categoria user-scoped sull'attributo trasmesso al client."""
    if obj is None:
        return None

    if isinstance(obj, Task):
        if obj.category:
            obj.category_name = obj.category.category_name
        return obj

    for task in obj:
        if task.category:
            task.category_name = task.category.category_name

    return obj


def _validate_user_category(
    db: Session,
    current_user: User,
    user_category_id: int | None,
) -> None:
    """Verifica che la categoria appartenga all'utente e sia compatibile con i task."""
    if user_category_id is None:
        return

    user_category = categories_repo.get_user_category(db, user_category_id, current_user.id)
    if not user_category:
        raise HTTPException(
            status_code=400,
            detail="Categoria task non valida o non accessibile.",
        )

    if user_category.genre not in (CategoryGenre.TASKS, CategoryGenre.COMMON):
        raise HTTPException(
            status_code=400,
            detail="La categoria selezionata non è utilizzabile per i task.",
        )


def create_task(db: Session, current_user: User, task_in: schemas.TaskCreate) -> Task:
    _validate_user_category(db, current_user, task_in.user_category_id)

    parent_task = (
        deps.get_task_owned(task_in.parent_id, current_user, db)
        if task_in.parent_id is not None
        else None
    )

    new_task = Task(
        titolo=task_in.titolo,
        descrizione=task_in.descrizione,
        data_start=task_in.data_start or datetime.now(timezone.utc),
        data_scadenza=task_in.data_scadenza,
        priorita=task_in.priorita,
        user_category_id=task_in.user_category_id,
        luogo=task_in.luogo,
        user_id=current_user.id,
        parent_id=parent_task.id if parent_task else None,
    )

    max_depth = deps.get_effective_max_depth(current_user, db)
    if new_task.calculate_depth(db_session=db) > max_depth:
        raise HTTPException(
            status_code=400,
            detail=(
                "Impossibile creare il sottotask. "
                "Raggiunto il limite massimo di annidamento consentito "
                f"(Max Livello effettivo: {max_depth})."
            ),
        )

    repo.add(db, new_task)
    new_task = repo.get_with_relations(db, new_task.id)
    populate_category_name(new_task)
    return new_task


def list_tasks(db: Session, current_user: User) -> schemas.PaginatedTasks:
    results = repo.list_active(db, current_user.id, _COMPLETED_LOOKBACK_DAYS)
    populate_category_name(results)
    total = len(results)
    return schemas.PaginatedTasks(
        items=results,
        total=total,
        limit=max(total, 1),
        offset=0,
    )


def get_task_family(db: Session, current_user: User, task_id: int) -> Task:
    task = repo.get_family(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato o non accessibile")
    populate_category_name(task)
    return task


def update_task(
    db: Session,
    current_user: User,
    task_id: int,
    task_in: schemas.TaskUpdate,
) -> Task:
    db_task = deps.get_task_owned(task_id, current_user, db)

    if task_in.parent_id is not None and deps.would_create_cycle(
        task_id, task_in.parent_id, current_user, db
    ):
        raise HTTPException(
            status_code=400,
            detail="Aggiornamento non valido: creerebbe un ciclo nella gerarchia dei task.",
        )

    if task_in.user_category_id is not None:
        _validate_user_category(db, current_user, task_in.user_category_id)

    update_data = task_in.model_dump(exclude_unset=True)
    old_fatto = db_task.fatto
    new_fatto = update_data.get("fatto")

    update_data.pop("data_fatto", None)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    if new_fatto is not None and new_fatto != old_fatto:
        db_task.data_fatto = datetime.now(timezone.utc) if new_fatto is True else None

    max_depth = deps.get_effective_max_depth(current_user, db)
    if db_task.calculate_depth(db_session=db) > max_depth:
        raise HTTPException(
            status_code=400,
            detail=(
                "Impossibile aggiornare il task. "
                "Raggiunto il limite massimo di annidamento consentito "
                f"(Max Livello effettivo: {max_depth})."
            ),
        )

    repo.commit(db)
    db.refresh(db_task)
    db_task = repo.get_with_relations(db, db_task.id)
    populate_category_name(db_task)
    return db_task


def delete_task(db: Session, current_user: User, task_id: int) -> None:
    db_task = deps.get_task_owned(task_id, current_user, db)
    repo.delete(db, db_task)