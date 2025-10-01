import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Heurística para resolver la URL base del backend en desarrollo.
// Prioriza EXPO_PUBLIC_API_URL, si no:
// - Web: usa hostname actual con puerto 8000
// - Android (emulador): 10.0.2.2 apunta al host
// - iOS (simulador): localhost
// Nota: En dispositivo físico, define EXPO_PUBLIC_API_URL con la IP LAN del host.
function extraerHost(valor: string | null | undefined): string | null {
  if (!valor || typeof valor !== 'string') {
    return null;
  }

  // Expo suele exponer valores como "exp://192.168.0.12:19000" o "192.168.0.12:19000"
  // Normalizamos eliminando esquema y query params si existen.
  const limpio = valor.split('?')[0]?.replace(/^[^:]+:\/\//, '') ?? '';
  if (!limpio) {
    return null;
  }

  const host = limpio.split(':')[0];
  return host || null;
}

function resolveExpoHost(): string | null {
  try {
    const explicit = extraerHost(Constants.expoConfig?.hostUri)
      ?? extraerHost((Constants as any).manifest2?.extra?.expoClient?.hostUri)
      ?? extraerHost((Constants as any).manifest?.debuggerHost);
    if (explicit) {
      return explicit;
    }
  } catch (_) {
    // Ignorar: en producción Constants.manifest puede no estar disponible
  }
  return null;
}

function guessDevApiUrl(): string {
  if (Platform.OS === 'web') {
    const host =
      typeof window !== 'undefined' && window.location?.hostname
        ? window.location.hostname
        : '127.0.0.1';
    return `http://${host}:8000`;
  }

  const expoHost = resolveExpoHost();
  if (expoHost) {
    return `http://${expoHost}:8000`;
  }

  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';
  }

  // iOS simulator o fallback
  return 'http://localhost:8000';
}

export const ApiUrl: string = process.env.EXPO_PUBLIC_API_URL ?? guessDevApiUrl();
