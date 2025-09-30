import axios, { AxiosError } from 'axios';
import { ApiUrl } from '../config';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Base URL centralizada en config.ts (resuelve según plataforma y variable de entorno)
const baseUrl = ApiUrl;

export const http = axios.create({
  baseURL: baseUrl,
  timeout: 15000,
});

// Token helpers
export const TOKEN_KEY = 'AUTH_TOKEN';
export async function setAuthToken(token: string) { await AsyncStorage.setItem(TOKEN_KEY, token); }
export async function getAuthToken(): Promise<string | null> { return AsyncStorage.getItem(TOKEN_KEY); }
export async function clearAuthToken() { await AsyncStorage.removeItem(TOKEN_KEY); }

// Attach interceptor once
http.interceptors.request.use(async (config) => {
  try {
    const token = await getAuthToken();
    if (token) {
      config.headers = config.headers || {};
      (config.headers as any)['Authorization'] = `Bearer ${token}`;
    }
  } catch {}
  return config;
});

export async function ping(): Promise<{ ok: boolean; url: string }>
{  try {
    // First try the new /health; fallback to /salud
    const res = await http.get('/health').catch(async () => http.get('/salud'));
    const ok = !!res?.data;
    return { ok, url: http.defaults.baseURL ?? '' };
  } catch (e) {
    return { ok: false, url: http.defaults.baseURL ?? '' };
  }
}

export function getNetworkErrorMessage(e: unknown): string {
  const err = e as AxiosError;
  if (err.code === 'ECONNABORTED') return 'La solicitud tardó demasiado (timeout).';
  if (err.message?.includes('Network Error')) return 'No hay conexión con el servidor.';
  return err.message || 'Error de red';
}
