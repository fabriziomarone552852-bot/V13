"""
Service del dominio Categories.
Gestisce l'orchestrazione tra Dizionario e Ponte, inclusa la pulizia dei record orfani.
"""
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.domains.categories import repository as repo
from backend.domains.categories import schemas
from backend.domains.categories.models import UserCategory
from backend.domains.users.models import User


def _get_or_create_dict_category(db: Session, name: str) -> int:
    """Trova o crea la voce nel dizionario globale."""
    dict_cat = repo.get_dict_category_by_name(db, name)
    if not dict_cat:
        dict_cat = repo.create_dict_category(db, name)
    return dict_cat.id


def create_category(db: Session, current_user: User, data: schemas.CategoryCreate) -> schemas.CategoryResponse:
    # 1. Recupera o crea nel dizionario globale
    dict_cat_id = _get_or_create_dict_category(db, data.name)

    # 2. Verifica se l'utente ha già associata questa categoria
    if repo.get_user_category_by_dict_id(db, dict_cat_id, current_user.id):
        raise HTTPException(status_code=400, detail="Hai già questa categoria salvata.")

    # 3. Crea il collegamento ponte
    user_cat = UserCategory(
        user_id=current_user.id,
        category_id=dict_cat_id,
        colore=data.colore,
        genre=data.genre,
    )
    saved_user_cat = repo.add_user_category(db, user_cat)
    
    return schemas.CategoryResponse(
        id=saved_user_cat.id,
        category_id=saved_user_cat.category_id,
        name=saved_user_cat.category.name,
        colore=saved_user_cat.colore,
        user_id=saved_user_cat.user_id,
        genre=saved_user_cat.genre
    )


def list_categories(db: Session, current_user: User, genre: Optional[int] = None) -> List[schemas.CategoryResponse]:
    user_cats = repo.list_for_user(db, current_user.id, genre)
    
    response_list: List[schemas.CategoryResponse] = []
    for uc in user_cats:
        response_list.append(
            schemas.CategoryResponse(
                id=uc.id,
                category_id=uc.category_id,
                name=uc.category.name,
                colore=uc.colore,
                user_id=uc.user_id,
                genre=uc.genre
            )
        )
    return response_list


def get_category(db: Session, current_user: User, category_id: int) -> schemas.CategoryResponse:
    uc = repo.get_user_category(db, category_id, current_user.id)
    if not uc:
        raise HTTPException(status_code=404, detail="Categoria non trovata")
        
    return schemas.CategoryResponse(
        id=uc.id,
        category_id=uc.category_id,
        name=uc.category.name,
        colore=uc.colore,
        user_id=uc.user_id,
        genre=uc.genre
    )


def update_category(
    db: Session,
    current_user: User,
    category_id: int,  # ID della riga ponte
    data: schemas.CategoryUpdate,
) -> schemas.CategoryResponse:
    uc = repo.get_user_category(db, category_id, current_user.id)
    if not uc:
        raise HTTPException(status_code=404, detail="Categoria non trovata")

    update_data = data.model_dump(exclude_unset=True)
    old_dict_id = uc.category_id

    # Se l'utente sta rinominando la categoria
    if "name" in update_data and update_data["name"] != uc.category.name:
        new_dict_id = _get_or_create_dict_category(db, update_data["name"])
        
        # Verifica se l'utente non sia GIA' collegato alla nuova categoria
        if new_dict_id != uc.category_id and repo.get_user_category_by_dict_id(db, new_dict_id, current_user.id):
            raise HTTPException(status_code=400, detail="Hai già una categoria con questo nuovo nome.")
            
        uc.category_id = new_dict_id

    # Aggiorna preferenze utente
    if "colore" in update_data:
        uc.colore = update_data["colore"]
    if "genre" in update_data:
        uc.genre = update_data["genre"]

    saved_uc = repo.save_user_category(db, uc)

    # Se la categoria è cambiata, controlliamo se la vecchia riga del dizionario è rimasta orfana
    if "name" in update_data and old_dict_id != saved_uc.category_id:
        if repo.count_links_for_category(db, old_dict_id) == 0:
            repo.delete_dict_category(db, old_dict_id)

    return schemas.CategoryResponse(
        id=saved_uc.id,
        category_id=saved_uc.category_id,
        name=saved_uc.category.name,
        colore=saved_uc.colore,
        user_id=saved_uc.user_id,
        genre=saved_uc.genre
    )


def delete_category(db: Session, current_user: User, category_id: int) -> None:
    uc = repo.get_user_category(db, category_id, current_user.id)
    if not uc:
        raise HTTPException(status_code=404, detail="Categoria non trovata")
    
    dict_cat_id = uc.category_id
    
    # Rimuoviamo il link dell'utente (UserCategory)
    repo.delete_user_category(db, uc)
    
    # Garbage Collector: se nessun altro utente utilizza questa parola globale, eliminiamola!
    if repo.count_links_for_category(db, dict_cat_id) == 0:
        repo.delete_dict_category(db, dict_cat_id)