"""Router HTTP del dominio Shopping (prefix /shopping)."""
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core import deps
from backend.domains.shopping import schemas, service
from backend.domains.users.models import User

router = APIRouter(prefix="/shopping", tags=["shopping"])


# --------------------------------------------------------------- Lists
@router.get("/lists", response_model=List[schemas.ShoppingListResponse])
def list_shopping_lists(
    include_private: bool = True,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.list_lists(db, current_user)


@router.post("/lists", response_model=schemas.ShoppingListResponse, status_code=201)
def create_shopping_list(
    list_in: schemas.ShoppingListCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.create_list(db, current_user, list_in)


@router.patch("/lists/{list_id}", response_model=schemas.ShoppingListResponse)
def update_shopping_list(
    list_id: int,
    list_in: schemas.ShoppingListUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.update_list(db, current_user, list_id, list_in)


@router.delete("/lists/{list_id}", status_code=204)
def delete_shopping_list(
    list_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service.delete_list(db, current_user, list_id)


# --------------------------------------------------------------- Items
@router.get("/items", response_model=List[schemas.ShoppingListItemResponse])
def list_shopping_items(
    is_purchased: Optional[bool] = None,
    shopping_list_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.list_items(db, current_user, is_purchased, shopping_list_id)


@router.post("/items", response_model=schemas.ShoppingListItemResponse, status_code=201)
def create_shopping_item(
    item_in: schemas.ShoppingListItemCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.create_item(db, current_user, item_in)


@router.patch("/items/{item_id}", response_model=schemas.ShoppingListItemResponse)
def update_shopping_item(
    item_id: int,
    item_in: schemas.ShoppingListItemUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.update_item(db, current_user, item_id, item_in)


@router.delete("/items/{item_id}", status_code=204)
def delete_shopping_item(
    item_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service.delete_item(db, current_user, item_id)


# --------------------------------------------------------------- Suppliers
@router.get("/suppliers", response_model=List[schemas.ShoppingSupplierResponse])
def list_suppliers(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.list_suppliers(db, current_user)


@router.post("/suppliers", response_model=schemas.ShoppingSupplierResponse, status_code=201)
def create_supplier(
    supplier_in: schemas.ShoppingSupplierCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.create_supplier(db, current_user, supplier_in)


@router.delete("/suppliers/{supplier_id}", status_code=204)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service.delete_supplier(db, current_user, supplier_id)


# --------------------------------------------------------------- Prices
@router.post("/items/{item_id}/prices", response_model=schemas.ShoppingPriceResponse, status_code=201)
def add_shopping_price(
    item_id: int,
    price_in: schemas.ShoppingPriceCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.add_price(db, current_user, item_id, price_in)


@router.patch("/prices/{price_id}", response_model=schemas.ShoppingPriceResponse)
def update_shopping_price(
    price_id: int,
    price_in: schemas.ShoppingPriceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return service.update_price(db, current_user, price_id, price_in)


@router.delete("/prices/{price_id}", status_code=204)
def delete_shopping_price(
    price_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service.delete_price(db, current_user, price_id)
