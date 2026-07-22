// frontend/src/hooks/uiMonth/useMonthSidebar.ts
import { useState, useMemo } from 'react';
import { useMonthlyEntryMutations } from '@/hooks/mutations/useMonthlyEntryMutations';

import { 
  MOOD_NAMES,
  SPHERE_NAMES,
  type SyncMonthResponse, 
  type TrackerItem, 
} from '@/types';

import { getTrackerColor, TRACKER_IDS } from '@/utils/trackerUtils'; 

export type MonthSidebarTab = 'moods' | 'spheres' | 'todos' | 'reflections';

export const useMonthSidebar = (monthData: SyncMonthResponse | undefined, currentMonthDateStr: string) => {
  const [activeSidebarTab, setActiveSidebarTab] = useState<MonthSidebarTab>('moods');

  const { saveMonthlyEntry } = useMonthlyEntryMutations(['monthSync', currentMonthDateStr]);

  const moodsUI = useMemo((): TrackerItem[] => {
    const vociDB = monthData?.monthly_entries || []; 

    return MOOD_NAMES.map(nome => {
      const feelId = TRACKER_IDS[nome];
      // 🪄 CORREZIONE: Cerchiamo matematicamente tramite l'ID numerico!
      const voceSalvata = vociDB.find(v => v.feel_type === feelId);

      return {
        id: String(feelId),
        name: nome,
        category: 'MOOD',
        colorHex: getTrackerColor(nome),
        // Ora troverà sempre il valore corretto, anche nell'istante del click
        currentValue: voceSalvata ? voceSalvata.feel_value : 0,
        previousValue: 0 
      };
    });
  }, [monthData]);

  const spheresUI = useMemo((): TrackerItem[] => {
    const vociDB = monthData?.monthly_entries || []; 

    return SPHERE_NAMES.map(nome => {
      const feelId = TRACKER_IDS[nome];
      // 🪄 CORREZIONE: Cerchiamo matematicamente tramite l'ID numerico!
      const voceSalvata = vociDB.find(v => v.feel_type === feelId);

      return {
        id: String(feelId),
        name: nome,
        category: 'SPHERE',
        colorHex: getTrackerColor(nome),
        currentValue: voceSalvata ? voceSalvata.feel_value : 0,
        previousValue: 0 
      };
    });
  }, [monthData]);

  const handleUpdateMood = (idStr: string, value: number): void => {
    const feel_type = Number(idStr);
    const existingEntry = monthData?.monthly_entries?.find(e => e.feel_type === feel_type);

    saveMonthlyEntry({ feel_type, value, dateStr: currentMonthDateStr, existingEntryId: existingEntry?.id });
  };

  const handleUpdateSphere = (idStr: string, value: number): void => {
    const feel_type = Number(idStr);
    const existingEntry = monthData?.monthly_entries?.find(e => e.feel_type === feel_type);

    saveMonthlyEntry({ feel_type, value, dateStr: currentMonthDateStr, existingEntryId: existingEntry?.id });
  };

  return { activeSidebarTab, setActiveSidebarTab, moodsUI, spheresUI, handleUpdateMood, handleUpdateSphere };
};