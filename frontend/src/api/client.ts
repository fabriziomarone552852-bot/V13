// src/api/client.ts
import axios from 'axios';

// Manteniamo la tua funzione originale per compatibilità
export function apiUrl(path: string) {
  if (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) {
    return `${window.APP_CONFIG.API_BASE_URL}${path}`;
  }
  return path;
}

// 1. Creiamo un "Client API" dedicato
export const apiClient = axios.create();

// 2. INTERCEPTOR DELLE RICHIESTE (In uscita)
apiClient.interceptors.request.use((config) => {
  // Configura la baseURL dinamicamente
  config.baseURL = window.APP_CONFIG?.API_BASE_URL || '';
  
  // Prendi il token da localStorage e attaccalo
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// 3. INTERCEPTOR DELLE RISPOSTE (In entrata)
apiClient.interceptors.response.use(
  (response) => response, // Se va tutto bene, restituisci i dati
  async (error) => {
    const originalRequest = error.config;

    // Se l'errore è 401 (scaduto) e non abbiamo ancora provato a fare il refresh (_retry)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Segnamo che stiamo riprovando (evita loop infiniti)

      const refreshToken = localStorage.getItem('refreshToken');
      
      if (refreshToken) {
        try {
          // Facciamo la chiamata di refresh usando axios "puro" per non passare da questo interceptor
          const response = await axios.post(apiUrl('/refresh'), {
            refresh_token: refreshToken
          });

          const { access_token } = response.data;

          // Aggiorniamo la cassaforte
          localStorage.setItem('token', access_token);
          if (response.data.refresh_token) {
            localStorage.setItem('refreshToken', response.data.refresh_token);
          }

          // Riproviamo la chiamata originale fallita con il NUOVO token!
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return axios(originalRequest);
          
        } catch (refreshError) {
          // Il refresh token è scaduto o non valido: buttiamo fuori l'utente!
          window.dispatchEvent(new Event('force-logout'));
          return Promise.reject(refreshError);
        }
      } else {
        // Niente refresh token: buttiamo fuori l'utente
        window.dispatchEvent(new Event('force-logout'));
      }
    }

    return Promise.reject(error);
  }
);