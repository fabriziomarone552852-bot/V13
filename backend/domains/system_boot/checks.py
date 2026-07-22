from __future__ import annotations

from .repository import SystemBootRepository


class SystemBootChecks:
    def __init__(self, repo: SystemBootRepository) -> None:
        self.repo = repo

    def database_reachable(self) -> tuple[bool, str | None]:
        try:
            self.repo.ping()
            return True, None
        except Exception as exc:
            return False, f"{type(exc).__name__}: {exc}"

    def critical_tables_status(self) -> dict[str, bool]:
        return {
            "system_metadata": self.repo.table_exists("system_metadata"),
            "config": self.repo.table_exists("config"),
            "configcodes": self.repo.table_exists("config_codes"),
            "users": self.repo.table_exists("users"),
        }

    def users_schema_compatible(self) -> bool:
        users_exists = self.repo.table_exists("users")
        if not users_exists:
            return False

        has_issuperuser = self.repo.column_exists("users", "is_superuser")
        has_deletedat = self.repo.column_exists("users", "deleted_at")
        return has_issuperuser and has_deletedat

    def superuser_present(self) -> bool:
        compatible = self.users_schema_compatible()
        if not compatible:
            return False
        return self.repo.count_superusers() > 0