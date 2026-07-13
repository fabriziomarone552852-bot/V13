// src/hooks/useAutoResizeTextArea.ts
import { useLayoutEffect, useRef } from 'react';

export function useAutoResizeTextArea(value: string | undefined) {
  const ref = useRef<HTMLTextAreaElement>(null);

  // Sostituiamo useEffect con useLayoutEffect!
  useLayoutEffect(() => {
    if (ref.current) {
      
      // 1. REGOLE CSS INIETTATE: 
      // Garantiamo che non compaia mai la scrollbar verticale durante il ricalcolo 
      // e che padding/bordi siano inclusi nel calcolo dell'altezza.
      ref.current.style.boxSizing = 'border-box';
      ref.current.style.overflowY = 'hidden';

      // 2. Resettiamo l'altezza per ricalcolarla in base al contenuto effettivo
      ref.current.style.height = 'auto';
      
      // 3. Leggiamo la nuova altezza reale e la applichiamo istantaneamente
      ref.current.style.height = `${ref.current.scrollHeight}px`;
    }
  }, [value]);

  return ref;
}