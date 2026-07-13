// src/components/shared/shopping/ShoppingItemCreateModal.tsx
import React from 'react';
import type { ConfigOption } from '../../../types/shopping';
import type { ItemFormState } from './shoppingItems.utils';
import { getConfigOptionLabel } from './shoppingItems.utils';
import {
  shoppingButtonPrimaryClass,
  shoppingButtonSecondaryClass,
  shoppingInputClass,
  shoppingCardClass,
} from './shoppingUi';

interface ShoppingItemCreateModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  itemForm: ItemFormState;
  setItemForm: React.Dispatch<React.SetStateAction<ItemFormState>>;
  activeListId: number | null;
  unitOptions: ConfigOption[];
}

const ShoppingItemCreateModal: React.FC<ShoppingItemCreateModalProps> = ({
  open,
  onClose,
  onSubmit,
  itemForm,
  setItemForm,
  activeListId,
  unitOptions,
}) => {
  if (!open) return null;

  const hasActiveList = activeListId != null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm">
      <div className={`${shoppingCardClass} w-full max-w-xl p-6`}>
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-slate-800">
            Nuovo articolo
          </h3>
          <p className="text-sm text-slate-500">
            Inserisci rapidamente un articolo nella lista spesa attiva.
          </p>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          {!hasActiveList ? (
            <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
              Seleziona prima una lista per aggiungere un articolo.
            </div>
          ) : null}

          <div className="grid gap-4 md:grid-cols-2">
            <label className="flex flex-col gap-1 text-sm text-slate-600">
              Nome articolo
              <input
                type="text"
                className={shoppingInputClass}
                value={itemForm.productName}
                onChange={(e) =>
                  setItemForm((prev) => ({
                    ...prev,
                    productName: e.target.value,
                  }))
                }
                placeholder="Es. Pasta, latte, zucchero"
                required
                autoFocus
                disabled={!hasActiveList}
              />
            </label>

            <label className="flex flex-col gap-1 text-sm text-slate-600">
              Quantità
              <input
                type="number"
                min="0"
                step="0.01"
                className={shoppingInputClass}
                value={itemForm.quantity}
                onChange={(e) =>
                  setItemForm((prev) => ({
                    ...prev,
                    quantity: e.target.value,
                  }))
                }
                placeholder="Es. 2"
                disabled={!hasActiveList}
              />
            </label>

            <label className="flex flex-col gap-1 text-sm text-slate-600 md:col-span-2">
              Unità
              <select
                className={shoppingInputClass}
                value={itemForm.unitId}
                onChange={(e) =>
                  setItemForm((prev) => ({
                    ...prev,
                    unitId: e.target.value,
                  }))
                }
                disabled={!hasActiveList}
              >
                <option value="">Unità predefinita</option>
                {unitOptions.map((option) => (
                  <option key={option.id} value={String(option.id)}>
                    {getConfigOptionLabel(option)}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="flex flex-col gap-1 text-sm text-slate-600">
            Note
            <textarea
              className={`${shoppingInputClass} min-h-[96px] resize-y`}
              value={itemForm.notes}
              onChange={(e) =>
                setItemForm((prev) => ({
                  ...prev,
                  notes: e.target.value,
                }))
              }
              placeholder="Note opzionali"
              disabled={!hasActiveList}
            />
          </label>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className={shoppingButtonSecondaryClass}
            >
              Annulla
            </button>

            <button
              type="submit"
              className={shoppingButtonPrimaryClass}
              disabled={!hasActiveList || !itemForm.productName.trim()}
            >
              Crea articolo
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ShoppingItemCreateModal;