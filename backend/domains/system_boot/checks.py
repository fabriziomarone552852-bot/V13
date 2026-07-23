import logging

from .repository import SystemBootRepository

logger = logging.getLogger(__name__)


class SystemBootChecks:
    def __init__(self, repo: SystemBootRepository) -> None:
        self.repo = repo

    def database_reachable(self) -> tuple[bool, str | None]:
        try:
            self.repo.ping()
            return True, None
        except Exception as exc:
            logger.exception("Database ping failed during system boot checks")
            return False, f"{type(exc).__name__}: {exc}"

    def critical_tables_status(self) -> dict[str, bool]:
        return {
            "system_metadata": self.repo.table_exists("system_metadata"),
            "config": self.repo.table_exists("config"),
            "config_codes": self.repo.table_exists("config_codes"),
            "users": self.repo.table_exists("users"),
        }

    def superuser_present(self) -> bool:
        users_exists = self.repo.table_exists("users")
        if not users_exists:
            return False

        has_is_superuser = self.repo.column_exists("users", "is_superuser")
        has_deleted_at = self.repo.column_exists("users", "deleted_at")
        if not (has_is_superuser and has_deleted_at):
            return False

        return self.repo.count_superusers() > 0