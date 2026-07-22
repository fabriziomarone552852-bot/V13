// frontend/src/hooks/uiMonth/useMonthPageLogic.ts
import { useCallback } from 'react';
import { useAgendaMonth } from '@/hooks/useAgendaMonth'
import { useMonthNavigation } from './useMonthNavigation';
import { useMonthTasksEvents } from './useMonthTasksEvents';
import { useMonthNotes } from './useMonthNotes';
import { useMonthSidebar } from './useMonthSidebar';
import { useMonthModals } from './useMonthModals';
import type { DbTask, NoteVariant } from '@/types'; 

// IL CONTRATTO DEFINITIVO: Nessun 'any'
export interface UseMonthPageLogicResult {
  state: {
    monthTargetDate: Date;
    startStr: string;
    monthName: string;
    year: number;
    isLoading: boolean;
    isError: boolean;
    
    activeSidebarTab: ReturnType<typeof useMonthSidebar>['activeSidebarTab'];
    setActiveSidebarTab: ReturnType<typeof useMonthSidebar>['setActiveSidebarTab'];
    moodsUI: ReturnType<typeof useMonthSidebar>['moodsUI'];
    spheresUI: ReturnType<typeof useMonthSidebar>['spheresUI'];
    
    // 🪄 CORREZIONE 1: Usiamo i task mappati per la UI, non quelli grezzi
    monthTasksUI: ReturnType<typeof useMonthTasksEvents>['mappedTasks']; 
    
    isNotesOpen: ReturnType<typeof useMonthNotes>['isNotesOpen'];
    setIsNotesOpen: ReturnType<typeof useMonthNotes>['setIsNotesOpen'];
    editingNoteId: ReturnType<typeof useMonthNotes>['editingNoteId'];
    setEditingNoteId: ReturnType<typeof useMonthNotes>['setEditingNoteId'];
    mappedNotes: ReturnType<typeof useMonthNotes>['mappedNotes'];
  };
  modals: ReturnType<typeof useMonthModals>; 
  apiData: ReturnType<typeof useAgendaMonth>['monthData'];
  
  handlers: {
    handlePrevMonth: () => void;
    handleNextMonth: () => void;
    handleResetCurrentMonth: () => void;
    handleGoToDay: (dateStr: string) => void;
    
    // 🪄 CORREZIONE 2: Dichiariamo i due handler specifici che la vista richiede
    handleToggleTaskGrid: (task: DbTask, newStatus: boolean) => Promise<void>;
    handleToggleTaskSidebar: (id: number, currentStatus: boolean) => void;
    
    handleAddNote: () => void;
    handleAutoSaveNote: (id: number, text: string, variant: NoteVariant, isNew?: boolean) => void;
    handleDeleteNote: (id: number, isNew?: boolean) => void;
    handleUpdateMood: (id: string, val: number) => void;
    handleUpdateSphere: (id: string, val: number) => void;
    handleSaveGoal: (testo: string) => void;
    handleSavePriority: (id: number | undefined, testo: string) => void;
  };
}

export const useMonthPageLogic = (): UseMonthPageLogicResult => {
  const nav = useMonthNavigation();
  const agenda = useAgendaMonth(nav.firstDayStr, nav.lastDayStr);
  const sidebar = useMonthSidebar(agenda.monthData, nav.firstDayStr);
  const modals = useMonthModals();

  const tasksAndEvents = useMonthTasksEvents(
    agenda.monthData, 
    nav.firstDay, 
    nav.lastDay, 
    agenda.toggleTask
  );

  const notes = useMonthNotes({
    firstDayStr: nav.firstDayStr,
    lastDayStr: nav.lastDayStr,
    monthData: agenda.monthData,
    saveNote: agenda.saveNote,
    deleteNote: agenda.deleteNote
  });

  const handleSaveGoal = useCallback((testo: string) => {
    agenda.saveDailyEntry({
       id: agenda.monthData?.obiettivi?.[0]?.id,
       text: testo,
       tipo: 'OM',
       dateStr: nav.firstDayStr
    });
  }, [agenda, nav.firstDayStr]);

  const handleSavePriority = useCallback((id: number | undefined, testo: string) => {
    agenda.saveDailyEntry({
       id,
       text: testo,
       tipo: 'PM', 
       dateStr: nav.firstDayStr
    });
  }, [agenda, nav.firstDayStr]);

  // 🪄 CREIAMO L'HANDLER MANCANTE PER LA SIDEBAR (riceve solo ID e Stato)
  const handleToggleTaskSidebar = useCallback((id: number, currentStatus: boolean) => {
    agenda.toggleTask({ id, isDone: currentStatus });
  }, [agenda]);

  return {
    state: {
      monthTargetDate: nav.targetDate, 
      startStr: nav.firstDayStr,       
      monthName: nav.monthName,
      year: nav.year,
      isLoading: agenda.isLoading,
      isError: agenda.isError,
      activeSidebarTab: sidebar.activeSidebarTab,
      setActiveSidebarTab: sidebar.setActiveSidebarTab,
      moodsUI: sidebar.moodsUI,
      spheresUI: sidebar.spheresUI,
      monthTasksUI: tasksAndEvents.mappedTasks, // 🪄 Esportiamo i task formattati
      isNotesOpen: notes.isNotesOpen,
      setIsNotesOpen: notes.setIsNotesOpen,
      editingNoteId: notes.editingNoteId,
      setEditingNoteId: notes.setEditingNoteId,
      mappedNotes: notes.mappedNotes 
    },
    modals, 
    apiData: agenda.monthData,
    handlers: {
      handlePrevMonth: nav.handlePrevMonth,
      handleNextMonth: nav.handleNextMonth,
      handleResetCurrentMonth: nav.handleResetCurrentMonth,
      handleGoToDay: nav.handleGoToDay,
      handleToggleTaskGrid: tasksAndEvents.handleToggleTaskFromGrid, // 🪄 Handler per il calendario
      handleToggleTaskSidebar, // 🪄 Handler per la colonna laterale
      handleAddNote: notes.handleAddNote,
      handleAutoSaveNote: notes.handleAutoSaveNote,
      handleDeleteNote: notes.handleDeleteNote,
      handleUpdateMood: sidebar.handleUpdateMood,
      handleUpdateSphere: sidebar.handleUpdateSphere,
      handleSaveGoal,
      handleSavePriority
    }
  };
};