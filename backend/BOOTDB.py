#!/usr/bin/env python
"""
BOOTDB.py — Bootstrap multi-ambiente: crea le tabelle e semina i dati iniziali.

Uso:
    python -m backend.BOOTDB --env dev
    python -m backend.BOOTDB --env test
    python -m backend.BOOTDB --env prod
    python -m backend.BOOTDB         # menu interattivo

Flags opzionali:
    --skip-seed     Salta il seed dopo la creazione delle tabelle.
"""
from __future__ import annotations

import argparse
import sys

from dotenv import dotenv_values
from sqlalchemy import text

from backend.core.env import BACKEND_DIR
from backend.core.database import build_engine, build_session_factory
from backend.core.database import Base


VALID_ENVS = ("dev", "test", "prod")

ENV_DESCRIPTIONS = {
    "dev": "Sviluppo   — Docker PostgreSQL locale, porta 5433 (non persistente)",
    "test": "Test       — Docker PostgreSQL locale, porta 5432 (persistente)",
    "prod": "Produzione — PostgreSQL su NAS in LAN, porta 5432 (persistente)",
}


def _banner(text: str, char: str = "─", width: int = 62) -> None:
    print(f"\n  {char * width}")
    print(f"  {text}")
    print(f"  {char * width}")


def _pick_env_interactive() -> str:
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         BOOTDB — Selezione ambiente target                  ║")
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


def _load_env_values(target_env: str) -> dict[str, str]:
    """
    Legge il file .env.<env> in modo deterministico, senza dipendere
    dall'environment del processo.
    """
    env_file = BACKEND_DIR / f".env.{target_env}"

    if not env_file.is_file():
        print(f"\n  ✗ File '{env_file}' non trovato.")
        print("    Assicurati che esista e contenga DATABASE_URL.")
        sys.exit(1)

    env_vars = {
        key: value
        for key, value in dotenv_values(env_file).items()
        if value is not None
    }

    if "DATABASE_URL" not in env_vars or not str(env_vars["DATABASE_URL"]).strip():
        print(f"\n  ✗ DATABASE_URL non trovata in '{env_file.name}'.")
        sys.exit(1)

    return env_vars


def _import_all_models() -> None:
    from backend.core.models import import_all_models
    import_all_models()


def _print_db_fingerprint(local_engine) -> None:
    with local_engine.connect() as conn:
        row = conn.execute(
            text(
                """
                select
                    current_database(),
                    current_user,
                    inet_server_addr(),
                    inet_server_port(),
                    version()
                """
            )
        ).fetchone()

    if row is None:
        print("\n  ✗ Impossibile determinare il fingerprint del database.")
        sys.exit(1)

    print(
        "\n  [DB CHECK] "
        f"database={row[0]} "
        f"user={row[1]} "
        f"host={row[2]} "
        f"port={row[3]}"
    )
    print(f"  [DB CHECK] version={row[4]}")


def _step_create_tables(local_engine) -> int:
    _import_all_models()
    Base.metadata.create_all(bind=local_engine)

    tables = sorted(Base.metadata.tables.keys())
    print(f"\n  ✔  Tabelle create/verificate: {len(tables)}")
    for table_name in tables:
        print(f"      - {table_name}")
    return len(tables)


def _step_seed(local_engine, env_values: dict[str, str]) -> None:
    local_session_factory = build_session_factory(local_engine)

    from backend.SEEDDB import seed_database

    seed_database(
        session_factory=local_session_factory,
        env_values=env_values,
    )


def bootstrap_db(target_env: str, skip_seed: bool = False) -> None:
    _banner(f"BOOTDB — ambiente: {target_env.upper()}", char="═")

    env_values = _load_env_values(target_env)
    database_url = env_values["DATABASE_URL"].strip()

    print(f"\n  ✔  Ambiente : {target_env.upper()}")
    print(f"  ✔  DB target: {database_url}")

    local_engine = build_engine(database_url)

    try:
        _print_db_fingerprint(local_engine)

        _banner("FASE 1 / 2 — Creazione tabelle")
        _step_create_tables(local_engine)

        if skip_seed:
            print("\n  ⏭   --skip-seed attivo: seed saltato.\n")
        else:
            _banner("FASE 2 / 2 — Seed dati iniziali")
            _step_seed(local_engine, env_values)
    finally:
        local_engine.dispose()

    _banner(f"✅  Bootstrap completato per ambiente '{target_env}'.", char="═")


if __name__ == "__main__":
    chosen_env, skip_seed = _parse_args()

    if chosen_env is None:
        chosen_env = _pick_env_interactive()

    if chosen_env == "prod" and not _confirm_prod():
        print("\n  Operazione annullata.\n")
        sys.exit(0)

    bootstrap_db(chosen_env, skip_seed=skip_seed)