"""
DEPRECATO — non usare più.

Il cambio di ambiente NON avviene più copiando/scrivendo file .env (operazione
fragile e a rischio). Ora l'ambiente si seleziona SOLO in lettura tramite la
variabile d'ambiente APP_ENV.

Comandi:

    # Backend
    APP_ENV=dev  python run.py        # DB volatile  (Docker PostgreSQL locale)
    APP_ENV=test python run.py        # DB persistente (Docker PostgreSQL locale)
    APP_ENV=prod python run.py        # PostgreSQL su NAS in LAN

    # In alternativa, con uvicorn direttamente:
    APP_ENV=test uvicorn backend.main:app --reload

Su Windows (PowerShell):

    $env:APP_ENV="test"; python run.py

I file backend/.env.dev | .env.test | .env.prod restano statici e non vengono
mai modificati dal programma.
"""
import sys

_MESSAGGIO = __doc__


def main() -> int:
    print(_MESSAGGIO)
    print(
        "Questo script non modifica più alcun file. Imposta APP_ENV e avvia "
        "il backend con i comandi mostrati sopra."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
