// src/components/shared/shopping/ShoppingItemsToolbar.tsx
import React, { useId } from 'react';
import {
  shoppingButtonPrimaryClass,
  shoppingInputClass,
} from './shoppingUi';

type FiltroStato = 'tutti' | 'aperti' | 'completati';

interface ShoppingItemsToolbarProps {
  currentListName: string;
  activeListId: number | null;
  searchQuery: string;
  filtroStato: FiltroStato;
  onFiltroStatoChange: (value: FiltroStato) => void;
  onAddItem: () => void;
}

const ShoppingItemsToolbar: React.FC<ShoppingItemsToolbarProps> = ({
  currentListName,
  activeListId,
  searchQuery,
  filtroStato,
  onFiltroStatoChange,
  onAddItem,
}) => {
  const hasActiveList = activeListId != null;
  const filterId = useId();

  return (
    <>
      <div className="shrink-0 flex items-center justify-between gap-3">
        <div className="min-w-0">
          <h2 className="truncate text-sm font-bold uppercase tracking-wider text-slate-700">
            {currentListName}
          </h2>

          {searchQuery ? (
            <p className="mt-1 truncate text-xs text-slate-500">
              Filtro ricerca attivo:{' '}
              <span className="font-medium text-slate-700">{searchQuery}</span>
            </p>
          ) : null}
        </div>

        <button
          type="button"
          onClick={onAddItem}
          className={`${shoppingButtonPrimaryClass} shrink-0 text-xs`}
          disabled={!hasActiveList}
        >
          + Articolo
        </button>
      </div>

      <div className="shrink-0 flex gap-2">
        <div className="w-full sm:w-40">
          <label htmlFor={filterId} className="sr-only">
            Filtra articoli per stato
          </label>
          <select
            id={filterId}
            className={`${shoppingInputClass} w-full`}
            value={filtroStato}
            onChange={(e) =>
              onFiltroStatoChange(e.target.value as FiltroStato)
            }
            disabled={!hasActiveList}
          >
            <option value="tutti">Tutti</option>
            <option value="aperti">Aperti</option>
            <option value="completati">Completati</option>
          </select>
        </div>
      </div>
    </>
  );
};

export default ShoppingItemsToolbar;