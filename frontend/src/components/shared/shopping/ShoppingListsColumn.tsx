// src/components/shared/shopping/ShoppingListsColumn.tsx
import React, { useEffect, useId, useMemo, useState } from 'react';
import { useShoppingMutations } from '@/hooks/shopping/useShoppingMutations';
import { useModal } from '@/hooks/useModals';
import type {
  ConfigOption,
  ShoppingGroupSummary,
  ShoppingListSummary,
} from '@/types/shopping';
import {
  shoppingButtonPrimaryClass,
  shoppingButtonSecondaryClass,
  shoppingCardClass,
  shoppingInputClass,
} from './shoppingUi';

interface ListFormState {
  groupId: string;
  visibilityId: string;
  statusId: string;
  name: string;
  description: string;
}

interface ShoppingListsColumnProps {
  lists: ShoppingListSummary[];
  loadingLists: boolean;
  activeListId: number | null;
  setActiveListId: (id: number | null) => void;
  groups: ShoppingGroupSummary[];
  listVisibilityOptions: ConfigOption[];
  listStatusOptions: ConfigOption[];
}

const makeEmptyForm = (
  listVisibilityOptions: ConfigOption[] = []
): ListFormState => ({
  groupId: '',
  visibilityId: listVisibilityOptions[0]
    ? String(listVisibilityOptions[0].id)
    : '',
  statusId: '',
  name: '',
  description: '',
});

const getConfigOptionLabel = (option: ConfigOption) =>
  option.displayName?.trim() || option.codeName;

const renderConfigOptions = (options: ConfigOption[]) =>
  options.map((option) => (
    <option key={option.id} value={String(option.id)}>
      {getConfigOptionLabel(option)}
    </option>
  ));

interface ListModalProps {
  title: string;
  form: ListFormState;
  setForm: React.Dispatch<React.SetStateAction<ListFormState>>;
  groups: ShoppingGroupSummary[];
  listVisibilityOptions: ConfigOption[];
  listStatusOptions: ConfigOption[];
  onClose: () => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => Promise<void> | void;
  submitLabel: string;
}

