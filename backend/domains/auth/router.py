"""Router HTTP del dominio Auth (register / login / refresh)."""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.core import deps
from backend.domains.auth import service
from backend.domains.auth.schemas import (
    RefreshTokenRequest,
    RequiredPasswordChangeRequest,
    Token,
    TokenPairResponse,
)
from backend.domains.users import schemas as users_schemas

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=users_schemas.UserResponse, status_code=201)
def register(
    user_in: users_schemas.UserCreate,
    db: Session = Depends(deps.get_db),
):
    return service.register(db, user_in)


@router.post("/login", response_model=TokenPairResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
):
    return service.login(db, form_data.username, form_data.password)


@router.post("/refresh", response_model=Token)
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(deps.get_db),
):
    return service.refresh(db, payload.refresh_token)


@router.post("/change-password-required", response_model=TokenPairResponse)
def change_password_required(
    payload: RequiredPasswordChangeRequest,
    db: Session = Depends(deps.get_db),
    token_payload: dict[str, object] = Depends(deps.require_password_change_scope),
):
    return service.change_password_required(db, str(token_payload["sub"]), payload)