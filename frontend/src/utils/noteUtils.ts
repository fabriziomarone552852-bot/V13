// frontend/src/utils/noteUtils.ts
import type { DailyEntry, LocalNoteEntry, NoteVariant } from '@/types';
import { isNoteVariant } from '@/types';

// 1. Creiamo la Guardia di Tipo (Il "buttafuori")
// Questa funzione dice: "Se restituisco vero, allora 'entry' è sicuramente una LocalNoteEntry"
export const isLocalNoteEntry = (entry: DailyEntry): entry is LocalNoteEntry => {
  return isNoteVariant(entry.tipo);
};

// 2. La funzione di filtraggio pulita e sicura
export const filterNotes = (notes: DailyEntry[] | undefined): LocalNoteEntry[] => {
  if (!notes || notes.length === 0) return [];

  // Grazie alla Guardia di Tipo, il filter capisce automaticamente 
  // che il risultato finale sarà una lista di LocalNoteEntry. Nessuna forzatura necessaria!
  return notes.filter(isLocalNoteEntry);
};

// 3. Funzione per le varianti (rimane invariata)
export const getRandomVariant = (): NoteVariant => {
  const variants: NoteVariant[] = ['N1', 'N2', 'N3', 'N4']; 
  const randomIndex = Math.floor(Math.random() * variants.length);
  return variants[randomIndex];
};