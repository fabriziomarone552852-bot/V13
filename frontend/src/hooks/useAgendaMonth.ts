// frontend/src/hooks/useAgendaMonth.ts
import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/apiService';
import { useTaskMutations } from './mutations/useTaskMutations';
import { useNoteMutations } from './mutations/useNoteMutations';
import { useDailyEntryMutations } from './mutations/useDailyEntryMutations';
import { useEventMutations } from './mutations/useEventMutations';
import type { SyncMonthResponse, DailyEntry } from '@/types'; 

// 1. IL CONTRATTO DELLA CACHE (Frontend Model)
// Estendiamo i dati grezzi del server creando i cassetti che servono alle mutazioni
export interface MonthCacheData extends SyncMonthResponse {
  note: DailyEntry[];
  obiettivi: DailyEntry[];
  priorita: DailyEntry[];
  eventi_positivi: DailyEntry[]; 
  eventi_negativi: DailyEntry[];
}

export const useAgendaMonth = (startStr: string, endStr: string) => {
  const queryKey = ['monthSync', startStr];

  const taskMutations = useTaskMutations(['tasks']);
  
  // 2. Diciamo alle mutazioni di lavorare su MonthCacheData
  const noteMutations = useNoteMutations<MonthCacheData>(queryKey);
  const entryMutations = useDailyEntryMutations<MonthCacheData>(queryKey);
  const eventMutations = useEventMutations<MonthCacheData>(queryKey);

  const { data: monthData, isLoading, isError } = useQuery({
    queryKey,
    queryFn: async (): Promise<MonthCacheData> => {
      // Chiamata API rigorosa con il contratto del server
      const data = await api.get<SyncMonthResponse>(`/sync/month?start_date=${startStr}&end_date=${endStr}`);
      
      if (!data) throw new Error("Impossibile caricare i dati mensili");
      
      // 🪄 3. LA MAGIA (Data Mapper): Smistiamo i dati in RAM!
      const entries = data.daily_entries || [];

      return {
        ...data, // Mantiene start_date, end_date, tasks, events, monthly_entries
        
        // Creiamo i cassetti filtrando il grande array in RAM
        note: entries.filter(e => ['N1', 'N2', 'N3', 'N4'].includes(e.tipo)),
        obiettivi: entries.filter(e => e.tipo === 'OM'),
        priorita: entries.filter(e => e.tipo === 'PM'),
        eventi_positivi: entries.filter(e => e.tipo === 'EP'),
        eventi_negativi: entries.filter(e => e.tipo === 'EN'),
      };
    },
    staleTime: 5 * 60 * 1000,
  });

  return {
    monthData,
    isLoading,
    isError,
    saveDailyEntry: entryMutations.saveDailyEntry,
    toggleTask: taskMutations.toggleTask,
    saveNote: noteMutations.saveNote,
    deleteNote: noteMutations.deleteNote,
    deleteEventFromCache: eventMutations.deleteEvent,
  };
};