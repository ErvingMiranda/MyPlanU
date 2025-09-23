import Toast from 'react-native-toast-message';

export function showSuccess(message: string) {
  Toast.show({ type: 'success', text1: message, position: 'bottom' });
}

export function showError(message: string) {
  Toast.show({ type: 'error', text1: message, position: 'bottom' });
}

export function showInfo(message: string) {
  Toast.show({ type: 'info', text1: message, position: 'bottom' });
}

export { Toast };

export function showRetry(message: string, onRetry: () => void) {
  Toast.show({
    type: 'error',
    text1: message,
    text2: 'Tocar para reintentar',
    position: 'bottom',
    onPress: onRetry,
    visibilityTime: 4000,
    autoHide: true,
  });
}
