"""Repository del dominio Shopping — solo accesso ai dati."""
from typing import List, Optional

from sqlalchemy.orm import Session, selectinload

from backend.domains.config.models import ConfigCode
from backend.domains.shopping.models import (
    ShoppingList,
    ShoppingListItem,
    ShoppingPrice,
    ShoppingSupplier,
)


def _list_loaders():
    return (
        selectinload(ShoppingList.items)
        .selectinload(ShoppingListItem.prices)
        .selectinload(ShoppingPrice.supplier),
        selectinload(ShoppingList.items).selectinload(ShoppingListItem.created_by_user),
        selectinload(ShoppingList.items).selectinload(ShoppingListItem.updated_by_user),
    )


def _item_loaders():
    return (
        selectinload(ShoppingListItem.prices).selectinload(ShoppingPrice.supplier),
        selectinload(ShoppingListItem.created_by_user),
        selectinload(ShoppingListItem.updated_by_user),
    )


# --- Lists ---
def list_lists(db: Session, owner_id: int) -> List[ShoppingList]:
    return (
        db.query(ShoppingList)
        .options(*_list_loaders())
        .filter(ShoppingList.owner_id == owner_id)
        .order_by(ShoppingList.created_at.asc())
        .all()
    )


def get_list_owned(db: Session, list_id: int, owner_id: int) -> Optional[ShoppingList]:
    return (
        db.query(ShoppingList)
        .filter(ShoppingList.id == list_id, ShoppingList.owner_id == owner_id)
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
        .join(ShoppingList)
        .options(*_item_loaders())
        .filter(ShoppingList.owner_id == owner_id)
    )
    if shopping_list_id is not None:
        query = query.filter(ShoppingListItem.shopping_list_id == shopping_list_id)
    if is_purchased is not None:
        query = query.filter(ShoppingListItem.is_purchased == is_purchased)
    return query.order_by(ShoppingListItem.created_at.asc()).all()


def get_item_owned(db: Session, item_id: int, owner_id: int) -> Optional[ShoppingListItem]:
    return (
        db.query(ShoppingListItem)
        .join(ShoppingList)
        .filter(ShoppingListItem.id == item_id, ShoppingList.owner_id == owner_id)
        .first()
    )


# --- Suppliers ---
def list_suppliers(db: Session) -> List[ShoppingSupplier]:
    return db.query(ShoppingSupplier).order_by(ShoppingSupplier.name.asc()).all()


def get_supplier(db: Session, supplier_id: int) -> Optional[ShoppingSupplier]:
    return db.query(ShoppingSupplier).filter(ShoppingSupplier.id == supplier_id).first()


def find_supplier_by_name(db: Session, name: str) -> Optional[ShoppingSupplier]:
    return db.query(ShoppingSupplier).filter(ShoppingSupplier.name.ilike(name)).first()


def supplier_has_prices(db: Session, supplier_id: int) -> bool:
    return (
        db.query(ShoppingPrice).filter(ShoppingPrice.supplier_id == supplier_id).first()
        is not None
    )


def active_supplier_status_id(db: Session) -> Optional[int]:
    return (
        db.query(ConfigCode.id)
        .filter(
            ConfigCode.code_type == "supplier_status",
            ConfigCode.code_value == "active",
        )
        .scalar()
    )


# --- Prices ---
def get_price(db: Session, price_id: int) -> Optional[ShoppingPrice]:
    return db.query(ShoppingPrice).filter(ShoppingPrice.id == price_id).first()


# --- Generici ---
def add(db: Session, obj) -> None:
    db.add(obj)


def commit(db: Session) -> None:
    db.commit()


def refresh(db: Session, obj) -> None:
    db.refresh(obj)


def delete(db: Session, obj) -> None:
    db.delete(obj)
    db.commit()
