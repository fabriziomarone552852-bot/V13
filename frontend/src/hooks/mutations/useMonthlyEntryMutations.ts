// frontend/src/hooks/mutations/useMonthlyEntryMutations.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/apiService';
import type { DbMonthlyEntry } from '@/types/monthlyentries';

export interface SaveMonthlyEntryPayload {
  feel_type: number;
  value: number;
  dateStr: string;
  existingEntryId?: number; 
}

// 🪄 ZERO ANY: Creiamo un'interfaccia sicura e locale per la cache in memoria
interface MonthCacheData {
  monthly_entries?: DbMonthlyEntry[];
  [key: string]: unknown; // Permette le altre proprietà senza far arrabbiare TypeScript
}

export const useMonthlyEntryMutations = (queryKey: string[]) => {
  const queryClient = useQueryClient();

  const saveEntryMutation = useMutation({
    mutationFn: async (payload: SaveMonthlyEntryPayload): Promise<DbMonthlyEntry> => {
      // Se abbiamo un ID valido, facciamo l'aggiornamento (PATCH)
      if (payload.existingEntryId && payload.existingEntryId > 0) {
        const response = await api.patch(`/monthly-entries/${payload.existingEntryId}`, {
          feel_value: payload.value
        });
        return response as DbMonthlyEntry;
      }

      // Altrimenti è un nuovo inserimento (POST)
      const dateObj = new Date(payload.dateStr);
      const dataForServer = {
        year: dateObj.getFullYear(),
        month: dateObj.getMonth() + 1,
        feel_type: payload.feel_type,
        feel_value: payload.value
      };
      
      const response = await api.post('/monthly-entries', dataForServer);
      return response as DbMonthlyEntry;
    },

    // --- AGGIORNAMENTO ISTANTANEO (Il motore del grafico) ---
    onMutate: async (newEntry) => {
      await queryClient.cancelQueries({ queryKey });
      
      const previousData = queryClient.getQueryData<MonthCacheData>(queryKey);
      const tempId = -(Date.now()); // ID negativo per non confonderlo col Database

      queryClient.setQueryData<MonthCacheData>(queryKey, (old) => {
        if (!old) return old;
        
        const currentEntries = old.monthly_entries || [];
        const index = currentEntries.findIndex(e => e.feel_type === newEntry.feel_type);

        let updatedEntries = [...currentEntries];

        if (index !== -1) {
          updatedEntries[index] = { ...updatedEntries[index], feel_value: newEntry.value };
        } else {
          updatedEntries.push({
            id: tempId, 
            user_id: 0,
            year: parseInt(newEntry.dateStr.substring(0, 4)),
            month: parseInt(newEntry.dateStr.substring(5, 7)),
            feel_type: newEntry.feel_type,
            feel_value: newEntry.value,
            feel_name: null // Sicuro, perché ora cerchiamo tramite feel_type!
          });
        }

        return { ...old, monthly_entries: updatedEntries };
      });

      return { previousData, tempId };
    },

    onSuccess: (savedEntry, newEntry, context) => {
      // Scambiamo di nascosto l'ID finto con quello vero
      if (context?.tempId) {
         queryClient.setQueryData<MonthCacheData>(queryKey, (old) => {
            if (!old) return old;
            const updatedEntries = (old.monthly_entries || []).map(e => 
               e.id === context.tempId ? savedEntry : e
            );
            return { ...old, monthly_entries: updatedEntries };
         });
      }
    },

    onError: (err, newEntry, context) => {
      console.error("Errore salvataggio tracker:", err);
      if (context?.previousData) queryClient.setQueryData(queryKey, context.previousData);
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey });
    }
  });

  return { saveMonthlyEntry: saveEntryMutation.mutate };
};