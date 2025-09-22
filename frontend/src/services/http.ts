// API调用
import router from '@/router';
import { ElMessage } from 'element-plus';
import { appConfig } from '@/config';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface RequestOptions extends RequestInit {
  data?: unknown;
  skipAuthRedirect?: boolean;
}

const safeMethods: HttpMethod[] = ['GET'];

function isSafeMethod(method?: string) {
  if (!method) return true;
  return safeMethods.includes(method.toUpperCase() as HttpMethod) || ['HEAD', 'OPTIONS'].includes(method.toUpperCase());
}

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

async function send<T = unknown>(url: string, options: RequestOptions = {}): Promise<T> {
  const endpoint = url.startsWith('http') ? url : new URL(url, appConfig.apiBase).toString();
  const headers = new Headers(options.headers || {});
  const token = localStorage.getItem('token');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }
  if (options.data && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (!isSafeMethod(options.method) && !headers.has('X-CSRFToken')) {
    const csrf = getCsrfToken();
    if (csrf) {
      headers.set('X-CSRFToken', csrf);
    }
  }

  const response = await fetch(endpoint, {
    ...options,
    method: options.method || 'GET',
    headers,
    body: options.data ? JSON.stringify(options.data) : options.body,
    credentials: options.credentials ?? 'include',
  });

  if (response.ok) {
    const contentType = response.headers.get('Content-Type') || '';
    if (contentType.includes('application/json')) {
      return (await response.json()) as T;
    }
    return (await response.text()) as unknown as T;
  }

  const message = await extractMessage(response);
  if (response.status === 401 && !options.skipAuthRedirect) {
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
