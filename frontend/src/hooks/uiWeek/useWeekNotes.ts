// frontend/src/hooks/uiWeek/useWeekNotes.ts
import { useState, useCallback, useMemo } from 'react';
import { getLocalTodayStr } from '@/utils/dateUtils';
import { filterNotes, getRandomVariant } from '@/utils/noteUtils';
import type { NoteVariant, LocalNoteEntry, SyncWeekResponse } from '@/types';

// 🪄 Le dipendenze usano i nomi esatti del database: data_riferimento, testo, tipo
export interface UseWeekNotesDependencies {
  mondayStr: string;
  sundayStr: string;
  weekData: SyncWeekResponse | undefined;
  saveNote: (payload: { id?: number; data_riferimento: string; testo: string; tipo: NoteVariant; isNew?: boolean }) => void;
  deleteNote: (id: number) => void;
}

export const useWeekNotes = ({ mondayStr, sundayStr, weekData, saveNote, deleteNote }: UseWeekNotesDependencies) => {
  const [isNotesOpen, setIsNotesOpen] = useState<boolean>(false);
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);

  // 1. FILTRAGGIO SICURO
  // Grazie a filterNotes, TypeScript sa che mappedNotes è un array di LocalNoteEntry purissime.
  const mappedNotes = useMemo((): LocalNoteEntry[] => {
    return filterNotes(weekData?.note); 
  }, [weekData?.note]);

  const handleAddNote = useCallback((): void => {
    const tempId = Date.now();
    const todayStr = getLocalTodayStr();
    const isThisWeek = todayStr >= mondayStr && todayStr <= sundayStr;
    const initialTargetDate = isThisWeek ? todayStr : mondayStr;
    const noteVariant = getRandomVariant();

    saveNote({ 
      id: tempId, 
      tipo: noteVariant, 
      data_riferimento: initialTargetDate, 
      testo: "", 
      isNew: true 
    });
    setEditingNoteId(tempId);
  }, [mondayStr, sundayStr, saveNote]);

  const handleAutoSaveNote = useCallback((id: number, testo: string, tipo: NoteVariant, isNew?: boolean): void => {
    // 2. RICERCA SICURA (Nessuna forzatura di tipo!)
    // Cerchiamo dentro 'mappedNotes' invece che dentro 'weekData.note'.
    // TypeScript capisce da solo che 'n' è una LocalNoteEntry.
    const existingNote = mappedNotes.find(n => n.id === id);
    const existingDate = existingNote?.data_riferimento ?? mondayStr; 

    saveNote({ 
      id, 
      testo, 
      data_riferimento: existingDate, 
      tipo, 
      isNew 
    });
  }, [mappedNotes, mondayStr, saveNote]); // 🪄 NOTA: abbiamo aggiunto mappedNotes nelle dipendenze

  const handleDeleteNote = useCallback((id: number): void => {
    deleteNote(id); 
  }, [deleteNote]);

  return {
    isNotesOpen,
    setIsNotesOpen,
    editingNoteId,
    setEditingNoteId,
    mappedNotes,
    handleAddNote,
    handleAutoSaveNote,
    handleDeleteNote
  };
};