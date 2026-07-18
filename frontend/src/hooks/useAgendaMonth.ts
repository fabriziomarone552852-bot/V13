// frontend/src/hooks/useAgendaMonth.ts
import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/apiService';
import { useTaskMutations } from './mutations/useTaskMutations';
import { useNoteMutations } from './mutations/useNoteMutations';
import { useDailyEntryMutations } from './mutations/useDailyEntryMutations';
import { useEventMutations } from './mutations/useEventMutations';
import type { DbTask, DbEvent, DailyEntry, MonthlyEntry } from '@/types'; 

export interface SyncMonthResponse {
  start_date: string;
  end_date: string;
  tasks: DbTask[];
  events: DbEvent[]; 
  note: DailyEntry[]; 
  obiettivi: DailyEntry[];
  priorita: DailyEntry[];
  eventi_positivi: DailyEntry[]; 
  eventi_negativi: DailyEntry[]; 
  tracker_entries: MonthlyEntry[]; 
}

export const useAgendaMonth = (startStr: string, endStr: string) => {
  const queryKey = ['monthSync', startStr];

  const taskMutations = useTaskMutations(['tasks']);
  
  // Ora TypeScript è felice perché SyncMonthResponse ha note: DailyEntry[]
  const noteMutations = useNoteMutations<SyncMonthResponse>(queryKey);
  const entryMutations = useDailyEntryMutations<SyncMonthResponse>(queryKey);
  const eventMutations = useEventMutations<SyncMonthResponse>(queryKey);

  const { data: monthData, isLoading, isError } = useQuery({
    queryKey,
    queryFn: async (): Promise<SyncMonthResponse> => {
      const data = await api.get<SyncMonthResponse>(`/sync/month?start_date=${startStr}&end_date=${endStr}`);
      
      if (!data) throw new Error("Impossibile caricare i dati mensili");
      
      return {
        start_date: data.start_date || startStr,
        end_date: data.end_date || endStr,
        tasks: data.tasks ?? [],
        events: data.events ?? [],
        note: data.note ?? [], 
        obiettivi: data.obiettivi ?? [],
        priorita: data.priorita ?? [],
        eventi_positivi: data.eventi_positivi ?? [],
        eventi_negativi: data.eventi_negativi ?? [],
        tracker_entries: data.tracker_entries ?? []
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