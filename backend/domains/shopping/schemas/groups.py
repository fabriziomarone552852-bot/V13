"""
Schemas for shopping groups and memberships.
"""
from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field, field_validator, model_validator
from backend.core.schemas import ORMBaseModel, StrictBaseModel

VALID_SHOPPING_GROUP_ROLE_CODES = {"reader", "editor", "admin", "owner"}

class ShoppingGroupCreate(StrictBaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Il nome del gruppo non può essere vuoto.")
        return value

class ShoppingGroupUpdate(StrictBaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Il nome del gruppo non può essere vuoto.")
        return value

class ShoppingGroupResponse(ORMBaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str] = None
    status_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

class ShoppingGroupMemberCreate(StrictBaseModel):
    user_id: int
    role_id: int
    _is_role_valid: bool = False

    @field_validator("user_id")
    @classmethod
    def validate_user_exists(cls, value: int) -> int:
        from backend.api.deps import get_db
        from backend.domains.users.repos import user_repo
        db = next(get_db())
        user = user_repo.get(db, id=value)
        if not user:
            raise ValueError(f"L'utente con id={value} non esiste.")
        return value

    @model_validator(mode="after")
    def validate_role_is_shopping_group_role(self) -> "ShoppingGroupMemberCreate":
        from backend.api.deps import get_db
        from backend.domains.config.repos import config_code_repo
        db = next(get_db())
        role = config_code_repo.get_by_id_and_type(db, id=self.role_id, code_type="shopping_group_role")
        if not role:
            raise ValueError(f"Il ruolo con id={self.role_id} non è un ruolo valido per i gruppi di shopping.")
        return self

class ShoppingGroupMemberUpdate(StrictBaseModel):
    role_id: int

class ShoppingGroupMemberInvite(StrictBaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role_code: str

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        return value or None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: Optional[EmailStr]) -> Optional[EmailStr]:
        if value is None:
            return value
        return str(value).strip().lower()

    @field_validator("role_code")
    @classmethod
    def validate_role_code(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in VALID_SHOPPING_GROUP_ROLE_CODES:
            raise ValueError("role_code non valido")
        return value

    @model_validator(mode="after")
    def validate_identity_pair(self) -> "ShoppingGroupMemberInvite":
        if not self.username and not self.email:
            raise ValueError("Devi fornire email oppure username.")
        return self

class ShoppingGroupMemberRoleUpdate(StrictBaseModel):
    role_code: str

    @field_validator("role_code")
    @classmethod
    def validate_role_code(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in VALID_SHOPPING_GROUP_ROLE_CODES:
            raise ValueError("role_code non valido")
        return value

class ShoppingGroupMemberResponse(ORMBaseModel):
    id: int
    group_id: int
    user_id: int
    role_id: int
    added_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    removed_at: Optional[datetime] = None
