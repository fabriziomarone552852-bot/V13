"""Analytics domain service."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from backend.core import models
from backend.domains.shopping import (
    InventoryBatch,
    ShoppingListItem,
    ShoppingSupplier,
)


@dataclass
class SupplierPriceMetrics:
    supplier: ShoppingSupplier
    last_batch: InventoryBatch
    best_batch: InventoryBatch
    avg_normal_price: Optional[Decimal]


def _get_item_owned(db: Session, shopping_list_item_id: int, user_id: int) -> ShoppingListItem:
    item = (
        db.query(ShoppingListItem)
        .options(
            selectinload(ShoppingListItem.product),
            selectinload(ShoppingListItem.shopping_list),
        )
        .filter(ShoppingListItem.id == shopping_list_item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item non trovato")

    if item.shopping_list.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Non autorizzato")

    return item


def _get_product_batches(
    db: Session,
    product_id: int,
) -> List[InventoryBatch]:
    return (
        db.query(InventoryBatch)
        .options(
            selectinload(InventoryBatch.supplier),
            selectinload(InventoryBatch.product),
        )
        .filter(InventoryBatch.product_id == product_id)
        .filter(InventoryBatch.deleted_at.is_(None))
        .order_by(InventoryBatch.purchase_date.desc(), InventoryBatch.id.desc())
        .all()
    )


def _group_metrics_by_supplier(
    batches: List[InventoryBatch],
) -> List[SupplierPriceMetrics]:
    grouped: dict[int, List[InventoryBatch]] = defaultdict(list)

    for batch in batches:
        if batch.supplier_id is None or batch.supplier is None:
            continue
        grouped[int(batch.supplier_id)].append(batch)

    metrics: List[SupplierPriceMetrics] = []

    for supplier_batches in grouped.values():
        supplier_batches.sort(
            key=lambda b: (b.purchase_date, b.id),
            reverse=True,
        )

        last_batch = supplier_batches[0]
        best_batch = min(
            supplier_batches,
            key=lambda b: (b.purchase_price, b.purchase_date, b.id),
        )

        normal_batches = [b for b in supplier_batches if not b.is_on_sale]
        avg_normal_price: Optional[Decimal] = None
        if normal_batches:
            total = sum((b.purchase_price for b in normal_batches), Decimal("0"))
            avg_normal_price = total / Decimal(len(normal_batches))

        metrics.append(
            SupplierPriceMetrics(
                supplier=last_batch.supplier,
                last_batch=last_batch,
                best_batch=best_batch,
                avg_normal_price=avg_normal_price,
            )
        )

    metrics.sort(key=lambda m: m.supplier.name.lower())
    return metrics


def get_supplier_price_summaries(
    db: Session,
    current_user: models.User,
    shopping_list_item_id: int,
) -> list[dict]:
    item = _get_item_owned(db, shopping_list_item_id, current_user.id)
    batches = _get_product_batches(db, item.product_id)

    metrics = _group_metrics_by_supplier(batches)

    return [
        {
            "supplier_id": metric.supplier.id,
            "supplier_name": metric.supplier.name,
            "last_price": metric.last_batch.purchase_price,
            "last_purchase_date": metric.last_batch.purchase_date,
            "best_price": metric.best_batch.purchase_price,
            "best_purchase_date": metric.best_batch.purchase_date,
            "avg_normal_price": metric.avg_normal_price,
            "is_last_price_on_sale": metric.last_batch.is_on_sale,
        }
        for metric in metrics
    ]


def get_price_history(
    db: Session,
    current_user: models.User,
    shopping_list_item_id: int,
) -> list[dict]:
    item = _get_item_owned(db, shopping_list_item_id, current_user.id)
    batches = _get_product_batches(db, item.product_id)

    history = []
    for batch in sorted(batches, key=lambda b: (b.purchase_date, b.id)):
        history.append(
            {
                "batch_id": batch.id,
                "date": batch.purchase_date,
                "price": batch.purchase_price,
                "supplier_id": batch.supplier.id if batch.supplier else None,
                "supplier_name": batch.supplier.name if batch.supplier else None,
                "is_on_sale": batch.is_on_sale,
            }
        )

    return history