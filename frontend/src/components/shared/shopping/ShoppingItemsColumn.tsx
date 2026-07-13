import React, {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useMemo,
  useState,
} from 'react';
import { useShoppingMutations } from '@/hooks/shopping/useShoppingMutations';
import { useModal } from '@/hooks/useModals';

import type {
  ConfigOption,
  ShoppingListItem,
  ShoppingListSummary,
  ShoppingSupplierOption,
} from '../../../types/shopping';

import { shoppingCardClass } from './shoppingUi';
import {
  emptyItemForm,
  emptyPurchaseForm,
  getEurCurrencyId,
} from './shoppingItems.utils';
import type {
  ItemFormState,
  PurchaseFormState,
} from './shoppingItems.utils';

import ShoppingItemCreateModal from './ShoppingItemCreateModal';
import ShoppingItemEditModal from './ShoppingItemEditModal';
import ShoppingPurchaseModal from './ShoppingPurchaseModal';
import ShoppingItemsToolbar from './ShoppingItemsToolbar';
import ShoppingItemsList from './ShoppingItemsList';
import ShoppingQuickAddBar from './ShoppingQuickAddBar';

type FiltroStato = 'tutti' | 'aperti' | 'completati';

export interface ShoppingItemsColumnHandle {
  openCreateModal: () => void;
}

interface ShoppingItemsColumnProps {
  items: ShoppingListItem[];
  suppliers: ShoppingSupplierOption[];
  unitOptions: ConfigOption[];
  currencyOptions: ConfigOption[];
  offerFlagOptions: ConfigOption[];
  loading: boolean;
  activeListId: number | null;
  activeList: ShoppingListSummary | null;
  searchQuery: string;
}

const ShoppingItemsColumn = forwardRef<
  ShoppingItemsColumnHandle,
  ShoppingItemsColumnProps
