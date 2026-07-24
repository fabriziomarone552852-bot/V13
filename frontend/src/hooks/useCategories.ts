// src/hooks/useCategories.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/apiService';
import type { Category, CategoryGenre } from '../types';

// 🛡️ VIA LUNGA: Creiamo due interfacce stringenti.
// 1. Il contratto che il Frontend passa alla funzione (il form)
export interface CategoryFormInput {
  category_name: string;
  colore?: string;
  genre?: CategoryGenre | number;
}

// 2. Il DTO (Data Transfer Object) esatto che il Backend accetta
export interface CategoryCreatePayload {
  name: string;          // Mappatura corretta
  colore?: string;
  genre?: CategoryGenre | number;
}

export const useCategories = () => {
  const queryClient = useQueryClient();

  // 1. Lettura
  const { data: dbCategories = [], isLoading } = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: async () => {
      const data = await api.get<{ items?: Category[] } | Category[]>('/categories');
      if (!data) return [];
      return Array.isArray(data) ? data : (data?.items || []);
    },
    staleTime: Infinity,
  });

  // 2. Creazione: Trasformazione Type-Safe prima dell'invio
  const addCategoryMutation = useMutation({
    // Accettiamo i dati dal form (CategorySelect.tsx)
    mutationFn: async (newCatForm: CategoryFormInput): Promise<Category> => {
      
      // TRADUZIONE: Prepariamo il pacchetto perfetto per il server
      const payloadPerServer: CategoryCreatePayload = {
        name: newCatForm.category_name, // Il server vuole 'name'
        colore: newCatForm.colore,
        genre: newCatForm.genre,
      };

      const result = await api.post<Category>('/categories', payloadPerServer);
      if (!result) throw new Error("Creazione fallita");
      return result;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['categories'] })
  });

  // 3. Aggiornamento (Metodo PATCH corretto)
  const updateCategoryMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string | number; data: Partial<Category> }): Promise<Category> => {
      const result = await api.patch<Category>(`/categories/${id}`, data);
      if (!result) throw new Error("Aggiornamento fallito");
      return result;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['categories'] })
  });

  return { 
    dbCategories, 
    isLoading,
    addCategory: addCategoryMutation.mutateAsync,
    updateCategory: updateCategoryMutation.mutateAsync
  };
};