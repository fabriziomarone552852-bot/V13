"""
SEEDDB.py — inserimento dati iniziali.

Uso:
    python -m backend.SEEDDB --env dev
    python -m backend.SEEDDB --env test
    python -m backend.SEEDDB --env prod
    python -m backend.SEEDDB             # menu interattivo
"""
from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from dotenv import dotenv_values
from sqlalchemy import or_, text

from backend.core.env import BACKEND_DIR
from backend.core.database import build_engine, build_session_factory
from backend.core.models import import_all_models
from backend.core.deps import get_password_hash
from backend.domains.categories.models import UserCategory
from backend.domains.config import Config, ConfigCode
from backend.domains.monthly_entries.models import MonthlyFeeling
from backend.domains.shopping.models import ShoppingSupplier
from backend.domains.users.models import User


VALID_ENVS = ("dev", "test", "prod")


def _parse_args() -> str | None:
    parser = argparse.ArgumentParser(
        description="Seed dei dati iniziali per l'ambiente selezionato.",
    )
    parser.add_argument(
        "--env",
        choices=VALID_ENVS,
        metavar="{dev|test|prod}",
        help="Ambiente target: dev, test oppure prod.",
    )
    args, _ = parser.parse_known_args()
    return args.env


def _pick_env_interactive() -> str:
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         SEEDDB — Selezione ambiente target                  ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  [1] dev                                                   ║")
    print("║  [2] test                                                  ║")
    print("║  [3] prod                                                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    while True:
        raw = input("\n  Scegli (1/2/3) oppure digita 'dev'/'test'/'prod': ").strip().lower()
        if raw in VALID_ENVS:
            return raw
        if raw in ("1", "2", "3"):
            return VALID_ENVS[int(raw) - 1]
        print(f"  ✗ Valore non valido. Ammessi: {', '.join(VALID_ENVS)} oppure 1/2/3.")


def _confirm_prod() -> bool:
    print("\n  ⚠️  Stai per eseguire il seed sul database di PRODUZIONE.")
    answer = input("     Digita 'PROD' per confermare: ").strip()
    return answer == "PROD"


def _load_env_values(target_env: str) -> dict[str, str]:
    env_file = BACKEND_DIR / f".env.{target_env}"

    if not env_file.is_file():
        print(f"\n  ✗ File '{env_file}' non trovato.")
        sys.exit(1)

    env_values = {
        key: value
        for key, value in dotenv_values(env_file).items()
        if value is not None
    }

    database_url = str(env_values.get("DATABASE_URL", "")).strip()
    if not database_url:
        print(f"\n  ✗ DATABASE_URL non trovata in '{env_file.name}'.")
        sys.exit(1)

    return env_values


def _get_default_max_subtask_depth(env_values: dict[str, str]) -> int:
    raw = env_values.get("DEFAULT_MAX_SUBTASK_DEPTH", "10")
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        print(f"\n  ✗ DEFAULT_MAX_SUBTASK_DEPTH non valido: {raw!r}")
        sys.exit(1)


def _get_default_users(default_max_subtask_depth: int) -> list[dict]:
    return [
        {
            "id": 1,
            "username": "amedeo",
            "email": "amedeo@sinasce.lol",
            "password": "amedeo",
            "is_superuser": True,
            "must_change_password": True,
            "max_subtask_depth_user": default_max_subtask_depth,
        },
        {
            "id": 2,
            "username": "marcello",
            "email": "marcello@sinasce.lol",
            "password": "marcello",
            "is_superuser": True,
            "must_change_password": True,
            "max_subtask_depth_user": default_max_subtask_depth,
        },
        {
            "id": 3,
            "username": "signore",
            "email": "signore@sinasce.lol",
            "password": "signore",
            "is_superuser": False,
            "must_change_password": True,
            "max_subtask_depth_user": default_max_subtask_depth,
        },
        {
            "id": 4,
            "username": "signori",
            "email": "signori@sinasce.lol",
            "password": "signori",
            "is_superuser": False,
            "must_change_password": True,
            "max_subtask_depth_user": default_max_subtask_depth,
        },
    ]


DEFAULT_USER_CATEGORIES = [
    {"category_name": "Lavoro", "colore": "#68EEB4", "genre": 3},
    {"category_name": "Famiglia", "colore": "#68EEB4", "genre": 3},
    {"category_name": "Salute", "colore": "#68EEB4", "genre": 3},
    {"category_name": "Studio", "colore": "#68EEB4", "genre": 3},
    {"category_name": "Gioia", "colore": "#68EEB4", "genre": 4},
    {"category_name": "Tristezza", "colore": "#68EEB4", "genre": 4},
    {"category_name": "Rabbia", "colore": "#68EEB4", "genre": 4},
    {"category_name": "Disgusto", "colore": "#68EEB4", "genre": 4},
    {"category_name": "Paura", "colore": "#68EEB4", "genre": 4},
]

DEFAULT_MONTHLY_FEELINGS = [
    {"feel_name": "Gioia"},
    {"feel_name": "Tristezza"},
    {"feel_name": "Rabbia"},
    {"feel_name": "Disgusto"},
    {"feel_name": "Paura"},
    {"feel_name": "Famiglia"},
    {"feel_name": "Coppia"},
    {"feel_name": "Salute"},
    {"feel_name": "Mente"},
    {"feel_name": "Amici"},
    {"feel_name": "Finanze"},
    {"feel_name": "Divertimento"},
    {"feel_name": "Lavoro"},
]

DEFAULT_CONFIG_CODES = [
    {"code_type": "currency", "code_value": "EUR", "code_name": "Euro", "description": "Euro", "active": True, "sort_order": 1},
    {"code_type": "group_status", "code_value": "active", "code_name": "Active", "description": "Gruppo attivo", "active": True},
    {"code_type": "group_status", "code_value": "archived", "code_name": "Archived", "description": "Gruppo archiviato", "active": True},
    {"code_type": "item_status", "code_value": "active", "code_name": "Active", "description": "Item attivo", "active": True},
    {"code_type": "item_status", "code_value": "purchased", "code_name": "Purchased", "description": "Item acquistato", "active": True},
    {"code_type": "list_status", "code_value": "active", "code_name": "Active", "description": "Lista attiva", "active": True},
    {"code_type": "list_status", "code_value": "closed", "code_name": "Closed", "description": "Lista chiusa", "active": True},
    {"code_type": "list_visibility", "code_value": "group", "code_name": "Group", "description": "Lista di gruppo", "active": True},
    {"code_type": "list_visibility", "code_value": "private", "code_name": "Private", "description": "Lista privata", "active": True},
    {"code_type": "notification_type", "code_value": "generic", "code_name": "Generic", "description": "Notifica generica", "active": True},
    {"code_type": "offer_flag", "code_value": "no", "code_name": "No offer", "description": "Prezzo non in offerta", "active": True, "sort_order": 1},
    {"code_type": "offer_flag", "code_value": "yes", "code_name": "Offer", "description": "Prezzo in offerta", "active": True, "sort_order": 2},
    {"code_type": "shared_activity_action_type", "code_value": "create", "code_name": "Create", "description": "Creazione", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "update", "code_name": "Update", "description": "Aggiornamento", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "delete", "code_name": "Delete", "description": "Eliminazione logica o fisica", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "restore", "code_name": "Restore", "description": "Ripristino", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "archive", "code_name": "Archive", "description": "Archiviazione", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "close", "code_name": "Close", "description": "Chiusura", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "reopen", "code_name": "Reopen", "description": "Riapertura", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "complete", "code_name": "Complete", "description": "Completamento", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "uncomplete", "code_name": "Uncomplete", "description": "Annullamento completamento", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "add_member", "code_name": "Add Member", "description": "Aggiunta membro", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "remove_member", "code_name": "Remove Member", "description": "Rimozione membro", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "update_role", "code_name": "Update Role", "description": "Aggiornamento ruolo", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "share", "code_name": "Share", "description": "Condivisione", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "unshare", "code_name": "Unshare", "description": "Revoca condivisione", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "login", "code_name": "Login", "description": "Accesso utente", "active": True},
    {"code_type": "shared_activity_action_type", "code_value": "logout", "code_name": "Logout", "description": "Uscita utente", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "shopping_group", "code_name": "Shopping Group", "description": "Entità gruppo shopping", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "shopping_group_member", "code_name": "Shopping Group Member", "description": "Entità membro gruppo shopping", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "shopping_list", "code_name": "Shopping List", "description": "Entità lista shopping", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "shopping_list_item", "code_name": "Shopping List Item", "description": "Entità elemento lista shopping", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "shopping_supplier", "code_name": "Shopping Supplier", "description": "Entità fornitore shopping", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "shopping_price", "code_name": "Shopping Price", "description": "Entità prezzo shopping", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "task", "code_name": "Task", "description": "Entità task", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "event", "code_name": "Event", "description": "Entità evento", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "countdown", "code_name": "Countdown", "description": "Entità countdown", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "habit", "code_name": "Habit", "description": "Entità habit", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "habit_period", "code_name": "Habit Period", "description": "Periodo habit", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "habit_log", "code_name": "Habit Log", "description": "Log giornaliero habit", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "daily_entry", "code_name": "Daily Entry", "description": "Voce giornaliera", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "category", "code_name": "Category", "description": "Categoria condivisa", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "user", "code_name": "User", "description": "Utente", "active": True},
    {"code_type": "shared_activity_entity_type", "code_value": "config", "code_name": "Config", "description": "Configurazione applicativa", "active": True},
    {"code_type": "shared_activity_module", "code_value": "shopping", "code_name": "Shopping", "description": "Modulo shopping", "active": True},
    {"code_type": "shared_activity_module", "code_value": "tasks", "code_name": "Tasks", "description": "Modulo task condivisi", "active": True},
    {"code_type": "shared_activity_module", "code_value": "events", "code_name": "Events", "description": "Modulo eventi condivisi", "active": True},
    {"code_type": "shared_activity_module", "code_value": "countdowns", "code_name": "Countdowns", "description": "Modulo countdown condivisi", "active": True},
    {"code_type": "shared_activity_module", "code_value": "habits", "code_name": "Habits", "description": "Modulo habit condivise", "active": True},
    {"code_type": "shared_activity_module", "code_value": "daily", "code_name": "Daily", "description": "Modulo daily entries condivise", "active": True},
    {"code_type": "shared_activity_module", "code_value": "sharing", "code_name": "Sharing", "description": "Operazioni trasversali di condivisione", "active": True},
    {"code_type": "shared_activity_module", "code_value": "system", "code_name": "System", "description": "Operazioni di sistema", "active": True},
    {"code_type": "shopping_group_role", "code_value": "owner", "code_name": "Owner", "description": "Proprietario del gruppo shopping", "active": True, "sort_order": 1},
    {"code_type": "shopping_group_role", "code_value": "admin", "code_name": "Admin", "description": "Amministratore del gruppo shopping", "active": True, "sort_order": 2},
    {"code_type": "shopping_group_role", "code_value": "editor", "code_name": "Editor", "description": "Può modificare liste e acquisti aperti", "active": True, "sort_order": 3},
    {"code_type": "shopping_group_role", "code_value": "reader", "code_name": "Reader", "description": "Può solo visualizzare", "active": True, "sort_order": 4},
    {"code_type": "shopping_group_status", "code_value": "active", "code_name": "Active", "description": "Stato attivo per gruppi shopping", "active": True},
    {"code_type": "shopping_group_status", "code_value": "inactive", "code_name": "Inactive", "description": "Stato inattivo per gruppi shopping", "active": True},
    {"code_type": "shopping_item_status", "code_value": "open", "code_name": "Open", "description": "Elemento aperto", "active": True, "sort_order": 1},
    {"code_type": "shopping_item_status", "code_value": "purchased", "code_name": "Purchased", "description": "Elemento acquistato", "active": True, "sort_order": 2},
    {"code_type": "shopping_item_status", "code_value": "archived", "code_name": "Archived", "description": "Elemento archiviato", "active": True, "sort_order": 3},
    {"code_type": "shopping_list_status", "code_value": "active", "code_name": "Active", "description": "Lista attiva", "active": True, "sort_order": 1},
    {"code_type": "shopping_list_status", "code_value": "closed", "code_name": "Closed", "description": "Lista chiusa", "active": True, "sort_order": 2},
    {"code_type": "shopping_list_status", "code_value": "archived", "code_name": "Archived", "description": "Lista archiviata", "active": True, "sort_order": 3},
    {"code_type": "shopping_list_visibility", "code_value": "private", "code_name": "Private", "description": "Lista privata", "active": True, "sort_order": 1},
    {"code_type": "shopping_list_visibility", "code_value": "group", "code_name": "Group", "description": "Lista condivisa con un gruppo", "active": True, "sort_order": 2},
    {"code_type": "shopping_unit", "code_value": "conf", "code_name": "CONF", "description": "Confezione", "active": True, "sort_order": 10},
    {"code_type": "shopping_unit", "code_value": "paq", "code_name": "PAQ", "description": "Pacco", "active": True, "sort_order": 20},
    {"code_type": "shopping_unit", "code_value": "bt", "code_name": "BT", "description": "Bottiglia", "active": True, "sort_order": 30},
    {"code_type": "shopping_unit", "code_value": "bar", "code_name": "BAR", "description": "Barattolo", "active": True, "sort_order": 40},
    {"code_type": "shopping_unit", "code_value": "g", "code_name": "G", "description": "Grammi", "active": True, "sort_order": 50},
    {"code_type": "shopping_unit", "code_value": "hg", "code_name": "HG", "description": "Ettogrammi", "active": True, "sort_order": 60},
    {"code_type": "shopping_unit", "code_value": "kg", "code_name": "KG", "description": "Chilogrammi", "active": True, "sort_order": 70},
    {"code_type": "shopping_unit", "code_value": "lt", "code_name": "LT", "description": "Litri", "active": True, "sort_order": 80},
    {"code_type": "shopping_unit", "code_value": "pz", "code_name": "PZ", "description": "Pezzi", "active": True, "sort_order": 90},
    {"code_type": "shopping_unit", "code_value": "rot", "code_name": "ROT", "description": "Rotolo", "active": True, "sort_order": 100},
    {"code_type": "shopping_unit", "code_value": "scat", "code_name": "SCAT", "description": "Scatola", "active": True, "sort_order": 110},
    {"code_type": "shopping_unit", "code_value": "tub", "code_name": "TUB", "description": "Tubetto", "active": True, "sort_order": 120},
    {"code_type": "shopping_unit", "code_value": "bust", "code_name": "BUST", "description": "Busta", "active": True, "sort_order": 130},
    {"code_type": "shopping_unit", "code_value": "fl", "code_name": "FL", "description": "Flacone", "active": True, "sort_order": 140},
    {"code_type": "shopping_unit", "code_value": "vas", "code_name": "VAS", "description": "Vaschetta", "active": True, "sort_order": 150},
    {"code_type": "shopping_unit", "code_value": "brik", "code_name": "BRIK", "description": "Brik", "active": True, "sort_order": 160},
    {"code_type": "shopping_unit", "code_value": "mazz", "code_name": "MAZZ", "description": "Mazzo", "active": True, "sort_order": 170},
    {"code_type": "shopping_unit", "code_value": "fett", "code_name": "FETT", "description": "Fette", "active": True, "sort_order": 180},
    {"code_type": "shopping_unit", "code_value": "m", "code_name": "M", "description": "Metri", "active": True, "sort_order": 190},
    {"code_type": "shopping_unit", "code_value": "latt", "code_name": "LATT", "description": "Lattina", "active": True, "sort_order": 200},
    {"code_type": "shopping_unit", "code_value": "ret", "code_name": "RET", "description": "Retina", "active": True, "sort_order": 210},
    {"code_type": "shopping_unit", "code_value": "paqf", "code_name": "PAQF", "description": "Pacco famiglia", "active": True, "sort_order": 220},
    {"code_type": "shopping_unit", "code_value": "ric", "code_name": "RIC", "description": "Ricarica", "active": True, "sort_order": 230},
    {"code_type": "shopping_unit", "code_value": "cm", "code_name": "CM", "description": "Centimetri", "active": True, "sort_order": 240},
    {"code_type": "shopping_unit", "code_value": "grapp", "code_name": "GRAPP", "description": "Grappolo", "active": True, "sort_order": 250},
    {"code_type": "shopping_unit", "code_value": "spic", "code_name": "SPIC", "description": "Spicchi", "active": True, "sort_order": 260},
    {"code_type": "shopping_unit", "code_value": "kit", "code_name": "KIT", "description": "Kit", "active": True, "sort_order": 270},
    {"code_type": "shopping_unit", "code_value": "mm", "code_name": "MM", "description": "Millimetri", "active": True, "sort_order": 280},
    {"code_type": "shopping_unit", "code_value": "cl", "code_name": "CL", "description": "Centilitri", "active": True, "sort_order": 290},
    {"code_type": "shopping_unit", "code_value": "ml", "code_name": "ML", "description": "Millilitri", "active": True, "sort_order": 300},
    {"code_type": "supplier_status", "code_value": "active", "code_name": "Active", "description": "Fornitore attivo", "active": True},
    {"code_type": "supplier_status", "code_value": "inactive", "code_name": "Inactive", "description": "Fornitore inattivo", "active": True},
]

DEFAULT_SUPPLIERS = ["Coop", "Carni e Affini", "MD", "Lidl", "Eurospin", "Famila"]


def _build_password_hash(password: str) -> str:
    return get_password_hash(password)


def _find_existing_user(db, payload: dict) -> User | None:
    normalized_username = payload["username"].strip().lower()
    normalized_email = payload["email"].strip().lower()

    user = db.query(User).filter(User.id == payload["id"]).first()
    if user is not None:
        return user

    return (
        db.query(User)
        .filter(
            or_(
                User.username == normalized_username,
                User.email == normalized_email,
            )
        )
        .first()
    )


def _insert_default_user_if_missing(db, payload: dict) -> User:
    existing = _find_existing_user(db, payload)
    if existing is not None:
        return existing

    user = User(
        id=payload["id"],
        username=payload["username"].strip().lower(),
        email=payload["email"].strip().lower(),
        password_hash=_build_password_hash(payload["password"]),
        max_subtask_depth_user=payload["max_subtask_depth_user"],
        is_superuser=payload.get("is_superuser", False),
        must_change_password=payload.get("must_change_password", True),
    )
    db.add(user)
    db.flush()
    return user


def _seed_default_users(db, default_users: Sequence[dict]) -> list[User]:
    users: list[User] = []
    for payload in default_users:
        users.append(_insert_default_user_if_missing(db, payload))
    db.flush()
    return users


def _seed_default_user_categories_for_user(db, user_id: int) -> int:
    inserted = 0

    for item in DEFAULT_USER_CATEGORIES:
        normalized_category_name = item["category_name"].strip().lower()

        existing = (
            db.query(UserCategory)
            .filter(
                UserCategory.user_id == user_id,
                UserCategory.category_name == normalized_category_name,
            )
            .first()
        )
        if existing is not None:
            continue

        db.add(
            UserCategory(
                user_id=user_id,
                category_name=normalized_category_name,
                colore=item["colore"],
                genre=item["genre"],
            )
        )
        db.flush()
        inserted += 1

    return inserted


def _seed_default_user_categories(db, users: Sequence[User]) -> dict[int, int]:
    inserted_by_user: dict[int, int] = {}
    for user in users:
        inserted_by_user[user.id] = _seed_default_user_categories_for_user(db, user.id)
    return inserted_by_user


def _sync_users_id_sequence(db) -> None:
    db.execute(
        text(
            """
            SELECT setval(
                pg_get_serial_sequence('users', 'id'),
                COALESCE((SELECT MAX(id) FROM users), 1),
                (SELECT MAX(id) IS NOT NULL FROM users)
            )
            """
        )
    )
    db.flush()


def _ensure_config(db, default_max_subtask_depth: int) -> bool:
    existing = db.query(Config).filter(Config.key == "max_subtask_depth").first()
    if existing is not None:
        return False

    db.add(
        Config(
            key="max_subtask_depth",
            value=str(default_max_subtask_depth),
            descrizione="Numero massimo di livelli consentiti per la nidificazione dei sottotask.",
        )
    )
    db.flush()
    return True


def _seed_config_codes(db) -> dict[tuple[str, str], int]:
    code_ids: dict[tuple[str, str], int] = {}

    for code in DEFAULT_CONFIG_CODES:
        payload = {"sort_order": None, **code}

        existing = (
            db.query(ConfigCode)
            .filter(
                ConfigCode.code_type == payload["code_type"],
                ConfigCode.code_value == payload["code_value"],
            )
            .first()
        )

        if existing is not None:
            code_ids[(existing.code_type, existing.code_value)] = existing.id
            continue

        obj = ConfigCode(**payload)
        db.add(obj)
        db.flush()
        code_ids[(obj.code_type, obj.code_value)] = obj.id

    return code_ids


def _get_code_id(code_ids: dict[tuple[str, str], int], code_type: str, code_value: str) -> int:
    key = (code_type, code_value)
    if key not in code_ids:
        raise RuntimeError(f"ConfigCode mancante: {code_type}.{code_value}")
    return code_ids[key]


def _seed_default_suppliers(db, created_by_user_id: int, supplier_status_id: int) -> int:
    inserted = 0

    for supplier_name in DEFAULT_SUPPLIERS:
        normalized = supplier_name.strip().lower()

        existing = (
            db.query(ShoppingSupplier)
            .filter(ShoppingSupplier.name_normalized == normalized)
            .first()
        )
        if existing is not None:
            continue

        db.add(
            ShoppingSupplier(
                name=supplier_name,
                name_normalized=normalized,
                status_id=supplier_status_id,
                created_by_user_id=created_by_user_id,
            )
        )
        db.flush()
        inserted += 1

    return inserted


def _seed_monthly_feelings(db) -> int:
    inserted = 0

    for feeling in DEFAULT_MONTHLY_FEELINGS:
        feel_name = feeling["feel_name"].strip()

        existing = (
            db.query(MonthlyFeeling)
            .filter(MonthlyFeeling.feel_name == feel_name)
            .first()
        )
        if existing is not None:
            continue

        db.add(MonthlyFeeling(feel_name=feel_name))
        db.flush()
        inserted += 1

    return inserted


def seed_database(
    session_factory,
    env_values: dict[str, str],
) -> None:
    """
    session_factory: factory SQLAlchemy esplicita per il DB target.
    env_values: valori letti deterministicamente da .env.<env>.
    """
    default_max_subtask_depth = _get_default_max_subtask_depth(env_values)
    default_users = _get_default_users(default_max_subtask_depth)

    print("=" * 70)
    print("AVVIO SEED DATI INIZIALI (Smart Agenda API)")
    print("=" * 70)

    import_all_models()

    db = session_factory()
    try:
        print("[1/5] Verifica o creazione utenti di default...")
        seed_users = _seed_default_users(db, default_users)
        db.commit()
        _sync_users_id_sequence(db)
        db.commit()

        for user in seed_users:
            db.refresh(user)
            print(
                f"-> Utente pronto: id={user.id}, "
                f"username={user.username}, email={user.email}, "
                f"is_superuser={user.is_superuser}, "
                f"must_change_password={user.must_change_password}"
            )

        seed_owner = seed_users[0]

        print("[2/5] Seed user_categories di default per ogni utente seed...")
        inserted_user_categories = _seed_default_user_categories(db, seed_users)
        db.commit()
        for user in seed_users:
            print(
                f"-> User categories inserite per {user.username}: "
                f"{inserted_user_categories.get(user.id, 0)}."
            )

        print("[3/5] Seed configurazioni amministrative di base...")
        inserted_config = _ensure_config(db, default_max_subtask_depth)
        db.commit()
        print(f"-> Config base inserita: {1 if inserted_config else 0}.")

        print("[4/5] Seed ConfigCode globali...")
        code_ids = _seed_config_codes(db)
        db.commit()
        print(f"-> ConfigCode disponibili/allineati: {len(code_ids)}.")

        print("[5/5] Seed fornitori e monthly feelings di default...")
        supplier_status_id = _get_code_id(code_ids, "supplier_status", "active")
        inserted_suppliers = _seed_default_suppliers(
            db=db,
            created_by_user_id=seed_owner.id,
            supplier_status_id=supplier_status_id,
        )
        inserted_monthly_feelings = _seed_monthly_feelings(db)
        db.commit()
        print(
            f"-> Fornitori inseriti: {inserted_suppliers}. "
            f"Monthly feelings inseriti: {inserted_monthly_feelings}."
        )

    except Exception as exc:
        db.rollback()
        print(f"ERROR durante il seed dei dati iniziali: {exc}")
        sys.exit(1)
    finally:
        db.close()

    print("=" * 70)
    print("SEED COMPLETATO CON SUCCESSO! Sistema pronto.")
    print("=" * 70)


if __name__ == "__main__":
    chosen_env = _parse_args()

    if chosen_env is None:
        chosen_env = _pick_env_interactive()

    if chosen_env == "prod" and not _confirm_prod():
        print("\n  Operazione annullata.\n")
        sys.exit(0)

    env_values = _load_env_values(chosen_env)
    database_url = env_values["DATABASE_URL"].strip()
    engine = build_engine(database_url)
    session_factory = build_session_factory(engine)

    try:
        seed_database(session_factory=session_factory, env_values=env_values)
    finally:
        engine.dispose()