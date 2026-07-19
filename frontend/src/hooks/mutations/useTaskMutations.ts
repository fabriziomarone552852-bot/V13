import { useMutation, useQueryClient, type QueryKey } from '@tanstack/react-query';
import { api } from '@/api/apiService';
import type { DbTask } from '@/types';

// 🪄 1. Definiamo i contratti in modo rigoroso, zero unknown.
export interface CacheWithTasks {
  tasks?: DbTask[];
}

// Uniamo i due casi possibili per la cache
type TaskCacheData = DbTask[] | CacheWithTasks;

// 🪄 2. Funzione generica protetta
const updateCacheSafely = <T extends TaskCacheData>(
  oldData: T | undefined, 
  updaterFn: (tasks: DbTask[]) => DbTask[]
): T | undefined => {
  if (!oldData) return oldData;
  
  // CASO 1: È direttamente un array
  if (Array.isArray(oldData)) {
    return updaterFn(oldData) as T;
  }

  // CASO 2: È un oggetto che contiene la proprietà 'tasks'
  if (typeof oldData === 'object' && oldData !== null && 'tasks' in oldData) {
    return {
      ...oldData,
      tasks: updaterFn(oldData.tasks || [])
    } as T;
  }

  return oldData;
};

export function useTaskMutations(queryKey: QueryKey) {
  const queryClient = useQueryClient();

  // --- 1. TOGGLE TASK ---
  const toggleTaskMutation = useMutation({
    mutationFn: async ({ id, isDone }: { id: number; isDone: boolean }) => {
      const result = await api.patch<DbTask>(`/tasks/${id}`, { fatto: isDone });
      if (!result) throw new Error("Errore durante il toggle: risposta vuota");
      return result;
    },
    
    onMutate: async ({ id, isDone }) => {
      const toggleUpdater = (tasks: DbTask[]) => tasks.map(t => 
        t.id === id ? { 
          ...t, 
          fatto: isDone, 
          completato: isDone, 
          data_fatto: isDone ? new Date().toISOString() : null 
        } : t
      );

      // 🪄 3. Diciamo a setQueriesData l'esatto tipo in ingresso: <TaskCacheData>
      queryClient.setQueriesData<TaskCacheData>({ queryKey: ['daySync'] }, (old) => updateCacheSafely(old, toggleUpdater));
      queryClient.setQueriesData<TaskCacheData>({ queryKey: ['weekSync'] }, (old) => updateCacheSafely(old, toggleUpdater));
      queryClient.setQueriesData<TaskCacheData>({ queryKey: ['tasks'] }, (old) => updateCacheSafely(old, toggleUpdater));

      return { id };
    },
    
    onError: (err) => {
      console.error("Errore durante il toggle del task:", err);
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'daySync' });
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'weekSync' });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
    
    onSettled: () => {
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'daySync' });
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'weekSync' });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    }
  });

  // --- 2. SALVA TASK (CREA O AGGIORNA) ---
  const saveTaskMutation = useMutation({
    mutationFn: async (taskData: Partial<DbTask> & { id?: number }) => {
      const { id, subtasks, ...payload } = taskData;
      
      if (payload.data_scadenza !== undefined) {
        if (!payload.data_scadenza || payload.data_scadenza.trim() === "") {
          payload.data_scadenza = null; 
        } else {
          payload.data_scadenza = payload.data_scadenza.substring(0, 10);
        }
      }

      const result = id 
        ? await api.patch<DbTask>(`/tasks/${id}`, payload)
        : await api.post<DbTask>('/tasks', payload);
        
      if (!result) throw new Error("Errore: impossibile salvare il task");
      return result;
    },
    
    onMutate: async (newTask) => {
      const tempId = newTask.id || Date.now();
      const isUpdate = !!newTask.id;

      const saveUpdater = (currentTasks: DbTask[]) => {
        const existingTask = isUpdate ? currentTasks.find(t => t.id === newTask.id) : undefined;
        
        const fakeTask: DbTask = {
          ...existingTask,
          ...newTask,
          id: tempId,
          titolo: newTask.titolo || "Nuovo Task",
          completato: newTask.fatto ?? false,
          fatto: newTask.fatto ?? false,
        } as DbTask;

        return isUpdate
          ? currentTasks.map(t => (t.id === newTask.id ? fakeTask : t))
          : [...currentTasks, fakeTask];
      };

      queryClient.setQueriesData<TaskCacheData>({ queryKey: ['daySync'] }, (old) => updateCacheSafely(old, saveUpdater));
      queryClient.setQueriesData<TaskCacheData>({ queryKey: ['weekSync'] }, (old) => updateCacheSafely(old, saveUpdater));
      queryClient.setQueriesData<TaskCacheData>({ queryKey: ['tasks'] }, (old) => updateCacheSafely(old, saveUpdater));

      return { tempId };
    },

    onSuccess: (savedTaskFromDB, newTask, context) => {
      if (!newTask.id && context?.tempId && savedTaskFromDB) {
        const swapIdUpdater = (currentTasks: DbTask[]) => currentTasks.map(t => 
          t.id === context.tempId ? savedTaskFromDB : t
        );
        
        queryClient.setQueriesData<TaskCacheData>({ queryKey: ['daySync'] }, (old) => updateCacheSafely(old, swapIdUpdater));
        queryClient.setQueriesData<TaskCacheData>({ queryKey: ['weekSync'] }, (old) => updateCacheSafely(old, swapIdUpdater));
        queryClient.setQueriesData<TaskCacheData>({ queryKey: ['tasks'] }, (old) => updateCacheSafely(old, swapIdUpdater));
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'daySync' });
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'weekSync' });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    }
  });

  // --- 3. ELIMINA TASK ---
  const deleteTaskMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/tasks/${id}`);
      return { id };
    },
    
    onMutate: async (taskId) => {
      const deleteUpdater = (currentTasks: DbTask[]) => 
        currentTasks.filter(t => t.id !== taskId && t.parent_id !== taskId);

      queryClient.setQueriesData<TaskCacheData>({ queryKey: ['daySync'] }, (old) => updateCacheSafely(old, deleteUpdater));
      queryClient.setQueriesData<TaskCacheData>({ queryKey: ['weekSync'] }, (old) => updateCacheSafely(old, deleteUpdater));
      queryClient.setQueriesData<TaskCacheData>({ queryKey: ['tasks'] }, (old) => updateCacheSafely(old, deleteUpdater));

      return { taskId };
    },
    
    onError: (err) => {
      console.error("Errore eliminazione task:", err);
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'daySync' });
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'weekSync' });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
    
    onSettled: () => {
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'daySync' });
      queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] === 'weekSync' });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    }
  });

  return {
    toggleTask: toggleTaskMutation.mutate,
    saveTask: saveTaskMutation.mutateAsync,
    deleteTask: deleteTaskMutation.mutate,
  };
}