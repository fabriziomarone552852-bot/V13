import { useMutation, useQueryClient, type QueryKey } from '@tanstack/react-query';
import { api } from '@/api/apiService';
import type { DbEvent } from '@/types';
import type { EventDeletePayload } from '@/components/shared/events/EventDetailModal';

export interface CacheWithEvents {
  events?: DbEvent[];
}

type CachedEvent = DbEvent & { originalId?: number | string; dateStr?: string };

// Definiamo il contratto unificato
type EventCacheData = CachedEvent[] | CacheWithEvents;

export function useEventMutations<T extends CacheWithEvents>(queryKey: QueryKey) {
  const queryClient = useQueryClient();

  const saveEventMutation = useMutation({
    mutationFn: async (eventData: Partial<DbEvent> & { id?: string | number, originalId?: string | number }) => {
      const { id, originalId, ...payload } = eventData;
      
      if (payload.data_inizio && payload.data_inizio.trim() === "") {
        payload.data_inizio = new Date().toISOString(); 
      }
      if (payload.data_fine && payload.data_fine.trim() === "") {
        payload.data_fine = null; 
      }

      let result;
      if (id && String(id).indexOf('temp') === -1 && !String(id).includes('-')) {
        const realId = originalId || id;
        result = await api.patch<DbEvent>(`/events/${realId}`, payload);
      } else {
        result = await api.post<DbEvent>('/events', payload);
      }
      
      if (!result) throw new Error("Errore nel salvataggio dell'evento");
      return result;
    },
    
    onMutate: async (newEvent) => {
      const tempId = newEvent.id || `temp-${Date.now()}`;
      const isUpdate = !!newEvent.id && String(newEvent.id).indexOf('temp') === -1;

      // 🪄 Aggiunto il generico C per permettere la corretta inferenza del tipo
      const updateGlobalCache = <C extends EventCacheData>(oldData: C | undefined): C | undefined => {
        if (!oldData) return oldData;
        
        const currentEvents: CachedEvent[] = Array.isArray(oldData) 
            ? oldData as CachedEvent[]
            : (oldData as CacheWithEvents).events as CachedEvent[] || [];

        const existingEvent = isUpdate ? currentEvents.find(e => e.id === newEvent.id) : undefined;

        const fakeEvent: DbEvent = {
          ...existingEvent,
          ...newEvent,
          id: tempId,
          titolo: newEvent.titolo || 'Nuovo Evento',
          data_inizio: newEvent.data_inizio || new Date().toISOString(),
        } as DbEvent;

        const newEvents = isUpdate
            ? currentEvents.map(e => (e.id === newEvent.id ? fakeEvent : e))
            : [...currentEvents, fakeEvent];

        if (Array.isArray(oldData)) {
           return newEvents as C;
        }

        return { ...oldData, events: newEvents } as C;
      };

      queryClient.setQueriesData<EventCacheData>({ queryKey: ['daySync'] }, updateGlobalCache);
      queryClient.setQueriesData<EventCacheData>({ queryKey: ['weekSync'] }, updateGlobalCache);

      return { tempId };
    },

    onSuccess: (savedEvent, newEvent, context) => {
      if (!newEvent.id && context?.tempId && savedEvent) {
        const swapId = <C extends EventCacheData>(oldData: C | undefined): C | undefined => {
          if (!oldData) return oldData;
          
          const currentEvents: CachedEvent[] = Array.isArray(oldData) 
            ? oldData as CachedEvent[]
            : (oldData as CacheWithEvents).events as CachedEvent[] || [];
            
          const newEvents = currentEvents.map(e => e.id === context.tempId ? savedEvent : e);
          
          if (Array.isArray(oldData)) {
             return newEvents as C;
          }
          return { ...oldData, events: newEvents } as C;
        };
        
        queryClient.setQueriesData<EventCacheData>({ queryKey: ['daySync'] }, swapId);
        queryClient.setQueriesData<EventCacheData>({ queryKey: ['weekSync'] }, swapId);
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'daySync' });
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'weekSync' });
      queryClient.invalidateQueries({ queryKey: ['events'] });
    }
  });

  // --- 2. ELIMINA EVENTO ---
  const deleteEventMutation = useMutation({
    mutationFn: async (id: number | string) => {
      const originalId = String(id).split('-')[0];
      await api.delete(`/events/${originalId}`);
      return { id };
    },
    onMutate: async (deletedId) => {
      await queryClient.cancelQueries({ queryKey });
      const previousData = queryClient.getQueryData<T>(queryKey);

      const baseIdToDelete = String(deletedId).split('-')[0];

      queryClient.setQueryData<T>(queryKey, (old) => {
        if (!old) return old;
        return {
          ...old,
          events: (old.events || []).filter(e => String(e.id).split('-')[0] !== baseIdToDelete)
        };
      });

      return { previousData };
    },
    onError: (err, deletedId, context) => {
      console.error("Errore eliminazione evento:", err);
      if (context?.previousData) queryClient.setQueryData(queryKey, context.previousData);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'daySync' });
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'weekSync' });
      queryClient.invalidateQueries({ queryKey: ['events'] });
    }
  });

  const deleteRecurringEventMutation = useMutation({
    mutationFn: async (payload: EventDeletePayload) => {
      const { id, mode, dateStr, currentRrule, currentEsclusioni } = payload;

      if (mode === 'all') {
        return await api.delete(`/events/${id}`);
      }
      if (mode === 'single') {
        const newEsclusioni = currentEsclusioni ? `${currentEsclusioni},${dateStr}` : dateStr;
        return await api.patch(`/events/${id}`, { esclusioni: newEsclusioni });
      }
      if (mode === 'future') {
        const untilDate = dateStr.replace(/-/g, '');
        let newRrule = currentRrule || '';
        if (newRrule.includes('UNTIL=')) {
          newRrule = newRrule.replace(/UNTIL=\d{8}/, `UNTIL=${untilDate}`);
        } else {
          newRrule = `${newRrule};UNTIL=${untilDate}`;
        }
        return await api.patch(`/events/${id}`, { rrule: newRrule });
      }
    },
    
    onMutate: async (payload) => {
      await queryClient.cancelQueries({ 
        predicate: (query) => ['events', 'daySync', 'weekSync'].includes(query.queryKey[0] as string) 
      });

      // 🪄 Funzione completamente Type-Safe
      const updateCache = <C extends EventCacheData>(oldData: C | undefined): C | undefined => {
        if (!oldData) return oldData;
        
        const currentEvents: CachedEvent[] = Array.isArray(oldData) 
            ? oldData as CachedEvent[]
            : (oldData as CacheWithEvents).events as CachedEvent[] || [];
            
        let newEvents = [...currentEvents];
        
        if (payload.mode === 'all') {
           newEvents = newEvents.filter(e => String(e.originalId) !== String(payload.id) && String(e.id) !== String(payload.id));
        } else if (payload.mode === 'single') {
           const targetId = `${payload.id}-${payload.dateStr}`;
           newEvents = newEvents.filter(e => String(e.id) !== targetId);
        } else if (payload.mode === 'future') {
           newEvents = newEvents.filter(e => {
              if (String(e.originalId) === String(payload.id) || (e.id && String(e.id).startsWith(`${payload.id}-`))) {
                 const eventDate = e.dateStr || (e.data_inizio ? e.data_inizio.substring(0, 10) : '');
                 return eventDate < payload.dateStr;
              }
              return true;
           });
        }
        
        if (Array.isArray(oldData)) {
           return newEvents as C;
        }
        
        return { ...oldData, events: newEvents } as C;
      };

      queryClient.setQueriesData<EventCacheData>({ 
        predicate: (query) => ['events', 'daySync', 'weekSync'].includes(query.queryKey[0] as string) 
      }, updateCache);
    },

    onSettled: () => {
      queryClient.invalidateQueries({ 
        predicate: (query) => ['events', 'daySync', 'weekSync'].includes(query.queryKey[0] as string) 
      });
    },
    
    onError: (error) => {
      console.error("Errore durante l'eliminazione dell'evento:", error);
      alert("Si è verificato un errore durante l'eliminazione.");
      queryClient.invalidateQueries({ 
        predicate: (query) => ['events', 'daySync', 'weekSync'].includes(query.queryKey[0] as string) 
      });
    }
  });

  return {
    saveEvent: saveEventMutation.mutateAsync, 
    deleteEvent: deleteEventMutation.mutate,
    deleteRecurringEvent: deleteRecurringEventMutation.mutate,
  };
}