const ListModal: React.FC<ListModalProps> = ({
  title,
  form,
  setForm,
  groups,
  listVisibilityOptions,
  listStatusOptions,
  onClose,
  onSubmit,
  submitLabel,
}) => {
  const titleId = useId();
  const nameId = useId();
  const descriptionId = useId();
  const visibilityId = useId();
  const statusId = useId();
  const groupId = useId();

  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/30 p-4 backdrop-blur-sm">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={`${shoppingCardClass} w-full max-w-md p-5`}
      >
        <h2 id={titleId} className="mb-4 text-lg font-bold text-gray-900">
          {title}
        </h2>

        <form onSubmit={onSubmit} className="space-y-3">
          <div>
            <label htmlFor={nameId} className="mb-1 block text-xs font-medium text-gray-700">
              Nome lista
            </label>
            <input
              id={nameId}
              className={shoppingInputClass}
              placeholder="Nome lista"
              value={form.name}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, name: e.target.value }))
              }
              required
              autoFocus
            />
          </div>

          <div>
            <label
              htmlFor={descriptionId}
              className="mb-1 block text-xs font-medium text-gray-700"
            >
              Descrizione
            </label>
            <input
              id={descriptionId}
              className={shoppingInputClass}
              placeholder="Descrizione (opzionale)"
              value={form.description}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, description: e.target.value }))
              }
            />
          </div>

          <div>
            <label
              htmlFor={visibilityId}
              className="mb-1 block text-xs font-medium text-gray-700"
            >
              Visibilità
            </label>
            <select
              id={visibilityId}
              className={shoppingInputClass}
              value={form.visibilityId}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, visibilityId: e.target.value }))
              }
              required
            >
              <option value="">Seleziona visibilità</option>
              {renderConfigOptions(listVisibilityOptions)}
            </select>
          </div>

          <div>
            <label
              htmlFor={statusId}
              className="mb-1 block text-xs font-medium text-gray-700"
            >
              Stato
            </label>
            <select
              id={statusId}
              className={shoppingInputClass}
              value={form.statusId}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, statusId: e.target.value }))
              }
            >
              <option value="">Default backend</option>
              {renderConfigOptions(listStatusOptions)}
            </select>
          </div>

          <div>
            <label
              htmlFor={groupId}
              className="mb-1 block text-xs font-medium text-gray-700"
            >
              Gruppo
            </label>
            <select
              id={groupId}
              className={shoppingInputClass}
              value={form.groupId}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, groupId: e.target.value }))
              }
            >
              <option value="">Nessun gruppo</option>
              {groups.map((group) => (
                <option key={group.id} value={String(group.id)}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className={shoppingButtonSecondaryClass}
            >
              Annulla
            </button>
            <button type="submit" className={shoppingButtonPrimaryClass}>
              {submitLabel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const ShoppingListsColumn: React.FC<ShoppingListsColumnProps> = ({
  lists,
  loadingLists,
  activeListId,
  setActiveListId,
  groups,
  listVisibilityOptions,
  listStatusOptions,
}) => {
  const mutations = useShoppingMutations();
  const createModal = useModal<null>();
  const editModal = useModal<ShoppingListSummary>();

  const [form, setForm] = useState<ListFormState>(() =>
    makeEmptyForm(listVisibilityOptions)
  );
  const [editForm, setEditForm] = useState<ListFormState>(() =>
    makeEmptyForm(listVisibilityOptions)
  );

  useEffect(() => {
    setForm((prev) => {
      if (prev.visibilityId || listVisibilityOptions.length === 0) {
        return prev;
      }

      return {
        ...prev,
        visibilityId: String(listVisibilityOptions[0].id),
      };
    });
  }, [listVisibilityOptions]);

  useEffect(() => {
    setEditForm((prev) => {
      if (prev.visibilityId || listVisibilityOptions.length === 0) {
        return prev;
      }

      return {
        ...prev,
        visibilityId: String(listVisibilityOptions[0].id),
      };
    });
  }, [listVisibilityOptions]);

  const visibleLists = useMemo(() => lists, [lists]);

  const openCreateModal = () => {
    setForm(makeEmptyForm(listVisibilityOptions));
    createModal.open(null);
  };

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const trimmedName = form.name.trim();
    if (!trimmedName || !form.visibilityId) return;

    await mutations.createList({
      name: trimmedName,
      description: form.description.trim() || undefined,
      groupId: form.groupId ? Number(form.groupId) : undefined,
      visibilityId: Number(form.visibilityId),
      statusId: form.statusId ? Number(form.statusId) : undefined,
    });

    setForm(makeEmptyForm(listVisibilityOptions));
    createModal.close();
  };

  const handleSaveEdit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!editModal.data) return;

    const trimmedName = editForm.name.trim();
    if (!trimmedName) return;

    await mutations.updateList({
      id: editModal.data.id,
      data: {
        name: trimmedName,
        description: editForm.description.trim() || undefined,
        groupId: editForm.groupId ? Number(editForm.groupId) : undefined,
        visibilityId: editForm.visibilityId
          ? Number(editForm.visibilityId)
          : undefined,
        statusId: editForm.statusId ? Number(editForm.statusId) : undefined,
      },
    });

    editModal.close();
  };

  const handleDelete = async (list: ShoppingListSummary) => {
    if (!window.confirm(`Eliminare la lista "${list.name}"?`)) return;

    await mutations.deleteList(list.id);

    if (list.id === activeListId) {
      setActiveListId(null);
    }
  };

  const startEdit = (list: ShoppingListSummary) => {
    setEditForm({
      groupId: list.groupId == null ? '' : String(list.groupId),
      visibilityId: String(list.visibilityId),
      statusId: list.statusId == null ? '' : String(list.statusId),
      name: list.name,
      description: list.description ?? '',
    });

    editModal.open(list);
  };

  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      <div className="flex shrink-0 items-center justify-between">
        <h2 className="text-sm font-bold uppercase tracking-wider text-gray-700">
          Liste spesa
        </h2>

        <button
          type="button"
          onClick={openCreateModal}
          className={`${shoppingButtonSecondaryClass} text-xs`}
        >
          + Nuova
        </button>
      </div>

      <div className="min-h-0 flex-1 space-y-2 overflow-y-auto">
        {loadingLists ? (
          <p className="py-4 text-center text-xs text-gray-400">Caricamento...</p>
        ) : visibleLists.length === 0 ? (
          <p className="py-4 text-center text-xs text-gray-400">
            Nessuna lista. Creane una!
          </p>
        ) : (
          <>
            <button
              type="button"
              className={`${shoppingCardClass} w-full p-3 text-left transition hover:border-blue-300 ${
                activeListId === null ? 'border-blue-400 ring-1 ring-blue-200' : ''
              }`}
              onClick={() => setActiveListId(null)}
            >
              <p className="text-sm font-semibold text-gray-700">Tutte le liste</p>
            </button>

            {visibleLists.map((list) => {
              const isActive = activeListId === list.id;

              return (
                <div
                  key={list.id}
                  className={`${shoppingCardClass} ${
                    isActive ? 'border-blue-400 ring-1 ring-blue-200' : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 p-3">
                    <button
                      type="button"
                      className="min-w-0 flex-1 text-left"
                      onClick={() => setActiveListId(list.id)}
                    >
                      <p className="truncate text-sm font-semibold text-gray-800">
                        {list.name}
                      </p>

                      {list.description ? (
                        <p className="truncate text-xs text-gray-500">
                          {list.description}
                        </p>
                      ) : null}

                      <div className="mt-1 flex items-center gap-2 text-xs">
                        {list.groupId ? (
                          <span className="text-blue-500">Gruppo</span>
                        ) : (
                          <span className="text-gray-400">Privata</span>
                        )}

                        <span className="text-gray-300">•</span>
                        <span className="text-gray-500">
                          {list.openItemsCount} aperti / {list.purchasedItemsCount} presi
                        </span>
                      </div>
                    </button>

                    <div className="flex shrink-0 items-center gap-1">
                      {list.canEdit ? (
                        <button
                          type="button"
                          onClick={() => startEdit(list)}
                          className="rounded px-2 py-1 text-xs text-gray-400 hover:text-blue-500"
                          aria-label={`Modifica lista ${list.name}`}
                        >
                          ✎
                        </button>
                      ) : null}

                      {list.canDelete ? (
                        <button
                          type="button"
                          onClick={() => void handleDelete(list)}
                          className="rounded px-2 py-1 text-xs text-gray-400 hover:text-red-500"
                          aria-label={`Elimina lista ${list.name}`}
                        >
                          ✕
                        </button>
                      ) : null}
                    </div>
                  </div>
                </div>
              );
            })}
          </>
        )}
      </div>

      {createModal.isOpen ? (
        <ListModal
          title="Nuova lista spesa"
          form={form}
          setForm={setForm}
          groups={groups}
          listVisibilityOptions={listVisibilityOptions}
          listStatusOptions={listStatusOptions}
          onClose={createModal.close}
          onSubmit={handleCreate}
          submitLabel="Crea"
        />
      ) : null}

      {editModal.isOpen && editModal.data ? (
        <ListModal
          title="Modifica lista"
          form={editForm}
          setForm={setEditForm}
          groups={groups}
          listVisibilityOptions={listVisibilityOptions}
          listStatusOptions={listStatusOptions}
          onClose={editModal.close}
          onSubmit={handleSaveEdit}
          submitLabel="Salva"
        />
      ) : null}
    </div>
  );
};

export default ShoppingListsColumn;