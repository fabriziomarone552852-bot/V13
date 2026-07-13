Modello: Frontend Reattivo e Responsabile (R&R)

Responsabilità condivisa: Il Backend rimane la fonte di verità (Source of Truth) e l'unico validatore delle regole di business critiche (es. permessi, calcoli finanziari, persistenza).

Frontend Smart: Il Frontend ha il compito di gestire in autonomia la logica di interazione (es. validazioni di form lato client, gestione ottimizzata dello stato, manipolazione di dati non critici per la visualizzazione).

Obiettivo Performance: È ammessa e incoraggiata la logica nel frontend per eliminare chiamate API ridondanti e ridurre la latenza percepita, a patto che il backend esegua una validazione finale "a prova di bomba".

Sicurezza: La validazione lato client è per l'esperienza utente (UX); la validazione lato server è per la sicurezza. Entrambe sono obbligatorie.

Coerenza TypeScript: Ogni logica spostata nel frontend deve essere fortemente tipizzata per garantire che il contratto tra backend e frontend rimanga integro.