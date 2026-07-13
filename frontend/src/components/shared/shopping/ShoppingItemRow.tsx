// src/components/shared/shopping/ShoppingItemRow.tsx
import React from 'react';
import { Pencil, Trash2, Receipt, Check } from 'lucide-react';
import type { ShoppingListItem } from '../../../types/shopping';
import {
  shoppingCardClass,
  shoppingIconButtonClass,
} from './shoppingUi';

interface ShoppingItemRowProps {
  item: ShoppingListItem;
  onToggle: (item: ShoppingListItem) => void;
  onEdit: (item: ShoppingListItem) => void;
  onDelete: (item: ShoppingListItem) => void;
  onPurchase: (item: ShoppingListItem) => void;
}

const ShoppingItemRow: React.FC<ShoppingItemRowProps> = ({
  item,
  onToggle,
  onEdit,
  onDelete,
  onPurchase,
}) => {
  const itemLabel = item.productName || 'articolo';

  return (
    <div className={`${shoppingCardClass} flex items-center gap-2 p-2.5`}>
      <button
        type="button"
        onClick={() => onToggle(item)}
        className={[
          'inline-flex min-h-[44px] min-w-[44px] shrink-0 items-center justify-center rounded-full border-2 transition focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-1',
          item.isPurchased
            ? 'border-emerald-500 bg-emerald-500 text-white'
            : 'border-slate-300 bg-white text-transparent hover:border-emerald-400',
        ].join(' ')}
        aria-label={
          item.isPurchased
            ? `Segna ${itemLabel} come non acquistato`
            : `Segna ${itemLabel} come acquistato`
        }
        aria-pressed={item.isPurchased}
      >
        <Check className="h-4 w-4" aria-hidden="true" />
      </button>

      <div className="min-w-0 flex-1">
        <p
          className={[
            'truncate text-sm',
            item.isPurchased
              ? 'text-slate-400 line-through'
              : 'text-slate-800',
          ].join(' ')}
        >
          {item.productName}
        </p>

        <div className="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-400">
          {item.quantity != null ? (
            <span>
              {item.quantity}
              {item.unitCodeName ? ` ${item.unitCodeName}` : ''}
            </span>
          ) : null}

          {item.notes ? <span className="truncate">{item.notes}</span> : null}
        </div>
      </div>

      <div className="shrink-0 flex items-center gap-1">
        <button
          type="button"
          onClick={() => onPurchase(item)}
          className={shoppingIconButtonClass}
          aria-label={`Registra acquisto per ${itemLabel}`}
        >
          <Receipt className="h-4 w-4" aria-hidden="true" />
        </button>

        <button
          type="button"
          onClick={() => onEdit(item)}
          className={shoppingIconButtonClass}
          aria-label={`Modifica ${itemLabel}`}
        >
          <Pencil className="h-4 w-4" aria-hidden="true" />
        </button>

        <button
          type="button"
          onClick={() => onDelete(item)}
          className={[
            shoppingIconButtonClass,
            'border-red-200 text-red-500 hover:bg-red-50 hover:text-red-600 focus:ring-red-100',
          ].join(' ')}
          aria-label={`Elimina ${itemLabel}`}
        >
          <Trash2 className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
};

export default ShoppingItemRow;