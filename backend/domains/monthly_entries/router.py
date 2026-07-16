"""
Monthly entries HTTP router.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.core import deps
from backend.domains.monthly_entries import schemas, service
from backend.domains.users.models import User

router = APIRouter(prefix="/monthly-entries", tags=["monthly-entries"])


@router.get("/feelings", response_model=List[schemas.MonthlyFeelingResponse])
def list_feelings(db: Session = Depends(deps.get_db)):
    return service.list_feelings(db)


@router.post(
    "/feelings",
    response_model=schemas.MonthlyFeelingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_feeling(
    feeling_in: schemas.MonthlyFeelingCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_superuser),
):
    return service.create_feeling(db, current_user, feeling_in)


@router.patch("/feelings/{feeling_id}", response_model=schemas.MonthlyFeelingResponse)
def update_feeling(
    feeling_id: int,
    feeling_in: schemas.MonthlyFeelingUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_superuser),
):
    return service.update_feeling(db, current_user, feeling_id, feeling_in)


@router.delete("/feelings/{feeling_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feeling(
    feeling_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_superuser),
):
    service.delete_feeling(db, current_user, feeling_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", response_model=List[schemas.MonthlyEntryResponse])
def list_entries(
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.list_entries(db, current_user, year, month)


@router.get("/{year}/{month}", response_model=List[schemas.MonthlyEntryResponse])
def list_entries_by_month(
    year: int,
    month: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.list_entries(db, current_user, year, month)


@router.post(
    "",
    response_model=schemas.MonthlyEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_entry(
    entry_in: schemas.MonthlyEntryCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.create_entry(db, current_user, entry_in)


@router.patch("/{entry_id}", response_model=schemas.MonthlyEntryResponse)
def update_entry(
    entry_id: int,
    entry_in: schemas.MonthlyEntryUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.update_entry(db, current_user, entry_id, entry_in)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service.delete_entry(db, current_user, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
