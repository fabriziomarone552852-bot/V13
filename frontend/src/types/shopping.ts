// src/types/shopping.ts

/* =========================
 * Shared primitives
 * ========================= */

export type ShoppingViewMode = 'items' | 'bulk-purchase';

export interface ConfigOption {
  id: number;
  codeName: string;
  codeValue?: string | null;
  displayName?: string | null;
  description?: string | null;
  sortOrder?: number | null;
  isActive?: boolean;
}

export interface ShoppingGroupSummary {
  id: number;
  name: string;
  description?: string | null;
  visibilityId?: number | null;
  statusId?: number | null;
  canEdit?: boolean;
  canDelete?: boolean;
}

export interface ShoppingSupplierOption {
  id: number;
  name: string;
  statusId?: number | null;
  statusCodeName?: string | null;
  isActive?: boolean;
}

export interface ShoppingProductOption {
  id: number;
  nameNormalized: string;
  displayName: string;
  defaultUnitId?: number | null;
  defaultUnitCodeName?: string | null;
  lastPurchasePrice?: number | null;
  lastPurchaseCurrencyId?: number | null;
  lastPurchaseCurrencyCodeName?: string | null;
  lastSupplierId?: number | null;
  lastSupplierName?: string | null;
  lastPurchaseDate?: string | null;
}

/* =========================
 * Read models
 * ========================= */

export interface ShoppingListSummary {
  id: number;
  name: string;
  description?: string | null;
  groupId?: number | null;
  groupName?: string | null;
  visibilityId: number;
  visibilityCodeName?: string | null;
  statusId?: number | null;
  statusCodeName?: string | null;
  openItemsCount: number;
  purchasedItemsCount: number;
  totalItemsCount: number;
  canEdit: boolean;
  canDelete: boolean;
  canArchive?: boolean;
}

export interface ShoppingListItem {
  id: number;
  shoppingListId: number;
  productId: number;
  
  // Refactor: nameOriginal rimosso, introdotto productName
  productName: string; 
  nameNormalized: string;

  quantity?: number | null;
  unitId?: number | null;
  unitCodeName?: string | null;
  notes?: string | null;

  isPurchased: boolean;

  // I dati dell'ultimo acquisto possono restare se calcolati lato backend da InventoryBatch
  lastPrice?: number | null;
  lastCurrencyId?: number | null;
  lastCurrencyCodeName?: string | null;
  lastSupplierId?: number | null;
  lastSupplierName?: string | null;
  lastPurchaseDate?: string | null;

  createdAt?: string;
  updatedAt?: string;
}

export interface InventoryBatchRow {
  id: number;
  productId: number;
  productNameNormalized?: string | null;

  shoppingListItemId?: number | null;
  shoppingListId?: number | null;
  shoppingListName?: string | null;

  supplierId?: number | null;
  supplierName?: string | null;

  quantity?: number | null;
  unitId?: number | null;
  unitCodeName?: string | null;

  purchasePrice: number;
  currencyId?: number | null;
  currencyCodeName?: string | null;

  offerFlagId?: number | null;
  offerFlagCodeName?: string | null;

  purchaseDate: string;
  expirationDate?: string | null;
}

export interface ShoppingProductInsights {
  productId: number;
  lastPrice?: number | null;
  lastCurrencyId?: number | null;
  lastCurrencyCodeName?: string | null;
  lastSupplierId?: number | null;
  lastSupplierName?: string | null;
  lastPurchaseDate?: string | null;

  bestPrice?: number | null;
  bestCurrencyId?: number | null;
  bestCurrencyCodeName?: string | null;
  bestSupplierId?: number | null;
  bestSupplierName?: string | null;

  averagePrice?: number | null;
  totalPurchases?: number;
}

export interface ShoppingConfigBundle {
  unitOptions: ConfigOption[];
  itemStatusOptions: ConfigOption[];
  currencyOptions: ConfigOption[];
  offerFlagOptions: ConfigOption[];
  visibilityOptions: ConfigOption[];
  listStatusOptions: ConfigOption[];
}

/* =========================
 * API write payloads
 * ========================= */

export interface ShoppingPriceCreatePayload {
  shoppingListId: number;
  shoppingListItemId: number;
  productId: number | null;
  supplierId?: number | null;
  purchaseDate: string;
  price: number;
  currencyId?: number | null;
  offerFlagId?: number | null;
  expirationDate?: string | null;
}

