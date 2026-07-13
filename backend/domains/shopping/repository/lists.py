"""
Repository per ShoppingList e ShoppingListItem.
Solo accesso ai dati, nessuna regola di business.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from backend.domains.shopping.models import ShoppingList, ShoppingListItem
from .common import soft_delete_criteria, list_loaders, item_loaders


# --- Lists ---

def list_lists(db: Session, owner_id: int) -> List[ShoppingList]:
    return (
        db.query(ShoppingList)
        .options(*list_loaders(), *soft_delete_criteria())
        .filter(
            ShoppingList.owner_id == owner_id,
            ShoppingList.deleted_at.is_(None),
        )
        .order_by(ShoppingList.created_at.asc())
        .all()
    )


def get_list_owned(db: Session, list_id: int, owner_id: int) -> Optional[ShoppingList]:
    return (
        db.query(ShoppingList)
        .options(*list_loaders(), *soft_delete_criteria())
        .filter(
            ShoppingList.id == list_id,
            ShoppingList.owner_id == owner_id,
            ShoppingList.deleted_at.is_(None),
        )
        .first()
    )


# --- Items ---

def list_items(
    db: Session,
    owner_id: int,
    shopping_list_id: Optional[int] = None,
    is_purchased: Optional[bool] = None,
) -> List[ShoppingListItem]:
    query = (
        db.query(ShoppingListItem)
        .join(ShoppingList, ShoppingList.id == ShoppingListItem.shopping_list_id)
        .options(*item_loaders(), *soft_delete_criteria())
        .filter(
            ShoppingList.owner_id == owner_id,
            ShoppingList.deleted_at.is_(None),
            ShoppingListItem.deleted_at.is_(None),
        )
    )

    if shopping_list_id is not None:
        query = query.filter(ShoppingListItem.shopping_list_id == shopping_list_id)

    if is_purchased is not None:
        query = query.filter(ShoppingListItem.is_purchased == is_purchased)

    return query.order_by(ShoppingListItem.created_at.asc()).all()


def get_item_owned(db: Session, item_id: int, owner_id: int) -> Optional[ShoppingListItem]:
    return (
        db.query(ShoppingListItem)
        .join(ShoppingList, ShoppingList.id == ShoppingListItem.shopping_list_id)
        .options(*item_loaders(), *soft_delete_criteria())
        .filter(
            ShoppingListItem.id == item_id,
            ShoppingList.owner_id == owner_id,
            ShoppingList.deleted_at.is_(None),
            ShoppingListItem.deleted_at.is_(None),
        )
        .first()
    )