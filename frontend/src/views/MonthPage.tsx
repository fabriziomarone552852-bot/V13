import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router';
import { startOfMonth, format } from 'date-fns';
import { it } from 'date-fns/locale';

// --- IMPORT COMPONENTI CONDIVISI ---
import NotesSidebar from '@/components/day/NotesSidebar';
import { SharedAgendaHeader } from '@/components/shared/SharedAgendaHeader';
import { GoalsAndPrioritiesPanel } from '@/components/shared/GoalsAndPrioritiesPanel';

// --- IMPORT ARCHITETTURA & UTILS ---
import { useDay } from '@/context/DayContext';
import { formatDateString } from '@/utils/dateUtils';
import { getRandomVariant } from '@/utils/noteUtils';
import { type NoteVariant } from '@/types';

import { useAgendaDay } from '@/hooks/useAgendaDay';

// ** DA CREARE: il tuo hook per il fetching mensile **
// import { useAgendaMonth } from '@/hooks/useAgendaMonth';

const MonthPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // 1. STATO DELLA DATA (Adattato per il Mese)
  const { dataRiferimento: targetDate, changeDate: setTargetDate } = useDay();
  
  // Ci assicuriamo di avere sempre il 1° del mese
  const monthTargetDate = useMemo(() => startOfMonth(targetDate), [targetDate]);
  const monthTargetDateStr = formatDateString(monthTargetDate);

  // Etichette per l'Header (es. "LUG 2026")
  const displayName = format(monthTargetDate, 'MMM yyyy', { locale: it }).toUpperCase();
  const formattedDate = format(monthTargetDate, 'MMMM yyyy', { locale: it });
  
  // Controllo IsToday (per l'Header)
  const today = new Date();
  const isCurrentMonth = today.getMonth() === monthTargetDate.getMonth() && today.getFullYear() === monthTargetDate.getFullYear();

  // Intercettiamo navigazione esterna
  useEffect(() => {
    const state = location.state as { selectedDate?: string } | null;
    if (state?.selectedDate) {
      setTargetDate(startOfMonth(new Date(state.selectedDate)));
      navigate(location.pathname, { replace: true, state: {} }); 
    }
  }, [location.state, setTargetDate, navigate, location.pathname]);

  // 2. FETCH DEI DATI E STATO UI
  // Sostituisci questo con il tuo vero hook useAgendaMonth
  /*
  const { 
    monthData, isLoading, saveNote, deleteNote, saveObiettivo, savePriorita 
  } = useAgendaMonth(monthTargetDateStr);
  */
 
  // Dummy data per evitare errori in questa bozza
  const isLoading = false;
  const monthData: any = null; // ELIMINA QUESTO ANY QUANDO HAI I TIPI
  const saveObiettivo = (obj: any) => {};
  const savePriorita = (obj: any) => {};
  const saveNote = (obj: any) => {};
  const deleteNote = (id: number) => {};

  const [isNotesOpen, setIsNotesOpen] = useState<boolean>(false);
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  
  // STATO GRAFICO: Colonna Mutevole
  const [activeSidebarTab, setActiveSidebarTab] = useState<'moods' | 'spheres' | 'todos'>('moods');

  // --- 4. HANDLERS DATE ---
  const handlePrevMonth = useCallback(() => { 
    const d = new Date(monthTargetDate); 
    d.setMonth(d.getMonth() - 1); 
    setTargetDate(d); 
  }, [monthTargetDate, setTargetDate]);

  const handleNextMonth = useCallback(() => { 
    const d = new Date(monthTargetDate); 
    d.setMonth(d.getMonth() + 1); 
    setTargetDate(d); 
  }, [monthTargetDate, setTargetDate]);

  const handleResetToday = useCallback(() => { 
    setTargetDate(startOfMonth(new Date())); 
  }, [setTargetDate]);

  const handleDateChange = useCallback((newDate: Date) => {
    setTargetDate(startOfMonth(newDate));
  }, [setTargetDate]);

  // --- 5. HANDLER AZIONI (Gestione Note Mensili) ---
  
  // Logica per gestire la data della nota: se sono nel mese corrente uso "oggi", altrimenti il 1° o l'ultimo del mese.
  const getNoteDateStr = useCallback(() => {
    if (isCurrentMonth) return formatDateString(today);
    // Se non siamo nel mese corrente, la mettiamo al 1° del mese visualizzato
    return monthTargetDateStr;
  }, [isCurrentMonth, monthTargetDateStr]);

  const handleAddNote = useCallback(() => {
    const tempId = Date.now();
    saveNote({ 
      id: tempId, 
      dateStr: getNoteDateStr(), 
      text: "", 
      variant: getRandomVariant(), 
      isNew: true 
    });
    setEditingNoteId(tempId);
  }, [saveNote, getNoteDateStr]);

  const handleAutoSaveNote = useCallback((id: number, text: string, variant: NoteVariant, isNew?: boolean) => {
    saveNote({ id, text, dateStr: getNoteDateStr(), variant, isNew });
  }, [saveNote, getNoteDateStr]);


  // --- 6. RENDER ---

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center font-bold text-gray-500 animate-pulse">
        Caricamento mese...
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 max-w-[1600px] mx-auto min-h-full xl:h-full xl:overflow-hidden relative">
      
      {/* SEZIONE TOP */}
      <div className="flex flex-col xl:flex-row gap-6 shrink-0 items-stretch justify-between w-full">
        {/* COMPONENTE HEADER CONDIVISO */}
        <SharedAgendaHeader 
          title={displayName} 
          subtitle={formattedDate} 
          currentDate={monthTargetDate} 
          isToday={isCurrentMonth} 
          onPrev={handlePrevMonth} 
          onNext={handleNextMonth} 
          onResetToday={handleResetToday} 
          onChangeDate={handleDateChange}
          viewMode="month" // Importante per far capire al DatePicker che siamo nel Mese
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

      {/* SEZIONE CENTRALE (Copiando l'idea di 4 colonne totali che avevi descritto) */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 flex-1 min-h-0">
        
        {/* COLONNA MUTEVOLE (1 su 4) */}
        <div className="xl:col-span-1 h-full flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
           <div className="flex bg-gray-50 border-b border-gray-200">
             <button 
                className={`flex-1 p-3 text-sm font-semibold transition-colors ${activeSidebarTab === 'moods' ? 'text-blue-600 bg-white border-b-2 border-blue-500' : 'text-gray-500 hover:bg-gray-100'}`}
                onClick={() => setActiveSidebarTab('moods')}
             >Umori</button>
             <button 
                className={`flex-1 p-3 text-sm font-semibold transition-colors ${activeSidebarTab === 'spheres' ? 'text-blue-600 bg-white border-b-2 border-blue-500' : 'text-gray-500 hover:bg-gray-100'}`}
                onClick={() => setActiveSidebarTab('spheres')}
             >Sfere</button>
             <button 
                className={`flex-1 p-3 text-sm font-semibold transition-colors ${activeSidebarTab === 'todos' ? 'text-blue-600 bg-white border-b-2 border-blue-500' : 'text-gray-500 hover:bg-gray-100'}`}
                onClick={() => setActiveSidebarTab('todos')}
             >To-Do</button>
           </div>
           
           <div className="flex-1 p-4 overflow-y-auto">
              {activeSidebarTab === 'moods' && <div>Qui vanno gli Umori!</div>}
              {activeSidebarTab === 'spheres' && <div>Qui vanno le Sfere!</div>}
              {activeSidebarTab === 'todos' && <div>Qui vanno i To-Do!</div>}
           </div>
        </div>

        {/* CALENDARIO GIGANTE CON PIXEL (3 su 4) */}
        <div className="xl:col-span-3 h-full flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 p-4 min-h-0 w-full min-w-0">
          <div className="flex-1 flex items-center justify-center text-gray-400 font-bold">
             [Il Calendario Mensile con i Pixel andrà costruito qui]
          </div>
        </div>

      </div>

      {/* SIDEBAR DELLE NOTE (Riutilizzata!) */}
      <NotesSidebar 
        isOpen={isNotesOpen} 
        notes={monthData?.note || []} // Passa le note del mese
        editingNoteId={editingNoteId}
        onOpen={() => setIsNotesOpen(true)} 
        onClose={() => setIsNotesOpen(false)}
        onAddNote={handleAddNote} 
        onAutoSaveNote={handleAutoSaveNote}
        onDeleteNote={(id) => deleteNote(id)}
        clearEditingNoteId={() => setEditingNoteId(null)}
        selectedDateStr={monthTargetDateStr} // Nuova prop per forzare il caricamento/salvataggio nel mese giusto
      />
    </div>
  );
};

export default MonthPage;