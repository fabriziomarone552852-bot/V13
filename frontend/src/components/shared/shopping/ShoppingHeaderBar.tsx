import React from 'react';
import {
  Plus,
  Search,
  ShoppingCart,
  ListChecks,
  PackageOpen,
  SlidersHorizontal,
} from 'lucide-react';
import type { ShoppingViewMode } from '../../../types/shopping';

interface ShoppingHeaderBarProps {
  activeListId?: number | null;
  activeListName?: string | null;
  listModeLabel?: string | null;
  openItemsCount: number;
  purchasedItemsCount: number;
  totalItemsCount: number;
  searchQuery: string;
  onSearchChange: (value: string) => void;
  viewMode: ShoppingViewMode;
  onViewModeChange: (mode: ShoppingViewMode) => void;
  onAddItem: () => void;
  onOpenActions?: () => void;
  className?: string;
}

const pillBase =
  'inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-medium';

const ShoppingHeaderBar: React.FC<ShoppingHeaderBarProps> = ({
  activeListId,
  activeListName,
  listModeLabel,
  openItemsCount,
  purchasedItemsCount,
  totalItemsCount,
  searchQuery,
  onSearchChange,
  viewMode,
  onViewModeChange,
  onAddItem,
  onOpenActions,
  className = '',
}) => {
  const hasActiveList = activeListId != null;
  const searchInputId = 'shopping-header-search';

  return (
    <header
      className={[
        'sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80',
        className,
      ].join(' ')}
    >
      <div className="flex flex-col gap-3 px-3 py-3 sm:px-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="truncate text-lg font-semibold text-slate-900">
                {hasActiveList ? activeListName || 'Lista senza nome' : 'Shopping'}
              </h1>

              {listModeLabel ? (
                <span className={`${pillBase} border-sky-200 bg-sky-50 text-sky-700`}>
                  <PackageOpen className="h-3.5 w-3.5" aria-hidden="true" />
                  {listModeLabel}
                </span>
              ) : null}

              {hasActiveList ? (
                <span className={`${pillBase} border-slate-200 bg-slate-50 text-slate-700`}>
                  <ListChecks className="h-3.5 w-3.5" aria-hidden="true" />
                  {openItemsCount} aperti
                </span>
              ) : null}

              {hasActiveList ? (
                <span className={`${pillBase} border-emerald-200 bg-emerald-50 text-emerald-700`}>
                  <ShoppingCart className="h-3.5 w-3.5" aria-hidden="true" />
                  {purchasedItemsCount} acquistati
                </span>
              ) : null}

              {hasActiveList ? (
                <span className={`${pillBase} border-slate-200 bg-slate-50 text-slate-600`}>
                  Totale {totalItemsCount}
                </span>
              ) : null}
            </div>

            <p className="mt-1 truncate text-sm text-slate-500">
              {hasActiveList
                ? 'La lista resta il focus principale; le azioni secondarie sono spostate fuori dal viewport.'
                : 'Seleziona una lista per iniziare a lavorare sugli articoli.'}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div
              className="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1"
              aria-label="Modalità visualizzazione shopping"
            >
              <button
                type="button"
                onClick={() => onViewModeChange('items')}
                className={[
                  'rounded-md px-3 py-1.5 text-sm font-medium transition',
                  viewMode === 'items'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900',
                ].join(' ')}
                aria-pressed={viewMode === 'items'}
              >
                Articoli
              </button>

              <button
                type="button"
                onClick={() => onViewModeChange('bulk-purchase')}
                className={[
                  'rounded-md px-3 py-1.5 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50',
                  viewMode === 'bulk-purchase'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900',
                ].join(' ')}
                disabled={!hasActiveList}
                aria-pressed={viewMode === 'bulk-purchase'}
              >
                Acquisto multiplo
              </button>
            </div>

            {onOpenActions ? (
              <button
                type="button"
                onClick={onOpenActions}
                className="inline-flex min-h-[44px] items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                disabled={!hasActiveList}
              >
                <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
                Azioni
              </button>
            ) : null}

            <button
              type="button"
              onClick={onAddItem}
              className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-sky-600 px-3 py-2 text-sm font-medium text-white hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!hasActiveList}
            >
              <Plus className="h-4 w-4" aria-hidden="true" />
              Aggiungi
            </button>
          </div>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label htmlFor={searchInputId} className="sr-only">
            Cerca un articolo nella lista attiva
          </label>

          <div className="relative block w-full sm:max-w-md">
            <Search
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
              aria-hidden="true"
            />
            <input
              id={searchInputId}
              type="search"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Cerca un articolo nella lista attiva..."
              className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm text-slate-900 outline-none ring-0 placeholder:text-slate-400 focus:border-sky-400"
              disabled={!hasActiveList}
            />
          </div>

          {hasActiveList ? (
            <div className="text-xs text-slate-500 sm:ml-auto">
              Vista ottimizzata per mantenere il maggior spazio verticale possibile agli items.
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
};

export default ShoppingHeaderBar;
export type { ShoppingHeaderBarProps };