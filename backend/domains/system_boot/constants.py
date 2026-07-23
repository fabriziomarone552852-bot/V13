from typing import Final

SUPPORTED_SCHEMA_VERSION: Final[str] = "1.0.0"
SUPPORTED_SEED_VERSION: Final[str] = "1.0.0"

BOOT_ALLOWED_ENVIRONMENTS: Final[set[str]] = {"dev", "test", "prod"}

BOOT_STATUS_EMPTY: Final[str] = "EMPTY"
BOOT_STATUS_SCHEMA_CREATED: Final[str] = "SCHEMA_CREATED"
BOOT_STATUS_SEEDED: Final[str] = "SEEDED"
BOOT_STATUS_SUPERUSER_REQUIRED: Final[str] = "SUPERUSER_REQUIRED"
BOOT_STATUS_READY: Final[str] = "READY"
BOOT_STATUS_ERROR: Final[str] = "ERROR"

CRITICAL_TABLES: Final[tuple[str, ...]] = (
    "system_metadata",
    "config",
    "configcodes",
    "users",
)