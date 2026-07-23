"""Router HTTP del dominio Users."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.core import deps
from backend.domains.users import schemas, service
from backend.domains.users.models import User

router = APIRouter(tags=["users"])


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(deps.get_current_app_user)):
    """Ritorna i dati principali dell'utente loggato."""
    return current_user


@router.get("/me/settings", response_model=schemas.UserSettingsResponse)
def get_my_settings(current_user: User = Depends(deps.get_current_app_user)):
    """Ritorna le impostazioni utente."""
    return current_user


@router.patch("/me/settings", response_model=schemas.UserSettingsResponse)
def update_my_settings(
    settings_in: schemas.UserSettingsUpdate,
    current_user: User = Depends(deps.get_current_app_user),
    db: Session = Depends(deps.get_db),
):
    return service.update_settings(db, current_user, settings_in)


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_my_account(
    current_user: User = Depends(deps.get_current_app_user),
    db: Session = Depends(deps.get_db),
):
    service.soft_delete_user(
        db=db,
        current_user=current_user,
        deleted_by_user_id=current_user.id,
    )
    return {"detail": "Account disattivato correttamente"}