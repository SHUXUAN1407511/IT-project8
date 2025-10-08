interface ImportMetaEnv {
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_ENV?: 'development' | 'staging' | 'production';
  readonly VITE_PUBLIC_BASE?: string;
  readonly VITE_ROUTER_BASE?: string;
  readonly VITE_API_BASE: string;
  readonly VITE_WS_URL?: string;
  readonly VITE_FEATURE_EXPORT?: string;
  readonly VITE_DEV_PORT?: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare global {
  interface Window {
    __APP_CONFIG__?: Partial<{
      apiBase: string;
      routerBase: string;
      wsUrl?: string;
      features?: { export: boolean };
    }>;
  }
}
export {};
