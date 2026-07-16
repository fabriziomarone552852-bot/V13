// frontend/src/types/monthlyentries.ts

export type MonthlyEntryType = 
  | 'mood_sadness' | 'mood_happiness' | 'mood_anger' | 'mood_disgust' | 'mood_fear'
  | 'sphere_work' | 'sphere_love' | 'sphere_family' | 'sphere_finance' 
  | 'sphere_health' | 'sphere_fun' | 'sphere_mind' | 'sphere_friendship';

export interface MonthlyEntry {
  id: number;
  user_id: number;
  yearId: number; 
  monthId: string; 
  type: MonthlyEntryType; // Invece di string generico!
  value: number;
}