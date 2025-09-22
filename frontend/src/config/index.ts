/**
 * 将.env 文件与 window.__APP_CONFIG__ 进行合并，并导出 appConfig
 */

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

// 'true'/'false' -> boolean
const toBool = (v: unknown, fallback = false) =>
  String(v ?? '').toLowerCase() === 'true' ? true : fallback;

// Build-time values from .env
const env = import.meta.env;
const assignmentTypesEnv = (env.VITE_ASSIGNMENT_TYPES || '')
  .split(',')
  .map((item: string) => item.trim())
  .filter((item: string) => item.length > 0);

const defaultAssignmentTypes = ['Project', 'Essay', 'Quiz', 'Reflection', 'Lab'];

const envConfig: AppConfig = {
  appName: env.VITE_APP_NAME || 'AI Use Declaration',
  env: (env.VITE_APP_ENV as AppEnv) || (env.DEV ? 'development' : 'production'),
  apiBase: env.VITE_API_BASE || 'http://localhost:8000',
  routerBase: env.VITE_ROUTER_BASE || '/',
  wsUrl: env.VITE_WS_URL || undefined,
  features: {
    export: toBool(env.VITE_FEATURE_EXPORT, true),
  },
  assignmentTypes: assignmentTypesEnv.length ? assignmentTypesEnv : defaultAssignmentTypes,
};

// Runtime overrides from public/config.js
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

// Support both `import { appConfig }` and `import appConfig`
export default appConfig;
