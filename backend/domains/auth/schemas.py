"""
Auth domain schemas.
Pydantic models for authentication request and response payloads.
"""
from __future__ import annotations

from pydantic import Field

from backend.core.password_policy import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH
from backend.core.schemas import StrictBaseModel


class Token(StrictBaseModel):
    access_token: str
    token_type: str
    must_change_password: bool = False
    is_superuser: bool = False
    access_scope: str = "app"


class TokenPairResponse(StrictBaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    must_change_password: bool = False
    is_superuser: bool = False
    access_scope: str = "app"


class RefreshTokenRequest(StrictBaseModel):
    refresh_token: str


class RequiredPasswordChangeRequest(StrictBaseModel):
    current_password: str
    new_password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )