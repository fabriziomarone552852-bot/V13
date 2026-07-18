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
import type { NoteVariant, DailyEntry, CalendarEvent, UITask, MonthlyEntryType } from '@/types';

export type SidebarTab = 'moods' | 'spheres' | 'todos' | 'reflections';

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

// 🪄 LA VIA LUNGA E SICURA: La Guardia di Tipo
// Controlla dinamicamente se la stringa in ingresso fa parte delle nostre definizioni valide.
const isMonthlyEntryType = (value: string): value is MonthlyEntryType => {
  const validMoods = MOOD_DEFS.map(def => def.id as string);
  const validSpheres = SPHERE_DEFS.map(def => def.id as string);
  return validMoods.includes(value) || validSpheres.includes(value);
};

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

  const moodsUI: TrackerItem[] = useMemo(() => {
    return MOOD_DEFS.map(def => {
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
    // 🪄 VERIFICA DI SICUREZZA: Niente più 'as'!
    if (isMonthlyEntryType(id)) {
      saveMonthlyEntry({ type: id, value: val, dateStr: startStr });
    } else {
      console.error(`Tentativo di salvataggio fallito: L'ID "${id}" non è un tipo di umore valido.`);
    }
  };

  const handleUpdateSphere = (id: string, val: number) => {
    // 🪄 VERIFICA DI SICUREZZA
    if (isMonthlyEntryType(id)) {
      saveMonthlyEntry({ type: id, value: val, dateStr: startStr });
    } else {
      console.error(`Tentativo di salvataggio fallito: L'ID "${id}" non è un tipo di sfera valido.`);
    }
  };

  const handleAddNote = useCallback(() => {
    const tempId = Date.now();
    saveNote({ 
        id: tempId, 
        data_riferimento: startStr, 
        testo: "", 
        tipo: getRandomVariant(), 
        isNew: true 
    });
    setEditingNoteId(tempId);
  }, [saveNote, startStr]);

  const handleAutoSaveNote = useCallback((id: number, testo: string, tipo: NoteVariant, isNew?: boolean) => {
    saveNote({ id, testo, data_riferimento: startStr, tipo, isNew });
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