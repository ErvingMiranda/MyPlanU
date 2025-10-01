import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Heurística para resolver la URL base del backend en desarrollo.
// Prioriza EXPO_PUBLIC_API_URL, si no:
// - Web: usa hostname actual con puerto 8000
// - Android (emulador): 10.0.2.2 apunta al host
// - iOS (simulador): localhost
// Nota: En dispositivo físico, define EXPO_PUBLIC_API_URL con la IP LAN del host.
function resolveExpoHost(): string | null {
  try {
    const explicit = Constants.expoConfig?.hostUri
      ?? (Constants as any).manifest2?.extra?.expoClient?.hostUri
      ?? (Constants as any).manifest?.debuggerHost;
    if (explicit && typeof explicit === 'string') {
      const host = explicit.split(':')[0];
      if (host) {
        return host;
      }
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
