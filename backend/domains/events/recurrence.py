# backend/domains/events/recurrence.py
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from dateutil.rrule import rrulestr

from backend.domains.events.models import Event
from backend.domains.events.schemas import EventResponse


UTC = timezone.utc


def _ensure_naive(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(UTC).replace(tzinfo=None)


def expand_events_for_range(
    events_db: list[Event],
    start_date: date,
    end_date: date,
) -> list[EventResponse]:
    eventi_espansi: list[EventResponse] = []

    range_start = datetime.combine(start_date, time.min)
    range_end = datetime.combine(end_date, time.max)

    for ev in events_db:
        ev_start = _ensure_naive(ev.data_inizio)
        ev_end = _ensure_naive(ev.data_fine) if ev.data_fine else ev_start
        base_schema = EventResponse.model_validate(ev)

        if not ev.rrule:
            if ev_start <= range_end and ev_end >= range_start:
                eventi_espansi.append(base_schema)
            continue

        try:
            date_escluse = set(ev.esclusioni.split(",")) if ev.esclusioni else set()
            rule = rrulestr(ev.rrule, dtstart=ev_start)
            occorrenze = rule.between(range_start, range_end, inc=True)
            durata = ev_end - ev_start if ev.data_fine else timedelta(0)

            for occorrenza in occorrenze:
                giorno_str = occorrenza.strftime("%Y-%m-%d")
                if giorno_str in date_escluse:
                    continue

                updates = {"data_inizio": occorrenza}
                if ev.data_fine:
                    updates["data_fine"] = occorrenza + durata

                eventi_espansi.append(base_schema.model_copy(update=updates))

        except Exception:
            if ev_start <= range_end and ev_end >= range_start:
                eventi_espansi.append(base_schema)

    eventi_espansi.sort(key=lambda event: _ensure_naive(event.data_inizio))
    return eventi_espansi