import sys
from collections.abc import Sequence

from sqlalchemy import and_, or_, text
from backend.core import deps
from backend.core.database import SessionLocal
from backend.domains.categories.models import UserCategory
from backend.domains.config import Config, ConfigCode
from backend.domains.monthly_entries.models import MonthlyFeeling
from backend.domains.shopping.models import ShoppingSupplier
from backend.domains.users.models import User
from backend.settings import DEFAULT_MAX_SUBTASK_DEPTH


DEFAULT_USERS = [
    {
        "id": 1,
        "username": "amedeo",
        "email": "amedeo@sinasce.lol",
        "password": "amedeo",
        "is_superuser": True,
        "must_change_password": True,
        "max_subtask_depth_user": DEFAULT_MAX_SUBTASK_DEPTH,
    },
    {
        "id": 2,
        "username": "marcello",
        "email": "marcello@sinasce.lol",
        "password": "marcello",
        "is_superuser": True,
        "must_change_password": True,
        "max_subtask_depth_user": DEFAULT_MAX_SUBTASK_DEPTH,
    },
    {
        "id": 3,
        "username": "signore",
        "email": "signore@sinasce.lol",
        "password": "signore",
        "is_superuser": False,
        "must_change_password": True,
        "max_subtask_depth_user": DEFAULT_MAX_SUBTASK_DEPTH,
    },
    {
        "id": 4,
        "username": "signori",
        "email": "signori@sinasce.lol",
        "password": "signori",
        "is_superuser": False,
        "must_change_password": True,
        "max_subtask_depth_user": DEFAULT_MAX_SUBTASK_DEPTH,
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
    return deps.get_password_hash(password)


def _ensure_default_user(db, payload: dict) -> User:
    normalized_username = payload["username"].strip().lower()
    normalized_email = payload["email"].strip().lower()

    user = db.query(User).filter(User.id == payload["id"]).first()
    if user is None:
        user = db.query(User).filter(
            or_(
                User.username == normalized_username,
                User.email == normalized_email,
            )
        ).first()

    if user is None:
        user = User(
            id=payload["id"],
            username=normalized_username,
            email=normalized_email,
            password_hash=_build_password_hash(payload["password"]),
            max_subtask_depth_user=payload.get("max_subtask_depth_user", DEFAULT_MAX_SUBTASK_DEPTH),
            is_superuser=payload.get("is_superuser", False),
            must_change_password=payload.get("must_change_password", True),
        )
        db.add(user)
        db.flush()
        return user

    if user.id != payload["id"]:
        raise RuntimeError(
            f"Esiste già un utente con username/email={normalized_username}/{normalized_email} "
            f"ma con id diverso da {payload['id']}."
        )

    changed = False

    if user.username != normalized_username:
        user.username = normalized_username
        changed = True

    if user.email != normalized_email:
        user.email = normalized_email
        changed = True

    if not user.password_hash:
        user.password_hash = _build_password_hash(payload["password"])
        changed = True

    wanted_depth = payload.get("max_subtask_depth_user", DEFAULT_MAX_SUBTASK_DEPTH)
    if user.max_subtask_depth_user is None or user.max_subtask_depth_user < 1:
        user.max_subtask_depth_user = wanted_depth
        changed = True

    wanted_superuser = payload.get("is_superuser", False)
    if user.is_superuser != wanted_superuser:
        user.is_superuser = wanted_superuser
        changed = True

    wanted_mcp = payload.get("must_change_password", True)
    if user.must_change_password != wanted_mcp:
        user.must_change_password = wanted_mcp
        changed = True

    if changed:
        db.add(user)
        db.flush()

    return user


def _seed_default_users(db) -> list[User]:
    users: list[User] = []
    for payload in DEFAULT_USERS:
        user = _ensure_default_user(db, payload)
        users.append(user)
    db.flush()
    return users


def _seed_default_user_categories_for_user(db, user_id: int) -> int:
    inserted = 0

    for item in DEFAULT_USER_CATEGORIES:
        payload = {**item, "user_id": user_id}

        existing = (
            db.query(UserCategory)
            .filter(
                and_(
                    UserCategory.user_id == payload["user_id"],
                    UserCategory.category_name == payload["category_name"],
                )
            )
            .first()
        )

        if existing:
            updated = False

            if getattr(existing, "colore", None) != payload["colore"]:
                existing.colore = payload["colore"]
                updated = True

            if getattr(existing, "genre", None) != payload["genre"]:
                existing.genre = payload["genre"]
                updated = True

            if updated:
                db.add(existing)
                db.flush()

            continue

        db.add(UserCategory(**payload))
        inserted += 1

    if inserted:
        db.flush()

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


def _ensure_config(db) -> None:
    existing = db.query(Config).filter(Config.key == "max_subtask_depth").first()
    if existing is None:
        db.add(
            Config(
                key="max_subtask_depth",
                value=str(DEFAULT_MAX_SUBTASK_DEPTH),
                descrizione="Numero massimo di livelli consentiti per la nidificazione dei sottotask.",
            )
        )
        db.flush()


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

        if existing:
            updated = False

            if existing.code_name != payload["code_name"]:
                existing.code_name = payload["code_name"]
                updated = True

            if existing.description != payload["description"]:
                existing.description = payload["description"]
                updated = True

            if existing.active != payload["active"]:
                existing.active = payload["active"]
                updated = True

            if getattr(existing, "sort_order", None) != payload["sort_order"]:
                existing.sort_order = payload["sort_order"]
                updated = True

            if updated:
                db.add(existing)
                db.flush()

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

        if existing:
            updated = False

            if existing.name != supplier_name:
                existing.name = supplier_name
                updated = True

            if existing.status_id != supplier_status_id:
                existing.status_id = supplier_status_id
                updated = True

            if existing.created_by_user_id != created_by_user_id:
                existing.created_by_user_id = created_by_user_id
                updated = True

            if updated:
                db.add(existing)
                db.flush()

            continue

        db.add(
            ShoppingSupplier(
                name=supplier_name,
                name_normalized=normalized,
                status_id=supplier_status_id,
                created_by_user_id=created_by_user_id,
            )
        )
        inserted += 1

    return inserted


def _seed_monthly_feelings(db) -> int:
    inserted = 0

    for feeling in DEFAULT_MONTHLY_FEELINGS:
        feel_name = feeling["feel_name"].strip()
        existing = db.query(MonthlyFeeling).filter(MonthlyFeeling.feel_name == feel_name).first()
        if existing:
            continue
        db.add(MonthlyFeeling(feel_name=feel_name))
        inserted += 1

    if inserted:
        db.flush()

    return inserted


def _align_users_subtask_depth(db) -> int:
    users_without_depth = db.query(User).filter(
        or_(
            User.max_subtask_depth_user.is_(None),
            User.max_subtask_depth_user < 1,
        )
    ).all()

    for user in users_without_depth:
        user.max_subtask_depth_user = DEFAULT_MAX_SUBTASK_DEPTH
        db.add(user)

    if users_without_depth:
        db.flush()

    return len(users_without_depth)


def seed_database(session_factory=None) -> None:
    """
    session_factory: se fornito, viene usato al posto del SessionLocal globale.
    Permette a BOOTDB.py di iniettare un engine/session dedicati all'ambiente
    scelto senza toccare il singleton di core.database.
    """
    print("=" * 70)
    print("AVVIO SEED DATI INIZIALI (Smart Agenda API)")
    print("=" * 70)

    _SessionFactory = session_factory if session_factory is not None else SessionLocal

    db = _SessionFactory()
    try:
        print("[1/6] Verifica o creazione utenti di default...")
        seed_users = _seed_default_users(db)
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

        print("[2/6] Verifica user_categories di default per ogni utente seed...")
        inserted_user_categories = _seed_default_user_categories(db, seed_users)
        db.commit()
        for user in seed_users:
            print(
                f"-> User categories inserite/aggiornate per {user.username}: "
                f"{inserted_user_categories.get(user.id, 0)}."
            )

        print("[3/6] Verifica configurazioni amministrative...")
        _ensure_config(db)
        db.commit()
        print("-> Configurazioni amministrative verificate/inserite.")

        print("[4/6] Verifica ConfigCode globali...")
        code_ids = _seed_config_codes(db)
        db.commit()
        print(f"-> ConfigCode allineati: {len(code_ids)}.")

        print("[5/6] Verifica fornitori e monthly feelings di default...")
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

        print("[6/6] Riallineamento utenti esistenti...")
        aligned_users = _align_users_subtask_depth(db)
        db.commit()
        print(f"-> Utenti riallineati su max_subtask_depth_user: {aligned_users}.")

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
    seed_database()
