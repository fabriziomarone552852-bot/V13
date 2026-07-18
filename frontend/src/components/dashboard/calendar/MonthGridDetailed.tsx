// frontend/src/components/dashboard/calendar/MonthGridDetailed.tsx
import React, { useMemo } from 'react';
import type { CalendarState } from '@/hooks/useCalendarState';
import type { CalendarEvent, DbTask, Category } from '@/types';
import { pad } from '@/utils/dateUtils';
import { isEventInDay } from '@/utils/eventUtils';
import { MonthDayCell } from './MonthDayCell';

import type { CalendarGridItem } from './MonthGrid';

interface MonthGridDetailedProps {
  state: CalendarState;
  events: CalendarEvent[];
  tasks?: DbTask[];
  allCategories?: Category[];
  onDayClick?: (dateStr: string) => void;
  onAddEventClick?: (dateStr: string) => void;
  onMoodChange?: (dateStr: string, categoryId: number | null) => void;
}

const MonthGridDetailed: React.FC<MonthGridDetailedProps> = ({
  state,
  events,
  tasks = [],
  allCategories = [],
  onDayClick,
  onAddEventClick,
  onMoodChange
}) => {
  const { monthYear, monthIndex, mainFirstDayIndex, mainDaysInMonth, todayStr } = state;

  // 2. SCUDO DI PERFORMANCE FRONTEND (Zero 'any' e Lookup O(1))
  const itemsByDate = useMemo(() => {
    if (monthYear === undefined || monthIndex === undefined) return {};

    const dictionary: Record<string, CalendarGridItem[]> = {};
    const safeTasks = Array.isArray(tasks) ? tasks : [];
    const safeEvents = Array.isArray(events) ? events : [];

    // Inizializza il dizionario per tutti i giorni del mese
    for (let i = 1; i <= mainDaysInMonth; i++) {
      const dateKey = `${monthYear}-${pad(monthIndex + 1)}-${pad(i)}`;
      dictionary[dateKey] = [];
    }

    // Mappatura Tasks
    safeTasks.forEach((t: DbTask) => {
      if (t.data_scadenza) {
        const tDate = t.data_scadenza.substring(0, 10);
        if (dictionary[tDate]) {
          dictionary[tDate].push({
            id: `task-${t.id}`,
            title: t.titolo, 
            type: 'task', 
            category: t.category?.name || 'Generico',
            isMultiDay: false, 
            categoryColor: t.category?.color || '#9CA3AF', // Fallback sicuro
            done: !!t.fatto // Assicura che sia un booleano
          });
        }
      }
    });

    // Mappatura Eventi
    safeEvents.forEach((e: CalendarEvent) => {
      for (let i = 1; i <= mainDaysInMonth; i++) {
        const dateKey = `${monthYear}-${pad(monthIndex + 1)}-${pad(i)}`;
        if (isEventInDay(e, dateKey)) {
          dictionary[dateKey].push({
            id: `event-${e.id}`,
            title: e.title, 
            type: 'event', 
            category: e.category, 
            time: e.time, 
            endTime: e.endTime,
            dateStr: e.dateStr, 
            endDateStr: e.endDateStr,
            isMultiDay: !!e.tutto_il_giorno || (!!e.endDateStr && e.endDateStr !== e.dateStr),
            // CORREZIONE ERRORE TYPESCRIPT: Fallback per categoryColor
            categoryColor: e.categoryColor || '#3B82F6', 
            done: false
          });
        }
      }
    });

    // Ordinamento (come nel file originale)
    Object.keys(dictionary).forEach(key => {
      dictionary[key].sort((a, b) => {
        if (a.isMultiDay !== b.isMultiDay) return a.isMultiDay ? -1 : 1;
        if (a.type === 'event' && b.type === 'event' && a.time && b.time) {
          return a.time.localeCompare(b.time);
        }
        if (a.done !== b.done) return a.done ? 1 : -1;
        return a.title.localeCompare(b.title);
      });
    });

    return dictionary;
  }, [tasks, events, monthYear, monthIndex, mainDaysInMonth]);

  if (monthYear === undefined || monthIndex === undefined) return null;

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-visible relative transition-none z-0 hover:z-[60]">
      
      {/* HEADER GIORNI */}
      <div className="grid grid-cols-7 gap-1 text-center mb-1 flex-shrink-0">
        {['L', 'M', 'M', 'G', 'V', 'S', 'D'].map((day, i) => (
          <div key={i} className="text-xs font-bold text-gray-400 uppercase py-1">{day}</div>
        ))}
      </div>
      
      {/* GRIGLIA */}
      <div className="grid grid-cols-7 gap-1 flex-1 min-h-0 pb-1 auto-rows-fr">
        {Array.from({ length: mainFirstDayIndex }).map((_, i) => (
          <div key={`empty-start-${i}`} className="p-2 border-transparent min-h-0"></div>
        ))}
        
        {Array.from({ length: mainDaysInMonth }).map((_, i) => {
          const dayNum = i + 1;
          const dateKey = `${monthYear}-${pad(monthIndex + 1)}-${pad(dayNum)}`;
          
          return (
            <MonthDayCell 
              key={dateKey}
              dateKey={dateKey}
              dayNum={dayNum}
              isToday={dateKey === todayStr}
              items={itemsByDate[dateKey] || []}
              onDayClick={onDayClick}
              onAddEventClick={onAddEventClick}
              showMoodSelector={true} 
              onMoodChange={onMoodChange}
              allCategories={allCategories} 
            />
          );
        })}

        {Array.from({ length: 42 - (mainFirstDayIndex + mainDaysInMonth) }).map((_, i) => (
          <div key={`empty-end-${i}`} className="p-2 border-transparent min-h-0"></div>
        ))}
      </div>
    </div>
  );
};

export default MonthGridDetailed;