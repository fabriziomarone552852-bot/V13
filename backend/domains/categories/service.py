"""
Service del dominio Categories.
Gestisce categorie completamente user-scoped.
"""
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.domains.categories import repository as repo
from backend.domains.categories import schemas
from backend.domains.categories.models import UserCategory
from backend.domains.users.models import User


def _to_response(user_category: UserCategory) -> schemas.CategoryResponse:
    return schemas.CategoryResponse(
        id=user_category.id,
        category_name=user_category.category_name,
        colore=user_category.colore,
        user_id=user_category.user_id,
        genre=user_category.genre,
    )


def create_category(
    db: Session,
    current_user: User,
    data: schemas.CategoryCreate,
) -> schemas.CategoryResponse:
    existing = repo.get_user_category_by_name(db, data.name, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Hai già questa categoria salvata.")

    user_category = UserCategory(
        user_id=current_user.id,
        category_name=data.name,
        colore=data.colore,
        genre=data.genre,
    )
    saved_user_category = repo.add_user_category(db, user_category)
    return _to_response(saved_user_category)


def list_categories(
    db: Session,
    current_user: User,
    genre: Optional[int] = None,
) -> List[schemas.CategoryResponse]:
    user_categories = repo.list_for_user(db, current_user.id, genre)
    return [_to_response(user_category) for user_category in user_categories]


def get_category(
    db: Session,
    current_user: User,
    category_id: int,
) -> schemas.CategoryResponse:
    user_category = repo.get_user_category(db, category_id, current_user.id)
    if not user_category:
        raise HTTPException(status_code=404, detail="Categoria non trovata")

    return _to_response(user_category)


def update_category(
    db: Session,
    current_user: User,
    category_id: int,
    data: schemas.CategoryUpdate,
) -> schemas.CategoryResponse:
    user_category = repo.get_user_category(db, category_id, current_user.id)
    if not user_category:
        raise HTTPException(status_code=404, detail="Categoria non trovata")

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != user_category.category_name:
        existing = repo.get_user_category_by_name(db, update_data["name"], current_user.id)
        if existing and existing.id != user_category.id:
            raise HTTPException(
                status_code=400,
                detail="Hai già una categoria con questo nome.",
            )
        user_category.category_name = update_data["name"]

    if "colore" in update_data:
        user_category.colore = update_data["colore"]

    if "genre" in update_data:
        user_category.genre = update_data["genre"]

    saved_user_category = repo.save_user_category(db, user_category)
    return _to_response(saved_user_category)


def delete_category(
    db: Session,
    current_user: User,
    category_id: int,
) -> None:
    user_category = repo.get_user_category(db, category_id, current_user.id)
    if not user_category:
        raise HTTPException(status_code=404, detail="Categoria non trovata")

    repo.delete_user_category(db, user_category)