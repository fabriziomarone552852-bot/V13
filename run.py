"""
Avvio del backend dalla ROOT del repository.

L'ambiente viene scelto tramite la variabile APP_ENV (dev|test|prod),
gestita da backend/core/config.py. Esempi:

    APP_ENV=dev  python run.py
    APP_ENV=test python run.py
    APP_ENV=prod python run.py

Non è più necessario aggiungere 'backend' al PYTHONPATH: tutti gli import
del backend usano il package 'backend.*' e funzionano eseguendo dalla root.
"""
import os
import uvicorn

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    reload = os.environ.get("RELOAD", "false").lower() in ("1", "true", "yes")
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload)
