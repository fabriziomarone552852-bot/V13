// src/components/day/NotesSidebar.tsx
import React, { useState, useEffect } from 'react';
import type { LocalNoteEntry, NoteVariant } from '@/types';
import { isNoteVariant } from '@/types'; // 🪄 Importiamo la guardia di tipo!
import { CloseIcon, TrashIcon, PlusIcon, NoteIcon } from '@/components/shared/utils/Icons';
import { useAutoResizeTextArea } from '@/hooks/useAutoResizeTextArea';
import { useDebounce } from '@/hooks/useDebounce';

const NOTE_STYLES: Record<NoteVariant, { card: string; ring: string; text: string; placeholder: string; btnHover: string; btnBg: string; btnText: string }> = {
  N1: { card: 'bg-yellow-100', ring: 'ring-yellow-400/50', text: 'text-yellow-900', placeholder: 'placeholder-yellow-800/40', btnBg: 'bg-yellow-300/30', btnHover: 'hover:bg-yellow-300/80', btnText: 'text-yellow-800/40 hover:text-red-600' },
  N2: { card: 'bg-green-100', ring: 'ring-green-400/50', text: 'text-green-900', placeholder: 'placeholder-green-800/40', btnBg: 'bg-green-300/30', btnHover: 'hover:bg-green-300/80', btnText: 'text-green-800/40 hover:text-red-600' },
  N3: { card: 'bg-blue-100', ring: 'ring-blue-400/50', text: 'text-blue-900', placeholder: 'placeholder-blue-800/40', btnBg: 'bg-blue-300/30', btnHover: 'hover:bg-blue-300/80', btnText: 'text-blue-800/40 hover:text-red-600' },
  N4: { card: 'bg-pink-100', ring: 'ring-pink-400/50', text: 'text-pink-900', placeholder: 'placeholder-pink-800/40', btnBg: 'bg-pink-300/30', btnHover: 'hover:bg-pink-300/80', btnText: 'text-pink-800/40 hover:text-red-600' },
};

const SmartNoteCard: React.FC<{
  nota: LocalNoteEntry;
  isInitiallyEditing: boolean;
  onAutoSave: (id: number, testo: string, tipo: NoteVariant, isNew?: boolean) => void;
  onDelete: (id: number, isNew?: boolean) => void;
  clearNewStatus: () => void;
}> = ({ nota, isInitiallyEditing, onAutoSave, onDelete, clearNewStatus }) => {
  const [isEditing, setIsEditing] = useState(isInitiallyEditing);
  const [testoLocal, setTestoLocal] = useState(nota.testo);
  
  const debouncedText = useDebounce(testoLocal, 1000);
  const textareaRef = useAutoResizeTextArea(testoLocal);

  // 🪄 VERIFICA DI SICUREZZA
  // Se il tipo che arriva dal database è corretto lo usiamo, altrimenti forziamo 'N1' di default.
  // Nessun "as" necessario, TypeScript ora sa che safeVariant è sicuramente una NoteVariant.
  const safeVariant: NoteVariant = isNoteVariant(nota.tipo) ? nota.tipo : 'N1';
  const styles = NOTE_STYLES[safeVariant];

  useEffect(() => {
    if (debouncedText !== nota.testo) {
      if (debouncedText.trim() === "") {
        onDelete(nota.id, nota.isNew);
      } else {
        onAutoSave(nota.id, debouncedText, safeVariant, nota.isNew);
        clearNewStatus();
      }
    }
  }, [debouncedText]);

  const handleBlur = () => {
    setIsEditing(false);
    if (testoLocal.trim() === "") {
      onDelete(nota.id, nota.isNew);
    } else if (testoLocal !== nota.testo) {
      onAutoSave(nota.id, testoLocal, safeVariant, nota.isNew);
      clearNewStatus();
    }
  };

  return (
    <div 
      onClick={() => { if (!isEditing) setIsEditing(true); }} 
      className={`p-4 rounded-br-2xl rounded-tl-lg rounded-tr-lg rounded-bl-lg shadow-md relative group min-h-[5rem] transition-colors ${styles.card} ${isEditing ? `cursor-text ring-2 ${styles.ring}` : 'cursor-pointer hover:shadow-lg'}`}
    >
      <div className="absolute bottom-0 right-0 w-4 h-4 bg-black/10 rounded-tl-lg rounded-br-2xl pointer-events-none"></div>
      
      <button 
        onClick={(e) => { e.stopPropagation(); onDelete(nota.id, nota.isNew); }} 
        className={`absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-full z-10 ${styles.btnText} ${styles.btnBg} ${styles.btnHover}`} 
        title="Elimina nota"
      >
        <TrashIcon className="w-4 h-4" />
      </button>

      {isEditing ? (
        <textarea
          ref={textareaRef}
          autoFocus
          value={testoLocal}
          onChange={(e) => setTestoLocal(e.target.value)}
          onFocus={(e) => e.target.setSelectionRange(e.target.value.length, e.target.value.length)}
          onBlur={handleBlur}
          placeholder="Scrivi qui la tua nota..."
          className={`w-full bg-transparent border-none focus:ring-0 resize-none outline-none text-sm font-medium leading-relaxed font-mono p-0 overflow-hidden pr-6 custom-scrollbar ${styles.text} ${styles.placeholder}`}
          rows={1}
        />
      ) : (
        <p className={`text-sm font-medium leading-relaxed font-mono whitespace-pre-wrap break-words pr-6 ${styles.text}`}>
          {testoLocal || <span className="italic opacity-60">Nota vuota... Clicca per scrivere.</span>}
        </p>
      )}
    </div>
  );
};

