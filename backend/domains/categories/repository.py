"""
Repository del dominio Categories.
"""
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from backend.domains.categories.models import Category, UserCategory


def get_dict_category_by_name(db: Session, name: str) -> Optional[Category]:
    """Cerca una categoria nel dizionario globale."""
    return db.query(Category).filter(Category.name == name).first()


def create_dict_category(db: Session, name: str) -> Category:
    """Crea una nuova voce nel dizionario globale."""
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_user_category_by_dict_id(db: Session, category_id: int, user_id: int) -> Optional[UserCategory]:
    """Verifica se l'utente è già associato a questa categoria del dizionario."""
    return db.query(UserCategory).filter(
        UserCategory.category_id == category_id,
        UserCategory.user_id == user_id
    ).first()


def get_user_category(db: Session, user_category_id: int, user_id: int) -> Optional[UserCategory]:
    """Recupera il record ponte verificando la proprietà dell'utente."""
    return db.query(UserCategory).options(
        joinedload(UserCategory.category)
    ).filter(
        UserCategory.id == user_category_id,
        UserCategory.user_id == user_id
    ).first()


def list_for_user(db: Session, user_id: int, genre: Optional[int] = None) -> List[UserCategory]:
    """Elenca le categorie associate all'utente."""
    query = db.query(UserCategory).options(
        joinedload(UserCategory.category)
    ).filter(UserCategory.user_id == user_id)
    
    if genre is not None:
        query = query.filter(UserCategory.genre.in_([genre, 3]))
        
    query = query.join(UserCategory.category).order_by(Category.name.asc())
    return query.all()


def add_user_category(db: Session, user_category: UserCategory) -> UserCategory:
    db.add(user_category)
    db.commit()
    db.refresh(user_category)
    db.refresh(user_category, ["category"])
    return user_category


def save_user_category(db: Session, user_category: UserCategory) -> UserCategory:
    db.commit()
    db.refresh(user_category)
    return user_category


def delete_user_category(db: Session, user_category: UserCategory) -> None:
    db.delete(user_category)
    db.commit()


def count_links_for_category(db: Session, category_id: int) -> int:
    """Conta quanti utenti usano ancora questa categoria globale."""
    return db.query(UserCategory).filter(UserCategory.category_id == category_id).count()


def delete_dict_category(db: Session, category_id: int) -> None:
    """Rimuove un record dal dizionario globale."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        db.delete(category)
        db.commit()