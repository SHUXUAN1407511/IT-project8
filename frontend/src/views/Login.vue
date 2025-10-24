<template>
  <div class="login-page">
    <el-card class="login-card" shadow="hover">
      <h2 class="title">AI Use Declaration Platform</h2>
      <p class="subtitle">
        Sign in with your authorised account to manage courses and AI declaration templates.
      </p>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @keyup.enter="submit"
      >
        <el-form-item label="Username" prop="username">
          <el-input
            v-model="form.username"
            placeholder="e.g. sc.user"
          />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="Enter password"
          />
        </el-form-item>
        <el-button
          type="primary"
          class="full"
          :loading="loading"
          @click="submit"
        >
          Sign In
        </el-button>
      </el-form>

      <div class="links">
        <el-link type="primary" @click="openForgotDialog">Forgot password?</el-link>
        <el-divider direction="vertical" />
        <router-link class="register-link" :to="{ name: 'Register' }">
          Need an account? Register
        </router-link>
      </div>

    </el-card>

    <el-dialog
      v-model="forgotDialog.visible"
      title="Reset Password"
      width="420px"
      @closed="resetForgotDialog"
    >
      <p class="dialog-hint">
        Enter your email address and we'll send a password reset link if your account is found.
      </p>
      <el-form
        ref="forgotFormRef"
        :model="forgotDialog.form"
        :rules="forgotRules"
        label-position="top"
      >
        <el-form-item label="Email" prop="email">
          <el-input
            v-model="forgotDialog.form.email"
            placeholder="name@example.com"
            :disabled="forgotDialog.submitting"
          />
        </el-form-item>
        <el-form-item label="Username (optional)">
          <el-input
            v-model="forgotDialog.form.username"
            placeholder="Provide if you remember it"
            :disabled="forgotDialog.submitting"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="forgotDialog.visible = false" :disabled="forgotDialog.submitting">
          Cancel
        </el-button>
        <el-button
          type="primary"
          :loading="forgotDialog.submitting"
          @click="submitForgot"
        >
          Send reset link
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { useUserStore, type UserRole } from '@/store/useUserStore';
import { getErrorMessage } from '@/utils/errors';
import API from '@/services/api';

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

const forgotFormRef = ref<FormInstance>();
const forgotDialog = reactive({
  visible: false,
  submitting: false,
  form: {
    email: '',
    username: '',
  },
});

const forgotRules: FormRules = {
  email: [
    { required: true, message: 'Please enter your email.', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email.', trigger: 'blur' },
  ],
};

function routeByRole(role: UserRole) {
  if (role === 'admin') {
    router.push('/admin');
  }
  if (role === 'sc') {
    router.push('/sc');
  }
  if (role === 'tutor') {
    router.push('/tutor');
  }
}

function submit() {
  if (loading.value) {
    return;
  }
  formRef.value?.validate(async (valid) => {
    if (!valid) {
      return;
    }
    loading.value = true;
    try {
      await userStore.login({
        username: form.username,
        password: form.password,
      });
      routeByRole(userStore.role as UserRole);
      ElMessage.success('Signed in successfully.');
    } catch (error) {
      const message = getErrorMessage(error, 'Sign-in failed. Please try again.');
      ElMessage.error(message);
    } finally {
      loading.value = false;
    }
  });
}

function openForgotDialog() {
  resetForgotDialog();
  forgotDialog.visible = true;
}

function resetForgotDialog() {
  forgotDialog.form.email = '';
  forgotDialog.form.username = '';
  forgotDialog.submitting = false;
  forgotFormRef.value?.clearValidate();
}

async function submitForgot() {
  if (forgotDialog.submitting) {
    return;
  }
  try {
    await forgotFormRef.value?.validate();
  } catch {
    return;
  }
  forgotDialog.submitting = true;
  try {
    await API.auth.requestPasswordReset({
      email: forgotDialog.form.email,
      username: forgotDialog.form.username || undefined,
    });
    ElMessage.success('If the details match an account, a reset email has been sent.');
    forgotDialog.visible = false;
  } catch (error) {
    const message = getErrorMessage(error, 'Failed to request password reset.');
    ElMessage.error(message);
  } finally {
    forgotDialog.submitting = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f6f9fc 0%, #edf1f5 100%);
  padding: 24px;
}
.login-card {
  width: 380px;
}
.title {
  text-align: center;
  margin-bottom: 4px;
}
.subtitle {
  text-align: center;
  color: #606266;
  margin-bottom: 20px;
  font-size: 13px;
}
.full {
  width: 100%;
}
.links {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 12px;
  gap: 8px;
}
.register-link {
  color: #409eff;
  font-size: 13px;
}
.dialog-hint {
  color: #606266;
  margin: 0;
}
</style>
