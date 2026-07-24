"""
Users domain schemas.
Pydantic models for API request/response validation.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr, Field, field_validator, model_validator

from backend.core.password_policy import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH
from backend.core.schemas import ORMBaseModel, StrictBaseModel


class UserCreate(StrictBaseModel):
    """Request model for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserResponse(ORMBaseModel):
    """Response model for user data."""
    id: int
    username: str
    email: EmailStr
    max_subtask_depth_user: int | None = 3
    is_superuser: bool = False
    must_change_password: bool = False


class UserPublicResponse(ORMBaseModel):
    """Public response model with limited user info."""
    id: int
    username: str


class UserSettingsResponse(ORMBaseModel):
    """Response model for user settings."""
    id: int
    username: str
    email: EmailStr
    max_subtask_depth_user: int | None = 3
    is_superuser: bool = False
    must_change_password: bool = False


class UserAdminResponse(ORMBaseModel):
    """Administrative response model, includes soft-delete metadata."""
    id: int
    username: str
    email: EmailStr
    max_subtask_depth_user: int | None = 3
    is_superuser: bool = False
    must_change_password: bool = False
    deleted_at: datetime | None = None
    deleted_by_user_id: int | None = None


class UserSettingsUpdate(StrictBaseModel):
    """Request model for updating user settings."""
    email: EmailStr | None = None
    current_password: str | None = Field(
        None,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )
    new_password: str | None = Field(
        None,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )
    confirm_new_password: str | None = Field(
        None,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )
    max_subtask_depth_user: int | None = Field(None, ge=1, le=15)

    @model_validator(mode="after")
    def validate_password_change(self) -> "UserSettingsUpdate":
        provided = [self.current_password, self.new_password, self.confirm_new_password]
        if any(value is not None for value in provided):
            if not all(value is not None for value in provided):
                raise ValueError(
                    "Per cambiare password devi fornire current_password, new_password e confirm_new_password."
                )
            if self.new_password != self.confirm_new_password:
                raise ValueError("new_password e confirm_new_password non coincidono.")
        return self

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr | None) -> str | None:
        if value is None:
            return value
        return str(value).strip().lower()