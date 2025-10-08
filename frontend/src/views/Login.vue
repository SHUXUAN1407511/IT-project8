<template>
  <div class="login-page">
    <el-card class="login-card" shadow="hover">
      <h2 class="title">AI Use Declaration Platform</h2>
      <p class="subtitle">Sign in with your authorised account to manage courses and AI declaration templates.</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="submit">
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" placeholder="e.g. sc.user" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="Enter password" />
        </el-form-item>
        <el-button type="primary" class="full" :loading="loading" @click="submit">Sign In</el-button>
      </el-form>

      <div class="links">
        <el-link type="primary" @click="openForgotDialog">Forgot password?</el-link>
        <el-divider direction="vertical" />
        <router-link class="register-link" :to="{ name: 'Register' }">Need an account? Register</router-link>
      </div>

      <div class="quick-login">
        <span class="hint">Quick role switch:</span>
        <el-button size="small" @click="quickLogin('admin')">Admin</el-button>
        <el-button size="small" @click="quickLogin('sc')">SC</el-button>
        <el-button size="small" @click="quickLogin('tutor')">Tutor</el-button>
      </div>
    </el-card>

    <el-dialog v-model="forgotDialog.visible" title="Reset Password" width="420px">
      <p class="dialog-hint">Enter Email address and send an email to reset.</p>
      <template #footer>
        <el-button type="primary" @click="forgotDialog.visible = false">Reset</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { useUserStore, type UserRole } from '@/store/user';

const router = useRouter();
const userStore = useUserStore();

const formRef = ref<FormInstance>();
const form = reactive({
  username: '',
  password: '',
});

const loading = ref(false);

const rules: FormRules = {
  username: [{ required: true, message: 'Please enter your username.', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter your password.', trigger: 'blur' }],
};

const forgotDialog = reactive({
  visible: false,
});

function routeByRole(role: UserRole) {
  if (role === 'admin') router.push('/admin');
  if (role === 'sc') router.push('/sc');
  if (role === 'tutor') router.push('/tutor');
}

function submit() {
  if (loading.value) return;
  formRef.value?.validate(async (valid) => {
    if (!valid) return;
    loading.value = true;
    try {
      await userStore.login({
        username: form.username,
        password: form.password,
      });
      routeByRole(userStore.role as UserRole);
      ElMessage.success('Signed in successfully.');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Sign-in failed, please try again.';
      ElMessage.error(message);
    } finally {
      loading.value = false;
    }
  });
}

function quickLogin(role: UserRole) {
  userStore.loginAs(role);
  routeByRole(role);
  ElMessage.success(`Switched to ${role.toUpperCase()} demo account.`);
}

function openForgotDialog() {
  forgotDialog.visible = true;
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #f6f9fc 0%, #edf1f5 100%); padding: 24px; }
.login-card { width: 380px; }
.title { text-align:center; margin-bottom:4px; }
.subtitle { text-align:center; color:#606266; margin-bottom:20px; font-size:13px; }
.full { width:100%; }
.links { display:flex; justify-content:flex-end; align-items:center; margin-top:12px; gap:8px; }
.register-link { color:#409eff; font-size:13px; }
.quick-login { display:flex; align-items:center; gap:8px; justify-content:center; font-size:13px; }
.hint { color:#606266; }
.dialog-hint { color:#606266; margin:0; }
</style>
