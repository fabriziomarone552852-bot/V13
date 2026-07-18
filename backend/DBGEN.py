def bootstrap_db() -> None:
    # Svuota i metadati prima di iniziare a importare per evitare conflitti speculativi
    Base.metadata.clear() 
    
    imported_modules = _import_domain_models()
    # ... resto del codice invariato
	
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
        except ModuleNotFoundError as exc:
            if exc.name == models_module_name:
                continue
            raise

        models_file = Path(getattr(models_module, "__file__", ""))
        if not models_file.exists():
            continue

        # Se è un pacchetto (__init__.py), iteriamo i sottomoduli 
        # MA non aggiungiamo il pacchetto padre alla lista per evitare duplicati
        if models_file.name == "__init__.py":
            models_pkg_path = [str(models_file.parent)]
            for submodule_info in pkgutil.iter_modules(models_pkg_path):
                submodule_name = submodule_info.name
                if submodule_name.startswith("_"):
                    continue

                full_submodule_name = f"{models_module_name}.{submodule_name}"
                try:
                    importlib.import_module(full_submodule_name)
                    if full_submodule_name not in imported_modules:
                        imported_modules.append(full_submodule_name)
                except ModuleNotFoundError as exc:
                    if exc.name == full_submodule_name:
                        continue
                    raise
        else:
            # È un file models.py singolo, lo aggiungiamo direttamente
            if models_module_name not in imported_modules:
                imported_modules.append(models_module_name)

    return imported_modules