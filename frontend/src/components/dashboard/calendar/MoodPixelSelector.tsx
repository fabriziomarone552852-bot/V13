import React, { useEffect, useState } from 'react';
import { CategoryGenre, type Category } from '@/types'; 
import { useOutsideClick } from '@/hooks/useOutsideClick'; 
import { DropdownIcon, CloseIcon } from '@/components/shared/utils/Icons'; 
import { useCategories } from '@/hooks/useCategories'; 

interface MoodPixelSelectorProps {
  selectedCategoryId: number | null;
  onChange: (categoryId: number) => void;
}

// Interfaccia rigorosa per il form locale (Zero 'any')
interface NewMoodFormState {
  name: string;
  color: string;
}

export const MoodPixelSelector: React.FC<MoodPixelSelectorProps> = ({ 
  selectedCategoryId, 
  onChange 
}) => {
  // 1. CHIAMATA AL SERVER: Scarichiamo tutte le categorie[cite: 10]
  const { addCategory, dbCategories } = useCategories();

  // 2. LOGICA FRONTEND: Filtriamo solo quelle di tipo MOOD (Genere 4)
  const moodCategories: Category[] = dbCategories.filter(
    (c: Category) => c.genre === CategoryGenre.MOOD
  );
  
  // STATI LOCALI RIGOROSAMENTE TIPIZZATI
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
  const [isNewModalOpen, setIsNewModalOpen] = useState<boolean>(false);
  const [newMoodForm, setNewMoodForm] = useState<NewMoodFormState>({ name: '', color: '#3B82F6' });
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [openUpwards, setOpenUpwards] = useState<boolean>(false);

  // Troviamo il mood selezionato
  const selectedMood: Category | undefined = moodCategories.find(
    (c: Category) => c.id === selectedCategoryId
  );

  // Gestione chiusura click esterno[cite: 10]
  const wrapperRef = useOutsideClick<HTMLDivElement>(() => {
    if (isDropdownOpen) setIsDropdownOpen(false);
  });

  // Calcolo intelligente dello spazio per il menu a cascata[cite: 10]
  useEffect(() => {
    if (isDropdownOpen && wrapperRef.current) {
      const rect = wrapperRef.current.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;
      setOpenUpwards(spaceBelow < 220); 
    }
  }, [isDropdownOpen]);

  const handleSaveNew = async () => {
    const nomePulito = newMoodForm.name.trim();
    if (!nomePulito) return;

    // Controllo duplicati strictly typed[cite: 10]
    const existingCat = dbCategories.find(
      (c: Category) => c.name.toLowerCase() === nomePulito.toLowerCase()
    );

    try {
      if (existingCat) {
        setErrorMsg("Mood già esistente!");
        return; 
      }

      // Salvataggio tramite la mutazione di React Query[cite: 10]
      const newCat: Category = await addCategory({ 
        name: nomePulito, 
        color: newMoodForm.color, 
        genre: CategoryGenre.MOOD 
      });
      
      // Passiamo l'ID al componente genitore
      if (newCat.id) {
         onChange(newCat.id);
      }
      
      setIsNewModalOpen(false);
      setNewMoodForm({ name: '', color: '#3B82F6' });
      setErrorMsg('');
    } catch (err) {
      console.error(err);
      setErrorMsg("Errore durante la creazione.");
    }
  };

  return (
    <div className="relative" ref={wrapperRef}>
      
      {/* BOTTONE PRINCIPALE CHE MOSTRA IL MOOD SCELTO */}
      <div 
        onClick={() => setIsDropdownOpen(!isDropdownOpen)} 
        className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm bg-white cursor-pointer flex justify-between items-center hover:border-blue-500 transition-colors"
      >
        <div className="flex items-center gap-2">
          {selectedMood ? (
            <>
              <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: selectedMood.color || '#9CA3AF' }}></span>
              <span className="text-gray-700 font-medium truncate">{selectedMood.name}</span>
            </>
          ) : (
            <span className="text-gray-400">Inserisci Mood...</span>
          )}
        </div>
        <DropdownIcon isDropdownOpen={isDropdownOpen} />
      </div>

      {/* MENU A CASCATA DEI MOOD (Filtro Locale) */}
      {isDropdownOpen && (
        <div className={`absolute z-[100] w-full bg-white border border-gray-100 rounded-xl shadow-xl py-1 animate-fadeIn flex flex-col ${
          openUpwards ? 'bottom-full mb-2' : 'top-full mt-1'
        }`}>
          <div className="max-h-48 overflow-y-auto">
            {moodCategories.map((cat: Category) => (
              <div 
                key={cat.id} 
                onClick={() => { if(cat.id) { onChange(cat.id); setIsDropdownOpen(false); } }} 
                className="px-3 py-2 text-sm hover:bg-gray-50 cursor-pointer flex items-center gap-2 transition-colors"
              >
                <span className="w-3 h-3 rounded-full border border-gray-200 shrink-0" style={{ backgroundColor: cat.color || '#9CA3AF' }}></span>
                <span className="text-gray-700 truncate">{cat.name}</span>
              </div>
            ))}
            
            {moodCategories.length === 0 && (
              <div className="px-3 py-4 text-xs text-center text-gray-400">
                Nessun mood personale.
              </div>
            )}
          </div>
          
          {/* TASTO CREA NUOVO IN FONDO AL MENU */}
          <div className="border-t border-gray-100 p-1 bg-gray-50 mt-1 rounded-b-xl">
             <button 
               type="button" 
               onClick={() => { setIsDropdownOpen(false); setIsNewModalOpen(true); }} 
               className="w-full py-1.5 text-xs font-bold text-blue-600 hover:bg-blue-100 rounded-lg transition-colors flex items-center justify-center gap-1"
             >
               <span>+</span> Crea Nuovo
             </button>
          </div>
        </div>
      )}

      {/* POPUP CREAZIONE NUOVO MOOD (Esattamente come il tuo template)[cite: 10] */}
      {isNewModalOpen && (
        <div className="fixed inset-0 bg-gray-900/40 backdrop-blur-sm flex items-center justify-center z-[110] p-4" onClick={() => setIsNewModalOpen(false)}>
          <div className="w-64 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden pointer-events-auto" onClick={e => e.stopPropagation()}>
            <div className="px-4 py-3 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <h4 className="text-sm font-extrabold text-gray-800 uppercase tracking-wider">Nuovo Mood</h4>
              <button type="button" onClick={() => setIsNewModalOpen(false)} className="text-gray-400 hover:text-red-500"><CloseIcon className="h-4 w-4" /></button>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Stato d'Animo</label>
                <input 
                  type="text" 
                  value={newMoodForm.name} 
                  onChange={e => setNewMoodForm({...newMoodForm, name: e.target.value})} 
                  placeholder="es. Felice, Produttivo..."
                  className="w-full px-3 py-2 border rounded-lg text-sm focus:border-blue-500 outline-none" 
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Colore (HEX)</label>
                <div className="flex gap-2">
                  <input type="color" value={newMoodForm.color} onChange={e => setNewMoodForm({...newMoodForm, color: e.target.value})} className="w-10 h-10 p-0.5 border rounded-lg cursor-pointer" />
                  <input type="text" value={newMoodForm.color} onChange={e => setNewMoodForm({...newMoodForm, color: e.target.value})} className="flex-1 px-3 py-2 border rounded-lg text-sm uppercase outline-none focus:border-blue-500" />
                </div>
              </div>
              {errorMsg && <p className="text-xs text-red-500 font-bold">{errorMsg}</p>}
              <button type="button" onClick={handleSaveNew} className="w-full py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-bold text-sm">Salva</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};