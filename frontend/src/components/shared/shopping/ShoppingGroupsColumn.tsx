// src/components/shared/shopping/ShoppingGroupsColumn.tsx
import React from 'react';
import type { ShoppingGroupSummary } from '@/types/shopping';
import {
  shoppingButtonSecondaryClass,
  shoppingCardClass,
} from './shoppingUi';

interface ShoppingGroupsColumnProps {
  groups: ShoppingGroupSummary[];
  loading?: boolean;
  selectedGroupId?: number | null;
  onSelectGroup?: (groupId: number | null) => void;
  onCreateGroup?: () => void;
}

const ShoppingGroupsColumn: React.FC<ShoppingGroupsColumnProps> = ({
  groups,
  loading = false,
  selectedGroupId = null,
  onSelectGroup,
  onCreateGroup,
}) => {
  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      <div className="flex shrink-0 items-center justify-between">
        <h2 className="text-sm font-bold uppercase tracking-wider text-gray-700">
          Gruppi spesa
        </h2>

        {onCreateGroup ? (
          <button
            type="button"
            onClick={onCreateGroup}
            className={`${shoppingButtonSecondaryClass} text-xs`}
          >
            + Nuovo
          </button>
        ) : null}
      </div>

      <div className="min-h-0 flex-1 space-y-2 overflow-y-auto">
        {loading ? (
          <p className="py-4 text-center text-xs text-gray-400">
            Caricamento gruppi...
          </p>
        ) : groups.length === 0 ? (
          <p className="py-4 text-center text-xs text-gray-400">
            Nessun gruppo disponibile.
          </p>
        ) : (
          <>
            <button
              type="button"
              className={`${shoppingCardClass} w-full p-3 text-left transition hover:border-blue-300 ${
                selectedGroupId === null
                  ? 'border-blue-400 ring-1 ring-blue-200'
                  : ''
              }`}
              onClick={() => onSelectGroup?.(null)}
            >
              <p className="text-sm font-semibold text-gray-700">Tutti i gruppi</p>
            </button>

            {groups.map((group) => {
              const isSelected = selectedGroupId === group.id;

              return (
                <button
                  key={group.id}
                  type="button"
                  className={`${shoppingCardClass} w-full p-3 text-left transition hover:border-blue-300 ${
                    isSelected ? 'border-blue-400 ring-1 ring-blue-200' : ''
                  }`}
                  onClick={() => onSelectGroup?.(isSelected ? null : group.id)}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-gray-800">
                        {group.name}
                      </p>

                      {group.description ? (
                        <p className="truncate text-xs text-gray-500">
                          {group.description}
                        </p>
                      ) : null}
                    </div>

                    <span className="ml-2 shrink-0 text-xs text-gray-400">
                      #{group.id}
                    </span>
                  </div>
                </button>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
};

export default ShoppingGroupsColumn;