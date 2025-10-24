<template>
  <div class="user-page">
    <div class="page-header">
      <div>
        <h2>User & Access Management</h2>
      </div>
    </div>

    <el-card class="filters" shadow="never">
      <div class="filter-row">
        <el-input
          v-model="searchQuery"
          placeholder="Search by name or email"
          clearable
          class="filter-item"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="roleFilter" placeholder="Role" clearable class="filter-item">
          <el-option label="Administrator" value="admin" />
          <el-option label="Subject Coordinator" value="sc" />
          <el-option label="Tutor" value="tutor" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable class="filter-item">
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
      </div>
    </el-card>

    <el-card shadow="never">
      <el-table
        :data="filteredUsers"
        stripe
        border
        height="480"
        empty-text="No users yet"
      >
        <el-table-column prop="name" label="Name" min-width="160" />
        <el-table-column prop="username" label="Username" min-width="140" />
        <el-table-column prop="email" label="Email" min-width="200" />
        <el-table-column label="Role" width="160">
          <template #default="{ row }">
            {{ roleLabel(row.role) }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? 'Active' : 'Inactive' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLoginAt" label="Last sign-in" width="200">
          <template #default="{ row }">
            {{ formatDate(row.lastLoginAt) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">Edit</el-button>
            <el-button link @click="toggleStatus(row)">
              {{ row.status === 'active' ? 'Disable' : 'Enable' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="Edit user" width="520px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="Name" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="Role" prop="role">
          <el-select v-model="form.role" placeholder="Select a role">
            <el-option label="Administrator" value="admin" />
            <el-option label="Subject Coordinator" value="sc" />
            <el-option label="Tutor" value="tutor" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submit">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import { useDataStore, type ManagedUser } from '@/store/useDataStore';
import type { UserRole } from '@/store/useUserStore';

const dataStore = useDataStore();

onMounted(async () => {
  await dataStore.fetchUsers();
});

const searchQuery = ref('');
const roleFilter = ref('');
const statusFilter = ref('');

const filteredUsers = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  return dataStore.users.filter((user) => {
    const email = user.email?.toLowerCase() || '';
    const matchesQuery = !query || user.name.toLowerCase().includes(query) || email.includes(query);
    const matchesRole = !roleFilter.value || user.role === roleFilter.value;
    const matchesStatus = !statusFilter.value || user.status === statusFilter.value;
    return matchesQuery && matchesRole && matchesStatus;
  });
});

const dialogVisible = ref(false);
const formRef = ref<FormInstance>();

const form = reactive({
  id: '',
  name: '',
  username: '',
  email: '',
  role: '' as UserRole | '',
  phone: '',
  organization: '',
  bio: '',
});

const formRules: FormRules = {
  name: [{ required: true, message: 'Please enter a name.', trigger: 'blur' }],
  username: [{ required: true, message: 'Please enter a username.', trigger: 'blur' }],
  email: [
    { type: 'email', message: 'Please enter a valid email address.', trigger: 'blur' },
  ],
  role: [{ required: true, message: 'Please choose a role.', trigger: 'change' }],
};

function openEditDialog(user: ManagedUser) {
  form.id = user.id;
  form.name = user.name;
  form.username = user.username;
  form.email = user.email || '';
  form.role = user.role;
  form.phone = user.phone || '';
  form.organization = user.organization || '';
  form.bio = user.bio || '';
  dialogVisible.value = true;
}

function submit() {
  formRef.value?.validate(async (valid) => {
    if (!valid) {
      return;
    }
    await dataStore.updateUser(form.id, {
      name: form.name,
      username: form.username,
      email: form.email || undefined,
      role: form.role as UserRole,
      phone: form.phone,
      organization: form.organization,
      bio: form.bio,
    });
    ElMessage.success('User details updated.');
    dialogVisible.value = false;
  });
}

async function toggleStatus(user: ManagedUser) {
  const next = user.status === 'active' ? 'inactive' : 'active';
  await dataStore.toggleUserStatus(user.id, next);
  ElMessage.success(next === 'active' ? 'Account enabled.' : 'Account disabled.');
}

function roleLabel(role: string) {
  if (role === 'admin') {
    return 'Administrator';
  }
  if (role === 'sc') {
    return 'Subject Coordinator';
  }
  if (role === 'tutor') {
    return 'Tutor';
  }
  return role;
}

function formatDate(value?: string) {
  if (!value) {
    return '—';
  }
  return new Intl.DateTimeFormat('en-AU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}
</script>

<style scoped>
.user-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.page-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 16px;
}
.subtitle {
  color: #606266;
}
.filters {
  padding: 12px 16px;
}
.filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.filter-item {
  width: 220px;
}
</style>
