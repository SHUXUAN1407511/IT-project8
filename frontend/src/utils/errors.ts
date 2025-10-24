import axios from 'axios';

export function getErrorMessage(error: unknown, fallback = 'Request failed.') {
  if (axios.isAxiosError(error)) {
    const message = (error.message || '').trim();
    if (message) {
      return message;
    }
  }
  if (error instanceof Error) {
    const message = (error.message || '').trim();
    if (message) {
      return message;
    }
  }
  if (typeof error === 'string') {
    const message = error.trim();
    if (message) {
      return message;
    }
  }
  if (typeof error === 'object' && error && 'message' in (error as Record<string, unknown>)) {
    const message = String((error as Record<string, unknown>).message || '').trim();
    if (message) {
      return message;
    }
  }
  return fallback;
}
