<template>
  <div class="register-page">
    <el-card class="register-card" shadow="hover">
      <h2 class="title">Create Your Account</h2>
      <p class="subtitle">Register as an admin, subject coordinator or tutor.</p>

      <el-form
        ref="formRef"
        class="auth-form"
        :model="form"
        :rules="rules"
        label-position="top"
        @keyup.enter="submit"
      >
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" placeholder="Choose a username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="Create a password"
            autocomplete="new-password"
          />
        </el-form-item>
        <el-form-item label="Confirm Password" prop="confirm">
          <el-input
            v-model="form.confirm"
            type="password"
            show-password
            placeholder="Re-enter password"
            autocomplete="new-password"
          />
        </el-form-item>
        <el-form-item label="Role" prop="role">
          <el-select v-model="form.role" placeholder="Select a role">
            <el-option label="Administrator" value="admin" />
            <el-option label="Subject Coordinator" value="sc" />
            <el-option label="Tutor" value="tutor" />
          </el-select>
        </el-form-item>
        <el-button type="primary" class="full" :loading="loading" @click="submit">
          Create Account
        </el-button>
      </el-form>

      <div class="links">
        <span>Already registered?</span>
        <router-link class="login-link" :to="{ name: 'Login' }">Back to sign in</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { useUserStore } from '@/store/user';
import type { UserRole } from '@/services/api';

const router = useRouter();
const userStore = useUserStore();

const formRef = ref<FormInstance>();
const form = reactive({
  username: '',
  password: '',
  confirm: '',
  role: '' as '' | UserRole,
});

const loading = ref(false);

const rules: FormRules = {
  username: [{ required: true, message: 'Please enter a username.', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter a password.', trigger: 'blur' }],
  confirm: [
    { required: true, message: 'Please confirm your password.', trigger: 'blur' },
    {
      validator: (_rule, value: string, callback: (error?: Error) => void) => {
        if (!value) {
          callback();
          return;
        }
        if (value !== form.password) {
          callback(new Error('Passwords do not match.'));
          return;
        }
        callback();
      },
      trigger: ['blur', 'change'],
    },
  ],
  role: [{ required: true, message: 'Please select a role.', trigger: 'change' }],
};

async function submit() {
  if (loading.value) return;
  formRef.value?.validate(async (valid) => {
    if (!valid) return;
    loading.value = true;
    try {
      await userStore.register({
        username: form.username,
        password: form.password,
        role: form.role as UserRole,
      });
      ElMessage.success('Registration successful. Please log in.');
      router.push({ name: 'Login' });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Registration failed.';
      ElMessage.error(message);
    } finally {
      loading.value = false;
    }
  });
}
</script>

<style scoped>
.register-page { min-height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #f6f9fc 0%, #edf1f5 100%); padding: 24px; }
.register-card { width: 380px; }
.title { text-align: center; margin-bottom: 4px; }
.subtitle { text-align: center; color: #606266; margin-bottom: 20px; font-size: 13px; }
.auth-form { display: flex; flex-direction: column; gap: 12px; }
.full { width: 100%; }
.links { margin-top: 16px; font-size: 13px; text-align: center; display: flex; justify-content: center; gap: 6px; align-items: center; color: #606266; }
.login-link { color: #409eff; }
</style>
