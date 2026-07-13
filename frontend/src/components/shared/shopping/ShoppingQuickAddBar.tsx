// src/components/shared/shopping/ShoppingQuickAddBar.tsx
import React, { useId } from 'react';
import type { ConfigOption } from '../../../types/shopping';
import { getConfigOptionLabel } from './shoppingItems.utils';
import {
  shoppingButtonPrimaryClass,
  shoppingInputClass,
} from './shoppingUi';

interface ShoppingQuickAddBarProps {
  activeListId: number | null;
  unitOptions: ConfigOption[];
  quickName: string;
  quickQuantity: string;
  quickUnitId: string;
  loading?: boolean;
  onQuickNameChange: (value: string) => void;
  onQuickQuantityChange: (value: string) => void;
  onQuickUnitChange: (value: string) => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
}

const ShoppingQuickAddBar: React.FC<ShoppingQuickAddBarProps> = ({
  activeListId,
  unitOptions,
  quickName,
  quickQuantity,
  quickUnitId,
  loading = false,
  onQuickNameChange,
  onQuickQuantityChange,
  onQuickUnitChange,
  onSubmit,
}) => {
  const hasActiveList = activeListId != null;
  const disabled = !hasActiveList || !quickName.trim() || loading;

  const quickNameId = useId();
  const quickQuantityId = useId();
  const quickUnitFieldId = useId();

  return (
    <form
      onSubmit={onSubmit}
      className="shrink-0 rounded-2xl border border-slate-200 bg-slate-50 p-2"
    >
      <div className="grid grid-cols-1 gap-2 md:grid-cols-[minmax(0,1fr)_110px_150px_auto]">
        <div>
          <label htmlFor={quickNameId} className="sr-only">
            Nome articolo
          </label>
          <input
            id={quickNameId}
            type="text"
            className={shoppingInputClass}
            placeholder={
              hasActiveList
                ? 'Aggiungi rapidamente un articolo...'
                : 'Seleziona prima una lista'
            }
            value={quickName}
            onChange={(e) => onQuickNameChange(e.target.value)}
            disabled={!hasActiveList || loading}
          />
        </div>

        <div>
          <label htmlFor={quickQuantityId} className="sr-only">
            Quantità
          </label>
          <input
            id={quickQuantityId}
            type="number"
            min="0"
            step="0.01"
            className={shoppingInputClass}
            placeholder="Qtà"
            value={quickQuantity}
            onChange={(e) => onQuickQuantityChange(e.target.value)}
            disabled={!hasActiveList || loading}
          />
        </div>

        <div>
          <label htmlFor={quickUnitFieldId} className="sr-only">
            Unità di misura
          </label>
          <select
            id={quickUnitFieldId}
            className={shoppingInputClass}
            value={quickUnitId}
            onChange={(e) => onQuickUnitChange(e.target.value)}
            disabled={!hasActiveList || loading}
          >
            <option value="">Unità</option>
            {unitOptions.map((option) => (
              <option key={option.id} value={String(option.id)}>
                {getConfigOptionLabel(option)}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          className={`${shoppingButtonPrimaryClass} whitespace-nowrap text-xs`}
          disabled={disabled}
        >
          + Aggiungi
        </button>
      </div>
    </form>
  );
};

export default ShoppingQuickAddBar;