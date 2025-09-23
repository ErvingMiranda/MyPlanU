import axios, { AxiosError } from 'axios';

// Prefer .env via Expo public variables and provide sane defaults
// EXPO_PUBLIC_API_URL is already used elsewhere; keep it but also support API_BASE_URL
const baseUrl = process.env.EXPO_PUBLIC_API_URL || process.env.API_BASE_URL || 'http://127.0.0.1:8000';

export const http = axios.create({
  baseURL: baseUrl,
  timeout: 15000,
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
