// frontend/src/types/monthlyentries.ts

export const MOOD_NAMES = ['Gioia', 'Tristezza', 'Rabbia', 'Disgusto', 'Paura'] as const;
export const SPHERE_NAMES = ['Coppia', 'Famiglia', 'Amici', 'Svago', 'Mente', 'Lavoro', 'Finanze', 'Salute'] as const;

export type FixedMoodName = typeof MOOD_NAMES[number];
export type FixedSphereName = typeof SPHERE_NAMES[number];

export type TrackerName = FixedMoodName | FixedSphereName;
export type TrackerCategory = 'MOOD' | 'SPHERE';

export interface DbMonthlyEntry {
  id: number;
  user_id: number;
  year: number;
  month: number;
  feel_type: number;
  feel_value: number;
  feel_name: TrackerName | null; 
  feel_category?: TrackerCategory; 
}

export interface TrackerItem {
  id: string; 
  name: TrackerName; 
  category: TrackerCategory;
  colorHex: string;
  currentValue: number;  
  previousValue: number;
}