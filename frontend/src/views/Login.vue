<template>
  <div class="login-page">
    <div class="login-box">
      <h1>AI Use Declaration</h1>

      <form class="form" @submit.prevent="submit">
        <label class="field">
          <span>Username</span>
          <input v-model="form.username" type="text" autocomplete="username" />
        </label>

        <label class="field">
          <span>Password</span>
          <input v-model="form.password" type="password" autocomplete="current-password" />
        </label>

        <label class="field">
          <span>Role</span>
          <select v-model="form.role">
            <option value="">Select user type</option>
            <option value="admin">Admin</option>
            <option value="sc">Subject Coordinator</option>
            <option value="tutor">Tutor</option>
          </select>
        </label>

        <button class="submit" type="submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Log in' }}
        </button>
      </form>

      <p class="switch">
        Need an account?
        <router-link :to="{ name: 'Register' }">Register</router-link>
      </p>

      <div class="quick">
        <span>Quick demo roles:</span>
        <button type="button" @click="quickLogin('admin')">Admin</button>
        <button type="button" @click="quickLogin('sc')">SC</button>
        <button type="button" @click="quickLogin('tutor')">Tutor</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore, type UserRole } from '@/store/user';

const router = useRouter();
const userStore = useUserStore();

const form = reactive({
  username: '',
  password: '',
  role: '' as '' | UserRole,
});

const loading = ref(false);

async function submit() {
  if (!form.username || !form.password) {
    ElMessage.error('Please enter username and password.');
    return;
  }
  const fallbackRole = (form.role || 'admin') as UserRole;
  loading.value = true;
  try {
    await userStore.login({
      username: form.username,
      password: form.password,
      role: fallbackRole,
    });
    routeByRole(userStore.role as UserRole);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Login failed.';
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
}

function routeByRole(role: UserRole) {
  if (role === 'admin') router.push('/admin');
  if (role === 'sc') router.push('/sc');
  if (role === 'tutor') router.push('/tutor');
}

function quickLogin(role: UserRole) {
  userStore.loginAs(role);
  routeByRole(role);
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: flex; justify-content: center; align-items: center; background: #f0f0f0; padding: 16px; }
.login-box { width: 320px; background: #fff; border: 1px solid #dcdcdc; padding: 20px; box-shadow: none; }
.login-box h1 { font-size: 22px; margin-bottom: 4px; }
.hint { font-size: 13px; color: #666; margin-bottom: 16px; }
.form { display: flex; flex-direction: column; gap: 12px; }
.field { display: flex; flex-direction: column; gap: 4px; font-size: 13px; }
.field input,
.field select { border: 1px solid #bbb; padding: 6px; font-size: 14px; }
.submit { margin-top: 8px; padding: 8px; border: 1px solid #444; background: #fff; cursor: pointer; font-size: 14px; }
.submit:hover { background: #eee; }
.submit[disabled] { cursor: progress; opacity: 0.75; }
.switch { margin-top: 12px; font-size: 13px; text-align: center; }
.switch a { color: #0066cc; }
.quick { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 8px; font-size: 12px; align-items: center; }
.quick button { border: 1px solid #999; background: #fff; padding: 4px 8px; cursor: pointer; }
.quick button:hover { background: #f5f5f5; }
</style>
