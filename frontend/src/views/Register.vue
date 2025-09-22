<template>
  <div class="auth-page">
    <div class="auth-box">
      <h1>Create Account</h1>
      <form class="form" @submit.prevent="submit">
        <label class="field">
          <span>Username</span>
          <input v-model="form.username" type="text" autocomplete="username" required />
        </label>
        <label class="field">
          <span>Password</span>
          <input v-model="form.password" type="password" autocomplete="new-password" required />
        </label>
        <label class="field">
          <span>Confirm Password</span>
          <input v-model="form.confirm" type="password" autocomplete="new-password" required />
        </label>
        <label class="field">
          <span>Role</span>
          <select v-model="form.role" required>
            <option value="">Select user type</option>
            <option value="admin">Admin</option>
            <option value="sc">Subject Coordinator</option>
            <option value="tutor">Tutor</option>
          </select>
        </label>
        <button class="submit" type="submit" :disabled="loading">
          {{ loading ? 'Submitting…' : 'Register' }}
        </button>
      </form>
      <p class="switch">
        Already registered?
        <router-link :to="{ name: 'Login' }">Back to login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/user';
import type { UserRole } from '@/services/api';

const router = useRouter();
const userStore = useUserStore();

const form = reactive<{ username: string; password: string; confirm: string; role: '' | UserRole }>(
  {
    username: '',
    password: '',
    confirm: '',
    role: '',
  },
);

const loading = ref(false);

async function submit() {
  if (!form.username || !form.password || !form.role) {
    ElMessage.error('Please fill in all required fields.');
    return;
  }
  if (form.password !== form.confirm) {
    ElMessage.error('Passwords do not match.');
    return;
  }
  loading.value = true;
  try {
    const role = form.role as UserRole;
    await userStore.register({
      username: form.username,
      password: form.password,
      role,
    });
    ElMessage.success('Registration successful. Please log in.');
    router.push({ name: 'Login' });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Registration failed.';
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; justify-content: center; align-items: center; background: #f0f0f0; padding: 16px; }
.auth-box { width: 340px; background: #fff; border: 1px solid #dcdcdc; padding: 24px; box-shadow: none; }
.auth-box h1 { font-size: 22px; margin-bottom: 12px; }
.form { display: flex; flex-direction: column; gap: 12px; }
.field { display: flex; flex-direction: column; gap: 4px; font-size: 13px; }
.field input,
.field select { border: 1px solid #bbb; padding: 6px; font-size: 14px; }
.submit { margin-top: 8px; padding: 8px; border: 1px solid #444; background: #fff; cursor: pointer; font-size: 14px; }
.submit[disabled] { cursor: not-allowed; opacity: 0.7; }
.switch { margin-top: 16px; font-size: 13px; text-align: center; }
.switch a { color: #0066cc; }
</style>
