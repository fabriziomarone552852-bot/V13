// src/components/shared/shopping/ShoppingItemEditModal.tsx
import React from 'react';
import type { ConfigOption } from '../../../types/shopping';
import type { ItemFormState } from './shoppingItems.utils';
import { getConfigOptionLabel } from './shoppingItems.utils';
import {
  shoppingButtonPrimaryClass,
  shoppingButtonSecondaryClass,
  shoppingCardClass,
  shoppingInputClass,
} from './shoppingUi';

interface ShoppingItemEditModalProps {
  open: boolean;
  editForm: ItemFormState;
  setEditForm: React.Dispatch<React.SetStateAction<ItemFormState>>;
  unitOptions: ConfigOption[];
  onClose: () => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
}

const ShoppingItemEditModal: React.FC<ShoppingItemEditModalProps> = ({
  open,
  editForm,
  setEditForm,
  unitOptions,
  onClose,
  onSubmit,
}) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/30 p-4 backdrop-blur-sm">
      <div className={`${shoppingCardClass} w-full max-w-md p-5`}>
        <h2 className="mb-4 text-lg font-bold text-slate-900">
          Modifica articolo
        </h2>

        <form onSubmit={onSubmit} className="space-y-3">
          <input
            className={shoppingInputClass}
            placeholder="Nome"
            value={editForm.productName}
            onChange={(e) =>
              setEditForm((prev) => ({
                ...prev,
                productName: e.target.value,
              }))
            }
            required
          />

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <input
              type="number"
              step="any"
              className={shoppingInputClass}
              placeholder="Quantità"
              value={editForm.quantity}
              onChange={(e) =>
                setEditForm((prev) => ({
                  ...prev,
                  quantity: e.target.value,
                }))
              }
            />

            <select
              className={shoppingInputClass}
              value={editForm.unitId}
              onChange={(e) =>
                setEditForm((prev) => ({
                  ...prev,
                  unitId: e.target.value,
                }))
              }
            >
              <option value="">Nessuna unità</option>
              {unitOptions.map((option) => (
                <option key={option.id} value={String(option.id)}>
                  {getConfigOptionLabel(option)}
                </option>
              ))}
            </select>
          </div>

          <textarea
            className={`${shoppingInputClass} min-h-[96px] resize-y`}
            placeholder="Note"
            value={editForm.notes}
            onChange={(e) =>
              setEditForm((prev) => ({
                ...prev,
                notes: e.target.value,
              }))
            }
          />

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className={shoppingButtonSecondaryClass}
            >
              Annulla
            </button>

            <button type="submit" className={shoppingButtonPrimaryClass}>
              Salva
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ShoppingItemEditModal;