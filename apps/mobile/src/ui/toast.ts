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
