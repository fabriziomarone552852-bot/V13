// frontend/src/hooks/uiMonth/useMonthSidebar.ts
import { useState } from 'react';

export type MonthSidebarTab = 'moods' | 'spheres' | 'todos' | 'reflections';

// 🪄 RIMOSSO IL '?'. Ora pretendiamo sempre un numero.
export interface TrackerItem {
  id: string;
  name: string;
  colorHex: string;
  currentValue: number;
  previousValue: number; 
}

export const useMonthSidebar = () => {
  const [activeSidebarTab, setActiveSidebarTab] = useState<MonthSidebarTab>('moods');

  // Dati di esempio rigorosi: previousValue è sempre presente
  const moodsUI: TrackerItem[] = [
    { id: '1', name: 'Energia', colorHex: '#eab308', currentValue: 3, previousValue: 4 },
    { id: '2', name: 'Umore', colorHex: '#ec4899', currentValue: 4, previousValue: 3 }
  ];
  
  const spheresUI: TrackerItem[] = [
    { id: '3', name: 'Lavoro', colorHex: '#3b82f6', currentValue: 2, previousValue: 2 },
    { id: '4', name: 'Salute', colorHex: '#22c55e', currentValue: 5, previousValue: 4 }
  ];

  const handleUpdateMood = (id: string, value: number): void => { /* ... */ };
  const handleUpdateSphere = (id: string, value: number): void => { /* ... */ };

  return { activeSidebarTab, setActiveSidebarTab, moodsUI, spheresUI, handleUpdateMood, handleUpdateSphere };
};