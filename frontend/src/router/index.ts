import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

import { useUserStore } from '@/store/user';
import pinia from '@/store';
import { appConfig } from '@/config';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false, layout: 'blank' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false, layout: 'blank' }
  },

  // Protected pages (main layout)
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/AdminDashboard.vue'),
    meta: { requiresAuth: true, roles: ['admin'], layout: 'main' }
  },
  {
    path: '/admin/users',
    name: 'AdminUserManagement',
    component: () => import('@/views/admin/AdminUserManagement.vue'),
    meta: { requiresAuth: true, roles: ['admin'], layout: 'main' }
  },
  {
    path: '/sc',
    name: 'SCDashboard',
    component: () => import('@/views/sc/SCDashboard.vue'),
    meta: { requiresAuth: true, roles: ['sc'], layout: 'main' }
  },
  {
    path: '/tutor',
    name: 'TutorDashboard',
    component: () => import('@/views/tutor/TutorDashboard.vue'),
    meta: { requiresAuth: true, roles: ['tutor'], layout: 'main' }
  },
  {
    path: '/courses',
    name: 'CourseManagement',
    component: () => import('@/views/courses/CourseManagement.vue'),
    meta: { requiresAuth: true, roles: ['sc'], layout: 'main' }
  },
  {
    path: '/assignments',
    name: 'AssignmentManagement',
    component: () => import('@/views/assignments/AssignmentManagement.vue'),
    meta: { requiresAuth: true, roles: ['sc', 'tutor'], layout: 'main' }
  },
  {
    path: '/templates/:assignmentId?',
    name: 'TemplateEditor',
    component: () => import('@/views/templates/TemplateEditor.vue'),
    meta: { requiresAuth: true, roles: ['sc', 'tutor'], layout: 'main' }
  },
  {
    path: '/scales',
    name: 'ScaleManagement',
    component: () => import('@/views/scales/ScaleManagement.vue'),
    meta: { requiresAuth: true, roles: ['admin', 'sc'], layout: 'main' }
  },
  {
    path: '/notifications',
    name: 'NotificationCenter',
    component: () => import('@/views/notifications/NotificationCenter.vue'),
    meta: { requiresAuth: true, roles: ['admin', 'sc', 'tutor'], layout: 'main' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/settings/SettingsPage.vue'),
    meta: { requiresAuth: true, roles: ['admin', 'sc', 'tutor'], layout: 'main' }
  },

  // 403/404
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/shared/Forbidden.vue'),
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/shared/NotFound.vue'),
    meta: { layout: 'blank' }
  }
];

const router = createRouter({
  history: createWebHistory(appConfig.routerBase),
  routes
});

// Route guard
router.beforeEach((to) => {
  const userStore = useUserStore(pinia);

  // Need auth?
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    return { name: 'Login' };
  }
  // Role check
  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    if (!userStore.role || !to.meta.roles.includes(userStore.role)) {
      return { name: 'Forbidden' };
    }
  }
  return true;
});

export default router;
