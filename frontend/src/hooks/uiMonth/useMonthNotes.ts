// frontend/src/hooks/uiMonth/useMonthNotes.ts
import { useState, useCallback, useMemo } from 'react';
import { filterNotes, getRandomVariant } from '@/utils/noteUtils';
import { getLocalTodayStr } from '@/utils/dateUtils';
import type { NoteVariant, LocalNoteEntry } from '@/types';
import type { SyncMonthResponse } from '@/types';

export interface UseMonthNotesDependencies {
  firstDayStr: string;
  lastDayStr: string;
  monthData: SyncMonthResponse | undefined;
  saveNote: (payload: { id?: number; data_riferimento: string; testo: string; tipo: NoteVariant; isNew?: boolean }) => void;
  deleteNote: (id: number) => void;
}

export const useMonthNotes = ({ firstDayStr, lastDayStr, monthData, saveNote, deleteNote }: UseMonthNotesDependencies) => {
  const [isNotesOpen, setIsNotesOpen] = useState<boolean>(false);
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);

  // Filtraggio rigoroso senza 'any'
  const mappedNotes = useMemo((): LocalNoteEntry[] => {
    return filterNotes(monthData?.daily_entries); 
  }, [monthData?.daily_entries]);

  const handleAddNote = useCallback((): void => {
    const tempId = Date.now();
    const todayStr = getLocalTodayStr();
    const isThisMonth = todayStr >= firstDayStr && todayStr <= lastDayStr;
    const initialTargetDate = isThisMonth ? todayStr : firstDayStr;

    saveNote({ 
      id: tempId, 
      tipo: getRandomVariant(), 
      data_riferimento: initialTargetDate, 
      testo: "", 
      isNew: true 
    });
    setEditingNoteId(tempId);
  }, [firstDayStr, lastDayStr, saveNote]);

  const handleAutoSaveNote = useCallback((id: number, testo: string, tipo: NoteVariant, isNew?: boolean): void => {
    const existingNote = mappedNotes.find(n => n.id === id);
    const existingDate = existingNote?.data_riferimento ?? firstDayStr; 

    saveNote({ id, testo, data_riferimento: existingDate, tipo, isNew });
  }, [mappedNotes, firstDayStr, saveNote]);

  return {
    isNotesOpen, setIsNotesOpen,
    editingNoteId, setEditingNoteId,
    mappedNotes,
    handleAddNote, handleAutoSaveNote, 
    handleDeleteNote: deleteNote
  };
};