>(
  (
    {
      items,
      suppliers,
      unitOptions,
      currencyOptions,
      offerFlagOptions,
      loading,
      activeListId,
      activeList,
      searchQuery,
    },
    ref
  ) => {
    const mutations = useShoppingMutations();
    const containerRef = React.useRef<HTMLDivElement>(null);

    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const editModal = useModal<ShoppingListItem>();
    const purchaseModal = useModal<ShoppingListItem>();

    const [filtroStato, setFiltroStato] = useState<FiltroStato>('tutti');

    const [itemForm, setItemForm] = useState<ItemFormState>(emptyItemForm());
    const [editForm, setEditForm] = useState<ItemFormState>(emptyItemForm());
    const [purchaseForm, setPurchaseForm] = useState<PurchaseFormState>(
      emptyPurchaseForm()
    );

    const [quickName, setQuickName] = useState('');
    const [quickQuantity, setQuickQuantity] = useState('');
    const [quickUnitId, setQuickUnitId] = useState('');
    const [quickAdding, setQuickAdding] = useState(false);

    const eurCurrencyId = useMemo(
      () => getEurCurrencyId(currencyOptions),
      [currencyOptions]
    );

    useEffect(() => {
      if (!eurCurrencyId) return;

      setPurchaseForm((prev) =>
        prev.currencyId ? prev : { ...prev, currencyId: eurCurrencyId }
      );
    }, [eurCurrencyId]);

    const buildCreateForm = (): ItemFormState => ({
      ...emptyItemForm(),
      shoppingListId: activeListId != null ? String(activeListId) : '',
    });

    const handleOpenCreate = () => {
      setItemForm(buildCreateForm());
      setIsCreateOpen(true);
    };

    useImperativeHandle(
      ref,
      () => ({
        openCreateModal: handleOpenCreate,
      }),
      [handleOpenCreate]
    );

    const filteredItems = useMemo(() => {
      let result = items;

      if (filtroStato === 'aperti') {
        result = result.filter((item) => !item.isPurchased);
      }

      if (filtroStato === 'completati') {
        result = result.filter((item) => item.isPurchased);
      }

      return result;
    }, [items, filtroStato]);

    const currentListName = activeList?.name ?? 'Lista spesa';

    const resetQuickAdd = () => {
      setQuickName('');
      setQuickQuantity('');
      setQuickUnitId('');
    };

    const handleCloseCreate = () => {
      setItemForm(buildCreateForm());
      setIsCreateOpen(false);
    };

    const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!itemForm.productName.trim()) return;
      if (!itemForm.shoppingListId) return;

      await mutations.createItem({
        shoppingListId: Number(itemForm.shoppingListId),
        productName: itemForm.productName.trim(),
        quantity: itemForm.quantity ? Number(itemForm.quantity) : undefined,
        unitId: itemForm.unitId ? Number(itemForm.unitId) : undefined,
        notes: itemForm.notes?.trim() || undefined,
      });

      handleCloseCreate();
    };

    const handleQuickAdd = async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (activeListId == null) return;
      if (!quickName.trim()) return;

      setQuickAdding(true);
      try {
        await mutations.createItem({
          shoppingListId: activeListId,
          productName: quickName.trim(),
          quantity: quickQuantity ? Number(quickQuantity) : undefined,
          unitId: quickUnitId ? Number(quickUnitId) : undefined,
          notes: undefined,
        });
        resetQuickAdd();
      } finally {
        setQuickAdding(false);
      }
    };

    const handleOpenEdit = (item: ShoppingListItem) => {
      setEditForm({
        shoppingListId:
          item.shoppingListId != null ? String(item.shoppingListId) : '',
        productName: item.productName ?? '',
        quantity: item.quantity != null ? String(item.quantity) : '',
        unitId: item.unitId != null ? String(item.unitId) : '',
        notes: item.notes ?? '',
      });

      editModal.open(item);
    };

    const handleCloseEdit = () => {
      setEditForm(emptyItemForm());
      editModal.close();
    };

    const handleEdit = async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!editModal.data) return;

      await mutations.updateItem({
        id: editModal.data.id,
        listId: editModal.data.shoppingListId,
        data: {
          productName: editForm.productName.trim() || undefined,
          quantity: editForm.quantity ? Number(editForm.quantity) : undefined,
          unitId: editForm.unitId ? Number(editForm.unitId) : undefined,
          notes: editForm.notes?.trim() || undefined,
        },
      });

      handleCloseEdit();
    };

    const handleDelete = async (item: ShoppingListItem) => {
      await mutations.deleteItem({
        id: item.id,
        listId: item.shoppingListId,
      });
    };

    const handleTogglePurchased = (item: ShoppingListItem) => {
      if (item.isPurchased) {
        // L'articolo è già acquistato.
        // Troviamo l'ultimo lotto di acquisto (inventory batch).
        const lastBatch = item.inventoryBatches?.[item.inventoryBatches.length - 1];
        if (lastBatch) {
          // Chiediamo conferma prima di eliminare l'acquisto.
          if (window.confirm(`Annullare l'acquisto per "${item.productName}"?`)) {
            mutations.deleteInventoryBatch({
              batchId: lastBatch.id,
              listId: item.shoppingListId,
            });
          }
        }
      } else {
        // L'articolo non è acquistato, apriamo la modale per registrarlo.
        handleOpenPurchase(item);
      }
    };

    const handleOpenPurchase = (item: ShoppingListItem) => {
      setPurchaseForm({
        ...emptyPurchaseForm(eurCurrencyId),
        purchaseDate: new Date().toISOString().slice(0, 10),
      });
      purchaseModal.open(item);
    };

    const handleClosePurchase = () => {
      setPurchaseForm(emptyPurchaseForm(eurCurrencyId));
      purchaseModal.close();
    };

    const handlePurchase = async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!purchaseModal.data) return;
      if (activeListId == null) return;
      if (!purchaseForm.price) return;

      await mutations.addInventoryBatch({
        itemId: purchaseModal.data.id,
        listId: activeListId,
        productId: purchaseModal.data.productId,
        supplierId: purchaseForm.supplierId
          ? Number(purchaseForm.supplierId)
          : undefined,
        purchaseDate: purchaseForm.purchaseDate,
        price: Number(purchaseForm.price),
        currencyId: purchaseForm.currencyId
          ? Number(purchaseForm.currencyId)
          : undefined,
        offerFlagId: purchaseForm.offerFlagId
          ? Number(purchaseForm.offerFlagId)
          : undefined,
      });

      handleClosePurchase();
    };

    return (
      <div className="flex h-full min-h-0 flex-col gap-3">
        <ShoppingItemsToolbar
          currentListName={currentListName}
          activeListId={activeListId}
          searchQuery={searchQuery}
          filtroStato={filtroStato}
          onFiltroStatoChange={setFiltroStato}
          onAddItem={handleOpenCreate}
        />

        <ShoppingQuickAddBar
          activeListId={activeListId}
          unitOptions={unitOptions}
          quickName={quickName}
          quickQuantity={quickQuantity}
          quickUnitId={quickUnitId}
          onQuickNameChange={setQuickName}
          onQuickQuantityChange={setQuickQuantity}
          onQuickUnitChange={setQuickUnitId}
          onSubmit={handleQuickAdd}
          loading={quickAdding}
        />

        <div className={`${shoppingCardClass} min-h-0 flex-1 overflow-hidden p-0`}>
          <ShoppingItemsList
            items={filteredItems}
          loading={loading && items.length === 0}
            containerRef={containerRef}
            onEdit={handleOpenEdit}
            onDelete={handleDelete}
            onToggle={handleTogglePurchased}
            onPurchase={handleOpenPurchase}
          />
        </div>

        <ShoppingItemCreateModal
          open={isCreateOpen}
          onClose={handleCloseCreate}
          onSubmit={handleCreate}
          itemForm={itemForm}
          setItemForm={setItemForm}
          activeListId={activeListId}
          unitOptions={unitOptions}
        />

        <ShoppingItemEditModal
          open={editModal.isOpen}
          onClose={handleCloseEdit}
          onSubmit={handleEdit}
          editForm={editForm}
          setEditForm={setEditForm}
          unitOptions={unitOptions}
        />

        <ShoppingPurchaseModal
          open={purchaseModal.isOpen}
          onClose={handleClosePurchase}
          onSubmit={handlePurchase}
          purchaseForm={purchaseForm}
          setPurchaseForm={setPurchaseForm}
          suppliers={suppliers}
          currencyOptions={currencyOptions}
          offerFlagOptions={offerFlagOptions}
          itemName={purchaseModal.data?.productName ?? ''}
        />
      </div>
    );
  }
);

ShoppingItemsColumn.displayName = 'ShoppingItemsColumn';

export default ShoppingItemsColumn;