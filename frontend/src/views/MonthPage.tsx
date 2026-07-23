// frontend/src/pages/MonthPage.tsx
import React, { useMemo } from 'react';
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
  
  const { changeDate: setTargetDate } = useDay();
  
  const { state, modals, apiData, handlers } = useMonthPageLogic();

  const { dbCategories } = useCategories();

  const displayName = format(state.monthTargetDate, 'MMMM', { locale: it }).toUpperCase();
  const formattedDate = format(state.monthTargetDate, 'yyyy', { locale: it });

  const isCurrentMonth = new Date().getMonth() === state.monthTargetDate.getMonth() && new Date().getFullYear() === state.monthTargetDate.getFullYear();

  const mappedEvents = useMemo(() => {
    return mapDbEventsToCalendarEvents(apiData?.events || [], state.startStr);
  }, [apiData?.events, state.startStr]);

  if (state.isLoading) {
    return <div className="flex h-full items-center justify-center font-bold text-gray-500 animate-pulse">Caricamento mese...</div>;
  }

  if (state.isError) {
    return <div className="flex h-full items-center justify-center text-red-500">Errore nel caricamento dei dati mensili.</div>;
  }

  return (
    <div className="flex flex-col gap-4 max-w-[1600px] mx-auto min-h-full xl:h-full xl:overflow-hidden relative">
      
      {/* 🪄 CORREZIONE 1: Aggiunto 'relative z-50' al contenitore dell'header. 
          Questo garantisce che l'header e il suo DatePicker siano fisicamente "sopra" la Sidebar (che ha z-40). */}
      <div className="flex flex-col xl:flex-row gap-6 shrink-0 items-stretch justify-between w-full relative z-50">
        <SharedAgendaHeader 
          title={displayName} 
          subtitle={formattedDate} 
          currentDate={state.monthTargetDate} 
          isToday={isCurrentMonth} 
          onPrev={handlers.handlePrevMonth} 
          onNext={handlers.handleNextMonth} 
          onResetToday={handlers.handleResetCurrentMonth} 
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
            onSaveGoal={handlers.handleSaveGoal} 
            onSavePriority={handlers.handleSavePriority}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 flex-1 min-h-0">
        
        {/* La Sidebar rimane z-40, ma ora è sottomessa all'header che è z-50 */}
        <div className="xl:col-span-1 h-full flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 relative z-40">
           
           {/* 🪄 CORREZIONE 2: Aggiunto 'relative z-20 shadow-sm' ai bottoni dei tab. 
               Ora i tab staranno sempre fisicamente "sopra" la finestra degli eventi. */}
           <div className="flex bg-gray-50 border-b border-gray-200 shrink-0 rounded-t-xl relative z-20 shadow-sm">
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${state.activeSidebarTab === 'moods' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => state.setActiveSidebarTab('moods')} title="Umori">😊</button>
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${state.activeSidebarTab === 'spheres' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => state.setActiveSidebarTab('spheres')} title="Sfere">🎯</button>
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${state.activeSidebarTab === 'todos' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => state.setActiveSidebarTab('todos')} title="To-Do">✅</button>
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${state.activeSidebarTab === 'reflections' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => state.setActiveSidebarTab('reflections')} title="Cose Positive / Negative">❤️</button>
           </div>
           
           {/* 🪄 CORREZIONE 3: Aggiunto 'relative z-10' al contenitore dei pannelli.
               Essendo z-10, tutto il suo contenuto (inclusa la finestra degli eventi) non potrà mai coprire i tab (che sono z-20). */}
           <div className="flex-1 flex flex-col min-h-0 bg-gray-50/50 rounded-b-xl overflow-visible relative z-10">
              {state.activeSidebarTab === 'moods' && (
                <TrackerPanel titleTop="Come mi sento" titleBottom="Review Mese Scorso" items={state.moodsUI} onUpdateValue={handlers.handleUpdateMood} />
              )}
              {state.activeSidebarTab === 'spheres' && (
                <TrackerPanel titleTop="Sfere di Influenza" titleBottom="Review Mese Scorso" items={state.spheresUI} onUpdateValue={handlers.handleUpdateSphere} />
              )}
              {state.activeSidebarTab === 'todos' && (
                <div className="p-3 h-full">
                  <TaskColumn 
                    tasks={state.monthTasksUI} 
                    onToggleTask={handlers.handleToggleTaskSidebar}
                    onSelectTask={modals.openTaskDetail} 
                    onAddTaskClick={() => modals.openTaskForm()} 
                  />
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
            onDayClick={handlers.handleGoToDay} 
            onToggleTask={handlers.handleToggleTaskGrid}
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
        notes={state.mappedNotes} 
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