"""Service del dominio Events — regole di business ed espansione ricorrenze."""
from datetime import date
from typing import Optional, Sequence, Union

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.domains.categories import repository as categories_repo
from backend.domains.categories.models import CategoryGenre
from backend.domains.events import repository as repo
from backend.domains.events import schemas
from backend.domains.events.models import Event
from backend.domains.users.models import User
from backend.pagination_schemas import PaginatedEvents
from backend.utils import expand_events_for_range


_NOT_FOUND = "Impegno non trovato o non accessibile"


def populate_category_name(
    obj: Union[Event, Sequence[Event], None],
) -> Union[Event, Sequence[Event], None]:
    """Copia il nome categoria user-scoped sull'attributo trasmesso al client."""
    if obj is None:
        return None

    if isinstance(obj, Event):
        if obj.category:
            obj.category_name = obj.category.category_name
        return obj

    for event in obj:
        if event.category:
            event.category_name = event.category.category_name

    return obj


def _validate_user_category(
    db: Session,
    current_user: User,
    user_category_id: int | None,
) -> None:
    """Verifica che la categoria appartenga all'utente e sia compatibile con gli eventi."""
    if user_category_id is None:
        return

    user_category = categories_repo.get_user_category(db, user_category_id, current_user.id)
    if not user_category:
        raise HTTPException(
            status_code=400,
            detail="Categoria evento non valida o non accessibile.",
        )

    if user_category.genre not in (CategoryGenre.EVENTS, CategoryGenre.COMMON):
        raise HTTPException(
            status_code=400,
            detail="La categoria selezionata non è utilizzabile per gli eventi.",
        )


def create_event(db: Session, current_user: User, event_in: schemas.EventCreate) -> Event:
    _validate_user_category(db, current_user, event_in.user_category_id)

    db_event = Event(
        titolo=event_in.titolo,
        descrizione=event_in.descrizione,
        data_inizio=event_in.data_inizio,
        data_fine=event_in.data_fine,
        tutto_il_giorno=event_in.tutto_il_giorno,
        luogo=event_in.luogo,
        user_category_id=event_in.user_category_id,
        user_id=current_user.id,
        rrule=event_in.rrule,
    )
    repo.add(db, db_event)

    db_event = repo.get_with_category(db, db_event.id)
    populate_category_name(db_event)
    return db_event


def list_events(
    db: Session,
    current_user: User,
    *,
    titolo: Optional[str] = None,
    descrizione: Optional[str] = None,
    luogo: Optional[str] = None,
    user_category_id: Optional[int] = None,
    tutto_il_giorno: Optional[bool] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    offset: int = 0,
) -> PaginatedEvents:
    total, events_db = repo.list_filtered(
        db,
        current_user.id,
        titolo=titolo,
        descrizione=descrizione,
        luogo=luogo,
        user_category_id=user_category_id,
        tutto_il_giorno=tutto_il_giorno,
        limit=limit,
        offset=offset,
    )

    populate_category_name(events_db)

    if start_date and end_date:
        items = expand_events_for_range(events_db, start_date, end_date)
    else:
        items = [schemas.EventResponse.model_validate(ev) for ev in events_db]

    return PaginatedEvents(items=items, total=total, limit=limit, offset=offset)


def update_event(
    db: Session,
    current_user: User,
    event_id: int,
    event_in: schemas.EventUpdate,
) -> Event:
    db_event = repo.get_owned(db, event_id, current_user.id)
    if not db_event:
        raise HTTPException(status_code=404, detail=_NOT_FOUND)

    if event_in.user_category_id is not None:
        _validate_user_category(db, current_user, event_in.user_category_id)

    update_data = event_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)

    repo.commit(db)
    db.refresh(db_event)

    db_event = repo.get_with_category(db, db_event.id)
    populate_category_name(db_event)
    return db_event


def delete_event(db: Session, current_user: User, event_id: int) -> None:
    db_event = repo.get_owned(db, event_id, current_user.id)
    if not db_event:
        raise HTTPException(status_code=404, detail=_NOT_FOUND)
    repo.delete(db, db_event)