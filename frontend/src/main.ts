import { createApp } from 'vue';
import App from './App.vue';

import router from '@/router';
import pinia from '@/store';

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

import permission from '@/directives/permission';
import { appConfig } from '@/config';

console.info('[AppConfig]', appConfig);

const app = createApp(App);
app.use(pinia);
app.use(router);
app.use(ElementPlus);
app.use(permission); // Register the v-permission directive
app.mount('#app');
