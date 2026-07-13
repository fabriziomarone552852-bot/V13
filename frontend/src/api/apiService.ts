// src/api/apiService.ts
import { apiClient } from './client'; 
import axios, { AxiosError, type AxiosRequestConfig } from 'axios';

// Interfaccia per gli errori di FastAPI o risposte standard di errore
export interface ApiErrorData {
  detail?: string | { loc: (string | number)[]; msg: string; type: string }[];
  message?: string;
}

// Funzione centralizzata per la gestione degli errori (Pura e Type-Safe)
const handleAxiosError = (error: unknown): never => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorData>; 
    
    if (axiosError.response) {
      const errorData = axiosError.response.data;
      let errorMessage = `Errore API: ${axiosError.response.status}`;

      // Gestione errore 422 di FastAPI
      if (Array.isArray(errorData?.detail)) {
        errorMessage = errorData.detail
          .map((err) => `${err.loc.join(' -> ')}: ${err.msg}`)
          .join(' | ');
      } 
      else if (typeof errorData?.detail === 'string') {
        errorMessage = errorData.detail;
      } 
      else if (errorData?.message) {
        errorMessage = errorData.message;
      }

      throw new Error(errorMessage);
    }
  }
  
  const genericError = error as Error;
  throw new Error(genericError.message || "Errore di rete o server non raggiungibile");
};

// L'oggetto 'api' è un modulo utility TypeScript puro (Singleton)
export const api = {
  /**
   * Esegue una richiesta GET.
   * Se il server restituisce 204 No Content, ritorna null.
   */
  get: async <T = unknown>(endpoint: string, options?: AxiosRequestConfig): Promise<T | null> => {
    try {
      const response = await apiClient.get<T>(endpoint, options);
      return response.status === 204 ? null : response.data;
    } catch (error) { 
      return handleAxiosError(error); 
    }
  },

  /**
   * Esegue una richiesta POST.
   */
  post: async <T = unknown, D = unknown>(endpoint: string, body?: D, options?: AxiosRequestConfig): Promise<T | null> => {
    try {
      const response = await apiClient.post<T>(endpoint, body, options);
      return response.status === 204 ? null : response.data;
    } catch (error) { 
      return handleAxiosError(error); 
    }
  },

  /**
   * Esegue una richiesta PATCH.
   */
  patch: async <T = unknown, D = unknown>(endpoint: string, body: D, options?: AxiosRequestConfig): Promise<T | null> => {
    try {
      const response = await apiClient.patch<T>(endpoint, body, options);
      return response.status === 204 ? null : response.data;
    } catch (error) { 
      return handleAxiosError(error); 
    }
  },

  /**
   * Esegue una richiesta DELETE.
   */
  delete: async <T = unknown>(endpoint: string, options?: AxiosRequestConfig): Promise<T | null> => {
    try {
      const response = await apiClient.delete<T>(endpoint, options);
      return response.status === 204 ? null : response.data;
    } catch (error) { 
      return handleAxiosError(error); 
    }
  }
};