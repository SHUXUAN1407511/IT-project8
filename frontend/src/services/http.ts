/// <reference types="vite/client" />
import router from '@/router';
import { ElMessage } from 'element-plus';
import { appConfig } from '@/config';
import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface RequestOptions extends RequestInit {
  data?: unknown;
  skipAuthRedirect?: boolean;
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  if (!value || typeof value !== 'object') return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

const safeMethods: HttpMethod[] = ['GET'];

function isSafeMethod(method?: string) {
  if (!method) return true;
  const upper = method.toUpperCase();
  return safeMethods.includes(upper as HttpMethod) || upper === 'HEAD' || upper === 'OPTIONS';
}

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

async function send<T = unknown>(url: string, options: RequestOptions = {}): Promise<T> {
  const resolvedOptions: RequestOptions = { ...options };
  const baseEndpoint = url.startsWith('http') ? url : new URL(url, appConfig.apiBase).toString();
  const username = localStorage.getItem('username');
  let endpoint = baseEndpoint;

  if (username) {
    const urlObject = new URL(baseEndpoint);
    if (!urlObject.searchParams.has('username')) {
      urlObject.searchParams.set('username', username);
    }
    endpoint = urlObject.toString();
    if (isPlainObject(resolvedOptions.data) && resolvedOptions.data.username === undefined) {
      resolvedOptions.data = { ...resolvedOptions.data, username };
    }
  }

  const headers = new Headers(resolvedOptions.headers || {});
  const token = localStorage.getItem('token');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }
  if (resolvedOptions.data && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (!isSafeMethod(resolvedOptions.method) && !headers.has('X-CSRFToken')) {
    const csrf = getCsrfToken();
    if (csrf) {
      headers.set('X-CSRFToken', csrf);
    }
  }

  const response = await fetch(endpoint, {
    ...resolvedOptions,
    method: resolvedOptions.method || 'GET',
    headers,
    body: resolvedOptions.data ? JSON.stringify(resolvedOptions.data) : resolvedOptions.body,
    credentials: resolvedOptions.credentials ?? 'include',
  });

  if (response.ok) {
    const contentType = response.headers.get('Content-Type') || '';
    if (contentType.includes('application/json')) {
      return (await response.json()) as T;
    }
    return (await response.text()) as unknown as T;
  }

  const message = await extractMessage(response);
  if (response.status === 401 && !resolvedOptions.skipAuthRedirect) {
    ElMessage.error('Session expired. Please sign in again.');
    await router.push({ name: 'Login' });
  } else if (response.status === 403) {
    ElMessage.error('You do not have permission to access this resource.');
    await router.push({ name: 'Forbidden' });
  } else {
    ElMessage.error(message);
  }
  throw new Error(message);
}

async function extractMessage(response: Response) {
  try {
    const data = await response.clone().json();
    return data?.message || response.statusText || 'Request failed.';
  } catch (error) {
    return response.statusText || (error as Error).message || 'Request failed.';
  }
}

function requestFactory(method: HttpMethod) {
  return <T = unknown>(url: string, options: RequestOptions = {}) =>
    send<T>(url, { ...options, method });
}

function normalizeBase(raw?: string) {
  const trimmed = (raw || '').trim().replace(/\/+$/, '');
  if (!trimmed || trimmed === '/api') return '';
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
  withCredentials: false, // 如果后面用 Session 登录，可以改 true
}) as TypedAxiosInstance;

http.interceptors.request.use((config) => {
  const username = (() => {
    try {
      return localStorage.getItem('username');
    } catch (error) {
      console.warn('Failed to read username from storage', error);
      return null;
    }
  })();

  if (!username) {
    return config;
  }

  if (config.params instanceof URLSearchParams) {
    if (!config.params.has('username')) {
      config.params.set('username', username);
    }
  } else {
    const currentParams =
      config.params && typeof config.params === 'object'
        ? { ...(config.params as Record<string, unknown>) }
        : {};
    if (currentParams.username === undefined) {
      currentParams.username = username;
      config.params = currentParams;
    }
  }

  if (isPlainObject(config.data)) {
    const body = config.data as Record<string, unknown>;
    if (body.username === undefined) {
      config.data = { ...body, username };
    }
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

// ✅ 响应拦截器：自动返回后端 JSON 对象
function attachResponseInterceptor(instance: TypedAxiosInstance) {
  instance.interceptors.response.use(
    (response) => response.data,
    (error) => {
      console.error('❌ API Error:', error.response?.data || error.message);
      return Promise.reject(error);
    },
  );
}

attachResponseInterceptor(http);
attachResponseInterceptor(authHttp);

export { authHttp };
export default http;
