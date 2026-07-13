// src/hooks/useAgendaDay.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/apiService';
import type { DbTask, Habit, HabitLog, SyncDayResponse, SaveHabitPayload, Countdown } from '@/types';
import { useTaskMutations } from './mutations/useTaskMutations';
import { useNoteMutations } from './mutations/useNoteMutations';
import { useDailyEntryMutations } from './mutations/useDailyEntryMutations';
import { useEventMutations } from './mutations/useEventMutations';

export interface SaveCountdownPayload {
  id?: number;
  title: string;
  targetDateStr: string;
  imageUrl?: string | null;
}

export const useAgendaDay = (dateStr: string) => {
  const queryClient = useQueryClient();
  const queryKey = ['daySync', dateStr];

  const noteMutations = useNoteMutations<SyncDayResponse>(queryKey);
  const { toggleTask } = useTaskMutations(['tasks']);
  const entryMutations = useDailyEntryMutations<SyncDayResponse>(queryKey);
  const eventMutations = useEventMutations<SyncDayResponse>(queryKey);

  const { data: dayData, isLoading, isError } = useQuery({
    queryKey,
    queryFn: async (): Promise<SyncDayResponse> => {
      const response = await api.get(`/sync/day?data_riferimento=${dateStr}`);
      
      if (!response) throw new Error("Impossibile caricare i dati della giornata");

      const rawData = response as SyncDayResponse;

      // 🪄 SOSTITUITI TUTTI GLI OPERATORI DEBOLI "||" CON "??", tipizzazione ferrea
      return {
        ...rawData,
        events: rawData?.events ?? [],
        countdowns: rawData?.countdowns ?? [],
        obiettivi: rawData?.obiettivi ?? [],
        priorita: rawData?.priorita ?? [],
        note: rawData?.note ?? [],
        
        tasks: (rawData?.tasks ?? []).map((t: DbTask) => ({
          ...t,
          subtasks: t.subtasks ?? [] 
        })),

        habits: (rawData?.habits ?? []).map((h: Habit) => ({
          ...h,
          periods: h.periods ?? [], 
          logs: h.logs ?? []        
        }))
      };
    }
  });

  // --- COUNTDOWN ---
  const saveCountdownMutation = useMutation({
    mutationFn: async (countdown: SaveCountdownPayload) => {
      const isUpdate = countdown.id && countdown.id < 1000000000;
      const payload = {
        title: countdown.title ?? "Nuovo Countdown",
        target_date: countdown.targetDateStr ?? new Date().toISOString(),
        immagine_url: countdown.imageUrl ?? null
      };
      const result = isUpdate
        ? await api.patch<Countdown>(`/countdowns/${countdown.id}`, payload)
        : await api.post<Countdown>('/countdowns', payload);

        if (!result) throw new Error("Errore nel salvataggio del countdown");
      return result;
    },
    onSuccess: (savedCountdown) => {
      queryClient.setQueryData<SyncDayResponse>(queryKey, (old) => {
        if (!old) return old;
        const currentCountdowns = old.countdowns ?? [];
        const exists = currentCountdowns.some(c => c.id === savedCountdown.id);
        return {
          ...old,
          countdowns: exists 
            ? currentCountdowns.map(c => c.id === savedCountdown.id ? savedCountdown : c) 
            : [...currentCountdowns, savedCountdown]
        };
      });
    }
  });

  const deleteCountdownMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/countdowns/${id}`);
      return id;
    },
    onSuccess: (_, deletedId) => {
      queryClient.setQueryData<SyncDayResponse>(queryKey, (old) => {
        if (!old) return old;
        return { ...old, countdowns: (old.countdowns ?? []).filter(c => c.id !== deletedId) };
      });
    }
  });

  // --- HABIT E ROUTINE ---
  const saveHabitMutation = useMutation({
    mutationFn: async (payload: SaveHabitPayload) => {
      const { data_inizio, target_completamenti, data_fine, periodId, periods, ...baseData } = payload.data;
      const result = payload.existingId
        ? await api.patch<Habit>(`/habits/${payload.existingId}`, baseData)
        : await api.post<Habit>('/habits', {
            ...baseData,
            periods: [{ data_inizio: dateStr, target: 1 }]
          });
          
      if (!result) throw new Error("Errore nel salvataggio dell'abitudine");
      return result;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey })
  });

  const deleteHabitMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/habits/${id}`);
      return id;
    },
    onSuccess: (_, deletedId) => {
      queryClient.setQueryData<SyncDayResponse>(queryKey, (old) => {
        if (!old) return old;
        return { ...old, habits: (old.habits ?? []).filter(h => h.id !== deletedId) };
      });
    }
  });

  const suspendHabitMutation = useMutation({
    mutationFn: async ({ habitId, periodId, endDate }: { habitId: number; periodId: number; endDate: string }) => {
      const result = await api.patch(`/habits/${habitId}/periods/${periodId}`, { data_fine: endDate });
      if (!result) throw new Error("Errore durante la sospensione");
      return result;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey })
  });

  const resumeHabitMutation = useMutation({
    mutationFn: async ({ habitId, target, startDate }: { habitId: number; target: number; startDate: string }) => {
      const result = await api.post(`/habits/${habitId}/periods`, { data_inizio: startDate, target });
      if (!result) throw new Error("Errore durante la ripresa");
      return result;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey })
  });

  const updateHabitPeriodMutation = useMutation({
    mutationFn: async ({ habitId, periodId, target }: { habitId: number; periodId: number; target: number }) => {
      const result = await api.patch(`/habits/${habitId}/periods/${periodId}`, { target });
      if (!result) throw new Error("Errore aggiornamento periodo");
      return result;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey })
  });

  // --- TRACKING GIORNALIERO ---
  const updateHabitLogMutation = useMutation({
    mutationFn: async ({ habitId, delta }: { habitId: number; delta: number }) => {
      const endpoint = delta > 0 ? `/habit-log?habit_id=${habitId}` : `/habit-log/decrement?habit_id=${habitId}`;
      await api.post(endpoint, { data_riferimento: dateStr });
      return { habitId, delta };
    },
    onMutate: async ({ habitId, delta }) => {
      await queryClient.cancelQueries({ queryKey });
      const previousData = queryClient.getQueryData(queryKey);
      
      queryClient.setQueryData(queryKey, (old: SyncDayResponse | undefined) => {
        if (!old) return old;
        return {
          ...old,
          habits: old.habits.map((h: Habit) => {
            if (h.id === habitId) {
              const currentLog = h.logs.find((l: HabitLog) => l.data_riferimento === dateStr) ?? { count: 0 };
              const newLogs = h.logs.filter((l: HabitLog) => l.data_riferimento !== dateStr);
              
              newLogs.push({ 
                ...currentLog, 
                habit_id: habitId,
                data_riferimento: dateStr, 
                // 🪄 Rimosso || 0 per garantire che conteggi a zero siano considerati validi e corretti!
                count: Math.max(0, (currentLog.count ?? 0) + delta) 
              } as HabitLog);
              
              return { ...h, logs: newLogs };
            }
            return h;
          })
        };
      });
      return { previousData };
    },
    onError: (err, variables, context) => {
      console.error("Errore del server durante l'untoggle!", err); 
      queryClient.setQueryData(queryKey, context?.previousData);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey });
    }
  });

  return {
    dayData,
    isLoading,
    isError,
    toggleTask,
    deleteEvent: eventMutations.deleteEvent,
    saveNote: noteMutations.saveNote,
    deleteNote: noteMutations.deleteNote,
    saveCountdown: saveCountdownMutation.mutateAsync,
    deleteCountdown: deleteCountdownMutation.mutateAsync,
    saveHabit: saveHabitMutation.mutateAsync,
    deleteHabit: deleteHabitMutation.mutateAsync,
    suspendHabit: suspendHabitMutation.mutateAsync,
    resumeHabit: resumeHabitMutation.mutateAsync,
    updateHabitPeriod: updateHabitPeriodMutation.mutateAsync,
    updateHabitLog: updateHabitLogMutation.mutateAsync,
    updateHabitCount: updateHabitLogMutation.mutateAsync, 
    saveObiettivo: (data: { id?: number; text: string }) => 
       entryMutations.saveDailyEntry({ id: data.id, tipo: 'OD', text: data.text, dateStr }),
    savePriorita: (data: { id?: number; text: string }) => 
       entryMutations.saveDailyEntry({ id: data.id, tipo: 'PD', text: data.text, dateStr }),
  };
};