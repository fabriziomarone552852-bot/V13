"""Analytics domain router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core import deps
from backend.domains.analytics import service
from backend.domains.users.models import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/shopping/items/{shopping_list_item_id}/supplier-prices")
def get_supplier_prices_for_item(
    shopping_list_item_id: int,
    current_user: User = Depends(deps.get_current_app_user),
    db: Session = Depends(deps.get_db),
):
    return service.get_supplier_price_summaries(db, current_user, shopping_list_item_id)


@router.get("/shopping/items/{shopping_list_item_id}/price-history")
def get_price_history_for_item(
    shopping_list_item_id: int,
    current_user: User = Depends(deps.get_current_app_user),
    db: Session = Depends(deps.get_db),
):
    return service.get_price_history(db, current_user, shopping_list_item_id)