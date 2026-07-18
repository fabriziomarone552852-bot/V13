from backend.core.database import Base, engine, SessionLocal  # IMPORT OBBLIGATORI: registrano tutte le tabelle nel metadata

import backend.domains.users.models
import backend.domains.categories.models
import backend.domains.tasks.models
import backend.domains.events.models
import backend.domains.planning.models
import backend.domains.shopping.models
import backend.domains.habits.models
import backend.domains.countdowns.models
import backend.domains.notifications.models
import backend.domains.audit.models
import backend.domains.config.models
import backend.domains.monthly_entries.models  # <<< AGGIUNTO

def bootstrap_db() -> None:
    Base.metadata.create_all(bind=engine)

    # opzionale ma utile debug
    print(f"Tabelle registrate: {len(Base.metadata.tables)}")
    for name in sorted(Base.metadata.tables.keys()):
        print(f" - {name}")

    # seed integrato
    # from backend.seed import seed_database
    # seed_database()


if __name__ == "__main__":
    bootstrap_db()