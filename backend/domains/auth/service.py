"""Service del dominio Auth — registrazione, login e refresh token."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.core.deps import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_refresh_token,
)
from backend.domains.auth.schemas import Token, TokenPairResponse
from backend.domains.users import repository as users_repo
from backend.domains.users import schemas as users_schemas
from backend.domains.users.models import User
from backend.domains.categories.models import UserCategory


DEFAULT_USER_CATEGORY_TEMPLATES = [
    {"category_name": "Lavoro", "colore": "#68EEB4", "genre": 3},
    {"category_name": "Famiglia", "colore": "#68EEB4", "genre": 3},
    {"category_name": "Salute", "colore": "#68EEB4", "genre": 3},
    {"category_name": "Studio", "colore": "#68EEB4", "genre": 3},
]


def _seed_default_user_categories_for_user(db: Session, user_id: int) -> None:
    """
    Inserisce le quattro categorie di default per il nuovo utente.
    La funzione è idempotente: se richiamata più volte non duplica le categorie.
    """
    for template in DEFAULT_USER_CATEGORY_TEMPLATES:
        existing = (
            db.query(UserCategory)
            .filter(
                UserCategory.user_id == user_id,
                UserCategory.category_name == template["category_name"],
            )
            .first()
        )

        if existing:
            existing.colore = template["colore"]
            existing.genre = template["genre"]
            continue

        obj = UserCategory(
            user_id=user_id,
            category_name=template["category_name"],
            colore=template["colore"],
            genre=template["genre"],
        )
        db.add(obj)

    db.commit()


def register(db: Session, user_in: users_schemas.UserCreate) -> User:
    username = user_in.username.strip().lower()
    email = str(user_in.email).strip().lower()

    deleted_user = users_repo.get_deleted_by_username_or_email(db, username, email)
    if deleted_user:
        raise HTTPException(
            status_code=400,
            detail=(
                "Username o Email associati a un account disattivato. "
                "Contattare un amministratore di sistema per la riattivazione."
            ),
        )

    if users_repo.username_or_email_exists(db, username, email):
        raise HTTPException(status_code=400, detail="Username o Email già registrati")

    user = users_repo.create_user(
        db,
        username,
        email,
        get_password_hash(user_in.password),
    )

    _seed_default_user_categories_for_user(db, user.id)
    db.refresh(user)

    return user


def login(db: Session, username: str, password: str) -> TokenPairResponse:
    username_normalized = username.strip().lower()
    user = users_repo.get_by_username(db, username_normalized)

    if not user or user.deleted_at is not None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password errati",
        )

    return TokenPairResponse(
        access_token=create_access_token(data={"sub": user.username}),
        refresh_token=create_refresh_token(data={"sub": user.username}),
        token_type="bearer",
        must_change_password=user.must_change_password,
        is_superuser=user.is_superuser,
    )


def refresh(db: Session, refresh_token: str) -> Token:
    username = verify_refresh_token(refresh_token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token non valido o scaduto",
        )

    username_normalized = username.strip().lower()
    user = users_repo.get_by_username(db, username_normalized)

    if not user or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato o non attivo",
        )

    return Token(
        access_token=create_access_token(data={"sub": user.username}),
        token_type="bearer",
        must_change_password=user.must_change_password,
        is_superuser=user.is_superuser,
    )