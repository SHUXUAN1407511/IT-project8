import router from '@/router';
import { ElMessage } from 'element-plus';
import { appConfig } from '@/config';

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

const http = {
  get: requestFactory('GET'),
  post: requestFactory('POST'),
  put: requestFactory('PUT'),
  patch: requestFactory('PATCH'),
  delete: requestFactory('DELETE'),
};

export default http;
