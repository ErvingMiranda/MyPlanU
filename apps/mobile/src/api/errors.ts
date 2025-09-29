import type { AxiosError } from 'axios';
import { getAuthToken, getNetworkErrorMessage } from './http';

export type HttpError = {
  code: number | 'NETWORK' | 'TIMEOUT';
  message: string;
  hint?: string;
};

export function mapHttpError(e: unknown): HttpError {
  const err = e as AxiosError & { isAxiosError?: boolean };
  const isAxios = !!err?.isAxiosError || !!err?.response || !!err?.request || typeof err?.code === 'string';
  if (!isAxios) return { code: 'NETWORK', message: String((e as any)?.message || e) };
  const status: number | undefined = (err as any)?.response?.status;
  if (err?.code === 'ECONNABORTED') return { code: 'TIMEOUT', message: 'La solicitud excedió el tiempo de espera.', hint: 'Verifica tu conexión o intenta de nuevo.' };
  if (status === 404) return { code: 404, message: (err as any)?.response?.data?.detail || 'Recurso no encontrado.' };
  if (status === 409) return { code: 409, message: (err as any)?.response?.data?.detail || 'Conflicto de datos.' };
  if (!status) return { code: 'NETWORK', message: getNetworkErrorMessage(err), hint: 'Revisa API_BASE_URL o tu conexión.' };
  return { code: status, message: (err as any)?.response?.data?.detail || err?.message || 'Error de servidor' };
}

// Optional: Axios interceptors to log durations and standardize network errors in dev
export function installAxiosInterceptors(axiosInstance: import('axios').AxiosInstance) {
  axiosInstance.interceptors.request.use((config) => {
    (config as any).metadata = { start: Date.now() };
    return config;
  });
  axiosInstance.interceptors.response.use(
    (response) => {
      const meta = (response.config as any).metadata;
      if (__DEV__ && meta?.start) {
        const ms = Date.now() - meta.start;
        // eslint-disable-next-line no-console
        console.debug(`[HTTP ${response.status}] ${response.config.method?.toUpperCase()} ${response.config.url} - ${ms}ms`);
      }
      return response;
    },
    (error) => {
      const cfg = error?.config ?? {};
      const start = (cfg as any)?.metadata?.start;
      if (__DEV__ && start) {
        const ms = Date.now() - start;
        // eslint-disable-next-line no-console
        console.debug(`[HTTP ERROR] ${cfg.method?.toUpperCase()} ${cfg.url} - ${ms}ms:`, error?.message);
      }
      return Promise.reject(error);
    }
  );
}

// Helper for fetch()-based clients to normalize errors
export async function fetchJson<T>(url: string, options: RequestInit | undefined, defaultMessage: string): Promise<T> {
  try {
    const token = await getAuthToken();
    const headers = new Headers(options?.headers as HeadersInit | undefined);
    if (token) headers.set('Authorization', `Bearer ${token}`);
    const res = await fetch(url, { ...(options ?? {}), headers });
    if (!res.ok) {
      let detail: string | undefined;
      try {
        const data: any = await res.json();
        detail = data?.detail || data?.message;
      } catch {
        // ignore JSON parse errors
      }
      const err: HttpError = { code: res.status, message: detail || defaultMessage };
      throw err;
    }
    return res.json() as Promise<T>;
  } catch (e: any) {
    if (e && (typeof e.code !== 'undefined')) throw e as HttpError;
    const msg = String(e?.message || e || defaultMessage);
    if (msg.includes('Network request failed')) {
      const err: HttpError = { code: 'NETWORK', message: 'No hay conexión con el servidor.', hint: 'Revisa API_BASE_URL o tu red.' };
      throw err;
    }
    const err: HttpError = { code: 'NETWORK', message: msg };
    throw err;
  }
}
