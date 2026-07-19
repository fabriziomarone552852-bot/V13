// frontend/src/hooks/uiMonth/useMonthSidebar.ts
import { useState, useMemo } from 'react';
import type { SyncMonthResponse } from '@/hooks/useAgendaMonth';

export type MonthSidebarTab = 'moods' | 'spheres' | 'todos' | 'reflections';

// 1. IL CONTRATTO PER LA UI: Come il componente vuole i dati
export interface TrackerItem {
  id: string;
  name: string;
  colorHex: string;
  currentValue: number;
  previousValue: number;
}

// 2. IL CONTRATTO PER IL DB: La forma esatta definita in schemas.py del Backend
export interface DbMonthlyEntry {
  id: number;
  user_id: number;
  year: number;
  month: number;
  feel_type: number;
  feel_value: number;
  feel_name: string | null;
}

export const useMonthSidebar = (monthData: SyncMonthResponse | undefined) => {
  const [activeSidebarTab, setActiveSidebarTab] = useState<MonthSidebarTab>('moods');

  // TRADUTTORE IN RAM: Prendiamo le carte dal DB e le filtriamo
  const moodsUI = useMemo((): TrackerItem[] => {
    // Sostituisci 'monthly_entries' con il nome esatto usato in SyncMonthResponse
    const tutteLeVoci: DbMonthlyEntry[] = monthData?.monthly_entries || []; 

    // Filtriamo solo i "feel_name" che consideriamo Umori
    const umoriGrezzi = tutteLeVoci.filter(entry => 
      entry.feel_name === "Energia" || 
      entry.feel_name === "Umore"
    );

    // Li "vestiamo" per la UI
    return umoriGrezzi.map(item => ({
      id: String(item.id),
      name: item.feel_name || 'Senza nome',
      colorHex: '#eab308', // Colore fisso o calcolato nel frontend
      currentValue: item.feel_value,
      previousValue: 0 // Se il DB non manda il mese scorso, mettiamo 0 di default per TypeScript
    }));
  }, [monthData]);

  // TRADUTTORE IN RAM: Facciamo la stessa cosa per le Sfere
  const spheresUI = useMemo((): TrackerItem[] => {
    const tutteLeVoci: DbMonthlyEntry[] = monthData?.monthly_entries || []; 

    // Filtriamo solo i "feel_name" che consideriamo Sfere
    const sfereGrezze = tutteLeVoci.filter(entry => 
      entry.feel_name === "Lavoro" || 
      entry.feel_name === "Salute" ||
      entry.feel_name === "Famiglia"
    );

    return sfereGrezze.map(item => ({
      id: String(item.id),
      name: item.feel_name || 'Senza nome',
      colorHex: '#3b82f6',
      currentValue: item.feel_value,
      previousValue: 0 
    }));
  }, [monthData]);

  const handleUpdateMood = (id: string, value: number): void => {
    console.log("Da implementare: Salva Umore", id, value);
  };

  const handleUpdateSphere = (id: string, value: number): void => {
    console.log("Da implementare: Salva Sfera", id, value);
  };

  return {
    activeSidebarTab,
    setActiveSidebarTab,
    moodsUI,
    spheresUI,
    handleUpdateMood,
    handleUpdateSphere
  };
};