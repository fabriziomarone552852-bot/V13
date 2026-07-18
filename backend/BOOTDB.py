#!/usr/bin/env python
"""
BOOTDB.py — Bootstrap multi-ambiente: crea le tabelle e semina i dati iniziali.

Uso:
    python -m backend.BOOTDB --env dev
    python -m backend.BOOTDB --env test
    python -m backend.BOOTDB --env prod
    python -m backend.BOOTDB            # menu interattivo

Flags opzionali:
    --skip-seed     Salta il seed dopo la creazione delle tabelle.
"""
from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
VALID_ENVS = ("dev", "test", "prod")

ENV_DESCRIPTIONS = {
    "dev":  "Sviluppo   — Docker PostgreSQL locale, porta 5433 (non persistente)",
    "test": "Test       — Docker PostgreSQL locale, porta 5432 (persistente)",
    "prod": "Produzione — PostgreSQL su NAS in LAN,  porta 5432 (persistente)",
}


# ──────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _banner(text: str, char: str = "─", width: int = 62) -> None:
    print(f"\n  {char * width}")
    print(f"  {text}")
    print(f"  {char * width}")


def _pick_env_interactive() -> str:
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         BOOTDB — Selezione ambiente target                   ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    for i, env in enumerate(VALID_ENVS, 1):
        print(f"║  [{i}] {ENV_DESCRIPTIONS[env]:<57}║")
    print("╚══════════════════════════════════════════════════════════════╝")
    while True:
        raw = input("\n  Scegli (1/2/3) oppure digita 'dev'/'test'/'prod': ").strip().lower()
        if raw in VALID_ENVS:
            return raw
        if raw in ("1", "2", "3"):
            return VALID_ENVS[int(raw) - 1]
        print(f"  ✗ Valore non valido. Ammessi: {', '.join(VALID_ENVS)} oppure 1/2/3.")


def _parse_args() -> tuple[str | None, bool]:
    """Ritorna (env_or_None, skip_seed)."""
    parser = argparse.ArgumentParser(
        description="Bootstrap del database + seed per l'ambiente selezionato.",
    )
    parser.add_argument(
        "--env",
        choices=VALID_ENVS,
        metavar="{dev|test|prod}",
        help="Ambiente target: dev, test oppure prod.",
    )
    parser.add_argument(
        "--skip-seed",
        action="store_true",
        default=False,
        help="Salta il seed dei dati iniziali dopo la creazione delle tabelle.",
    )
    args, _ = parser.parse_known_args()
    return args.env, args.skip_seed


def _confirm_prod() -> bool:
    print("\n  ⚠️  Stai per operare sul database di PRODUZIONE (NAS in LAN).")
    print("     CREATE TABLE IF NOT EXISTS + seed dei dati di sistema.")
    answer = input("     Digita 'PROD' per confermare: ").strip()
    return answer == "PROD"


# ──────────────────────────────────────────────────────────────────────────────
# CORE
# ──────────────────────────────────────────────────────────────────────────────

def _load_env_file(target_env: str) -> str:
    """
    Imposta APP_ENV, ricarica core.config e legge DATABASE_URL dal .env.
    Ritorna la DATABASE_URL.
    """
    os.environ["APP_ENV"] = target_env

    # Forza reload di core.config per rieseguire load_environment()
    import backend.core.config as _cfg_module
    importlib.reload(_cfg_module)

    backend_dir = Path(__file__).resolve().parent
    env_file = backend_dir / f".env.{target_env}"

    if not env_file.is_file():
        print(f"\n  ✗ File '{env_file}' non trovato.")
        print("    Assicurati che esista e contenga DATABASE_URL.")
        sys.exit(1)

    from dotenv import dotenv_values
    env_vars = dotenv_values(env_file)
    database_url = env_vars.get("DATABASE_URL") or os.environ.get("DATABASE_URL")

    if not database_url:
        print(f"\n  ✗ DATABASE_URL non trovata in '{env_file.name}'.")
        sys.exit(1)

    return database_url


