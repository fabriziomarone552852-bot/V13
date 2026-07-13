// src/hooks/useCategories.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/apiService';
import type { Category } from '../types';

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

  // 2. Creazione (AGGIUNTO : Promise<Category>)
  const addCategoryMutation = useMutation({
    mutationFn: async (newCat: Partial<Category>): Promise<Category> => {
      const result = await api.post<Category>('/categories', newCat);
      if (!result) throw new Error("Creazione fallita");
      return result;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['categories'] })
  });

  // 3. Aggiornamento (AGGIUNTO : Promise<Category>)
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