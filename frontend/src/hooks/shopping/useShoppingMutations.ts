import { useMutation, useQueryClient } from '@tanstack/react-query';

import {
  createShoppingList,
  updateShoppingList,
  deleteShoppingList,
  createShoppingListItem,
  updateShoppingListItem,
  deleteShoppingListItem,
  createShoppingSupplier,
  updateShoppingSupplier,
  deleteShoppingSupplier,
  addInventoryBatch,
  deleteInventoryBatch,
  toggleShoppingListItemPurchased,
  addShoppingPrice,
  updateShoppingPrice,
  deleteShoppingPrice,
  shoppingQueryKeys,
} from '@/api/shoppingApi';

import type {
  ShoppingListItem,
  ShoppingListCreatePayload,
  ShoppingListItemCreatePayload,
  ShoppingSupplierCreatePayload,
  InventoryBatchCreatePayload,
  UpdateShoppingListArgs,
  UpdateShoppingListItemArgs,
  DeleteShoppingListItemArgs,
  UpdateShoppingSupplierArgs,
  AddInventoryBatchArgs,
  DeleteInventoryBatchArgs,
  ToggleShoppingListItemPurchasedArgs,
  UpdateShoppingPriceArgs,
  ShoppingPriceCreatePayload,
  UseShoppingMutationsResult,
} from '@/types/shopping';

export const useShoppingMutations = (): UseShoppingMutationsResult => {
  const queryClient = useQueryClient();

  const invalidateLists = () =>
    queryClient.invalidateQueries({ queryKey: shoppingQueryKeys.lists() });

  const invalidateItems = (listId: number) =>
    queryClient.invalidateQueries({ queryKey: shoppingQueryKeys.items(listId) });

  const createListMutation = useMutation({
    mutationFn: (payload: ShoppingListCreatePayload) => createShoppingList(payload),
    onSuccess: async () => invalidateLists(),
  });

  const updateListMutation = useMutation({
    mutationFn: ({ id, data }: UpdateShoppingListArgs) => updateShoppingList(id, data),
    onSuccess: async () => invalidateLists(),
  });

  const deleteListMutation = useMutation({
    mutationFn: (id: number) => deleteShoppingList(id),
    onSuccess: async () => invalidateLists(),
  });

  const createItemMutation = useMutation({
    mutationFn: (payload: ShoppingListItemCreatePayload) => createShoppingListItem(payload),
    onSuccess: async (_created, vars) => {
      await Promise.all([invalidateLists(), invalidateItems(vars.shoppingListId)]);
    },
  });

  const updateItemMutation = useMutation({
    mutationFn: ({ id, listId, data }: UpdateShoppingListItemArgs) => updateShoppingListItem(id, listId, data),
    onSuccess: async (_updated, vars) => {
      await Promise.all([invalidateLists(), invalidateItems(vars.listId)]);
    },
  });

  const deleteItemMutation = useMutation({
    mutationFn: ({ id }: DeleteShoppingListItemArgs) => deleteShoppingListItem(id),
    onSuccess: async (_data, vars) => {
      if (vars.listId) await Promise.all([invalidateLists(), invalidateItems(vars.listId)]);
      else await invalidateLists();
    },
  });

  const togglePurchasedMutation = useMutation({
    mutationFn: ({ id, data }: ToggleShoppingListItemPurchasedArgs) =>
      toggleShoppingListItemPurchased(id, { isPurchased: data.isPurchased }),
    onSuccess: async (_item, vars) => {
      await Promise.all([invalidateLists(), invalidateItems(vars.listId)]);
    },
  });

  const createSupplierMutation = useMutation({
    mutationFn: (payload: ShoppingSupplierCreatePayload) => createShoppingSupplier(payload),
    onSuccess: async () => queryClient.invalidateQueries({ queryKey: shoppingQueryKeys.suppliers() }),
  });

  const updateSupplierMutation = useMutation({
    mutationFn: ({ id, data }: UpdateShoppingSupplierArgs) => updateShoppingSupplier(id, data),
    onSuccess: async () => queryClient.invalidateQueries({ queryKey: shoppingQueryKeys.suppliers() }),
  });

  const deleteSupplierMutation = useMutation({
    mutationFn: (id: number) => deleteShoppingSupplier(id),
    onSuccess: async () => queryClient.invalidateQueries({ queryKey: shoppingQueryKeys.suppliers() }),
  });

  const addInventoryBatchMutation = useMutation({
    mutationFn: ({ itemId, data }: AddInventoryBatchArgs) => addInventoryBatch(itemId, data),
    onSuccess: async (_d, vars) => {
      await Promise.all([invalidateLists(), invalidateItems(vars.listId)]);
    },
  });

  const deleteInventoryBatchMutation = useMutation({
    mutationFn: ({ batchId, listId }: DeleteInventoryBatchArgs) => deleteInventoryBatch(batchId),
    onSuccess: async (_d, vars) => {
      await Promise.all([invalidateLists(), invalidateItems(vars.listId)]);
    },
  });

  return {
    createList: (payload) => createListMutation.mutateAsync(payload),
    updateList: (args) => updateListMutation.mutateAsync(args),
    deleteList: (id) => deleteListMutation.mutateAsync(id),

    createItem: (payload) => createItemMutation.mutateAsync(payload),
    updateItem: (args) => updateItemMutation.mutateAsync(args),
    deleteItem: (args) => deleteItemMutation.mutateAsync(args),
    togglePurchased: (args) => togglePurchasedMutation.mutateAsync(args),

    createSupplier: (payload) => createSupplierMutation.mutateAsync(payload),
    updateSupplier: (args) => updateSupplierMutation.mutateAsync(args),
    deleteSupplier: (id) => deleteSupplierMutation.mutateAsync(id),

    addInventoryBatch: (args) => addInventoryBatchMutation.mutateAsync(args),
    deleteInventoryBatch: (args) => deleteInventoryBatchMutation.mutateAsync(args),

    // compat contract
    addPrice: (payload: ShoppingPriceCreatePayload) => addShoppingPrice(payload),
    updatePrice: (args: UpdateShoppingPriceArgs) => updateShoppingPrice(args.priceId, args.data),
    deletePrice: (priceId: number) => deleteShoppingPrice(priceId),
  } as UseShoppingMutationsResult;
};