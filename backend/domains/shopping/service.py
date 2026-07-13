"""Service del dominio Shopping — regole di business per gruppi, liste, prodotti, articoli, fornitori e inventario."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.domains.shopping import repository as repo
from backend.domains.shopping.models.catalog import ShoppingProduct, ShoppingSupplier
from backend.domains.shopping.models.groups import ShoppingGroup, ShoppingGroupMember
from backend.domains.shopping.models.inventory import InventoryBatch
from backend.domains.shopping.models.lists import ShoppingList, ShoppingListItem
from backend.domains.shopping.schemas.catalog import ShoppingSupplierCreate, ShoppingSupplierUpdate
from backend.domains.shopping.schemas.config import ShoppingConfigBundle
from backend.domains.shopping.schemas.groups import (
    ShoppingGroupCreate,
    ShoppingGroupMemberCreate,
    ShoppingGroupMemberInvite,
    ShoppingGroupMemberRoleUpdate,
    ShoppingGroupUpdate,
)
from backend.domains.shopping.schemas.inventory import InventoryBatchCreate, InventoryBatchUpdate
from backend.domains.shopping.schemas.lists import (
    ShoppingListCreate,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingListUpdate,
)
from backend.domains.users.models import User


_LIST_NOT_FOUND = "Lista non trovata o non accessibile"
_ITEM_NOT_FOUND = "Articolo non trovato o non accessibile"
_GROUP_NOT_FOUND = "Gruppo non trovato o non accessibile"
_MEMBER_NOT_FOUND = "Membro non trovato nel gruppo"
_USER_NOT_FOUND = "Utente non trovato"
_ROLE_NOT_FOUND = "Ruolo non valido"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _today() -> date:
    return date.today()


def _normalize_name(value: str) -> str:
    return repo.normalize_name(value)


# ------------------------------------------------------------------ Groups
def list_groups(db: Session, current_user: User) -> List[ShoppingGroup]:
    return repo.list_groups(db, current_user.id)


def create_group(
    db: Session,
    current_user: User,
    group_in: ShoppingGroupCreate,
) -> ShoppingGroup:
    default_status_id = repo.active_group_status_id(db)
    if default_status_id is None:
        raise HTTPException(status_code=500, detail="ConfigCode group_status.active mancante")

    now = _now()
    db_group = ShoppingGroup(
        owner_id=current_user.id,
        name=group_in.name,
        description=group_in.description,
        status_id=group_in.status_id or default_status_id,
        created_at=now,
        updated_at=now,
    )
    return repo.create_group(db, db_group)


def update_group(
    db: Session,
    current_user: User,
    group_id: int,
    group_in: ShoppingGroupUpdate,
) -> ShoppingGroup:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)

    for field, value in group_in.model_dump(exclude_unset=True).items():
        setattr(db_group, field, value)
    db_group.updated_at = _now()

    return repo.update_group(db, db_group)


def delete_group(db: Session, current_user: User, group_id: int) -> None:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)
    repo.delete_group(db, db_group)


# ------------------------------------------------------------------ Group Members
def list_members(db: Session, current_user: User, group_id: int) -> List[ShoppingGroupMember]:
    group = repo.get_group_accessible(db, group_id, current_user.id)
    if not group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)
    return repo.list_members(db, group_id)


def add_member(
    db: Session,
    current_user: User,
    group_id: int,
    member_in: ShoppingGroupMemberCreate,
) -> ShoppingGroupMember:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)

    existing = repo.get_member(db, group_id, member_in.user_id)
    if existing:
        raise HTTPException(status_code=400, detail="L'utente è già membro del gruppo.")

    now = _now()
    db_member = ShoppingGroupMember(
        group_id=group_id,
        user_id=member_in.user_id,
        role_id=member_in.role_id,
        added_by_user_id=current_user.id,
        created_at=now,
        updated_at=now,
    )
    return repo.add_member(db, db_member)


def invite_member(
    db: Session,
    current_user: User,
    group_id: int,
    invite_in: ShoppingGroupMemberInvite,
) -> ShoppingGroupMember:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)

    target_user = repo.find_user_by_username_or_email(db, invite_in.username, invite_in.email)
    if not target_user:
        raise HTTPException(status_code=404, detail=_USER_NOT_FOUND)

    existing = repo.get_member(db, group_id, target_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="L'utente è già membro del gruppo.")

    role_id = repo.resolve_role_id(db, invite_in.role_code)
    if role_id is None:
        raise HTTPException(status_code=400, detail=_ROLE_NOT_FOUND)

    now = _now()
    db_member = ShoppingGroupMember(
        group_id=group_id,
        user_id=target_user.id,
        role_id=role_id,
        added_by_user_id=current_user.id,
        created_at=now,
        updated_at=now,
    )
    return repo.add_member(db, db_member)


def update_member_role(
    db: Session,
    current_user: User,
    group_id: int,
    user_id: int,
    role_in: ShoppingGroupMemberRoleUpdate,
) -> ShoppingGroupMember:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)

    db_member = repo.get_member(db, group_id, user_id)
    if not db_member:
        raise HTTPException(status_code=404, detail=_MEMBER_NOT_FOUND)

    role_id = repo.resolve_role_id(db, role_in.role_code)
    if role_id is None:
        raise HTTPException(status_code=400, detail=_ROLE_NOT_FOUND)

    db_member.role_id = role_id
    db_member.updated_at = _now()
    return repo.update_member(db, db_member)


def remove_member(db: Session, current_user: User, group_id: int, user_id: int) -> None:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)

    db_member = repo.get_member(db, group_id, user_id)
    if not db_member:
        raise HTTPException(status_code=404, detail=_MEMBER_NOT_FOUND)

    if db_member.user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Non puoi rimuovere te stesso. Trasferisci la proprietà o elimina il gruppo.",
        )

    repo.remove_member(db, db_member)


# ------------------------------------------------------------------ Lists
def list_lists(db: Session, current_user: User) -> List[ShoppingList]:
    return repo.list_lists(db, current_user.id)


def create_list(db: Session, current_user: User, list_in: ShoppingListCreate) -> ShoppingList:
    default_status_id = repo.active_list_status_id(db)
    if default_status_id is None:
        raise HTTPException(status_code=500, detail="ConfigCode list_status.active mancante")

    now = _now()
    db_list = ShoppingList(
        owner_id=current_user.id,
        group_id=list_in.group_id,
        visibility_id=list_in.visibility_id,
        status_id=list_in.status_id or default_status_id,
        name=list_in.name,
        description=list_in.description,
        created_at=now,
        updated_at=now,
    )
    repo.add(db, db_list)
    repo.commit(db)
    repo.refresh(db, db_list)
    return db_list


def update_list(
    db: Session,
    current_user: User,
    list_id: int,
    list_in: ShoppingListUpdate,
) -> ShoppingList:
    db_list = repo.get_list_owned(db, list_id, current_user.id)
    if not db_list:
        raise HTTPException(status_code=404, detail=_LIST_NOT_FOUND)

    for field, value in list_in.model_dump(exclude_unset=True).items():
        setattr(db_list, field, value)
    db_list.updated_at = _now()

    repo.commit(db)
    repo.refresh(db, db_list)
    return db_list


def delete_list(db: Session, current_user: User, list_id: int) -> None:
    db_list = repo.get_list_owned(db, list_id, current_user.id)
    if not db_list:
        raise HTTPException(status_code=404, detail=_LIST_NOT_FOUND)
    repo.delete(db, db_list)


# ------------------------------------------------------------------ Items
def list_items(
    db: Session,
    current_user: User,
    is_purchased: Optional[bool] = None,
    shopping_list_id: Optional[int] = None,
) -> List[ShoppingListItem]:
    return repo.list_items(db, current_user.id, shopping_list_id, is_purchased)


def create_item(
    db: Session,
    current_user: User,
    item_in: ShoppingListItemCreate,
) -> ShoppingListItem:
    db_list = repo.get_list_accessible(db, item_in.shopping_list_id, current_user.id)
    if not db_list:
        raise HTTPException(status_code=404, detail=_LIST_NOT_FOUND)

    normalized_name = _normalize_name(item_in.product_name)
    existing_open = repo.get_open_item_by_list_and_name(db, db_list.id, normalized_name)
    if existing_open:
        raise HTTPException(
            status_code=409,
            detail="Esiste già un articolo aperto con questo prodotto nella lista.",
        )

    db_product = repo.get_or_create_product_by_name(db, normalized_name, current_user.id)
    now = _now()

    db_item = ShoppingListItem(
        shopping_list_id=db_list.id,
        product_id=db_product.id,
        name_normalized=normalized_name,
        quantity=item_in.quantity,
        unit_id=item_in.unit_id,
        notes=item_in.notes,
        is_purchased=False,
        created_at=now,
        updated_at=now,
        created_by_user_id=current_user.id,
        updated_by_user_id=current_user.id,
    )
    repo.add(db, db_item)
    repo.commit(db)
    repo.refresh(db, db_item)
    return db_item


def update_item(
    db: Session,
    current_user: User,
    item_id: int,
    item_in: ShoppingListItemUpdate,
) -> ShoppingListItem:
    db_item = repo.get_item_accessible(db, item_id, current_user.id)
    if not db_item:
        raise HTTPException(status_code=404, detail=_ITEM_NOT_FOUND)

    update_data = item_in.model_dump(exclude_unset=True)

    if "product_name" in update_data and update_data["product_name"] is not None:
        normalized_name = _normalize_name(update_data["product_name"])

        existing_open = repo.get_open_item_by_list_and_name(
            db,
            db_item.shopping_list_id,
            normalized_name,
        )
        if existing_open and existing_open.id != db_item.id:
            raise HTTPException(
                status_code=409,
                detail="Esiste già un articolo aperto con questo prodotto nella lista.",
            )

        db_product = repo.get_or_create_product_by_name(db, normalized_name, current_user.id)
        db_item.product_id = db_product.id
        db_item.name_normalized = normalized_name
        update_data.pop("product_name")

    for field, value in update_data.items():
        setattr(db_item, field, value)

    db_item.updated_at = _now()
    db_item.updated_by_user_id = current_user.id

    repo.commit(db)
    repo.refresh(db, db_item)
    return db_item


def delete_item(db: Session, current_user: User, item_id: int) -> None:
    db_item = repo.get_item_accessible(db, item_id, current_user.id)
    if not db_item:
        raise HTTPException(status_code=404, detail=_ITEM_NOT_FOUND)
    repo.delete(db, db_item)


# ------------------------------------------------------------------ Suppliers
def list_suppliers(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
    limit: int = 20,
) -> List[ShoppingSupplier]:
    if search:
        return repo.search_suppliers(db, search=search, limit=limit)
    suppliers = repo.list_suppliers(db)
    return suppliers[:limit]


def create_supplier(
    db: Session,
    current_user: User,
    supplier_in: ShoppingSupplierCreate,
) -> ShoppingSupplier:
    if repo.find_supplier_by_name(db, supplier_in.name):
        raise HTTPException(status_code=400, detail="Esiste già un fornitore con questo nome.")

    default_status_id = repo.active_supplier_status_id(db)
    if default_status_id is None:
        raise HTTPException(status_code=500, detail="ConfigCode supplier_status.active mancante")

    now = _now()
    db_supplier = ShoppingSupplier(
        name=supplier_in.name,
        name_normalized=_normalize_name(supplier_in.name),
        status_id=supplier_in.status_id or default_status_id,
        created_by_user_id=current_user.id,
        updated_by_user_id=current_user.id,
        created_at=now,
        updated_at=now,
    )
    repo.add(db, db_supplier)
    repo.commit(db)
    repo.refresh(db, db_supplier)
    return db_supplier


def update_supplier(
    db: Session,
    current_user: User,
    supplier_id: int,
    supplier_in: ShoppingSupplierUpdate,
) -> ShoppingSupplier:
    db_supplier = repo.get_supplier(db, supplier_id)
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Fornitore non trovato")

    update_data = supplier_in.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"]:
        existing = repo.find_supplier_by_name(db, update_data["name"])
        if existing and existing.id != supplier_id:
            raise HTTPException(status_code=400, detail="Esiste già un fornitore con questo nome.")
        update_data["name_normalized"] = _normalize_name(update_data["name"])

    for field, value in update_data.items():
        setattr(db_supplier, field, value)

    db_supplier.updated_at = _now()
    db_supplier.updated_by_user_id = current_user.id

    repo.commit(db)
    repo.refresh(db, db_supplier)
    return db_supplier


def delete_supplier(db: Session, current_user: User, supplier_id: int) -> None:
    db_supplier = repo.get_supplier(db, supplier_id)
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Fornitore non trovato")

    if repo.supplier_has_batches(db, supplier_id):
        raise HTTPException(
            status_code=400,
            detail="Impossibile eliminare il fornitore: ha acquisti/lotti associati.",
        )
    repo.delete(db, db_supplier)


# ------------------------------------------------------------------ Inventory Batches
def add_inventory_batch(
    db: Session,
    current_user: User,
    item_id: int,
    batch_in: InventoryBatchCreate,
) -> InventoryBatch:
    db_item = repo.get_item_accessible(db, item_id, current_user.id)
    if not db_item:
        raise HTTPException(status_code=404, detail=_ITEM_NOT_FOUND)

    if batch_in.product_id != db_item.product_id:
        raise HTTPException(
            status_code=400,
            detail="Il product_id del lotto non corrisponde al prodotto dell'articolo di lista.",
        )

    if batch_in.supplier_id is not None and not repo.get_supplier(db, batch_in.supplier_id):
        raise HTTPException(status_code=404, detail="Fornitore non trovato")

    purchased_by_user_id = batch_in.purchased_by_user_id or current_user.id
    today = _today()

    db_batch = InventoryBatch(
        list_item_id=item_id,
        product_id=db_item.product_id,
        supplier_id=batch_in.supplier_id,
        purchase_date=batch_in.purchase_date,
        expiration_date=batch_in.expiration_date,
        quantity_purchased=batch_in.quantity_purchased,
        purchase_price=batch_in.purchase_price,
        is_on_sale=batch_in.is_on_sale,
        purchased_by_user_id=purchased_by_user_id,
        created_by_user_id=current_user.id,
        updated_by_user_id=None,
        created_at=today,
        updated_at=today,
    )
    repo.add(db, db_batch)

    db_item.is_purchased = True
    db_item.updated_at = _now()
    db_item.updated_by_user_id = current_user.id

    repo.commit(db)
    repo.refresh(db, db_batch)
    return db_batch


def update_inventory_batch(
    db: Session,
    current_user: User,
    batch_id: int,
    batch_in: InventoryBatchUpdate,
) -> InventoryBatch:
    db_batch = repo.get_batch(db, batch_id, current_user.id)
    if not db_batch:
        raise HTTPException(status_code=404, detail="Lotto/Acquisto non trovato")

    update_data = batch_in.model_dump(exclude_unset=True)

    if "supplier_id" in update_data and update_data["supplier_id"] is not None:
        if not repo.get_supplier(db, update_data["supplier_id"]):
            raise HTTPException(status_code=404, detail="Nuovo fornitore non trovato")

    if "product_id" in update_data and update_data["product_id"] is not None:
        if update_data["product_id"] != db_batch.product_id:
            raise HTTPException(
                status_code=400,
                detail="Il product_id del lotto non può essere modificato.",
            )

    if "list_item_id" in update_data and update_data["list_item_id"] is not None:
        if update_data["list_item_id"] != db_batch.list_item_id:
            raise HTTPException(
                status_code=400,
                detail="Il list_item_id del lotto non può essere modificato.",
            )

    for field, value in update_data.items():
        setattr(db_batch, field, value)

    db_batch.updated_at = _today()
    db_batch.updated_by_user_id = current_user.id

    repo.commit(db)
    repo.refresh(db, db_batch)
    return db_batch


def delete_inventory_batch(db: Session, current_user: User, batch_id: int) -> None:
    db_batch = repo.get_batch(db, batch_id, current_user.id)
    if not db_batch:
        raise HTTPException(status_code=404, detail="Lotto/Acquisto non trovato")

    db_batch.deleted_at = _today()
    db_batch.deleted_by_user_id = current_user.id
    db_batch.updated_at = _today()
    db_batch.updated_by_user_id = current_user.id

    repo.commit(db)

    if db_batch.list_item_id is not None and not repo.item_has_active_batches(db, db_batch.list_item_id):
        db_item = repo.get_item(db, db_batch.list_item_id)
        if db_item:
            db_item.is_purchased = False
            db_item.updated_at = _now()
            db_item.updated_by_user_id = current_user.id
            repo.commit(db)


# ------------------------------------------------------------------ Products
def list_products(
    db: Session,
    search: Optional[str] = None,
    limit: int = 20,
) -> List[ShoppingProduct]:
    return repo.list_products(db, search=search, limit=limit)


def get_product(
    db: Session,
    current_user: User,
    product_id: int,
) -> ShoppingProduct:
    db_product = repo.get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    return db_product


# ------------------------------------------------------------------ Config
def get_config_bundle(db: Session) -> ShoppingConfigBundle:
    return ShoppingConfigBundle(
        unitOptions=repo.get_config_options(db, "shopping_unit"),
        currencyOptions=repo.get_config_options(db, "currency"),
        offerFlagOptions=repo.get_config_options(db, "offer_flag"),
        visibilityOptions=repo.get_config_options(db, "list_visibility"),
        listStatusOptions=repo.get_config_options(db, "list_status"),
        groupStatusOptions=repo.get_config_options(db, "group_status"),
        groupRoleOptions=repo.get_config_options(db, "shopping_group_role"),
        supplierStatusOptions=repo.get_config_options(db, "supplier_status"),
    )