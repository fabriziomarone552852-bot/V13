from typing import Literal
from pydantic import BaseModel, Field, EmailStr, ConfigDict

EnvironmentKey = Literal["dev", "test", "prod"]
BootStatus = Literal[
    "EMPTY",
    "SCHEMA_CREATED",
    "SEEDED",
    "SUPERUSER_REQUIRED",
    "READY",
    "ERROR",
]

class BootInitRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    environment: EnvironmentKey
    db_name: str = Field(min_length=1, max_length=128)

class BootStatusResponse(BaseModel):
    environment: EnvironmentKey | None = None
    db_name: str | None = None
    db_reachable: bool
    schema_present: bool
    schema_version: str | None = None
    seed_version: str | None = None
    config_present: bool
    config_codes_present: bool
    users_present: bool
    superuser_present: bool
    boot_status: BootStatus
    next_action: str

class BootRunResponse(BaseModel):
    boot_status: BootStatus
    schema_created: bool
    seed_applied: bool
    superuser_required: bool
    message: str

class SuperUserBootstrapRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

class SuperUserBootstrapResponse(BaseModel):
    status: Literal["ok"]
    boot_status: BootStatus
    message: str

class BootStatusResponse(BaseModel):
    environment: EnvironmentKey | None = None
    db_name: str | None = None
    db_reachable: bool
    schema_present: bool
    schema_version: str | None = None
    seed_version: str | None = None
    config_present: bool
    config_codes_present: bool
    users_present: bool
    superuser_present: bool
    boot_status: BootStatus
    next_action: str
    diagnostic_message: str | None = None