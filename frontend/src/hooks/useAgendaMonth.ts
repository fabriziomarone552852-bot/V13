// frontend/src/hooks/useAgendaMonth.ts
import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/apiService';
import { useTaskMutations } from './mutations/useTaskMutations';
import { useNoteMutations } from './mutations/useNoteMutations';
import { useDailyEntryMutations } from './mutations/useDailyEntryMutations';
import { useEventMutations } from './mutations/useEventMutations';
import type { DbTask, CalendarEvent, NoteItem, DailyEntry, MonthlyEntry } from '@/types';

export interface SyncMonthResponse {
  start_date: string;
  end_date: string;
  tasks: DbTask[];
  events: CalendarEvent[];
  note: NoteItem[];
  obiettivi: DailyEntry[];
  priorita: DailyEntry[];
  eventi_positivi: DailyEntry[]; 
  eventi_negativi: DailyEntry[]; 
  tracker_entries: MonthlyEntry[]; 
}

export const useAgendaMonth = (startStr: string, endStr: string) => {
  const queryKey = ['monthSync', startStr];

  const taskMutations = useTaskMutations(['tasks']);
  const noteMutations = useNoteMutations<SyncMonthResponse>(queryKey);
  const entryMutations = useDailyEntryMutations<SyncMonthResponse>(queryKey);
  const eventMutations = useEventMutations<SyncMonthResponse>(queryKey);

  const { data: monthData, isLoading, isError } = useQuery({
    queryKey,
    queryFn: async (): Promise<SyncMonthResponse> => {
      const response = await api.get(`/sync/month?start_date=${startStr}&end_date=${endStr}`);
      if (!response) throw new Error("Impossibile caricare i dati mensili");
      
      const rawData = response as SyncMonthResponse;

      return {
        start_date: rawData.start_date || startStr,
        end_date: rawData.end_date || endStr,
        tasks: rawData.tasks ?? [],
        events: rawData.events ?? [],
        note: rawData.note ?? [],
        obiettivi: rawData.obiettivi ?? [],
        priorita: rawData.priorita ?? [],
        eventi_positivi: rawData.eventi_positivi ?? [],
        eventi_negativi: rawData.eventi_negativi ?? [],
        tracker_entries: rawData.tracker_entries ?? []
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