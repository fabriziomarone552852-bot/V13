// src/components/dashboard/calendar/MonthGrid.tsx
import React, { useMemo } from 'react';
import type { CalendarState } from '@/hooks/useCalendarState';
import type { CalendarEvent, DbTask } from '@/types';
import { pad } from '@/utils/dateUtils';
import { isEventInDay } from '@/utils/eventUtils';
import { MonthDayCell } from './MonthDayCell';

// 1. IL CONTRATTO UFFICIALE: Zero 'any', esportato per essere usato ovunque!
export type CalendarItemType = 'task' | 'event';

export interface CalendarGridItem {
  id: string | number;
  title: string;
  type: CalendarItemType;
  category: string;
  isMultiDay: boolean;
  categoryColor: string;
  done: boolean;
  time?: string;
  endTime?: string;
  dateStr?: string;
  endDateStr?: string;
}

interface MonthGridProps {
  state: CalendarState;
  events: CalendarEvent[];
  tasks: DbTask[];
  onDayClick?: (dateStr: string) => void;
  onAddEventClick?: (dateStr: string) => void;
}

const MonthGrid: React.FC<MonthGridProps> = ({ state, events, tasks, onDayClick, onAddEventClick }) => {
  const { monthYear, monthIndex, mainFirstDayIndex, mainDaysInMonth, todayStr } = state;

  // 2. MOTORE DI PERFORMANCE: Calcoliamo la griglia una sola volta
  const itemsByDate = useMemo(() => {
    if (monthYear === undefined || monthIndex === undefined) return {};

    const dictionary: Record<string, CalendarGridItem[]> = {};
    const safeTasks: DbTask[] = Array.isArray(tasks) ? tasks : [];
    const safeEvents: CalendarEvent[] = Array.isArray(events) ? events : [];

    // Inizializzazione O(1)
    for (let i = 1; i <= mainDaysInMonth; i++) {
      const dateKey = `${monthYear}-${pad(monthIndex + 1)}-${pad(i)}`;
      dictionary[dateKey] = [];
    }

    // Mappatura Tasks (Type-Safe)
    safeTasks.forEach((t: DbTask) => {
      if (t.data_scadenza) {
        const tDate = t.data_scadenza.substring(0, 10);
        if (dictionary[tDate]) {
          dictionary[tDate].push({
            id: `task-${t.id}`,
            title: t.titolo, 
            type: 'task', 
            category: t.category?.category_name || 'Generico',
            isMultiDay: false, 
            categoryColor: t.category?.colore || '#9CA3AF', 
            done: !!t.fatto
          });
        }
      }
    });

    // Mappatura Eventi (Type-Safe)
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
            categoryColor: e.categoryColor || '#3B82F6', 
            done: false
          });
        }
      }
    });

    // Ordinamento Intelligente
    Object.keys(dictionary).forEach(key => {
      dictionary[key].sort((a: CalendarGridItem, b: CalendarGridItem) => {
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

  // Se i dati del calendario non sono ancora pronti
  if (monthYear === undefined || monthIndex === undefined) return null;

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-visible relative transition-none z-0 hover:z-[60]">
      
      {/* HEADER GIORNI DELLA SETTIMANA */}
      <div className="grid grid-cols-7 gap-1 text-center mb-1 flex-shrink-0">
        {['L', 'M', 'M', 'G', 'V', 'S', 'D'].map((day, i) => (
          <div key={`header-${i}`} className="text-xs font-bold text-gray-400 uppercase py-1">{day}</div>
        ))}
      </div>
      
      {/* CORPO DELLA GRIGLIA */}
      <div className="grid grid-cols-7 gap-1 flex-1 min-h-0 pb-1 auto-rows-fr">
        
        {/* Celle vuote inizio mese */}
        {Array.from({ length: mainFirstDayIndex }).map((_, i) => (
          <div key={`empty-start-${i}`} className="p-2 border-transparent min-h-0"></div>
        ))}
        
        {/* Renderizziamo delegando tutto al componente intelligente MonthDayCell */}
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
            />
          );
        })}

        {/* Celle vuote fine mese */}
        {Array.from({ length: 42 - (mainFirstDayIndex + mainDaysInMonth) }).map((_, i) => (
          <div key={`empty-end-${i}`} className="p-2 border-transparent min-h-0"></div>
        ))}
      </div>
    </div>
  );
};

export default MonthGrid;