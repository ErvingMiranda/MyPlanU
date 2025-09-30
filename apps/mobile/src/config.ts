import { Platform } from 'react-native';

// Heurística para resolver la URL base del backend en desarrollo.
// Prioriza EXPO_PUBLIC_API_URL, si no:
// - Web: usa hostname actual con puerto 8000
// - Android (emulador): 10.0.2.2 apunta al host
// - iOS (simulador): localhost
// Nota: En dispositivo físico, define EXPO_PUBLIC_API_URL con la IP LAN del host.
function guessDevApiUrl(): string {
	if (Platform.OS === 'web') {
		const host = (typeof window !== 'undefined' && window.location && window.location.hostname) ? window.location.hostname : '127.0.0.1';
		return `http://${host}:8000`;
	}
	if (Platform.OS === 'android') return 'http://10.0.2.2:8000';
	// iOS simulator
	return 'http://localhost:8000';
}

export const ApiUrl: string = process.env.EXPO_PUBLIC_API_URL ?? guessDevApiUrl();
