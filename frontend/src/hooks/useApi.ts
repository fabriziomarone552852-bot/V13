// src/hooks/useApi.ts
import { useCallback } from 'react';
import { apiClient } from '../api/client'; // Importa il nostro nuovo "vigile"

export const useApi = () => {
  // Non ci serve più useAuth() qui dentro! L'interceptor fa tutto da solo.

  // Funzione per formattare gli errori esattamente come facevi prima
  const handleAxiosError = (error: any) => {
    if (error.response) {
      throw new Error(error.response.data?.detail || error.response.data?.message || `Errore API: ${error.response.status}`);
    }
    throw new Error(error.message || "Errore di rete o server non raggiungibile");
  };

  const get = useCallback(async (endpoint: string, options?: any) => {
    try {
      const response = await apiClient.get(endpoint, options);
      return response.status === 204 ? null : response.data;
    } catch (error) { return handleAxiosError(error); }
  }, []);

  const post = useCallback(async <T = unknown>(endpoint: string, body?: T) => {
    try {
      const response = await apiClient.post(endpoint, body);
      return response.status === 204 ? null : response.data;
    } catch (error) { return handleAxiosError(error); }
  }, []);

  const patch = useCallback(async <T = unknown>(endpoint: string, body: T) => {
    try {
      const response = await apiClient.patch(endpoint, body);
      return response.status === 204 ? null : response.data;
    } catch (error) { return handleAxiosError(error); }
  }, []);

  const del = useCallback(async (endpoint: string) => {
    try {
      const response = await apiClient.delete(endpoint);
      return response.status === 204 ? null : response.data;
    } catch (error) { return handleAxiosError(error); }
  }, []);

  return { get, post, patch, delete: del };
};