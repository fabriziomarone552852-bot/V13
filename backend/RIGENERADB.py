from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from backend.core.database import Base, SessionLocal, engine


def _import_domain_models() -> list[str]:
    imported_modules: list[str] = []

    domains_pkg = importlib.import_module("backend.domains")
    domains_path = [str(Path(domains_pkg.__file__).resolve().parent)]

    for module_info in pkgutil.iter_modules(domains_path):
        domain_name = module_info.name
        if domain_name.startswith("_"):
            continue

        models_module_name = f"backend.domains.{domain_name}.models"
        try:
            models_module = importlib.import_module(models_module_name)
            imported_modules.append(models_module_name)
        except ModuleNotFoundError as exc:
            if exc.name == models_module_name:
                continue
            raise

        models_file = Path(getattr(models_module, "__file__", ""))
        if not models_file.exists():
            continue

        if models_file.name == "__init__.py":
            models_pkg_path = [str(models_file.parent)]
            for submodule_info in pkgutil.iter_modules(models_pkg_path):
                submodule_name = submodule_info.name
                if submodule_name.startswith("_"):
                    continue

                full_submodule_name = f"{models_module_name}.{submodule_name}"
                try:
                    importlib.import_module(full_submodule_name)
                    imported_modules.append(full_submodule_name)
                except ModuleNotFoundError as exc:
                    if exc.name == full_submodule_name:
                        continue
                    raise

    return imported_modules


def bootstrap_db() -> None:
    imported_modules = _import_domain_models()

    print(f"Moduli models importati: {len(imported_modules)}")
    for module_name in imported_modules:
        print(f" - {module_name}")

    Base.metadata.create_all(bind=engine)

    print(f"Tabelle registrate nel metadata: {len(Base.metadata.tables)}")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f" - {table_name}")

    from backend.seed import seed_database

    try:
        seed_database()
    except TypeError:
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()


if __name__ == "__main__":
    bootstrap_db()
