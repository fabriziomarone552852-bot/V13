// src/components/shared/shopping/ShoppingPurchaseModal.tsx
import React, { useEffect, useId, useRef } from 'react';
import type {
  ConfigOption,
  ShoppingSupplierOption,
} from '../../../types/shopping';
import type { PurchaseFormState } from './shoppingItems.utils';
import { getConfigOptionLabel } from './shoppingItems.utils';
import {
  shoppingButtonPrimaryClass,
  shoppingButtonSecondaryClass,
  shoppingCardClass,
  shoppingInputClass,
} from './shoppingUi';

interface ShoppingPurchaseModalProps {
  open: boolean;
  itemName: string;
  purchaseForm: PurchaseFormState;
  setPurchaseForm: React.Dispatch<React.SetStateAction<PurchaseFormState>>;
  suppliers: ShoppingSupplierOption[];
  currencyOptions: ConfigOption[];
  offerFlagOptions: ConfigOption[];
  onClose: () => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
}

const ShoppingPurchaseModal: React.FC<ShoppingPurchaseModalProps> = ({
  open,
  itemName,
  purchaseForm,
  setPurchaseForm,
  suppliers,
  currencyOptions,
  offerFlagOptions,
  onClose,
  onSubmit,
}) => {
  const titleId = useId();
  const supplierId = useId();
  const priceId = useId();
  const purchaseDateId = useId();
  const currencyId = useId();
  const offerFlagId = useId();

  const priceInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', onKeyDown);
    priceInputRef.current?.focus();

    return () => {
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/30 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={`${shoppingCardClass} w-full max-w-2xl p-5`}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id={titleId} className="mb-2 text-lg font-bold text-slate-900">
          Registra acquisto
        </h2>

        <p className="mb-4 text-sm text-slate-500">
          Stai completando{' '}
          <span className="font-semibold text-slate-700">
            {itemName || 'articolo'}
          </span>
        </p>

        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="space-y-1">
              <label
                htmlFor={supplierId}
                className="text-sm font-medium text-slate-700"
              >
                Fornitore
              </label>
              <select
                id={supplierId}
                className={shoppingInputClass}
                value={purchaseForm.supplierId}
                onChange={(e) =>
                  setPurchaseForm((prev) => ({
                    ...prev,
                    supplierId: e.target.value,
                  }))
                }
              >
                <option value="">Nessun fornitore</option>
                {suppliers.map((supplier) => (
                  <option key={supplier.id} value={String(supplier.id)}>
                    {supplier.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label
                htmlFor={priceId}
                className="text-sm font-medium text-slate-700"
              >
                Prezzo
              </label>
              <input
                id={priceId}
                ref={priceInputRef}
                type="number"
                step="0.01"
                min="0"
                className={shoppingInputClass}
                placeholder="0,00"
                value={purchaseForm.price}
                onChange={(e) =>
                  setPurchaseForm((prev) => ({
                    ...prev,
                    price: e.target.value,
                  }))
                }
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="space-y-1">
              <label
                htmlFor={purchaseDateId}
                className="text-sm font-medium text-slate-700"
              >
                Data acquisto
              </label>
              <input
                id={purchaseDateId}
                type="date"
                className={shoppingInputClass}
                value={purchaseForm.purchaseDate}
                onChange={(e) =>
                  setPurchaseForm((prev) => ({
                    ...prev,
                    purchaseDate: e.target.value,
                  }))
                }
                required
              />
            </div>

            <div className="space-y-1">
              <label
                htmlFor={currencyId}
                className="text-sm font-medium text-slate-700"
              >
                Valuta
              </label>
              <select
                id={currencyId}
                className={shoppingInputClass}
                value={purchaseForm.currencyId}
                onChange={(e) =>
                  setPurchaseForm((prev) => ({
                    ...prev,
                    currencyId: e.target.value,
                  }))
                }
              >
                <option value="">Seleziona valuta</option>
                {currencyOptions.map((option) => (
                  <option key={option.id} value={String(option.id)}>
                    {getConfigOptionLabel(option)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-1">
            <label
              htmlFor={offerFlagId}
              className="text-sm font-medium text-slate-700"
            >
              Flag offerta
            </label>
            <select
              id={offerFlagId}
              className={shoppingInputClass}
              value={purchaseForm.offerFlagId}
              onChange={(e) =>
                setPurchaseForm((prev) => ({
                  ...prev,
                  offerFlagId: e.target.value,
                }))
              }
            >
              <option value="">Nessun flag offerta</option>
              {offerFlagOptions.map((option) => (
                <option key={option.id} value={String(option.id)}>
                  {getConfigOptionLabel(option)}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className={shoppingButtonSecondaryClass}
            >
              Annulla
            </button>

            <button type="submit" className={shoppingButtonPrimaryClass}>
              Conferma acquisto
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ShoppingPurchaseModal;