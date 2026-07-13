import { useMemo, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';

import {
  fetchShoppingLists,
  fetchShoppingListItems,
  fetchShoppingSuppliers,
  fetchShoppingConfig,
  shoppingQueryKeys,
} from '@/api/shoppingApi';

import type { UseShoppingDataResult } from '@/types/shopping';

export const useShoppingData = (): UseShoppingDataResult => {
  const queryClient = useQueryClient();
  const [activeListId, setActiveListId] = useState<number | null>(null);

  const listsQuery = useQuery({
    queryKey: shoppingQueryKeys.lists(),
    queryFn: ({ signal }) => fetchShoppingLists(signal),
    staleTime: 60_000,
    gcTime: 10 * 60_000,
  });

  const suppliersQuery = useQuery({
    queryKey: shoppingQueryKeys.suppliers(),
    queryFn: ({ signal }) => fetchShoppingSuppliers(signal),
    staleTime: 10 * 60_000,
    gcTime: 30 * 60_000,
  });

  const configQuery = useQuery({
    queryKey: shoppingQueryKeys.config(),
    queryFn: ({ signal }) => fetchShoppingConfig(signal),
    staleTime: 30 * 60_000,
    gcTime: 60 * 60_000,
  });

  const resolvedActiveListId = useMemo(() => {
    const lists = listsQuery.data ?? [];
    if (lists.length === 0) return null;

    if (activeListId !== null && lists.some((list) => list.id === activeListId)) {
      return activeListId;
    }

    return lists[0].id;
  }, [activeListId, listsQuery.data]);

  const itemsQuery = useQuery({
    queryKey: shoppingQueryKeys.items(resolvedActiveListId),
    queryFn: ({ signal }) => fetchShoppingListItems(resolvedActiveListId!, signal),
    enabled: resolvedActiveListId !== null,
    staleTime: 5_000,
    gcTime: 10 * 60_000,
    placeholderData: (previousData) => previousData,
  });

  const lists = listsQuery.data ?? [];
  const items = itemsQuery.data ?? [];
  const suppliers = suppliersQuery.data ?? [];
  const config = configQuery.data ?? null;

  const activeList = useMemo(
    () => lists.find((list) => list.id === resolvedActiveListId) ?? null,
    [lists, resolvedActiveListId]
  );

  const isInitialLoading =
    listsQuery.isLoading ||
    configQuery.isLoading ||
    suppliersQuery.isLoading ||
    (resolvedActiveListId !== null && itemsQuery.isLoading && items.length === 0);

  const refreshLists = async () => {
    await queryClient.invalidateQueries({
      queryKey: shoppingQueryKeys.lists(),
    });
  };

  const refreshItems = async (listId?: number | null) => {
    const targetListId = listId ?? resolvedActiveListId;
    if (targetListId === null) return;

    await queryClient.invalidateQueries({
      queryKey: shoppingQueryKeys.items(targetListId),
    });
  };

  const refreshSuppliers = async () => {
    await queryClient.invalidateQueries({
      queryKey: shoppingQueryKeys.suppliers(),
    });
  };

  const refreshConfig = async () => {
    await queryClient.invalidateQueries({
      queryKey: shoppingQueryKeys.config(),
    });
  };

  return {
    lists,
    activeListId: resolvedActiveListId,
    activeList,
    items,

    suppliers,
    products: [],
    config,

    listsLoading: listsQuery.isLoading,
    itemsLoading: itemsQuery.isLoading,
    suppliersLoading: suppliersQuery.isLoading,
    configLoading: configQuery.isLoading,

    isInitialLoading,

    setActiveListId,

    refreshLists,
    refreshItems,
    refreshSuppliers,
    refreshConfig,
  };
};