<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">AI Use Declaration</div>
      <el-menu :default-active="activeMenu" router>
        <el-menu-item
          v-for="menu in menus"
          :key="menu.path"
          :index="menu.path"
        >
          <span>{{ menu.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="spacer" />
        <div class="user">
          <div class="info">
            <strong>{{ userStore.userInfo?.name }}</strong>
            <span class="role">{{ roleLabel }}</span>
          </div>
          <el-button link type="primary" @click="logout">Sign out</el-button>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
      <HelpHint :hints="currentHint" />
    </el-container>
  </el-container>
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
  { path: '/admin/users', label: 'User management', roles: ['admin'] },
  { path: '/sc', label: 'Home', roles: ['sc'] },
  { path: '/tutor', label: 'Tutor home', roles: ['tutor'] },
  { path: '/courses', label: 'Course management', roles: ['sc'] },
  { path: '/assignments', label: 'Assignment management', roles: ['sc', 'tutor'] },
  { path: '/scales', label: 'AI Use Scale', roles: ['admin', 'sc'] },
  { path: '/notifications', label: 'Notification centre', roles: ['admin', 'sc', 'tutor'] },
  { path: '/settings', label: 'Account settings', roles: ['admin', 'sc', 'tutor'] },
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
      return 'Administrator';
    case 'sc':
      return 'Subject Coordinator';
    case 'tutor':
      return 'Tutor';
    default:
      return 'Guest';
  }
});

const hintMap: Record<string, string> = {
  AdminDashboard: 'AdminDashboard.',
  AdminUserManagement: 'AdminUserManagement.',
  CourseManagement: 'CourseManagement.',
  AssignmentManagement: 'AssignmentManagement.',
  TemplateEditor: 'TemplateEditor.',
  ScaleManagement: 'ScaleManagement.',
  NotificationCenter: 'NotificationCenter.',
  Settings: 'Settings.',
  SCDashboard: 'SCDashboard.',
  TutorDashboard: 'TutorDashboard.',
  default: 'default.',
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
.layout { height: 100vh; }
.aside { border-right: 1px solid #ebeef5; }
.logo { height: 56px; display: flex; align-items: center; padding: 0 16px; font-weight: 600; }
.header { display: flex; align-items: center; justify-content: flex-end; border-bottom: 1px solid #ebeef5; padding: 0 16px; }
.main { padding: 16px; }
.user { display: flex; gap: 12px; align-items: center; }
.info { display: flex; flex-direction: column; align-items: flex-end; }
.role { color: #909399; font-size: 12px; }
</style>
