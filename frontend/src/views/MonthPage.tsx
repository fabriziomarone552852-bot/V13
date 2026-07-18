// frontend/src/pages/MonthPage.tsx
import React, { useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { it } from 'date-fns/locale';

// --- IMPORT COMPONENTI CONDIVISI ---
import NotesSidebar from '@/components/day/NotesSidebar';
import { SharedAgendaHeader } from '@/components/shared/SharedAgendaHeader';
import { GoalsAndPrioritiesPanel } from '@/components/shared/GoalsAndPrioritiesPanel';
import CalendarColumn from '@/components/dashboard/CalendarColumn';
import TaskColumn from '@/components/shared/tasks/TaskColumn'; 
import MoodEventsBoard from '@/components/weekmonth/MoodEventsBoard';
import { TrackerPanel } from '@/components/weekmonth/TrackerPanel';
import NewEventModal from '@/components/shared/events/EventNewModal';
import EventDetailModal from '@/components/shared/events/EventDetailModal';

// --- HOOKS LOGICI E DATI ---
import { useMonthPageLogic } from '@/hooks/uiMonth/useMonthPageLogic';
import { useDay } from '@/context/DayContext';
import { useCategories } from '@/hooks/useCategories';
import { mapDbEventsToCalendarEvents } from '@/utils/eventUtils'; 

const MonthPage: React.FC = () => {
  const navigate = useNavigate();
  const { dataRiferimento: targetDate, changeDate: setTargetDate } = useDay();
  
  // Estraiamo la logica di pagina (Zero 'any', Zero mock!)
  const { state, modals, apiData, handlers } = useMonthPageLogic();

  // Estraiamo tutte le categorie dal DB per i pallini colorati del calendario
  const { dbCategories } = useCategories();

  const displayName = format(state.monthTargetDate, 'MMMM', { locale: it }).toUpperCase();
  const formattedDate = format(state.monthTargetDate, 'yyyy', { locale: it });

  const isCurrentMonth = new Date().getMonth() === state.monthTargetDate.getMonth() && new Date().getFullYear() === state.monthTargetDate.getFullYear();

  // 🪄 TRADUTTORE SICURO: Nessun 'any' richiesto.
  // mapDbEventsToCalendarEvents deve accettare (DbEvent[] | undefined) e restituire CalendarEvent[]
  const mappedEvents = useMemo(() => {
    return mapDbEventsToCalendarEvents(apiData?.events || [], state.startStr);
  }, [apiData?.events, state.startStr]);

  const handlePrevMonth = useCallback(() => { 
    const d = new Date(state.monthTargetDate); d.setMonth(d.getMonth() - 1); setTargetDate(d); 
  }, [state.monthTargetDate, setTargetDate]);

  const handleNextMonth = useCallback(() => { 
    const d = new Date(state.monthTargetDate); d.setMonth(d.getMonth() + 1); setTargetDate(d); 
  }, [state.monthTargetDate, setTargetDate]);

  const handleResetToday = useCallback(() => { setTargetDate(new Date()); }, [setTargetDate]);

  if (state.isLoading) {
    return <div className="flex h-full items-center justify-center font-bold text-gray-500 animate-pulse">Caricamento mese...</div>;
  }

  if (state.isError) {
    return <div className="flex h-full items-center justify-center text-red-500">Errore nel caricamento dei dati mensili.</div>;
  }

  return (
    <div className="flex flex-col gap-4 max-w-[1600px] mx-auto min-h-full xl:h-full xl:overflow-hidden relative">
      
      <div className="flex flex-col xl:flex-row gap-6 shrink-0 items-stretch justify-between w-full">
        <SharedAgendaHeader 
          title={displayName} 
          subtitle={formattedDate} 
          currentDate={state.monthTargetDate} 
          isToday={isCurrentMonth} 
          onPrev={handlePrevMonth} 
          onNext={handleNextMonth} 
          onResetToday={handleResetToday} 
          onChangeDate={setTargetDate}
          viewMode="month" 
        />

        <div className="flex-1 max-w-[1200px]">
          <GoalsAndPrioritiesPanel
            goalTitle="Obiettivo del Mese"
            prioritiesTitle="Priorità Mensili"
            dateKey={state.startStr}
            goalEntry={apiData?.obiettivi?.[0]}
            prioritiesEntries={apiData?.priorita}
            onSaveGoal={(testo) => console.log("Da implementare: Salva Obiettivo", testo)} 
            onSavePriority={(id, testo) => console.log("Da implementare: Salva Priorità", id, testo)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 flex-1 min-h-0">
        
        <div className="xl:col-span-1 h-full flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 relative z-40">
           <div className="flex bg-gray-50 border-b border-gray-200 shrink-0 rounded-t-xl">
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${state.activeSidebarTab === 'moods' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => state.setActiveSidebarTab('moods')} title="Umori">😊</button>
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${state.activeSidebarTab === 'spheres' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => state.setActiveSidebarTab('spheres')} title="Sfere">🎯</button>
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${state.activeSidebarTab === 'todos' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => state.setActiveSidebarTab('todos')} title="To-Do">✅</button>
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${state.activeSidebarTab === 'reflections' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => state.setActiveSidebarTab('reflections')} title="Cose Positive / Negative">❤️</button>
           </div>
           
           <div className="flex-1 flex flex-col min-h-0 bg-gray-50/50 rounded-b-xl overflow-visible">
              {state.activeSidebarTab === 'moods' && (
                <TrackerPanel titleTop="Come mi sento" titleBottom="Review Mese Scorso" items={state.moodsUI} onUpdateValue={handlers.handleUpdateMood} />
              )}
              {state.activeSidebarTab === 'spheres' && (
                <TrackerPanel titleTop="Sfere di Influenza" titleBottom="Review Mese Scorso" items={state.spheresUI} onUpdateValue={handlers.handleUpdateSphere} />
              )}
              {state.activeSidebarTab === 'todos' && (
                <div className="p-3 h-full">
                  <TaskColumn tasks={state.monthTasksUI} onToggleTask={handlers.handleToggleTask} onSelectTask={modals.openTaskDetail} onAddTaskClick={() => modals.openTaskForm()} />
                </div>
              )}
              {state.activeSidebarTab === 'reflections' && (
                <MoodEventsBoard layout="vertical" positiveEvents={apiData?.eventi_positivi || []} negativeEvents={apiData?.eventi_negativi || []} onAddMoodEvent={()=>{}} onUpdateMoodEvent={()=>{}} onDeleteMoodEvent={()=>{}} />
              )}
           </div>
        </div>

        <div className="xl:col-span-3 h-full flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 p-4 min-h-0 w-full min-w-0 overflow-visible relative z-10">
          <CalendarColumn 
             events={mappedEvents} 
             tasks={apiData?.tasks || []}
             allCategories={dbCategories}
             hideHeader={true}        
             forceView="Mese"   
             targetDate={state.monthTargetDate} 
             variant="detailed"    
             onDayClick={(dateStr) => navigate('/giorno', { state: { selectedDate: dateStr } })} 
             onSelectEvent={modals.openEventDetail} 
             onAddEventClick={(dataCliccata) => modals.openEventForm(null, dataCliccata ?? null)} 
             onMoodChange={(dateStr, categoryId) => {
               console.log(`Salva PX: Data ${dateStr}, Categoria ID: ${categoryId}`);
             }}
           />
         </div>    
      </div>

      <NotesSidebar 
        isOpen={state.isNotesOpen} 
        notes={apiData?.note || []} 
        editingNoteId={state.editingNoteId}
        onOpen={() => state.setIsNotesOpen(true)} 
        onClose={() => state.setIsNotesOpen(false)}
        onAddNote={handlers.handleAddNote} 
        onAutoSaveNote={handlers.handleAutoSaveNote}
        onDeleteNote={handlers.handleDeleteNote}
        clearEditingNoteId={() => state.setEditingNoteId(null)} 
      />

      <div className="relative z-[9999]">
        <EventDetailModal isOpen={modals.isDetailOpen} onClose={modals.closeEventDetail} selectedEvent={modals.selectedEvent} onDeleteClick={()=>{}} onEditClick={()=>{}} />
        <NewEventModal isOpen={modals.isFormOpen} onClose={modals.closeEventForm} eventToEdit={modals.eventToEdit} initialDate={modals.initialDate} onEventSaved={() => {}} />
      </div>

    </div>
  );
};

export default MonthPage;