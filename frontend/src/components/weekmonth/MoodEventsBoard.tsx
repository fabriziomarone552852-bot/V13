import React from 'react';
import type { MoodEvent, MoodEventType } from '@/types';
import { MoodEventColumn } from './MoodEventParts/MoodEventColumn';

interface MoodEventsBoardProps {
  positiveEvents: MoodEvent[];
  negativeEvents: MoodEvent[];
  onAddMoodEvent: (type: MoodEventType, title: string) => void;
  onUpdateMoodEvent: (id: number, newTitle: string) => void;
  onDeleteMoodEvent: (id: number) => void;
  layout?: 'horizontal' | 'vertical'; // <-- ZERO ANY
}

const MoodEventsBoard: React.FC<MoodEventsBoardProps> = ({
  positiveEvents,
  negativeEvents,
  onAddMoodEvent,
  onUpdateMoodEvent,
  onDeleteMoodEvent,
  layout = 'horizontal' // Default per WeekPage
}) => {
  const containerClass = layout === 'vertical' 
    ? "flex flex-col gap-6 w-full" 
    : "grid grid-cols-1 xl:grid-cols-2 gap-6 w-full"; 

  return (
    <div className={containerClass}>
      <MoodEventColumn 
        title="Cose Positive" type="EP" events={positiveEvents} themeColor="green"
        onAdd={onAddMoodEvent} onUpdate={onUpdateMoodEvent} onDelete={onDeleteMoodEvent}
        layout={layout} // Trasmettiamo il layout alla colonna!
      />
      <MoodEventColumn 
        title="Cose Negative" type="EN" events={negativeEvents} themeColor="red"
        onAdd={onAddMoodEvent} onUpdate={onUpdateMoodEvent} onDelete={onDeleteMoodEvent}
        layout={layout} // Trasmettiamo il layout alla colonna!
      />
    </div>
  );
};

export default MoodEventsBoard;