interface NotesSidebarProps {
  isOpen: boolean;
  notes: LocalNoteEntry[];
  editingNoteId: number | null;
  onOpen: () => void;
  onClose: () => void;
  onAddNote: () => void;
  onAutoSaveNote: (id: number, testo: string, tipo: NoteVariant, isNew?: boolean) => void;
  onDeleteNote: (id: number, isNew?: boolean) => void;
  clearEditingNoteId: () => void;
}

const NotesSidebar: React.FC<NotesSidebarProps> = ({ 
  isOpen, notes, editingNoteId, onOpen, onClose, onAddNote, onAutoSaveNote, onDeleteNote, clearEditingNoteId 
}) => {
  
  return (
    <>
      <div onClick={onOpen} className="fixed right-0 top-1/2 -translate-y-1/2 translate-x-8 hover:translate-x-0 w-20 hover:w-28 h-14 bg-[#fde047] hover:bg-[#facc15] text-yellow-900 rounded-l-2xl shadow-[-5px_0_15px_rgba(0,0,0,0.1)] flex items-center justify-start pl-3 cursor-pointer transition-all duration-300 z-60 border border-y-yellow-300 border-l-yellow-300 group">
        <NoteIcon className="w-6 h-6" />
        <span className="ml-2 font-black text-sm uppercase opacity-0 group-hover:opacity-100 transition-opacity delay-100">Note</span>
      </div>

      <div className={`fixed top-0 right-0 h-full w-96 bg-white shadow-[-10px_0_30px_rgba(0,0,0,0.1)] z-70 transform transition-transform duration-300 ease-in-out flex flex-col ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <h2 className="text-xl font-black text-gray-800 uppercase tracking-widest flex items-center gap-2">
            <NoteIcon className="w-5 h-5 text-yellow-500" />
            Note
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-red-500 transition-colors">
            <CloseIcon />
          </button>
        </div>
        
        <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-gray-50/50 custom-scrollbar">
          <button onClick={onAddNote} className="w-full py-2.5 border-2 border-dashed border-gray-300 rounded-xl text-gray-500 hover:border-blue-500 hover:text-blue-500 hover:bg-blue-50 active:scale-95 active:bg-blue-100 transition-all flex justify-center items-center font-bold text-sm gap-2">
            <PlusIcon />
            Nuova Nota
          </button>

          {notes.map(nota => (
            <SmartNoteCard 
              key={nota.id}
              nota={nota}
              isInitiallyEditing={editingNoteId === nota.id}
              onAutoSave={onAutoSaveNote}
              onDelete={onDeleteNote}
              clearNewStatus={clearEditingNoteId}
            />
          ))}
        </div>
      </div>
      {isOpen && <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-60 transition-opacity" onClick={onClose}></div>}
    </>
  );
};

export default NotesSidebar;