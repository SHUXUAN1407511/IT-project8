export type AppEnv = 'development' | 'staging' | 'production';

export interface AppConfig {
  appName: string;
  env: AppEnv;
  apiBase: string;
  routerBase: string;
  wsUrl?: string;
  features: {
    export: boolean;
  };
  assignmentTypes: string[];
}
const toBool = (v: unknown, fallback = false) =>
  String(v ?? '').toLowerCase() === 'true' ? true : fallback;
const env = import.meta.env;
const assignmentTypesEnv = (env.VITE_ASSIGNMENT_TYPES || '')
  .split(',')
  .map((item: string) => item.trim())
  .filter((item: string) => item.length > 0);

const defaultAssignmentTypes = ['Project', 'Essay', 'Quiz', 'Reflection', 'Lab'];

const fallbackOrigin =
  typeof window !== 'undefined' && window.location
    ? window.location.origin
    : 'http://127.0.0.1:8000';

function resolveApiBase(raw?: string) {
  const trimmed = (raw || '').trim();
  if (!trimmed) return fallbackOrigin;
  const withoutTrailingSlash = trimmed.replace(/\/+$/, '');
  const withoutApi = withoutTrailingSlash.endsWith('/api')
    ? withoutTrailingSlash.slice(0, -4)
    : withoutTrailingSlash;

  if (!withoutApi) return fallbackOrigin;
  if (/^https?:\/\//.test(withoutApi)) {
    return withoutApi;
  }
  if (withoutApi.startsWith('/')) {
    return `${fallbackOrigin}${withoutApi === '/' ? '' : withoutApi}`;
  }
  return `${fallbackOrigin}/${withoutApi}`;
}

const envConfig: AppConfig = {
  appName: env.VITE_APP_NAME || 'AI Use Declaration',
  env: (env.VITE_APP_ENV as AppEnv) || (env.DEV ? 'development' : 'production'),
  apiBase: resolveApiBase(env.VITE_API_BASE),
  routerBase: env.VITE_ROUTER_BASE || '/',
  wsUrl: env.VITE_WS_URL || undefined,
  features: {
    export: toBool(env.VITE_FEATURE_EXPORT, true),
  },
  assignmentTypes: assignmentTypesEnv.length ? assignmentTypesEnv : defaultAssignmentTypes,
};
const runtime = (window as any).__APP_CONFIG__ || {};

export const appConfig: AppConfig = {
  ...envConfig,
  ...runtime,
  features: { ...envConfig.features, ...(runtime.features || {}) },
  assignmentTypes:
    Array.isArray(runtime.assignmentTypes) && runtime.assignmentTypes.length
      ? runtime.assignmentTypes
      : envConfig.assignmentTypes,
};

export function useAppConfig() {
  return appConfig;
}
export default appConfig;
