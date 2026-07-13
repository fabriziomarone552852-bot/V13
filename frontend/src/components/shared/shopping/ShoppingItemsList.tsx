// src/components/shared/shopping/ShoppingItemsList.tsx
import React from 'react';
import type { ShoppingListItem } from '../../../types/shopping';
import ShoppingItemRow from './ShoppingItemRow';

interface ShoppingItemsListProps {
  loading: boolean;
  items: ShoppingListItem[];
  containerRef: React.RefObject<HTMLDivElement>;
  onToggle: (item: ShoppingListItem) => void;
  onEdit: (item: ShoppingListItem) => void;
  onDelete: (item: ShoppingListItem) => void;
  onPurchase: (item: ShoppingListItem) => void;
}

const ShoppingItemsList: React.FC<ShoppingItemsListProps> = ({
  loading,
  items,
  containerRef,
  onToggle,
  onEdit,
  onDelete,
  onPurchase,
}) => {
  return (
    <div
      ref={containerRef}
      className="flex h-full min-h-0 flex-col overflow-hidden"
    >
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-2">
        {loading ? (
          <p
            className="py-4 text-center text-xs text-gray-400"
            role="status"
            aria-live="polite"
          >
            Caricamento...
          </p>
        ) : items.length === 0 ? (
          <p className="py-4 text-center text-xs text-gray-400">
            Nessun articolo.
          </p>
        ) : (
          <ul className="space-y-1.5" role="list">
            {items.map((item) => (
              <li key={item.id}>
                <ShoppingItemRow
                  item={item}
                  onToggle={onToggle}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  onPurchase={onPurchase}
                />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ShoppingItemsList;