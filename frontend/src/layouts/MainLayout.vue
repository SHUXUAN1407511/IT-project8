<!--
侧边栏 + 顶部栏 + 内容区域
-->

<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="logo">AI Use</div>
      <ul class="menu">
        <li
          v-for="menu in menus"
          :key="menu.path"
          :class="{ active: menu.path === activeMenu }"
        >
          <router-link :to="menu.path">{{ menu.label }}</router-link>
        </li>
      </ul>
    </aside>

    <div class="content">
      <header class="topbar">
        <div class="user-block">
          <div class="name">{{ userStore.userInfo?.name || 'Unnamed User' }}</div>
          <div class="role">{{ roleLabel }}</div>
        </div>
        <button class="logout" type="button" @click="logout">Log out</button>
      </header>

      <main class="main">
        <router-view />
      </main>

      <HelpHint :hints="currentHint" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore, type UserRole } from '@/store/user';
import HelpHint from '@/components/HelpHint.vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

interface MenuItem {
  path: string;
  label: string;
  roles: UserRole[];
}

const MENU_ITEMS: MenuItem[] = [
  { path: '/admin', label: 'Dashboard', roles: ['admin'] },
  { path: '/admin/users', label: 'User Management', roles: ['admin'] },
  { path: '/sc', label: 'Home', roles: ['sc'] },
  { path: '/tutor', label: 'Tutor Home', roles: ['tutor'] },
  { path: '/courses', label: 'Courses', roles: ['sc'] },
  { path: '/assignments', label: 'Assignments', roles: ['sc', 'tutor'] },
  { path: '/scales', label: 'AI Use Scale', roles: ['admin', 'sc'] },
  { path: '/notifications', label: 'Notifications', roles: ['admin', 'sc', 'tutor'] },
  { path: '/settings', label: 'Settings', roles: ['admin', 'sc', 'tutor'] },
];

const menus = computed(() => MENU_ITEMS.filter((item) => item.roles.includes(userStore.role as UserRole)));

const activeMenu = computed(() => {
  const currentPath = route.path;
  const matched = MENU_ITEMS.find((item) => currentPath === item.path || currentPath.startsWith(item.path + '/'));
  return matched ? matched.path : currentPath;
});

const roleLabel = computed(() => {
  switch (userStore.role) {
    case 'admin':
      return 'Admin';
    case 'sc':
      return 'Subject Coordinator';
    case 'tutor':
      return 'Tutor';
    default:
      return 'Guest';
  }
});

const hintMap: Record<string, string> = {
  AdminDashboard: 'Check key metrics and clear any outstanding notifications to keep the team aligned.',
  AdminUserManagement: 'Filter by role or status to locate users quickly, then edit details or toggle access.',
  CourseManagement: 'Course hints.',
  AssignmentManagement: 'Assignment hints.',
  TemplateEditor: 'Template hints.',
  ScaleManagement: 'AI Use Scale hints.',
  NotificationCenter: 'Notification hints.',
  Settings: 'Setting hints.',
  SCDashboard: 'Hints.',
  TutorDashboard: 'Tutor hints.',
  default: 'Use this page to keep course materials and declarations up to date for your cohort.',
};

const currentHint = computed(() => {
  const key = typeof route.name === 'string' ? route.name : '';
  return hintMap[key] || hintMap.default;
});

function logout() {
  userStore.logout();
  router.push({ name: 'Login' });
}
</script>

<style scoped>
.layout { display: flex; min-height: 100vh; }
.sidebar { width: 200px; padding: 16px; background: #f8f8f8; border-right: 1px solid #ddd; }
.logo { font-weight: 700; margin-bottom: 16px; }
.menu { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 8px; }
.menu li { padding: 4px 0; font-size: 14px; }
.menu li.active { font-weight: 600; }
.menu a { color: inherit; text-decoration: none; }
.content { flex: 1; display: flex; flex-direction: column; }
.topbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid #ddd; background: #fff; }
.user-block { display: flex; flex-direction: column; font-size: 14px; }
.name { font-weight: 600; }
.role { color: #555; font-size: 12px; }
.logout { border: 1px solid #bbb; background: #fff; padding: 4px 12px; cursor: pointer; font-size: 13px; }
.logout:hover { background: #eee; }
.main { padding: 16px; }
</style>
