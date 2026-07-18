// frontend/src/hooks/uiMonth/useMonthPageLogic.ts
import { useState, useMemo, useCallback } from 'react';
import { startOfMonth, endOfMonth } from 'date-fns';
import { useDay } from '@/context/DayContext';
import { useTaskModals } from '@/context/TaskModalContext';
import { useEventModals } from '@/context/EventModalContext';
import { useAgendaMonth } from '@/hooks/useAgendaMonth';
import { useMonthlyEntryMutations } from '../mutations/useMonthlyEntryMutations';
import { formatDateString } from '@/utils/dateUtils';
import { buildTaskTree } from '@/utils/taskUtils';
import { getRandomVariant } from '@/utils/noteUtils';
import type { TrackerItem } from '@/components/weekmonth/TrackerPanel';
// 🪄 Importiamo i tipi corretti per mappare i grafici[cite: 6, 12]
import type { NoteVariant, DailyEntry, CalendarEvent, UITask, MonthlyEntryType } from '@/types';

export type SidebarTab = 'moods' | 'spheres' | 'todos' | 'reflections';

// MAPPE DI DEFINIZIONE: Tipizzazione rigorosa invece di stringhe libere[cite: 6]
const MOOD_DEFS: { id: MonthlyEntryType; name: string; colorHex: string }[] = [
  { id: 'mood_happiness', name: 'Gioia', colorHex: '#EAB308' },
  { id: 'mood_sadness', name: 'Tristezza', colorHex: '#3B82F6' },
  { id: 'mood_anger', name: 'Rabbia', colorHex: '#EF4444' },
  { id: 'mood_disgust', name: 'Disgusto', colorHex: '#22C55E' },
  { id: 'mood_fear', name: 'Paura', colorHex: '#A855F7' },
];

const SPHERE_DEFS: { id: MonthlyEntryType; name: string; colorHex: string }[] = [
  { id: 'sphere_finance', name: 'Finanze', colorHex: '#22C55E' },
  { id: 'sphere_health', name: 'Salute', colorHex: '#EF4444' },
  { id: 'sphere_family', name: 'Famiglia', colorHex: '#92400E' },
  { id: 'sphere_fun', name: 'Svago', colorHex: '#F97316' },
  { id: 'sphere_friendship', name: 'Amici', colorHex: '#EAB308' },
  { id: 'sphere_mind', name: 'Mente', colorHex: '#EC4899' },
  { id: 'sphere_work', name: 'Lavoro', colorHex: '#3B82F6' },
  { id: 'sphere_love', name: 'Coppia', colorHex: '#A855F7' },
];

export const useMonthPageLogic = () => {
  const { dataRiferimento: targetDate, changeDate: setTargetDate } = useDay();
  const monthTargetDate = useMemo(() => startOfMonth(targetDate), [targetDate]);
  
  const startStr = formatDateString(monthTargetDate);
  const endStr = formatDateString(endOfMonth(monthTargetDate));

  const { monthData, isLoading, isError, toggleTask, deleteEventFromCache, saveNote, deleteNote } = useAgendaMonth(startStr, endStr);

  const monthQueryKey = ['monthSync', startStr];
  const { saveMonthlyEntry } = useMonthlyEntryMutations(monthQueryKey);

  const [activeSidebarTab, setActiveSidebarTab] = useState<SidebarTab>('todos');
  const [isNotesOpen, setIsNotesOpen] = useState<boolean>(false);
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);

  const { openTaskDetail, openTaskForm } = useTaskModals();
  const { isDetailOpen, selectedEvent, isFormOpen, eventToEdit, initialDate, openEventDetail, closeEventDetail, openEventForm, closeEventForm } = useEventModals();

  const monthTasksUI: UITask[] = useMemo(() => buildTaskTree(monthData?.tasks || []), [monthData?.tasks]);

  // 🪄 LA VIA LUNGA: Addio mock, creiamo i dati per i grafici partendo dinamicamente dal database[cite: 12]
  const moodsUI: TrackerItem[] = useMemo(() => {
    return MOOD_DEFS.map(def => {
      const entry = monthData?.tracker_entries?.find(e => e.type === def.id);
      return {
        id: def.id,
        name: def.name,
        colorHex: def.colorHex,
        currentValue: entry?.value || 0,
        previousValue: 0 // In futuro scaricheremo anche il dato del mese scorso
      };
    });
  }, [monthData?.tracker_entries]);

  const spheresUI: TrackerItem[] = useMemo(() => {
    return SPHERE_DEFS.map(def => {
      const entry = monthData?.tracker_entries?.find(e => e.type === def.id);
      return {
        id: def.id,
        name: def.name,
        colorHex: def.colorHex,
        currentValue: entry?.value || 0,
        previousValue: 0
      };
    });
  }, [monthData?.tracker_entries]);

  const handleToggleTask = (id: number, currentStatus: boolean, e?: React.MouseEvent) => {
    e?.stopPropagation();
    toggleTask({ id, isDone: !currentStatus });
  };

  const handleUpdateMood = (id: string, val: number) => {
    const type = id as MonthlyEntryType; 
    saveMonthlyEntry({ type, value: val, dateStr: startStr });
  };

  const handleUpdateSphere = (id: string, val: number) => {
    const type = id as MonthlyEntryType;
    saveMonthlyEntry({ type, value: val, dateStr: startStr });
  };

  const handleAddNote = useCallback(() => {
    const tempId = Date.now();
    saveNote({ id: tempId, dateStr: startStr, text: "", variant: getRandomVariant(), isNew: true });
    setEditingNoteId(tempId);
  }, [saveNote, startStr]);

  const handleAutoSaveNote = useCallback((id: number, text: string, variant: NoteVariant, isNew?: boolean) => {
    saveNote({ id, text, dateStr: startStr, variant, isNew });
  }, [saveNote, startStr]);

  const handleDeleteNote = useCallback((id: number, isNew?: boolean) => {
    deleteNote(id); 
  }, [deleteNote]);

  return {
    state: {
      monthTargetDate,
      startStr,
      isLoading,
      isError,
      activeSidebarTab,
      setActiveSidebarTab,
      isNotesOpen,
      setIsNotesOpen,
      editingNoteId,
      setEditingNoteId,
      monthTasksUI,
      moodsUI,    
      spheresUI,  
    },
    modals: {
      openTaskDetail, openTaskForm,
      isDetailOpen, selectedEvent, isFormOpen, eventToEdit, initialDate, 
      openEventDetail, closeEventDetail, openEventForm, closeEventForm
    },
    apiData: monthData,
    handlers: {
      handleToggleTask,
      handleUpdateMood,
      handleUpdateSphere,
      handleAddNote,
      handleAutoSaveNote,
      handleDeleteNote,
    }
  };
};