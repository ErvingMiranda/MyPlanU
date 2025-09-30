import AsyncStorage from '@react-native-async-storage/async-storage';

import { setAuthToken, clearAuthToken, TOKEN_KEY } from '../api/http';

const USER_ID_KEY = 'AUTH_USER_ID';

function decodeBase64(input: string): string | null {
  const normalized = input.replace(/-/g, '+').replace(/_/g, '/');
  const padding = normalized.length % 4 === 0 ? normalized : `${normalized}${'='.repeat(4 - (normalized.length % 4))}`;
  if (typeof globalThis.atob === 'function') {
    try {
      return globalThis.atob(padding);
    } catch {
      return null;
    }
  }
  try {
    const globalBuffer = (globalThis as any)?.Buffer;
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const bufferModule = globalBuffer ? { Buffer: globalBuffer } : require('buffer');
    const BufferImpl: { from: (input: string, encoding: string) => { toString: (enc: string) => string } } | undefined = bufferModule?.Buffer;
    if (BufferImpl) {
      return BufferImpl.from(padding, 'base64').toString('utf8');
    }
  } catch {
    // ignore
  }
  return null;
}

function extraerUsuarioId(token: string): number | null {
  const partes = token.split('.');
  if (partes.length < 2) return null;
  const payloadCodificado = partes[1];
  const decodificado = decodeBase64(payloadCodificado);
  if (!decodificado) return null;
  try {
    const data = JSON.parse(decodificado);
    const sub = data?.sub;
    if (typeof sub === 'number') return sub;
    if (typeof sub === 'string') {
      const n = parseInt(sub, 10);
      return Number.isFinite(n) ? n : null;
    }
  } catch {
    return null;
  }
  return null;
}

export async function storeAuthSession(token: string): Promise<void> {
  await setAuthToken(token);
  const userId = extraerUsuarioId(token);
  if (userId != null) {
    await AsyncStorage.setItem(USER_ID_KEY, String(userId));
  } else {
    await AsyncStorage.removeItem(USER_ID_KEY);
  }
}

export async function getSessionUserId(): Promise<number | null> {
  const raw = await AsyncStorage.getItem(USER_ID_KEY);
  if (!raw) return null;
  const num = parseInt(raw, 10);
  return Number.isFinite(num) ? num : null;
}

export async function clearAuthSession(): Promise<void> {
  await clearAuthToken();
  await AsyncStorage.removeItem(USER_ID_KEY);
}

export async function hasAuthToken(): Promise<boolean> {
  const token = await AsyncStorage.getItem(TOKEN_KEY);
  return !!token;
}
