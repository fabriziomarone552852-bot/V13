import React, { useState, useMemo, useEffect } from 'react';
import { getMonday, getSunday, getISOWeekNumber, formatDateString } from '@/utils/dateUtils';
import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

// --- IMPORT COMPONENTI ---
import { SmartObiettivoTextarea } from '@/components/day/utils/SmartObiettivoTextarea';
import CalendarColumn from '@/components/dashboard/CalendarColumn';
import NotesSidebar from '@/components/day/NotesSidebar';
import { SharedAgendaHeader } from '@/components/shared/SharedAgendaHeader';
import MoodEventsBoard, { type MoodEvent, type MoodEventType } from '@/components/weekmonth/MoodEventsBoard';

// --- IMPORT MODALI ---
import EventDetailModal from '@/components/shared/events/EventDetailModal';
import EventNewModal from '@/components/shared/events/EventNewModal';
import TaskDetailModal from '@/components/shared/tasks/TaskDetailModal';
import TaskNewModal from '@/components/shared/tasks/TaskNewModal';

// --- TIPI ---
import type { Task, CalendarEvent, DailyEntry, TaskSummary, SyncWeekResponse, NoteVariant } from '@/types'; 
import { isNoteVariant } from '@/types';
import { useAgendaWeek } from '@/hooks/useAgendaWeek'; 
import { useAgendaMutations } from '@/hooks/useAgendaMutations';
import { useApi } from '@/hooks/useApi.ts';

// 1. TIPIZZAZIONE RIGOROSA (Via le intersezioni inline)
interface BackendDailyEntry extends Omit<DailyEntry, 'id'> {
  id: number;
}

interface FrontendNote extends DailyEntry {
  isNew?: boolean;
}