def _build_engine(database_url: str):
    """Costruisce un engine locale (non il singleton globale di core.database)."""
    from sqlalchemy import create_engine
    kwargs: dict = {"pool_pre_ping": True, "future": True}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, **kwargs)


def _import_all_models() -> None:
    """Importa tutti i modelli di dominio così che vengano registrati in Base.metadata."""
    import backend.domains.users.models           # noqa: F401
    import backend.domains.categories.models      # noqa: F401
    import backend.domains.tasks.models           # noqa: F401
    import backend.domains.events.models          # noqa: F401
    import backend.domains.planning.models        # noqa: F401
    import backend.domains.shopping.models        # noqa: F401
    import backend.domains.habits.models          # noqa: F401
    import backend.domains.countdowns.models      # noqa: F401
    import backend.domains.notifications.models   # noqa: F401
    import backend.domains.audit.models           # noqa: F401
    import backend.domains.config.models          # noqa: F401
    import backend.domains.monthly_entries.models # noqa: F401


# ──────────────────────────────────────────────────────────────────────────────
# STEP 1 — CREATE TABLES
# ──────────────────────────────────────────────────────────────────────────────

def _step_create_tables(local_engine) -> int:
    """Esegue create_all e ritorna il numero di tabelle registrate."""
    from backend.core.database import Base
    _import_all_models()

    Base.metadata.create_all(bind=local_engine)

    tables = sorted(Base.metadata.tables.keys())
    print(f"\n  ✔  Tabelle create/verificate: {len(tables)}")
    for t in tables:
        print(f"      - {t}")
    return len(tables)


# ──────────────────────────────────────────────────────────────────────────────
# STEP 2 — SEED
# ──────────────────────────────────────────────────────────────────────────────

def _step_seed(local_engine) -> None:
    """
    Lancia seed_database() di SEEDDB.py iniettando il SessionLocal
    costruito sull'engine locale — senza toccare il singleton globale.
    """
    from sqlalchemy.orm import sessionmaker
    LocalSession = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=local_engine,
        future=True,
    )

    # Import diretto della funzione di seed
    from backend.SEEDDB import seed_database
    seed_database(session_factory=LocalSession)


# ──────────────────────────────────────────────────────────────────────────────
# ORCHESTRATORE PRINCIPALE
# ──────────────────────────────────────────────────────────────────────────────

def bootstrap_db(target_env: str, skip_seed: bool = False) -> None:
    _banner(f"BOOTDB — ambiente: {target_env.upper()}", char="═")

    # 1. Carica il .env corretto e ottieni DATABASE_URL
    database_url = _load_env_file(target_env)
    print(f"\n  ✔  Ambiente : {target_env.upper()}")
    print(f"  ✔  DB target: {database_url}")

    # 2. Engine locale isolato
    local_engine = _build_engine(database_url)

    try:
        # ── FASE 1: Creazione tabelle ──────────────────────────────────────
        _banner("FASE 1 / 2 — Creazione tabelle")
        _step_create_tables(local_engine)

        # ── FASE 2: Seed dati iniziali ─────────────────────────────────────
        if skip_seed:
            print("\n  ⏭   --skip-seed attivo: seed saltato.\n")
        else:
            _banner("FASE 2 / 2 — Seed dati iniziali")
            _step_seed(local_engine)

    finally:
        local_engine.dispose()

    _banner(f"✅  Bootstrap completato per ambiente '{target_env}'.", char="═")


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    chosen_env, skip_seed = _parse_args()

    if chosen_env is None:
        chosen_env = _pick_env_interactive()

    if chosen_env == "prod" and not _confirm_prod():
        print("\n  Operazione annullata.\n")
        sys.exit(0)

    bootstrap_db(chosen_env, skip_seed=skip_seed)