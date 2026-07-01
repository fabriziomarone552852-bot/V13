"""Router HTTP del dominio Users (prefix /me)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core import deps
from backend.domains.users import schemas, service
from backend.domains.users.models import User

router = APIRouter(prefix="/me", tags=["users"])


@router.get("", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(deps.get_current_user)):
    """Ritorna i dati principali dell'utente loggato."""
    return current_user


@router.get("/settings", response_model=schemas.UserSettingsResponse)
def get_my_settings(current_user: User = Depends(deps.get_current_user)):
    """Ritorna le impostazioni utente (email, limite nidificazione, ecc.)."""
    return current_user


@router.patch("/settings", response_model=schemas.UserSettingsResponse)
def update_my_settings(
    settings_in: schemas.UserSettingsUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return service.update_settings(db, current_user, settings_in)
