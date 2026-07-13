import { useMemo, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';

import {
  fetchShoppingConfig,
  fetchShoppingListItems,
  fetchShoppingLists,
  fetchShoppingProducts,
  fetchShoppingSuppliers,
  shoppingQueryKeys,
} from '@/api/shoppingApi';

import type {
  ShoppingConfigBundle,
  ShoppingListItem,
  ShoppingListSummary,
  ShoppingProductOption,
  ShoppingSupplierOption,
  UseShoppingDataResult,
} from '@/types/shopping';

export const useShoppingData = (): UseShoppingDataResult => {
  const queryClient = useQueryClient();
  const [activeListId, setActiveListId] = useState<number | null>(null);

  const listsQuery = useQuery<ShoppingListSummary[]>({
    queryKey: shoppingQueryKeys.lists(),
    queryFn: ({ signal }) => fetchShoppingLists(signal),
    staleTime: 60_000,
    gcTime: 10 * 60_000,
  });

  const suppliersQuery = useQuery<ShoppingSupplierOption[]>({
    queryKey: shoppingQueryKeys.suppliers(),
    queryFn: ({ signal }) => fetchShoppingSuppliers(signal),
    staleTime: 10 * 60_000,
    gcTime: 30 * 60_000,
  });

  const configQuery = useQuery<ShoppingConfigBundle>({
    queryKey: shoppingQueryKeys.config(),
    queryFn: ({ signal }) => fetchShoppingConfig(signal),
    staleTime: 30 * 60_000,
    gcTime: 60 * 60_000,
  });

  const productsQuery = useQuery<ShoppingProductOption[]>({
    queryKey: shoppingQueryKeys.products(),
    queryFn: ({ signal }) => fetchShoppingProducts(signal),
    staleTime: 10 * 60_000,
    gcTime: 30 * 60_000,
  });

  const resolvedActiveListId = useMemo(() => {
    const lists = listsQuery.data ?? [];
    if (lists.length === 0) return null;

    if (
      activeListId !== null &&
      lists.some((list) => list.id === activeListId)
    ) {
      return activeListId;
    }

    return lists[0].id;
  }, [activeListId, listsQuery.data]);

  const hasActiveList = resolvedActiveListId !== null;

  const itemsQuery = useQuery<ShoppingListItem[]>({
    queryKey: shoppingQueryKeys.items(resolvedActiveListId),
    queryFn: ({ signal }) =>
      fetchShoppingListItems(resolvedActiveListId as number, signal),
    enabled: hasActiveList,
    staleTime: 5_000,
    gcTime: 10 * 60_000,
    placeholderData: (previousData) => previousData,
  });

  const lists = listsQuery.data ?? [];
  const items = itemsQuery.data ?? [];
  const suppliers = suppliersQuery.data ?? [];
  const products = productsQuery.data ?? [];
  const config = configQuery.data ?? null;

  const activeList = useMemo(
    () => lists.find((list) => list.id === resolvedActiveListId) ?? null,
    [lists, resolvedActiveListId]
  );

  const isInitialLoading =
    listsQuery.isLoading ||
    configQuery.isLoading ||
    suppliersQuery.isLoading ||
    productsQuery.isLoading ||
    (hasActiveList && itemsQuery.isLoading && items.length === 0);

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
    products,
    config,
    listsLoading: listsQuery.isLoading,
    itemsLoading: itemsQuery.isLoading,
    suppliersLoading: suppliersQuery.isLoading,
    productsLoading: productsQuery.isLoading,
    configLoading: configQuery.isLoading,
    isInitialLoading,
    setActiveListId,
    refreshLists,
    refreshItems,
    refreshSuppliers,
    refreshConfig,
  };
};