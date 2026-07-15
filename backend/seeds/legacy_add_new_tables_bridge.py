"""
Bridge provider:
- riusa la logica legacy di add_new_tables.py (se presente)
- permette transizione graduale verso seed provider moderni
- deve essere idempotente lato legacy script
"""

import importlib
from typing import Callable, Optional


class LegacyAddNewTablesBridgeProvider:
    name = "legacy_add_new_tables_bridge"
    order = 100  # prima di domains_seed (1000), ma dopo eventuali seed fondamentali <100

    LEGACY_MODULES = [
        "backend.add_new_tables",
        "add_new_tables",  # fallback per compatibilità
    ]

    LEGACY_FUNCTIONS = [
        "seed",
        "populate_base_data",
        "add_new_tables",
        "run",
        "main",
    ]

    def _load_legacy_callable(self) -> Optional[Callable]:
        for module_name in self.LEGACY_MODULES:
            try:
                module = importlib.import_module(module_name)
            except Exception:
                continue

            for fn_name in self.LEGACY_FUNCTIONS:
                fn = getattr(module, fn_name, None)
                if callable(fn):
                    print(f"[legacy-bridge] trovata funzione legacy: {module_name}.{fn_name}")
                    return fn

        return None

    def run(self, session) -> None:
        fn = self._load_legacy_callable()
        if fn is None:
            print("[legacy-bridge] modulo/funzione legacy non trovati, skip.")
            return

        # Tentiamo prima con session (best practice), poi senza args.
        try:
            fn(session)
            print("[legacy-bridge] esecuzione legacy completata (con session).")
            return
        except TypeError:
            pass

        fn()
        print("[legacy-bridge] esecuzione legacy completata (senza session).")


provider = LegacyAddNewTablesBridgeProvider()