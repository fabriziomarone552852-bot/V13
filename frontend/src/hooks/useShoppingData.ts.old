// src/hooks/shopping/useShoppingData.ts
import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useShoppingApi } from '../../api/shoppingApi';
import type {
  ShoppingConfigBundle,
  ShoppingListItem,
  ShoppingListSummary,
  ShoppingProductOption,
  ShoppingSupplierOption,
  UseShoppingDataResult,
} from '../../types/shopping';

export interface ShoppingItemsFilters {
  shoppingListId?: number | null;
  isPurchased?: boolean | null;
}

interface ShoppingBootstrapResponse {
  suppliers: ShoppingSupplierOption[];
  products: ShoppingProductOption[];
  config: ShoppingConfigBundle;
}

export const shoppingQueryKeys = {
  all: ['shopping'] as const,
  lists: () => [...shoppingQueryKeys.all, 'lists'] as const,
  items: (filters?: ShoppingItemsFilters) =>
    [
      ...shoppingQueryKeys.all,
      'items',
      filters?.shoppingListId ?? null,
      filters?.isPurchased ?? null,
    ] as const,
  bootstrap: () => [...shoppingQueryKeys.all, 'bootstrap'] as const,
};

export const useShoppingData = (
  initialActiveListId: number | null = null
): UseShoppingDataResult => {
  const api = useShoppingApi();
  const [activeListId, setActiveListId] = useState<number | null>(initialActiveListId);

  const {
    data: lists = [],
    isLoading: listsLoading,
    refetch: refetchLists,
  } = useQuery<ShoppingListSummary[]>({
    queryKey: shoppingQueryKeys.lists(),
    queryFn: async () => {
      const data = await api.fetchLists();
      return Array.isArray(data) ? data : [];
    },
  });

  const activeList = useMemo(
    () => lists.find((list) => list.id === activeListId) ?? null,
    [lists, activeListId]
  );

  const {
    data: items = [],
    isLoading: itemsLoading,
    refetch: refetchItems,
  } = useQuery<ShoppingListItem[]>({
    queryKey: shoppingQueryKeys.items({ shoppingListId: activeListId }),
    queryFn: async () => {
      if (activeListId == null) return [];
      const data = await api.fetchItems({
        shoppingListId: activeListId,
      });
      return Array.isArray(data) ? data : [];
    },
    enabled: activeListId != null,
  });

  const {
    data: bootstrap,
    isLoading: bootstrapLoading,
    refetch: refetchBootstrap,
  } = useQuery<ShoppingBootstrapResponse>({
    queryKey: shoppingQueryKeys.bootstrap(),
    queryFn: async () => {
      const data = await api.fetchBootstrap();
      return {
        suppliers: Array.isArray(data?.suppliers) ? data.suppliers : [],
        products: Array.isArray(data?.products) ? data.products : [],
        config: data?.config ?? {
          visibilityOptions: [],
          listStatusOptions: [],
          itemStatusOptions: [],
          unitOptions: [],
          currencyOptions: [],
          offerFlagOptions: [],
          groupRoleOptions: [],
        },
      };
    },
  });

  return {
    lists,
    activeListId,
    activeList,
    items,

    suppliers: bootstrap?.suppliers ?? [],
    products: bootstrap?.products ?? [],
    config: bootstrap?.config ?? null,

    listsLoading,
    itemsLoading,
    bootstrapLoading,

    setActiveListId,
    refreshLists: async () => {
      await refetchLists();
    },
    refreshItems: async (listId: number) => {
      if (activeListId !== listId) {
        setActiveListId(listId);
        return;
      }
      await refetchItems();
    },
    refreshBootstrap: async () => {
      await refetchBootstrap();
    },
  };
};