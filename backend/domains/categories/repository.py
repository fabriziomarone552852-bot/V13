"""
Repository del dominio Categories.
Categorie completamente user-scoped.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.domains.categories.models import CategoryGenre, UserCategory


def get_user_category_by_name(
    db: Session,
    name: str,
    user_id: int,
) -> Optional[UserCategory]:
    """Recupera una categoria utente per nome normalizzato."""
    return (
        db.query(UserCategory)
        .filter(
            UserCategory.user_id == user_id,
            UserCategory.category_name == name,
        )
        .first()
    )


def get_user_category(
    db: Session,
    user_category_id: int,
    user_id: int,
) -> Optional[UserCategory]:
    """Recupera una categoria verificando la proprietà dell'utente."""
    return (
        db.query(UserCategory)
        .filter(
            UserCategory.id == user_category_id,
            UserCategory.user_id == user_id,
        )
        .first()
    )


def list_for_user(
    db: Session,
    user_id: int,
    genre: Optional[int] = None,
) -> List[UserCategory]:
    """Elenca le categorie dell'utente ordinate per nome."""
    query = db.query(UserCategory).filter(UserCategory.user_id == user_id)

    if genre is not None:
        query = query.filter(
            UserCategory.genre.in_([genre, CategoryGenre.COMMON])
        )

    return query.order_by(UserCategory.category_name.asc()).all()


def add_user_category(db: Session, user_category: UserCategory) -> UserCategory:
    """Aggiunge una nuova categoria utente."""
    db.add(user_category)
    db.commit()
    db.refresh(user_category)
    return user_category


def save_user_category(db: Session, user_category: UserCategory) -> UserCategory:
    """Salva modifiche a una categoria utente."""
    db.commit()
    db.refresh(user_category)
    return user_category


def delete_user_category(db: Session, user_category: UserCategory) -> None:
    """Elimina una categoria utente."""
    db.delete(user_category)
    db.commit()