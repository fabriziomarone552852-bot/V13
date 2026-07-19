// frontend/src/hooks/mutations/useMonthlyEntryMutations.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/apiService';
import type { MonthlyEntryType, DbMonthlyEntry } from '@/types';

// IL CONTRATTO DEL PAYLOAD: Zero 'any'
export interface SaveMonthlyEntryPayload {
  type: MonthlyEntryType;
  value: number;
  dateStr: string; // Es: '2026-06-01', il backend estrarrà anno e mese
}

export const useMonthlyEntryMutations = (queryKeyToInvalidate: string[]) => {
  const queryClient = useQueryClient();

  const saveEntryMutation = useMutation({
    mutationFn: async (payload: SaveMonthlyEntryPayload): Promise<DbMonthlyEntry> => {
      // Chiamata API rigorosamente tipizzata
      const response = await api.post('/monthly-entries', payload);
      return response as DbMonthlyEntry;
    },
    onSuccess: () => {
      // Quando il salvataggio va a buon fine, invalidiamo la cache 
      // per forzare il ricaricamento del mese e aggiornare i grafici
      queryClient.invalidateQueries({ queryKey: queryKeyToInvalidate });
    },
    onError: (error: Error) => {
      console.error("Errore durante il salvataggio del tracker mensile:", error);
    }
  });

  return {
    saveMonthlyEntry: saveEntryMutation.mutate,
    isSavingMonthlyEntry: saveEntryMutation.isPending,
  };
};