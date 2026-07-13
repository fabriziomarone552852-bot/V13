// src/components/dashboard/EventDetailModal.tsx
import React, { useState } from 'react';
import type { CalendarEvent } from '@/types';
import { translateRRule } from '@/utils/rruleUtils';
import BaseModal from '@/components/shared/dialog/BaseModal';
import { useConfirm } from '@/context/ConfirmContext';
import { Badge } from '@/components/shared/utils/Badges';
import { EditIcon, TrashIcon, ArrowRightLongIcon, LocationIcon } from '@/components/shared/utils/Icons';
import { formatToItalianShortDate } from '@/utils/dateUtils';

export interface EventDeletePayload {
  id: number;
  mode: 'single' | 'future' | 'all';
  dateStr: string;
  currentRrule?: string;
  currentEsclusioni?: string;
}

interface EventDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedEvent: CalendarEvent | null; 
  onEditClick: () => void;
  onDeleteClick: (payload: EventDeletePayload) => void; 
}

const EventDetailModal: React.FC<EventDetailModalProps> = ({ 
  isOpen, onClose, selectedEvent, onEditClick, onDeleteClick 
}) => {
  const { confirm } = useConfirm();
  const [showRecurringDeleteOptions, setShowRecurringDeleteOptions] = useState(false);

  if (!isOpen || !selectedEvent) return null;

  const dataInizio = formatToItalianShortDate(selectedEvent.dateStr);
  const dataFine = formatToItalianShortDate(selectedEvent.endDateStr);
  const haFine = (dataFine && dataFine !== dataInizio) || selectedEvent.endTime;

  const handleDeleteClick = () => {
    if (selectedEvent.rrule) {
      setShowRecurringDeleteOptions(true);
    } else {
      confirm({
        title: "Elimina Evento",
        message: "Sei sicuro di voler eliminare definitivamente questo evento dal calendario? L'azione non è reversibile.",
        confirmText: "Elimina",
        isDestructive: true,
        onConfirm: () => {
          onDeleteClick({
            id: selectedEvent.originalId as number,
            mode: 'all',
            // 🛡️ Fix 1: Se undefined, passa una stringa vuota
            dateStr: selectedEvent.dateStr ?? '' 
          });
        }
      });
    }
  };

  // 🪄 2. Handler per i 3 bottoni ricorrenti
  const confirmRecurringDelete = (mode: 'single' | 'future' | 'all') => {
    onDeleteClick({
      id: selectedEvent.originalId as number,
      mode: mode,
      // 🛡️ Fix 1: Se undefined, passa stringa vuota
      dateStr: selectedEvent.dateStr ?? '', 
      
      // 🛡️ Trasformiamo eventuali null in undefined per compiacere TypeScript
      currentRrule: selectedEvent.rrule ?? undefined,
      
      // 🛡️ Fix 2: Trasformiamo eventuali null in undefined
      currentEsclusioni: selectedEvent.esclusioni ?? undefined 
    });
    setShowRecurringDeleteOptions(false);
  };

  const HeaderTags = (
    <Badge variant="category" colorHex={selectedEvent.categoryColor}>
      {selectedEvent.category}
    </Badge>
  );
  
  // const HeaderActions = (
  //   <>
  //     <button title="Modifica" onClick={onEditClick} className="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors">
  //       <EditIcon className="h-5 w-5" />
  //     </button>
  //     <button title="Elimina" onClick={handleDelete} className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
  //       <TrashIcon className="h-5 w-5" />
  //     </button>
  //   </>
  // );

  const HeaderActions = showRecurringDeleteOptions ? (
    <div className="flex gap-2 bg-red-50 p-2 rounded-lg border border-red-100">
       <span className="text-sm text-red-800 font-bold mr-2">Elimina:</span>
       <button onClick={() => confirmRecurringDelete('single')} className="text-xs bg-white text-red-600 px-2 py-1 rounded shadow-sm hover:bg-red-100">Solo questo</button>
       <button onClick={() => confirmRecurringDelete('future')} className="text-xs bg-white text-red-600 px-2 py-1 rounded shadow-sm hover:bg-red-100">Questo e futuri</button>
       <button onClick={() => confirmRecurringDelete('all')} className="text-xs bg-white text-red-600 px-2 py-1 rounded shadow-sm hover:bg-red-100">Tutta la serie</button>
       <button onClick={() => setShowRecurringDeleteOptions(false)} className="text-xs text-gray-500 ml-2 hover:underline">Annulla</button>
    </div>
  ) : (
    <>
      <button title="Modifica" onClick={onEditClick} className="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors">
        <EditIcon className="h-5 w-5" />
      </button>
      <button title="Elimina" onClick={handleDeleteClick} className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
        <TrashIcon className="h-5 w-5" />
      </button>
    </>
  );

      return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      title={HeaderTags}
      headerActions={HeaderActions}
      maxWidthClass="max-w-md"
    >
      <div className="space-y-4">
          
          <div>
            <h2 className="text-2xl font-extrabold text-gray-800">{selectedEvent.title}</h2>
            <div className="flex flex-wrap items-center gap-2 mt-2 text-sm font-bold text-red-500">
              <span>Data: {dataInizio} {selectedEvent.time && ` ${selectedEvent.time}`}</span>
              {haFine && (
                <>
                  <ArrowRightLongIcon />
                  <span>
                    {dataFine && dataFine !== dataInizio ? `${dataFine} ` : ''}
                    {selectedEvent.endTime && ` ${selectedEvent.endTime}`}
                  </span>
                </>
              )}
            </div>
            
            {selectedEvent.rrule && (
              <div className="mt-2 inline-block px-2.5 py-1 text-xs font-bold rounded-md bg-blue-100 text-blue-700">
                🔄 {translateRRule(selectedEvent.rrule, selectedEvent.dateStr)}
              </div>
            )}
          </div>

          {selectedEvent.location && (
            <div className="flex items-center gap-2 text-gray-600 text-sm">
              <LocationIcon />
              {selectedEvent.location}
            </div>
          )}
          
          {selectedEvent.description && (
            <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
              <h4 className="text-xs font-bold text-gray-500 uppercase mb-2 tracking-wider">Note aggiuntive</h4>
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{selectedEvent.description}</p>
            </div>
          )}

        </div>
        {/* FINE BODY */}
        
      
    </BaseModal>
  );
};

export default EventDetailModal;