import type { Category } from './categories';

export type MoodEventType = 'EP' | 'EN';
export type NoteVariant = 'N1' | 'N2' | 'N3' | 'N4';
export type DailyEntryType = 'OD' | 'PD' | 'OW' | 'PW' | 'PX' | MoodEventType | NoteVariant;

export interface DailyEntry {
  id: number;
  user_id: number;
  data_riferimento: string; 
  tipo: DailyEntryType;
  testo: string;
  immagine_url?: string | null;
  category_id?: number | null; 
  category?: Category | null; 
}

export interface LocalNoteEntry extends DailyEntry {
  isNew?: boolean;
}

// Definiamo le opzioni per i colori del pixel, niente stringhe libere
// ANCHE SE SARANNO FORMULATI I COLORIN NEL BACKEND IN USER_CATEGORIES TABLE
export type PixelColor = 'blu' | 'giallo' | 'rosso' | 'verde' | 'viola' | 'transparent';

export const isNoteVariant = (tipo: string): tipo is NoteVariant => {
  return ['N1', 'N2', 'N3', 'N4'].includes(tipo);
};
