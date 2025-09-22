import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
export default defineConfig(function (_a) {
    var mode = _a.mode;
    var env = loadEnv(mode, process.cwd(), '');
    return {
        plugins: [vue()],
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url)),
            },
        },
        base: env.VITE_PUBLIC_BASE || '/',
        server: { port: Number(env.VITE_DEV_PORT || 5174), open: true, strictPort: true },
        define: { __APP_NAME__: JSON.stringify(env.VITE_APP_NAME || 'AI Use Declaration') },
    };
});