export interface ShoppingListCreatePayload {
  name: string;
  description?: string;
  groupId?: number | null;
  visibilityId: number;
  statusId?: number | null;
}

export interface ShoppingListUpdatePayload {
  name?: string;
  description?: string | null;
  groupId?: number | null;
  visibilityId?: number | null;
  statusId?: number | null;
}

// REFACTOR: Usa productName invece di productId e nameOriginal
export interface ShoppingListItemCreatePayload {
  shoppingListId: number;
  productName: string;
  quantity?: number | null;
  unitId?: number | null;
  notes?: string | null;
}

// REFACTOR: Usa productName invece di productId e nameOriginal
export interface ShoppingListItemUpdatePayload {
  productName?: string;
  quantity?: number | null;
  unitId?: number | null;
  notes?: string | null;
}

export interface ToggleShoppingListItemPurchasedPayload {
  isPurchased: boolean;
}

export interface ShoppingSupplierCreatePayload {
  name: string;
  statusId?: number | null;
}

export interface ShoppingSupplierUpdatePayload {
  name?: string;
  statusId?: number | null;
}

export interface ShoppingPriceUpdatePayload {
  supplierId?: number | null;
  purchaseDate?: string;
  price?: number;
  currencyId?: number | null;
  offerFlagId?: number | null;
  expirationDate?: string | null;
}

/* =========================
 * Mutation argument objects
 * ========================= */

export interface UpdateShoppingListArgs {
  id: number;
  data: ShoppingListUpdatePayload;
}

export interface UpdateShoppingListItemArgs {
  id: number;
  listId: number;
  data: ShoppingListItemUpdatePayload;
}

export interface DeleteShoppingListItemArgs {
  id: number;
  listId?: number;
}

export interface ToggleShoppingListItemPurchasedArgs {
  id: number;
  listId: number;
  data: ToggleShoppingListItemPurchasedPayload;
}

export interface UpdateShoppingSupplierArgs {
  id: number;
  data: ShoppingSupplierUpdatePayload;
}

export interface UpdateShoppingPriceArgs {
  priceId: number;
  data: ShoppingPriceUpdatePayload;
  listId?: number;
}

/* =========================
 * Hook contracts
 * ========================= */

export interface UseShoppingDataResult {
  lists: ShoppingListSummary[];
  activeListId: number | null;
  activeList: ShoppingListSummary | null;
  items: ShoppingListItem[];

  suppliers: ShoppingSupplierOption[];
  products: ShoppingProductOption[];
  config: ShoppingConfigBundle | null;

  listsLoading: boolean;
  itemsLoading: boolean;
  suppliersLoading: boolean;
  configLoading: boolean;
  productsLoading: boolean;

  isInitialLoading: boolean;

  setActiveListId: (id: number | null) => void;

  refreshLists: () => Promise<unknown>;
  refreshItems: (listId?: number | null) => Promise<unknown>;
  refreshSuppliers: () => Promise<unknown>;
  refreshConfig: () => Promise<unknown>;
}

export interface UseShoppingMutationsResult {
  createList: (
    payload: ShoppingListCreatePayload
  ) => Promise<ShoppingListSummary>;

  updateList: (
    args: UpdateShoppingListArgs
  ) => Promise<ShoppingListSummary>;

  deleteList: (id: number) => Promise<void>;

  createItem: (
    payload: ShoppingListItemCreatePayload
  ) => Promise<ShoppingListItem>;

  updateItem: (
    args: UpdateShoppingListItemArgs
  ) => Promise<ShoppingListItem>;

  deleteItem: (args: DeleteShoppingListItemArgs) => Promise<void>;

  togglePurchased: (
    args: ToggleShoppingListItemPurchasedArgs
  ) => Promise<ShoppingListItem>;

  createSupplier: (
    payload: ShoppingSupplierCreatePayload
  ) => Promise<ShoppingSupplierOption>;

  updateSupplier: (
    args: UpdateShoppingSupplierArgs
  ) => Promise<ShoppingSupplierOption>;

  deleteSupplier: (id: number) => Promise<void>;

  addPrice: (payload: ShoppingPriceCreatePayload) => Promise<void>;

  updatePrice: (args: UpdateShoppingPriceArgs) => Promise<void>;

  deletePrice: (priceId: number) => Promise<void>;
}