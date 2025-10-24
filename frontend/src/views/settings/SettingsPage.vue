<template>
  <div class="settings-page">
    <h2>Account Settings</h2>

    <el-row :gutter="16">
      <el-col :span="24" :lg="12">
        <el-card shadow="never" class="panel">
          <h3>Profile</h3>
          <el-descriptions :column="1" border size="small" class="descriptions">
            <el-descriptions-item label="Username">{{ userInfo?.username }}</el-descriptions-item>
            <el-descriptions-item label="Role">{{ roleLabel }}</el-descriptions-item>
            <el-descriptions-item label="Email">{{ userInfo?.email }}</el-descriptions-item>
          </el-descriptions>
          <el-divider />
          <el-form
            :model="profileForm"
            :rules="profileRules"
            ref="profileFormRef"
            label-width="100px"
          >
            <el-form-item label="Name" prop="name">
              <el-input v-model="profileForm.name" />
            </el-form-item>
            <el-form-item label="Email" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProfile">Save changes</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="24" :lg="12">
        <el-card shadow="never" class="panel">
          <h3>Change Password</h3>
          <el-form
            :model="passwordForm"
            :rules="passwordRules"
            ref="passwordFormRef"
            label-width="150px"
          >
            <el-form-item label="Current password" prop="currentPassword">
              <el-input v-model="passwordForm.currentPassword" show-password />
            </el-form-item>
            <el-form-item label="New password" prop="newPassword">
              <el-input v-model="passwordForm.newPassword" show-password />
            </el-form-item>
            <el-form-item label="Confirm password" prop="confirmPassword">
              <el-input v-model="passwordForm.confirmPassword" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">Update password</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { getErrorMessage } from '@/utils/errors';
import { useUserStore } from '@/store/useUserStore';

const userStore = useUserStore();
const userInfo = computed(() => userStore.userInfo);

const profileFormRef = ref<FormInstance>();
const passwordFormRef = ref<FormInstance>();

const profileForm = reactive({
  name: '',
  email: '',
});

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
});

const profileRules: FormRules = {
  name: [{ required: true, message: 'Please enter your name.', trigger: 'blur' }],
  email: [
    { required: true, message: 'Please enter your email address.', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address.', trigger: 'blur' },
  ],
};

const passwordRules: FormRules = {
  currentPassword: [
    {
      required: true,
      message: 'Please enter your current password.',
      trigger: 'blur',
    },
  ],
  newPassword: [
    { required: true, message: 'Please enter a new password.', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters.', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm your new password.', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('The passwords do not match.'));
        } else {
          callback();
        }
      },
      trigger: 'blur',
    },
  ],
};

const roleLabel = computed(() => {
  switch (userInfo.value?.role) {
    case 'admin':
      return 'Administrator';
    case 'sc':
      return 'Subject Coordinator';
    case 'tutor':
      return 'Tutor';
    default:
      return 'Unknown role';
  }
});

async function saveProfile() {
  if (!profileFormRef.value) {
    return;
  }
  try {
    await profileFormRef.value.validate();
  } catch (error) {
    return;
  }
  try {
    await userStore.updateProfile({
      name: profileForm.name,
      email: profileForm.email,
    });
    ElMessage.success('Profile updated.');
  } catch (error) {
    ElMessage.error(getErrorMessage(error, 'Failed to update profile.'));
  }
}

watch(
  userInfo,
  (info) => {
    profileForm.name = info?.name || '';
    profileForm.email = info?.email || '';
  },
  { immediate: true }
);

async function changePassword() {
  if (!passwordFormRef.value) {
    return;
  }
  try {
    await passwordFormRef.value.validate();
  } catch (error) {
    return;
  }
  try {
    await userStore.changePassword(passwordForm.currentPassword, passwordForm.newPassword);
    ElMessage.success('Password updated.');
    passwordForm.currentPassword = '';
    passwordForm.newPassword = '';
    passwordForm.confirmPassword = '';
  } catch (error) {
    ElMessage.error(getErrorMessage(error, 'Failed to update password.'));
  }
}

onMounted(async () => {
  if (userStore.isAuthenticated) {
    try {
      await userStore.refreshProfile();
    } catch (error) {
      ElMessage.error(getErrorMessage(error, 'Failed to load profile.'));
    }
  }
});
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.subtitle {
  color: #606266;
}
.panel {
  height: 100%;
}
.descriptions {
  margin-bottom: 12px;
}
</style>
