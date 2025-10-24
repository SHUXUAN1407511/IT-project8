import router from '@/router';
import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosError,
} from 'axios';
import pinia from '@/store';
import { useUserStore } from '@/store/useUserStore';
import { logger } from '@/utils/logger';

function normalizeBase(raw?: string) {
  const trimmed = (raw || '').trim().replace(/\/+$/, '');
  if (!trimmed || trimmed === '/api') {
    return '';
  }
  return trimmed.endsWith('/api') ? trimmed.slice(0, -4) : trimmed;
}

const rawBase = import.meta.env.VITE_API_BASE;
const generalBase = normalizeBase(rawBase);
const explicitAuthBase = (import.meta.env.VITE_AUTH_BASE || '').trim();
const authBase =
  explicitAuthBase ||
  (generalBase ? `${generalBase.replace(/\/+$/, '')}/api` : '/api');

type TypedAxiosInstance = AxiosInstance & {
  get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>;
  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>;
  post<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T>;
  put<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T>;
  patch<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T>;
};

const http = axios.create({
  baseURL: generalBase || undefined,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
}) as TypedAxiosInstance;

function ensureAuthHeader(config: AxiosRequestConfig) {
  let token: string | null = null;
  try {
    token = window.localStorage.getItem('token');
  } catch (error) {
    logger.warn('Failed to read token from storage', error);
  }
  if (!token) {
    return;
  }
  const headers =
    config.headers && typeof config.headers === 'object'
      ? { ...config.headers }
      : {};
  if (!('Authorization' in headers)) {
    headers.Authorization = `Bearer ${token}`;
  }
  config.headers = headers;
}

// Block mutating requests that the current role is not allowed to perform.
http.interceptors.request.use((config) => {
  ensureAuthHeader(config);

  const userStore = useUserStore(pinia);
  const role = (userStore.role || userStore.userInfo?.role || '')
    .toString()
    .toLowerCase();
  const method = (config.method || 'GET').toUpperCase();

  const rawUrl = config.url ?? '';
  const [pathPart] = rawUrl.split('?');
  const normalizedPath = pathPart.replace(/^https?:\/\/[^/]+/i, '');

  if (
    normalizedPath.includes('/scale-records/save_version') &&
    method === 'POST' &&
    !['admin', 'sc'].includes(role)
  ) {
    return Promise.reject(new Error('You do not have permission to modify the AI use scale.'));
  }

  const assignmentsMutation = ['/assignments', '/assignments/'];
  if (
    assignmentsMutation.some((path) => normalizedPath.startsWith(path)) &&
    !normalizedPath.includes('/template') &&
    ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) &&
    !['admin', 'sc'].includes(role)
  ) {
    return Promise.reject(new Error('You do not have permission to modify assignments.'));
  }

  return config;
});

const authHttp = axios.create({
  baseURL: authBase,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
}) as TypedAxiosInstance;

function extractFirstMessage(value: unknown): string | null {
  if (!value) {
    return null;
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return trimmed ? trimmed : null;
  }
  if (Array.isArray(value)) {
    for (const item of value) {
      const message = extractFirstMessage(item);
      if (message) {
        return message;
      }
    }
    return null;
  }
  if (typeof value === 'object') {
    const record = value as Record<string, unknown>;
    for (const key of ['message', 'detail', 'error']) {
      const payload = record[key];
      const message = extractFirstMessage(payload);
      if (message) {
        return message;
      }
    }
    for (const nested of Object.values(record)) {
      const message = extractFirstMessage(nested);
      if (message) {
        return message;
      }
    }
  }
  return null;
}

function deriveAxiosErrorMessage(error: AxiosError) {
  const withoutResponse = (error.message || '').trim();
  if (!error.response) {
    return withoutResponse || 'Network error. Please check your connection and try again.';
  }

  const { status, data } = error.response;
  const rawUrl = error.config?.url || '';
  const normalizedUrl = rawUrl.replace(/^https?:\/\/[^/]+/i, '');

  if (status === 401) {
    if (normalizedUrl.includes('auth/login')) {
      return 'Invalid username or password.';
    }
    return 'Authentication required. Please sign in again.';
  }

  const extracted = extractFirstMessage(data);
  if (extracted) {
    return extracted;
  }

  if (status === 400) {
    return 'Unable to process the request. Please review your input and try again.';
  }
  if (status === 403) {
    return 'You do not have permission to perform this action.';
  }
  if (status === 404) {
    return 'Requested resource was not found.';
  }
  if (status >= 500) {
    return 'Server error. Please try again later.';
  }

  return withoutResponse || 'Request failed.';
}

function attachResponseInterceptor(instance: TypedAxiosInstance) {
  instance.interceptors.response.use(
    (response) => response.data,
    async (error: AxiosError) => {
      const message = deriveAxiosErrorMessage(error);
      if (message) {
        error.message = message;
      }

      const status = error.response?.status;
      const normalizedUrl = (error.config?.url || '').replace(
        /^https?:\/\/[^/]+/i,
        '',
      );

      const method = (error.config?.method || 'GET').toUpperCase();

      if (status === 401 && !normalizedUrl.includes('auth/login')) {
        const userStore = useUserStore(pinia);
        if (userStore.isAuthenticated) {
          await userStore.logout();
        }
        try {
          await router.push({ name: 'Login' });
        } catch {
          // ignore navigation failures triggered by duplicate redirects
        }
      } else if (
        status === 403 &&
        normalizedUrl &&
        !normalizedUrl.includes('/auth/login') &&
        method !== 'GET'
      ) {
        try {
          await router.push({ name: 'Forbidden' });
        } catch {
          // ignore navigation failures triggered by duplicate redirects
        }
      }

      logger.error('API error', error.response?.data || message || error.message);
      return Promise.reject(error);
    },
  );
}

attachResponseInterceptor(http);
attachResponseInterceptor(authHttp);

export { authHttp };
export default http;
