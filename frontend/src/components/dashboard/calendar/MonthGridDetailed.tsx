// frontend/src/components/dashboard/calendar/MonthGridDetailed.tsx
import React, { useMemo } from 'react';
import type { CalendarState } from '@/hooks/useCalendarState';
import type { CalendarEvent, DbTask } from '@/types';
import { pad } from '@/utils/dateUtils';
import { isEventInDay } from '@/utils/eventUtils';
import { MonthDayCell } from './MonthDayCell';

// 1. LA NOSTRA CLASSIFICAZIONE: Zero 'any'. Dichiariamo esattamente cosa entra nella cella.
export interface CalendarGridItem {
  id: string | number;
  title: string;
  type: 'task' | 'event';
  category: string;
  time?: string;
  endTime?: string;
  dateStr?: string;
  endDateStr?: string;
  isMultiDay: boolean;
  categoryColor: string;
  done: boolean;
}

interface MonthGridDetailedProps {
  state: CalendarState;
  events: CalendarEvent[];
  tasks?: DbTask[];
  onDayClick?: (dateStr: string) => void;
  onAddEventClick?: (dateStr: string) => void;
}

const MonthGridDetailed: React.FC<MonthGridDetailedProps> = ({
  state,
  events,
  tasks = [],
  onDayClick,
  onAddEventClick
}) => {
  const { monthYear, monthIndex, mainFirstDayIndex, mainDaysInMonth, todayStr } = state;

  // 2. SCUDO DI PERFORMANCE FRONTEND: Filtriamo eventi e task del mese una sola volta.
  const gridDays = useMemo(() => {
    if (monthYear === undefined || monthIndex === undefined) return [];

    const daysArray = [];

    for (let i = 1; i <= mainDaysInMonth; i++) {
      const dateKey = `${monthYear}-${pad(monthIndex + 1)}-${pad(i)}`;

      // Mappatura sicura dei Task (senza 'any')
      const dayTasks: CalendarGridItem[] = tasks
        .filter((t) => t.data_scadenza && t.data_scadenza.substring(0, 10) === dateKey)
        .map((t) => ({
          id: `task-${t.id}`,
          title: t.titolo,
          type: 'task',
          category: t.category?.name || 'Generico',
          isMultiDay: false,
          categoryColor: t.category?.colore || '#9CA3AF',
          done: !!t.fatto
        }));

      // Mappatura sicura degli Eventi (senza 'any')
      const dayEvents: CalendarGridItem[] = events
        .filter((e) => isEventInDay(e, dateKey))
        .map((e) => ({
          id: `event-${e.id}`,
          title: e.title,
          type: 'event',
          category: e.category,
          time: e.time,
          endTime: e.endTime,
          dateStr: e.dateStr,
          endDateStr: e.endDateStr,
          isMultiDay: !!e.tutto_il_giorno || (!!e.endDateStr && e.endDateStr !== e.dateStr),
          categoryColor: e.categoryColor,
          done: false
        }));

      daysArray.push({
        dayNum: i,
        dateKey,
        items: [...dayTasks, ...dayEvents]
      });
    }
    return daysArray;
  }, [monthYear, monthIndex, mainDaysInMonth, tasks, events]);

  if (monthYear === undefined || monthIndex === undefined) return null;

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-visible relative z-0">
      
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
        
        {/* RENDER COMPONENTE GIORNO (Senza ricalcoli inline) */}
        {gridDays.map((dayData) => (
          <MonthDayCell
            key={dayData.dateKey}
            dateKey={dayData.dateKey}
            dayNum={dayData.dayNum}
            isToday={dayData.dateKey === todayStr}
            items={dayData.items}
            onDayClick={onDayClick}
            onAddEventClick={onAddEventClick}
          />
        ))}

        {Array.from({ length: 42 - (mainFirstDayIndex + mainDaysInMonth) }).map((_, i) => (
          <div key={`empty-end-${i}`} className="p-2 border-transparent min-h-0"></div>
        ))}
      </div>
    </div>
  );
};

export default MonthGridDetailed;