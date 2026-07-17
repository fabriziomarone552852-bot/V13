import React, { useRef, useState } from 'react';
import { getHexColor } from '@/utils/uiUtils';
import { TimeDisplay, DateRangeDisplay } from '@/components/shared/utils/DateTimeDisplays';
import { useOutsideClick } from '@/hooks/useOutsideClick';
import type { CalendarGridItem } from './MonthGrid';

export type DailyMood = 'Gioia' | 'Tristezza' | 'Rabbia' | 'Disgusto' | 'Paura';

interface MoodConfig {
  name: DailyMood;
  bgClass: string;
  borderClass: string;
  emoji: string;
}

const MOODS: Record<DailyMood, MoodConfig> = {
  Gioia: { name: 'Gioia', bgClass: 'bg-yellow-50', borderClass: 'border-yellow-300', emoji: '😄' },
  Tristezza: { name: 'Tristezza', bgClass: 'bg-blue-50', borderClass: 'border-blue-300', emoji: '😢' },
  Rabbia: { name: 'Rabbia', bgClass: 'bg-red-50', borderClass: 'border-red-300', emoji: '😡' },
  Disgusto: { name: 'Disgusto', bgClass: 'bg-green-50', borderClass: 'border-green-300', emoji: '🤢' },
  Paura: { name: 'Paura', bgClass: 'bg-purple-50', borderClass: 'border-purple-300', emoji: '😨' },
};

interface MonthDayCellProps {
  dateKey: string;
  dayNum: number;
  isToday: boolean;
  items: CalendarGridItem[];
  initialMood?: DailyMood | null; 
  onDayClick?: (dateStr: string) => void;
  onAddEventClick?: (dateStr: string) => void;
  onMoodChange?: (dateStr: string, newMood: DailyMood | null) => void; 
  showMoodSelector?: boolean; // <-- MAGIA 1: La Flag di visibilità
}

