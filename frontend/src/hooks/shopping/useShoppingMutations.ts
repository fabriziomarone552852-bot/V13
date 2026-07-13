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
  shoppingQueryKeys,
} from '@/api/shoppingApi';

import type {
  ShoppingListCreatePayload,
  ShoppingListItem,
  ShoppingListItemCreatePayload,
  ShoppingSupplierCreatePayload,
  InventoryBatchCreatePayload,
  UpdateShoppingListArgs,
  UpdateShoppingListItemArgs,
  DeleteShoppingListItemArgs,
  UpdateShoppingSupplierArgs,
  AddInventoryBatchArgs,
  DeleteInventoryBatchArgs,
  UseShoppingMutationsResult,
} from '@/types/shopping';

export const useShoppingMutations = (): UseShoppingMutationsResult => {
  const queryClient = useQueryClient();

  const invalidateLists = () =>
    queryClient.invalidateQueries({ queryKey: shoppingQueryKeys.lists() });

  const invalidateItems = (listId: number) =>
    queryClient.invalidateQueries({
      queryKey: shoppingQueryKeys.items(listId),
    });

  const invalidateAllItems = () =>
    queryClient.invalidateQueries({
      queryKey: [...shoppingQueryKeys.all, 'items'],
    });

  const invalidateSuppliers = () =>
    queryClient.invalidateQueries({
      queryKey: shoppingQueryKeys.suppliers(),
    });

  const replaceItemInCache = (listId: number, nextItem: ShoppingListItem) => {
    queryClient.setQueryData<ShoppingListItem[]>(
      shoppingQueryKeys.items(listId),
      (current = []) =>
        current.map((item) => (item.id === nextItem.id ? nextItem : item))
    );
  };

  const removeItemFromCache = (listId: number, itemId: number) => {
    queryClient.setQueryData<ShoppingListItem[]>(
      shoppingQueryKeys.items(listId),
      (current = []) => current.filter((item) => item.id !== itemId)
    );
  };

  const appendItemToCache = (listId: number, nextItem: ShoppingListItem) => {
    queryClient.setQueryData<ShoppingListItem[]>(
      shoppingQueryKeys.items(listId),
      (current = []) => {
        const exists = current.some((item) => item.id === nextItem.id);
        return exists ? current : [...current, nextItem];
      }
    );
  };

  const createListMutation = useMutation({
    mutationFn: (payload: ShoppingListCreatePayload) =>
      createShoppingList(payload),
    onSuccess: async () => {
      await invalidateLists();
    },
  });

  const updateListMutation = useMutation({
    mutationFn: ({ id, data }: UpdateShoppingListArgs) =>
      updateShoppingList(id, data),
    onSuccess: async () => {
      await invalidateLists();
    },
  });

  const deleteListMutation = useMutation({
    mutationFn: (id: number) => deleteShoppingList(id),
    onSuccess: async () => {
      await invalidateLists();
    },
  });

  const createItemMutation = useMutation({
    mutationFn: (payload: ShoppingListItemCreatePayload) =>
      createShoppingListItem(payload),
    onSuccess: async (createdItem, vars: ShoppingListItemCreatePayload) => {
      appendItemToCache(vars.shoppingListId, createdItem);

      await Promise.all([
        invalidateLists(),
        invalidateItems(vars.shoppingListId),
      ]);
    },
  });

  const updateItemMutation = useMutation({
    mutationFn: ({ id, listId, data }: UpdateShoppingListItemArgs) =>
      updateShoppingListItem(id, listId, data),
    onSuccess: async (updatedItem, vars: UpdateShoppingListItemArgs) => {
      replaceItemInCache(vars.listId, updatedItem);

      await Promise.all([
        invalidateLists(),
        invalidateItems(vars.listId),
      ]);
    },
  });

  const deleteItemMutation = useMutation({
    mutationFn: ({ id }: DeleteShoppingListItemArgs) =>
      deleteShoppingListItem(id),
    onSuccess: async (_data, vars: DeleteShoppingListItemArgs) => {
      removeItemFromCache(vars.listId, vars.id);

      await Promise.all([
        invalidateLists(),
        invalidateItems(vars.listId),
      ]);
    },
  });

  const createSupplierMutation = useMutation({
    mutationFn: (payload: ShoppingSupplierCreatePayload) =>
      createShoppingSupplier(payload),
    onSuccess: async () => {
      await invalidateSuppliers();
    },
  });

  const updateSupplierMutation = useMutation({
    mutationFn: ({ id, data }: UpdateShoppingSupplierArgs) =>
      updateShoppingSupplier(id, data),
    onSuccess: async () => {
      await invalidateSuppliers();
    },
  });

  const deleteSupplierMutation = useMutation({
    mutationFn: (id: number) => deleteShoppingSupplier(id),
    onSuccess: async () => {
      await invalidateSuppliers();
    },
  });

  const addInventoryBatchMutation = useMutation({
    mutationFn: ({ itemId, data }: AddInventoryBatchArgs) =>
      addInventoryBatch(itemId, data),
    onSuccess: async (_data, vars: AddInventoryBatchArgs) => {
      await Promise.all([
        invalidateLists(),
        invalidateItems(vars.listId),
      ]);
    },
  });

  const deleteInventoryBatchMutation = useMutation({
    mutationFn: ({ batchId, listId }: DeleteInventoryBatchArgs) =>
      deleteInventoryBatch(batchId),
    onSuccess: async (_data, vars: DeleteInventoryBatchArgs) => {
      await Promise.all([invalidateLists(), invalidateItems(vars.listId)]);
    },
  });

  return {
    createList: (payload: ShoppingListCreatePayload) =>
      createListMutation.mutateAsync(payload),

    updateList: (args: UpdateShoppingListArgs) =>
      updateListMutation.mutateAsync(args),

    deleteList: (id: number) => deleteListMutation.mutateAsync(id),

    createItem: (payload: ShoppingListItemCreatePayload) =>
      createItemMutation.mutateAsync(payload),

    updateItem: (args: UpdateShoppingListItemArgs) =>
      updateItemMutation.mutateAsync(args),

    deleteItem: (args: DeleteShoppingListItemArgs) =>
      deleteItemMutation.mutateAsync(args),

    createSupplier: (payload: ShoppingSupplierCreatePayload) =>
      createSupplierMutation.mutateAsync(payload),

    updateSupplier: (args: UpdateShoppingSupplierArgs) =>
      updateSupplierMutation.mutateAsync(args),

    deleteSupplier: (id: number) => deleteSupplierMutation.mutateAsync(id),

    addInventoryBatch: (args: AddInventoryBatchArgs) =>
      addInventoryBatchMutation.mutateAsync(args),

    deleteInventoryBatch: (args: DeleteInventoryBatchArgs) =>
      deleteInventoryBatchMutation.mutateAsync(args),
  };
};