const WeekPage: React.FC = () => {
  // --- STATO DELLA DATA ---
  const [targetDate, setTargetDate] = useState<Date>(new Date());
  
  const monday = getMonday(targetDate);
  const sunday = getSunday(targetDate);
  const weekNumber = getISOWeekNumber(targetDate);
  const isCurrentWeek = weekNumber === getISOWeekNumber(new Date()) && monday.getFullYear() === new Date().getFullYear();

  const mondayStr = formatDateString(monday);
  const sundayStr = formatDateString(sunday);

  // --- HOOKS & SERVIZI ---
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const api = useApi();
  const { weekData, isLoading, saveWeeklyEntry } = useAgendaWeek(mondayStr, sundayStr);

  // --- STATI UI E MODALI ---
  const [isNotesOpen, setIsNotesOpen] = useState<boolean>(false);
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  
  // Dettagli (Visualizzazione)
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [selectedTask, setSelectedTask] = useState<TaskSummary | null>(null);
  
  // Modifiche (Form)
  const [eventToEdit, setEventToEdit] = useState<CalendarEvent | null>(null);
  const [taskToEdit, setTaskToEdit] = useState<TaskSummary | null>(null);
  const [isNewTaskModalOpen, setIsNewTaskModalOpen] = useState<boolean>(false);
  const [newEventDateStr, setNewEventDateStr] = useState<string | undefined>(undefined);
  const { updateTask, deleteEvent } = useAgendaMutations();

  // --- STATI EVENTI MOOD ---
  const [positiveEvents, setPositiveEvents] = useState<MoodEvent[]>([]);
  const [negativeEvents, setNegativeEvents] = useState<MoodEvent[]>([]);

  // --- HANDLERS DATA ---
  const handlePrevWeek = (): void => setTargetDate(prev => {
    const d = new Date(prev.getTime());
    d.setDate(d.getDate() - 7);
    return d;
  });
  
  const handleNextWeek = (): void => setTargetDate(prev => {
    const d = new Date(prev.getTime());
    d.setDate(d.getDate() + 7);
    return d;
  });
  
  const handleResetCurrentWeek = (): void => setTargetDate(new Date());

  const handleGoToDay = (dateStr: string): void => {
    navigate('/giorno', { state: { selectedDate: dateStr } }); 
  };

  // --- HANDLERS TASKS ---
  const handleToggleTaskFromGrid = async (task: Task, newStatus: boolean): Promise<void> => {
    queryClient.setQueryData<SyncWeekResponse>(['weekSync', mondayStr], (oldData: SyncWeekResponse | undefined) => {
      if (!oldData) return oldData;
      return {
        ...oldData,
        tasks: (oldData.tasks || []).map((t: Task) => 
          t.id === task.id ? { ...t, fatto: newStatus } : t
        )
      };
    });
    await updateTask({ id: task.id, data: { fatto: newStatus } });
  };

  const handleSelectTaskFromGrid = (task: Task): void => {
    const summary = mappedTasks.find(t => t.id === task.id);
    if (summary) setSelectedTask(summary);
  };

  // --- ADAPTERS DATI ---
  const filteredTasks = useMemo((): Task[] => {
    if (!weekData?.tasks) return [];
    return weekData.tasks.filter((t: Task) => {
      if (!t.data_scadenza) return true;
      const taskDate = new Date(t.data_scadenza);
      return taskDate >= monday && taskDate <= sunday;
    });
  }, [weekData?.tasks, monday, sunday]);

  const mappedTasks = useMemo((): TaskSummary[] => {
    return filteredTasks.map((t) => ({
      id: t.id,
      title: t.titolo,
      deadline: t.data_scadenza || "",
      dateStr: t.data_start,
      done: t.fatto,
      priority: t.priorita,
      category: t.category?.name || t.category_name || 'Generico',
      categoryColor: t.category?.colore || '#9ca3af',
      description: t.descrizione || "", 
      location: t.luogo || "",
      parent_id: t.parent_id,
      data_fatto: t.data_fatto,
      hasActiveSubtasks: !!t.subtasks && t.subtasks.some(st => !st.fatto)
    }));
  }, [filteredTasks]);

  const mappedEvents = useMemo((): CalendarEvent[] => {
    if (!weekData?.events) return [];
    return weekData.events.map((e) => ({
      id: `${e.id}-${e.data_inizio.substring(0, 10)}`,
      originalId: e.id,
      title: e.titolo,
      time: e.tutto_il_giorno ? undefined : e.data_inizio.substring(11, 16),
      endTime: (e.tutto_il_giorno || !e.data_fine) ? undefined : e.data_fine.substring(11, 16),
      dateStr: e.data_inizio.substring(0, 10),
      endDateStr: e.data_fine ? e.data_fine.substring(0, 10) : undefined,
      category: e.category?.name || e.category_name || 'Generico',
      categoryColor: e.category?.colore || '#9ca3af',
      description: e.descrizione || undefined,
      location: e.luogo || undefined,
      tutto_il_giorno: e.tutto_il_giorno,
      rrule: e.rrule || undefined
    }));
  }, [weekData?.events]);

  const mappedNotes = useMemo(() => {
    if (!weekData?.note) return [];
    return weekData.note
      .filter((n: DailyEntry) => isNoteVariant(n.tipo))
      .map((n: FrontendNote) => ({ 
        id: n.id, 
        text: n.testo, 
        variant: n.tipo as NoteVariant,
        dateStr: n.data_riferimento, 
        isNew: n.isNew 
      }));
  }, [weekData?.note]);

  // --- HANDLERS NOTE ---
  const handleAddNote = (variant: NoteVariant): void => {
    const newId = Date.now();
    setEditingNoteId(newId);
    
    queryClient.setQueryData<SyncWeekResponse>(['weekSync', mondayStr], (oldData: SyncWeekResponse | undefined) => {
      if (!oldData) return oldData;
      const newNote: FrontendNote = { 
        id: newId, 
        user_id: 0, 
        testo: "", 
        data_riferimento: mondayStr, 
        tipo: variant, 
        isNew: true 
      };
      return { 
        ...oldData, 
        note: [newNote, ...(oldData.note || [])] 
      };
    });
  };

  const handleAutoSaveNote = (id: number, text: string, variant: NoteVariant, isNew?: boolean): void => {
    queryClient.setQueryData<SyncWeekResponse>(['weekSync', mondayStr], (oldData: SyncWeekResponse | undefined) => {
      if (!oldData) return oldData;
      return { 
        ...oldData, 
        note: (oldData.note || []).map((n) => 
          n.id === id ? { ...n, testo: text, tipo: variant, isNew: false } : n
        ) 
      };
    });
    
    saveWeeklyEntry({ 
      id: isNew ? undefined : id, 
      text, 
      tipo: variant, 
      dateStr: mondayStr 
    });
  };

  const handleDeleteNote = (id: number, isNew?: boolean): void => {
    queryClient.setQueryData<SyncWeekResponse>(['weekSync', mondayStr], (oldData: SyncWeekResponse | undefined) => {
      if (!oldData) return oldData;
      return { ...oldData, note: (oldData.note || []).filter((n) => n.id !== id) };
    });
    
    if (!isNew) saveWeeklyEntry({ id, text: "", tipo: 'N1', dateStr: mondayStr }); 
  };

  // --- EFFETTI E HANDLERS MOOD EVENTS ---
  useEffect(() => {
    const fetchMoodEvents = async (): Promise<void> => {
      try {
        const data = (await api.get(`/daily-entries?start_date=${mondayStr}&end_date=${sundayStr}`)) as BackendDailyEntry[];

        const weekEntries = data.filter(entry => {
          const dateOnly = entry.data_riferimento.substring(0, 10);
          return dateOnly >= mondayStr && dateOnly <= sundayStr;
        });

        const positivi = weekEntries
          .filter(e => e.tipo === 'EP')
          .map(e => ({ id: e.id, title: e.testo, type: 'EP' as MoodEventType, date: e.data_riferimento.substring(0, 10) }));
        
        const negativi = weekEntries
          .filter(e => e.tipo === 'EN')
          .map(e => ({ id: e.id, title: e.testo, type: 'EN' as MoodEventType, date: e.data_riferimento.substring(0, 10) }));

        setPositiveEvents(positivi);
        setNegativeEvents(negativi);
      } catch (error) {
        console.error("Errore durante il caricamento degli eventi:", error);
      }
    };

    fetchMoodEvents();
  }, [mondayStr, sundayStr, api]);

  const handleAddMoodEvent = async (type: MoodEventType, testoInserito: string): Promise<void> => {
    try {
      const data = (await api.post('/daily-entries', {
        tipo: type,
        testo: testoInserito,
        data_riferimento: mondayStr 
      })) as BackendDailyEntry;

      const newEvent: MoodEvent = {
        id: data.id,
        title: data.testo, 
        type: data.tipo as MoodEventType,
        date: data.data_riferimento
      };

      if (type === 'EP') {
        setPositiveEvents(prev => [...prev, newEvent]);
      } else {
        setNegativeEvents(prev => [...prev, newEvent]);
      }
    } catch (error) {
      console.error("Errore nel salvataggio dell'evento:", error);
    }
  };

  const handleUpdateMoodEvent = async (id: number, newTitle: string): Promise<void> => {
    try {
      await api.patch(`/daily-entries/${id}`, { testo: newTitle });
      
      const updateState = (prev: MoodEvent[]) => 
        prev.map(ev => ev.id === id ? { ...ev, title: newTitle } : ev);

      setPositiveEvents(updateState);
      setNegativeEvents(updateState);
    } catch (error) {
      console.error("Errore durante l'aggiornamento:", error);
    }
  };

  const handleDeleteMoodEvent = async (id: number): Promise<void> => {
    try {
      await api.delete(`/daily-entries/${id}`);
      
      const filterState = (prev: MoodEvent[]) => prev.filter(ev => ev.id !== id);
      
      setPositiveEvents(filterState);
      setNegativeEvents(filterState);
    } catch (error) {
      console.error("Errore durante l'eliminazione:", error);
    }
  };

  // --- RENDER ---
  if (isLoading && !weekData) {
    return (
      <div className="flex h-full items-center justify-center font-bold text-gray-500 animate-pulse">
        Caricamento settimana...
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 max-w-[1600px] mx-auto min-h-full xl:h-full xl:overflow-hidden relative pt-2">
      
      {/* 1. SEZIONE TOP */}
      <div className="flex flex-col xl:flex-row gap-6 shrink-0 items-stretch">
        <SharedAgendaHeader 
          title={`SETT. ${weekNumber}`} 
          subtitle={`${monday.toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit'})} - ${sunday.toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit'})}`} 
          currentDate={targetDate} 
          isToday={isCurrentWeek}
          onPrev={handlePrevWeek} 
          onNext={handleNextWeek} 
          onResetToday={handleResetCurrentWeek} 
          onChangeDate={setTargetDate} 
          viewMode="week"
        />

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col flex-1 xl:flex-row gap-6 py-5 z-10">
          <div className="flex-1 xl:border-r border-gray-200 xl:pr-8 flex flex-col justify-center relative h-full">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2 shrink-0">Obiettivo della Settimana</h3>
            {(() => {
              const obiettivoObj = weekData?.obiettivo_settimanale;
              return (
                <SmartObiettivoTextarea 
                  key={`ob-week-${obiettivoObj?.id || 'empty'}-${mondayStr}`}
                  initialText={obiettivoObj?.testo || ""}
                  onSave={(testo) => saveWeeklyEntry({ id: obiettivoObj?.id, text: testo, tipo: 'OW', dateStr: mondayStr })}
                />
              );
            })()}
          </div>
          <div className="flex-1 flex flex-col justify-center min-w-[280px]">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-3">3 Priorità Settimanali</h3>
            <ul className="space-y-2.5">
              {[0, 1, 2].map(index => {
                const prioritaObj = weekData?.priorita_settimanali?.[index];
                return (
                  <li key={`pri-w-row-${index}`} className="flex items-center gap-3">
                    <span className="w-6 h-6 shrink-0 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center text-xs font-bold">{index + 1}</span>
                    <input 
                      key={`pri-week-${index}-${prioritaObj?.id || 'empty'}-${mondayStr}`} 
                      type="text" 
                      defaultValue={prioritaObj?.testo || ""} 
                      onBlur={(e) => saveWeeklyEntry({ id: prioritaObj?.id, text: e.target.value, tipo: 'PW', dateStr: mondayStr })} 
                      placeholder={`Priorità ${index + 1}`} 
                      className="w-full text-sm font-medium text-gray-700 border-none bg-transparent focus:ring-0 p-0 placeholder-gray-300" 
                    />
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </div>

      {/* 2. CALENDARIO */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 flex-1 min-h-0">
        <div className="xl:col-span-12 flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 p-5 h-full min-h-0 w-full min-w-0 overflow-hidden relative">
           <CalendarColumn 
             events={mappedEvents} 
             tasks={filteredTasks}
             hideHeader={true}        
             forceView="Settimana"   
             targetDate={targetDate} 
             variant="detailed"    
             onSelectEvent={setSelectedEvent}
             onDayClick={handleGoToDay}
             onSelectTask={handleSelectTaskFromGrid}
             onToggleTask={handleToggleTaskFromGrid}
           />
        </div>
      </div>
      
      <MoodEventsBoard 
        positiveEvents={positiveEvents}
        negativeEvents={negativeEvents}
        onAddMoodEvent={handleAddMoodEvent}
        onUpdateMoodEvent={handleUpdateMoodEvent}
        onDeleteMoodEvent={handleDeleteMoodEvent}
      />

      {/* CASSETTO NOTE NASCOSTO */}
      <NotesSidebar 
        isOpen={isNotesOpen} 
        notes={mappedNotes} 
        editingNoteId={editingNoteId}
        onOpen={() => setIsNotesOpen(true)} 
        onClose={() => setIsNotesOpen(false)}
        onAddNote={handleAddNote} 
        onAutoSaveNote={handleAutoSaveNote}
        onDeleteNote={handleDeleteNote}
        clearEditingNoteId={() => setEditingNoteId(null)}
      />

      {/* ================= MODALI EVENTO ================= */}
      {/* MODALI EVENTO */}
      {selectedEvent && (
        <EventDetailModal
          isOpen={true}
          onClose={() => setSelectedEvent(null)}
          selectedEvent={selectedEvent} 
          onEditClick={() => {
            setEventToEdit(selectedEvent);
            setSelectedEvent(null); 
          }}
          onDeleteClick={async (id: string | number) => { 
            const idReale = selectedEvent.originalId;
            
            if (idReale && deleteEvent) {
              try {
                // 1. Chiamiamo l'API per eliminare l'evento
                await deleteEvent(idReale);
                // 2. Invalidiamo la cache per far sparire l'evento dalla UI
                queryClient.invalidateQueries({ queryKey: ['weekSync', mondayStr] });
              } catch (error) {
                console.error("Errore durante l'eliminazione dell'evento:", error);
              }
            }
          }}
        />
      )}

      {/* CORREZIONE EVENTI: Il modale si apre se c'è una nuova data OPPURE un evento da modificare */}
      {(newEventDateStr !== undefined || eventToEdit !== null) && (
        <EventNewModal
          isOpen={true}
          onClose={() => {
            setNewEventDateStr(undefined);
            setEventToEdit(null);
          }}
          initialDate={newEventDateStr || eventToEdit?.dateStr} 
          eventToEdit={eventToEdit}
          onEventSaved={() => { 
            // 1. Invalidiamo la cache settimanale per mostrare l'evento aggiornato/creato
            queryClient.invalidateQueries({ queryKey: ['weekSync', mondayStr] });
            // 2. Resettiamo gli stati per chiudere il modale
            setNewEventDateStr(undefined); 
            setEventToEdit(null);
          }}
        />
      )}


      {/* ================= MODALI TASK ================= */}
      {selectedTask && (
        <TaskDetailModal
          isOpen={true}
          onClose={() => setSelectedTask(null)}
          selectedTask={selectedTask} 
          tasks={mappedTasks} 
          onToggleTask={(id: number) => {
            const taskOrigin = weekData?.tasks.find((t: Task) => t.id === id);
            if (taskOrigin) {
              handleToggleTaskFromGrid(taskOrigin, !taskOrigin.fatto);
            }
          }}
          onSelectTask={setSelectedTask}
          onEditClick={() => { 
            setTaskToEdit(selectedTask);
            setSelectedTask(null);
            setIsNewTaskModalOpen(true);
          }}
          onAddSubtask={() => { console.log("Add subtask"); }}
          
          // 🟢 AGGIUNGI QUESTO BLOCCO:
          onTaskDeleted={() => {
            // Forza il refresh della cache della settimana
            queryClient.invalidateQueries({ queryKey: ['weekSync', mondayStr] });
            // Assicuriamoci che il dettaglio si chiuda
            setSelectedTask(null);
          }}
        />
      )}

      {/* CORREZIONE TASK: Passiamo il callback di salvataggio per aggiornare la cache e chiudere */}
      {isNewTaskModalOpen && (
        <TaskNewModal
          isOpen={true}
          onClose={() => {
            setIsNewTaskModalOpen(false);
            setTaskToEdit(null);
          }}
          taskToEdit={taskToEdit}
          // Nota: Verifica se il tuo componente usa la prop 'onTaskSaved' o 'onSuccess' 
          // e allineala di conseguenza nel tuo TaskNewModal.tsx
          onTaskSaved={() => {
            // 1. Forza il refresh della cache della settimana attuale
            queryClient.invalidateQueries({ queryKey: ['weekSync', mondayStr] });
            // 2. Chiudi il modale e resetta lo stato di modifica
            setIsNewTaskModalOpen(false);
            setTaskToEdit(null);
          }}
        />
      )}

    </div>
  );
};

export default WeekPage;