export const MonthDayCell: React.FC<MonthDayCellProps> = ({ 
  dateKey, dayNum, isToday, items, initialMood, onDayClick, onAddEventClick, onMoodChange, showMoodSelector = false 
}) => {
  const [isHovered, setIsHovered] = useState<boolean>(false);
  const clickTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [selectedMood, setSelectedMood] = useState<DailyMood | null>(initialMood || null);
  const [isMoodMenuOpen, setIsMoodMenuOpen] = useState(false);

  const moodMenuRef = useOutsideClick<HTMLDivElement>(() => {
    if (isMoodMenuOpen) setIsMoodMenuOpen(false);
  });

  const hasItems = items.length > 0;
  const multiDayItems = items.filter(i => i.isMultiDay);
  const singleDayItems = items.filter(i => !i.isMultiDay);

  const handleSingleClick = () => {
    if (clickTimeoutRef.current) return;
    clickTimeoutRef.current = setTimeout(() => {
      if (onDayClick) onDayClick(dateKey);
      clickTimeoutRef.current = null;
    }, 250); 
  };

  const handleDoubleClick = () => {
    if (clickTimeoutRef.current) {
      clearTimeout(clickTimeoutRef.current);
      clickTimeoutRef.current = null;
    }
    if (onAddEventClick) onAddEventClick(dateKey);
  };

  const handleMoodSelect = (e: React.MouseEvent, mood: DailyMood | null) => {
    e.stopPropagation(); 
    setSelectedMood(mood);
    setIsMoodMenuOpen(false);
    if (onMoodChange) onMoodChange(dateKey, mood);
  };

  const activeMoodConfig = selectedMood ? MOODS[selectedMood] : null;
  
  const cellBg = activeMoodConfig 
    ? activeMoodConfig.bgClass 
    : 'bg-gray-50 hover:bg-blue-100/50';

  const cellBorder = activeMoodConfig 
    ? activeMoodConfig.borderClass 
    : 'border-gray-200 hover:border-blue-400';

  return (
    <div 
      onMouseEnter={() => { hasItems && setIsHovered(true); }} 
      onMouseLeave={() => setIsHovered(false)} 
      onClick={handleSingleClick}
      onDoubleClick={handleDoubleClick}
      className={`relative p-1.5 border rounded-lg cursor-pointer min-h-0 flex flex-col justify-between group transition-colors duration-300 ${cellBg} ${cellBorder} ${isHovered || isMoodMenuOpen ? 'z-[60]' : 'z-10'}`}
    >
      <div className="flex justify-between items-start w-full">
        <span className={`text-xs w-6 h-6 flex items-center justify-center rounded-full 
          ${isToday 
            ? 'bg-amber-500 text-white shadow-md ring-4 ring-amber-100 font-extrabold' 
            : 'text-gray-600 font-bold group-hover:text-blue-700'
          }`}
        >
          {dayNum}
        </span>

        {/* MAGIA 2: Blocchiamo il render se showMoodSelector è false (es. in Homepage) */}
        {showMoodSelector && (
          <div className="relative" ref={moodMenuRef} onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); setIsMoodMenuOpen(!isMoodMenuOpen); }}
              className={`text-base transition-all duration-200 flex items-center justify-center opacity-0 grayscale group-hover:opacity-40 hover:!opacity-100 hover:!grayscale-0`}
              title={activeMoodConfig ? activeMoodConfig.name : "Aggiungi umore"}
            >
              {activeMoodConfig ? activeMoodConfig.emoji : '🙂'}
            </button>

            {isMoodMenuOpen && (
              <div className="absolute z-[100] right-0 top-full mt-1 w-32 bg-white border border-gray-100 rounded-xl shadow-xl py-1 animate-fadeIn cursor-default">
                {Object.values(MOODS).map((mood) => (
                  <div key={mood.name} onClick={(e) => handleMoodSelect(e, mood.name)} className={`px-3 py-2 text-xs cursor-pointer flex items-center gap-2 transition-colors ${selectedMood === mood.name ? 'bg-blue-50 font-black' : 'hover:bg-gray-50 font-bold text-gray-600'}`}>
                    <span className="text-sm">{mood.emoji}</span><span>{mood.name}</span>
                  </div>
                ))}
                {selectedMood && (
                  <div onClick={(e) => handleMoodSelect(e, null)} className="px-3 py-2 mt-1 text-xs hover:bg-red-50 cursor-pointer flex items-center justify-center transition-colors text-red-500 font-bold border-t border-gray-100">
                    Rimuovi
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
      
      <div className="flex flex-col gap-1 justify-center items-center mt-auto h-5 mb-0.5 pointer-events-none">
        {multiDayItems.length > 0 && (
          <div className="flex gap-1 justify-center items-center w-full">
            {multiDayItems.slice(0, 3).map((item, idx) => <div key={`multi-${idx}`} className="h-1.5 w-3 rounded-full shrink-0" style={{ backgroundColor: getHexColor(item.categoryColor) }}></div>)}
            {multiDayItems.length > 3 && <span className="text-[8px] leading-none text-gray-400 font-bold">+</span>}
          </div>
        )}
        {singleDayItems.length > 0 && (
          <div className="flex gap-1 justify-center items-center w-full">
            {singleDayItems.slice(0, 4).map((item, idx) => <div key={`single-${idx}`} className="h-1.5 w-1.5 rounded-full shrink-0" style={{ backgroundColor: getHexColor(item.categoryColor) }}></div>)}
            {singleDayItems.length > 4 && <span className="text-[8px] leading-none text-gray-400 font-bold">+</span>}
          </div>
        )}
      </div>
      
      {isHovered && !isMoodMenuOpen && (
        <div className="absolute left-1/2 bottom-full transform -translate-x-1/2 w-56 pb-2 cursor-default" onClick={(e) => e.stopPropagation()}>
          <div className="bg-gray-900 text-white rounded-xl shadow-xl p-3 text-left border border-gray-800 animate-fadeIn relative">
            <p className="text-[10px] font-extrabold text-blue-400 uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">
              Impegni del {dateKey.split('-').reverse().slice(0,2).join('/')}
            </p>
            <div className="space-y-1.5 max-h-32 overflow-y-auto pr-1 custom-scrollbar">
              {items.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2 text-xs w-full min-w-0 py-0.5">
                  <span className={`h-1.5 rounded-full flex-shrink-0 ${item.isMultiDay ? 'w-3' : 'w-1.5'}`} style={{ backgroundColor: getHexColor(item.categoryColor) }} />
                  <div className="flex-1 min-w-0 text-gray-200 flex items-center gap-1.5 truncate">
                    {item.type === 'event' && <span className="text-[9px] font-bold text-gray-400 shrink-0 inline-flex items-center">{item.dateStr && item.endDateStr && item.dateStr !== item.endDateStr ? <DateRangeDisplay startStr={item.dateStr} endStr={item.endDateStr} /> : <TimeDisplay time={item.time} endTime={item.endTime} />}</span>}
                    <span className={`truncate ${item.done ? 'line-through text-gray-500 italic' : ''}`} title={item.title}>{item.title}</span>
                  </div>
                </div>
              ))}
            </div>
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
          </div>
        </div>
      )}
    </div>
  );
};