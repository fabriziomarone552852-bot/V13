import type { TrackerName } from '@/types';

export const TRACKER_COLORS: Record<TrackerName, string> = {
  // Moods
  'Gioia': '#FACC15',     // Giallo
  'Tristezza': '#3B82F6', // Blu
  'Rabbia': '#EF4444',    // Rosso
  'Disgusto': '#22C55E',  // Verde
  'Paura': '#A855F7',     // Viola
  
  // Sfere
  'Coppia': '#A855F7',    // Viola
  'Famiglia': '#78350F',  // Marrone
  'Amici': '#FACC15',     // Giallo
  'Svago': '#F97316',     // Arancione
  'Mente': '#EC4899',     // Rosa
  'Lavoro': '#3B82F6',    // Blu
  'Finanze': '#22C55E',   // Verde
  'Salute': '#EF4444',    // Rosso
};

// Funzione sicura per ottenere il colore
export const getTrackerColor = (name: TrackerName): string => {
  return TRACKER_COLORS[name] || '#9CA3AF'; // Grigio di fallback (non dovrebbe mai servire)
};

// Mappa fissa degli ID del Database
export const TRACKER_IDS: Record<TrackerName, number> = {
  'Gioia': 1, 'Tristezza': 2, 'Rabbia': 3, 'Disgusto': 4, 'Paura': 5,
  'Coppia': 6, 'Famiglia': 7, 'Amici': 8, 'Svago': 9, 'Mente': 10, 'Lavoro': 11, 'Finanze': 12, 'Salute': 13
};