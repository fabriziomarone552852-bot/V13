"""
Common helpers per il repository Shopping.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import selectinload, with_loader_criteria

from backend.domains.shopping.models import (
    ShoppingGroup,
    ShoppingGroupMember,
    ShoppingList,
    ShoppingListItem,
    ShoppingProduct,
    ShoppingSupplier,
    InventoryBatch,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_name(value: str) -> str:
    return value.strip().lower()


def soft_delete_criteria():
    """
    Criteri globali per soft-delete automatico sulle relazioni.
    """
    return (
        with_loader_criteria(ShoppingGroup, ShoppingGroup.deleted_at.is_(None)),
        with_loader_criteria(ShoppingGroupMember, ShoppingGroupMember.removed_at.is_(None)),
        with_loader_criteria(ShoppingList, ShoppingList.deleted_at.is_(None)),
        with_loader_criteria(ShoppingListItem, ShoppingListItem.deleted_at.is_(None)),
        with_loader_criteria(ShoppingProduct, ShoppingProduct.deleted_at.is_(None)),
        with_loader_criteria(ShoppingSupplier, ShoppingSupplier.deleted_at.is_(None)),
        with_loader_criteria(InventoryBatch, InventoryBatch.deleted_at.is_(None)),
    )


def list_loaders():
    return (
        selectinload(ShoppingList.items).selectinload(ShoppingListItem.product),
        selectinload(ShoppingList.items).selectinload(ShoppingListItem.unit),
        selectinload(ShoppingList.items).selectinload(ShoppingListItem.created_by_user),
        selectinload(ShoppingList.items).selectinload(ShoppingListItem.updated_by_user),
        selectinload(ShoppingList.items)
        .selectinload(ShoppingListItem.inventory_batches)
        .selectinload(InventoryBatch.product),
        selectinload(ShoppingList.items)
        .selectinload(ShoppingListItem.inventory_batches)
        .selectinload(InventoryBatch.supplier),
        selectinload(ShoppingList.items)
        .selectinload(ShoppingListItem.inventory_batches)
        .selectinload(InventoryBatch.created_by_user),
        selectinload(ShoppingList.items)
        .selectinload(ShoppingListItem.inventory_batches)
        .selectinload(InventoryBatch.purchased_by_user),
    )


def item_loaders():
    return (
        selectinload(ShoppingListItem.product),
        selectinload(ShoppingListItem.unit),
        selectinload(ShoppingListItem.created_by_user),
        selectinload(ShoppingListItem.updated_by_user),
        selectinload(ShoppingListItem.inventory_batches).selectinload(InventoryBatch.product),
        selectinload(ShoppingListItem.inventory_batches).selectinload(InventoryBatch.supplier),
        selectinload(ShoppingListItem.inventory_batches).selectinload(InventoryBatch.created_by_user),
        selectinload(ShoppingListItem.inventory_batches).selectinload(InventoryBatch.purchased_by_user),
    )