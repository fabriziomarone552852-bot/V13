import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router';
import { startOfMonth, format } from 'date-fns';
import { it } from 'date-fns/locale';

// --- IMPORT COMPONENTI CONDIVISI ---
import NotesSidebar from '@/components/day/NotesSidebar';
import { SharedAgendaHeader } from '@/components/shared/SharedAgendaHeader';
import { GoalsAndPrioritiesPanel } from '@/components/shared/GoalsAndPrioritiesPanel';
import CalendarColumn from '@/components/dashboard/CalendarColumn';
import TaskColumn from '@/components/shared/tasks/TaskColumn'; 
import MoodEventsBoard from '@/components/weekmonth/MoodEventsBoard';
import { TrackerPanel, type TrackerItem } from '@/components/weekmonth/TrackerPanel';

// --- IMPORT ARCHITETTURA & UTILS ---
import { useDay } from '@/context/DayContext';
import { formatDateString } from '@/utils/dateUtils';
import { getRandomVariant } from '@/utils/noteUtils';
import { buildTaskTree } from '@/utils/taskUtils'; 

// IMPORTIAMO TUTTI I TIPI NECESSARI (Zero 'any')
import type { 
  NoteVariant, 
  DailyEntry, 
  CalendarEvent, 
  DbTask, 
  NoteItem,
  UITask,       
  TaskSummary,
  MoodEvent,      
  MoodEventType   
} from '@/types';

// 1. IL CONTRATTO DEI DATI
interface AgendaMonthData {
  obiettivi?: DailyEntry[];
  priorita?: DailyEntry[];
  note?: NoteItem[];
  events?: CalendarEvent[];
  tasks?: DbTask[];
  positiveEvents?: MoodEvent[];
  negativeEvents?: MoodEvent[];
}

type SidebarTab = 'moods' | 'spheres' | 'todos' | 'reflections';

const MonthPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const { dataRiferimento: targetDate, changeDate: setTargetDate } = useDay();
  
  const monthTargetDate = useMemo(() => startOfMonth(targetDate), [targetDate]);
  const monthTargetDateStr = formatDateString(monthTargetDate);

  const displayName = format(monthTargetDate, 'MMMM', { locale: it }).toUpperCase();
  const formattedDate = format(monthTargetDate, 'yyyy', { locale: it });
  
  const today = useMemo(() => new Date(), []);
  const isCurrentMonth = today.getMonth() === monthTargetDate.getMonth() && today.getFullYear() === monthTargetDate.getFullYear();

  useEffect(() => {
    const state = location.state as { selectedDate?: string } | null;
    if (state?.selectedDate) {
      setTargetDate(startOfMonth(new Date(state.selectedDate)));
      navigate(location.pathname, { replace: true, state: {} }); 
    }
  }, [location.state, setTargetDate, navigate, location.pathname]);

  // Mock Dati
  const isLoading: boolean = false;
  const monthData: AgendaMonthData | null = {
    obiettivi: [], priorita: [], note: [], events: [], tasks: [], positiveEvents: [], negativeEvents: []  
  };

  const saveObiettivo = (obj: { id?: number; text: string }): void => {};
  const savePriorita = (obj: { id?: number; text: string }): void => {};
  const saveNote = (obj: { id: number; dateStr: string; text: string; variant: NoteVariant; isNew?: boolean }): void => {};
  const deleteNote = (id: number): void => {};

  const [isNotesOpen, setIsNotesOpen] = useState<boolean>(false);
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [activeSidebarTab, setActiveSidebarTab] = useState<SidebarTab>('todos');

  const handlePrevMonth = useCallback(() => { 
    const d = new Date(monthTargetDate); d.setMonth(d.getMonth() - 1); setTargetDate(d); 
  }, [monthTargetDate, setTargetDate]);

  const handleNextMonth = useCallback(() => { 
    const d = new Date(monthTargetDate); d.setMonth(d.getMonth() + 1); setTargetDate(d); 
  }, [monthTargetDate, setTargetDate]);

  const handleResetToday = useCallback(() => { setTargetDate(startOfMonth(new Date())); }, [setTargetDate]);
  const handleDateChange = useCallback((newDate: Date) => { setTargetDate(startOfMonth(newDate)); }, [setTargetDate]);

  const getNoteDateStr = useCallback(() => {
    if (isCurrentMonth) return formatDateString(today);
    return monthTargetDateStr;
  }, [isCurrentMonth, monthTargetDateStr, today]);

  const handleAddNote = useCallback(() => {
    const tempId = Date.now();
    saveNote({ id: tempId, dateStr: getNoteDateStr(), text: "", variant: getRandomVariant(), isNew: true });
    setEditingNoteId(tempId);
  }, [saveNote, getNoteDateStr]);

  const handleAutoSaveNote = useCallback((id: number, text: string, variant: NoteVariant, isNew?: boolean) => {
    saveNote({ id, text, dateStr: getNoteDateStr(), variant, isNew });
  }, [saveNote, getNoteDateStr]);

  const handleGoToDay = useCallback((dateStr: string) => { navigate('/giorno', { state: { selectedDate: dateStr } }); }, [navigate]);
  const handleSelectEvent = useCallback((event: CalendarEvent) => { console.log("Evento:", event.title); }, []);
  const handleToggleTask = useCallback((id: number, currentStatus: boolean, e?: React.MouseEvent) => { e?.stopPropagation(); }, []);
  const handleSelectTask = useCallback((task: TaskSummary) => { console.log('Task:', task.title); }, []);
  const handleAddTaskClick = useCallback(() => { console.log('Add Task'); }, []);

  const handleAddMoodEvent = useCallback(async (type: MoodEventType, title: string) => { console.log(`Salva ${type}:`, title); }, []);
  const handleUpdateMoodEvent = useCallback((id: number, newTitle: string) => { console.log(`Aggiorna ${id}:`, newTitle); }, []);
  const handleDeleteMoodEvent = useCallback((id: number) => { console.log(`Elimina:`, id); }, []);

  const monthTasksUI: UITask[] = useMemo(() => buildTaskTree(monthData?.tasks || []), [monthData?.tasks]);

  if (isLoading) {
    return <div className="flex h-full items-center justify-center font-bold text-gray-500 animate-pulse">Caricamento mese...</div>;
  }

  const [moodsMock, setMoodsMock] = useState<TrackerItem[]>([
    { id: 'm1', name: 'Gioia', colorHex: '#EAB308', currentValue: 7, previousValue: 8 },    // Giallo
    { id: 'm2', name: 'Tristezza', colorHex: '#3B82F6', currentValue: 3, previousValue: 4 }, // Blu
    { id: 'm3', name: 'Rabbia', colorHex: '#EF4444', currentValue: 4, previousValue: 2 },    // Rosso
    { id: 'm4', name: 'Disgusto', colorHex: '#22C55E', currentValue: 1, previousValue: 2 },  // Verde
    { id: 'm5', name: 'Paura', colorHex: '#A855F7', currentValue: 2, previousValue: 5 },     // Viola
  ]);

  const [spheresMock, setSpheresMock] = useState<TrackerItem[]>([
    { id: 's1', name: 'Finanze', colorHex: '#22C55E', currentValue: 6, previousValue: 5 },   // Verde
    { id: 's2', name: 'Salute', colorHex: '#EF4444', currentValue: 8, previousValue: 7 },    // Rosso
    { id: 's3', name: 'Famiglia', colorHex: '#92400E', currentValue: 9, previousValue: 9 },  // Marrone
    { id: 's4', name: 'Svago', colorHex: '#F97316', currentValue: 4, previousValue: 6 }, // Arancione
    { id: 's5', name: 'Amici', colorHex: '#EAB308', currentValue: 7, previousValue: 6 },     // Giallo
    { id: 's6', name: 'Mente', colorHex: '#EC4899', currentValue: 5, previousValue: 3 },     // Rosa
    { id: 's7', name: 'Lavoro', colorHex: '#3B82F6', currentValue: 8, previousValue: 7 },    // Blu
    { id: 's8', name: 'Coppia', colorHex: '#A855F7', currentValue: 9, previousValue: 8 },    // Viola
  ]);

  const handleUpdateMood = (id: string, val: number) => {
    setMoodsMock(prev => prev.map(m => m.id === id ? { ...m, currentValue: val } : m));
  };

  const handleUpdateSphere = (id: string, val: number) => {
    setSpheresMock(prev => prev.map(s => s.id === id ? { ...s, currentValue: val } : s));
  };

  return (
    <div className="flex flex-col gap-4 max-w-[1600px] mx-auto min-h-full xl:h-full xl:overflow-hidden relative">
      
      <div className="flex flex-col xl:flex-row gap-6 shrink-0 items-stretch justify-between w-full">
        <SharedAgendaHeader 
          title={displayName} 
          subtitle={formattedDate} 
          currentDate={monthTargetDate} 
          isToday={isCurrentMonth} 
          onPrev={handlePrevMonth} 
          onNext={handleNextMonth} 
          onResetToday={handleResetToday} 
          onChangeDate={handleDateChange}
          viewMode="month" 
        />

        <div className="flex-1 max-w-[1200px]">
          <GoalsAndPrioritiesPanel
            goalTitle="Obiettivo del Mese"
            prioritiesTitle="Priorità Mensili"
            dateKey={monthTargetDateStr}
            goalEntry={monthData?.obiettivi?.[0]}
            prioritiesEntries={monthData?.priorita}
            onSaveGoal={(testo) => saveObiettivo({ id: monthData?.obiettivi?.[0]?.id, text: testo })}
            onSavePriority={(id, testo) => savePriorita({ id, text: testo })}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 flex-1 min-h-0">
        
        {/* COLONNA MUTEVOLE (1 su 4) */}
        {/* MAGIA INGEGNERISTICA 1: Rimosso overflow-hidden, aggiunto z-40 per permettere l'overlay sul calendario */}
        <div className="xl:col-span-1 h-full flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 relative z-40">
           
           {/* HEADER TABS CON SIMBOLI */}
           <div className="flex bg-gray-50 border-b border-gray-200 shrink-0 rounded-t-xl">
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${activeSidebarTab === 'moods' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => setActiveSidebarTab('moods')} title="Umori">😊</button>
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${activeSidebarTab === 'spheres' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => setActiveSidebarTab('spheres')} title="Sfere">🎯</button>
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${activeSidebarTab === 'todos' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => setActiveSidebarTab('todos')} title="To-Do">✅</button>
             <button className={`flex-1 py-3 text-xl transition-all flex items-center justify-center ${activeSidebarTab === 'reflections' ? 'bg-white border-b-2 border-blue-500 opacity-100 scale-110' : 'hover:bg-gray-100 opacity-40 grayscale hover:grayscale-0'}`} onClick={() => setActiveSidebarTab('reflections')} title="Cose Positive / Negative">❤️</button>
           </div>
           
           {/* CONTENUTO MUTEVOLE */}
           {/* MAGIA INGEGNERISTICA 2: Rimosso overflow-y-auto globale. Usiamo overflow-visible. 
               Lasciamo che i singoli tab gestiscano il proprio scroll se necessario! */}
           <div className="flex-1 flex flex-col min-h-0 bg-gray-50/50 rounded-b-xl overflow-visible">
              
              {activeSidebarTab === 'moods' && (
                <div className="h-full flex flex-col overflow-hidden">
                  <TrackerPanel 
                    titleTop="Come mi sento" 
                    titleBottom="Review Mese Scorso" 
                    items={moodsMock} 
                    onUpdateValue={handleUpdateMood} 
                  />
                </div>
              )}
              
              {activeSidebarTab === 'spheres' && (
                <div className="h-full flex flex-col overflow-hidden">
                  <TrackerPanel 
                    titleTop="Sfere di Influenza" 
                    titleBottom="Review Mese Scorso" 
                    items={spheresMock} 
                    onUpdateValue={handleUpdateSphere} 
                  />
                </div>
              )}

              {activeSidebarTab === 'todos' && (
                <div className="p-3 h-full">
                  {/* TaskColumn gestisce già il proprio scroll internamente! */}
                  <TaskColumn 
                    tasks={monthTasksUI}
                    onToggleTask={handleToggleTask}
                    onSelectTask={handleSelectTask}
                    onAddTaskClick={handleAddTaskClick}
                  />
                </div>
              )}
              
              {activeSidebarTab === 'reflections' && (
                <div className="p-3 h-full flex flex-col overflow-visible">
                  <MoodEventsBoard 
                    layout="vertical"
                    positiveEvents={monthData?.positiveEvents || []}
                    negativeEvents={monthData?.negativeEvents || []}
                    onAddMoodEvent={handleAddMoodEvent}      
                    onUpdateMoodEvent={handleUpdateMoodEvent} 
                    onDeleteMoodEvent={handleDeleteMoodEvent}  
                  />
                </div>
              )}
           </div>
        </div>

        {/* CALENDARIO MENSILE DETTAGLIATO (3 su 4) */}
        <div className="xl:col-span-3 h-full flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 p-4 min-h-0 w-full min-w-0 overflow-hidden relative">
          <CalendarColumn 
             events={monthData?.events || []} 
             tasks={monthData?.tasks || []}
             hideHeader={true}        
             forceView="Mese"   
             targetDate={monthTargetDate} 
             variant="detailed"    
             onDayClick={handleGoToDay}
             onSelectEvent={handleSelectEvent}
           />
        </div>
      </div>

      <NotesSidebar 
        isOpen={isNotesOpen} 
        notes={monthData?.note || []} 
        editingNoteId={editingNoteId}
        onOpen={() => setIsNotesOpen(true)} 
        onClose={() => setIsNotesOpen(false)}
        onAddNote={handleAddNote} 
        onAutoSaveNote={handleAutoSaveNote}
        onDeleteNote={(id) => deleteNote(id)}
        clearEditingNoteId={() => setEditingNoteId(null)}
      />
    </div>
  );
};

export default MonthPage;