<template>
  <div class="assignments-page">
    <div class="page-header">
      <div>
        <h2>Assignment Management</h2>
      </div>
      <el-space :size="8">
        <el-button
          v-if="canManageAssignmentTypes"
          type="primary"
          plain
          @click="openTypeManager"
        >
          Manage assignment types
        </el-button>
        <el-button type="primary" :disabled="!canManageAssignments" @click="openCreateDialog">
          New assignment
        </el-button>
      </el-space>
    </div>

    <el-card class="filters" shadow="never">
      <div class="filter-row">
        <el-select
          v-model="selectedCourseId"
          placeholder="Choose a course"
          filterable
          class="filter-item"
          @change="onCourseChange"
        >
          <el-option
            v-for="course in courseOptions"
            :key="course.id"
            :label="`${course.name} (${course.term})`"
            :value="course.id"
          />
        </el-select>
        <el-input
          v-model="searchQuery"
          placeholder="Search by assignment name"
          clearable
          class="filter-item"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="typeFilter"
          placeholder="Assignment type"
          clearable
          class="filter-item"
        >
          <el-option
            v-for="type in assignmentTypeOptions"
            :key="type"
            :label="type"
            :value="type"
          />
        </el-select>
        <el-select
          v-model="statusFilter"
          placeholder="Template status"
          clearable
          class="filter-item"
        >
          <el-option label="Not created" value="missing" />
          <el-option label="Draft" value="draft" />
          <el-option label="Published" value="published" />
        </el-select>
      </div>
    </el-card>

    <el-card shadow="never">
      <el-table
        :data="filteredAssignments"
        stripe
        border
        height="480"
        empty-text="Select a course to view assignments"
      >
        <el-table-column
          prop="name"
          label="Assignment"
          min-width="220"
          show-overflow-tooltip
        />
        <el-table-column
          prop="type"
          label="Type"
          width="140"
        />
        <el-table-column
          label="Tutors"
          width="220"
        >
          <template #default="{ row }">
            <el-tag
              v-for="tutor in resolveTutors(row.tutorIds)"
              :key="tutor.id"
              size="small"
              type="info"
              class="tag"
            >
              {{ tutor.name }}
            </el-tag>
            <span v-if="!row.tutorIds.length" class="muted">Unassigned</span>
          </template>
        </el-table-column>
        <el-table-column
          label="Declaration template"
          width="220"
        >
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.aiDeclarationStatus)">
              {{ statusLabel(row.aiDeclarationStatus) }}
            </el-tag>
            <div class="timestamp" v-if="row.templateUpdatedAt">
              {{ formatDate(row.templateUpdatedAt) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column
          label="Actions"
          width="240"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button link type="primary" @click="goToTemplate(row)">
              Manage template
            </el-button>
            <el-button
              link
              type="primary"
              v-permission="['admin', 'sc']"
              @click="openEditDialog(row)"
            >
              Edit
            </el-button>
            <el-button
              link
              type="danger"
              v-permission="['admin', 'sc']"
              @click="confirmDelete(row)"
            >
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="assignmentDialogVisible"
      :title="assignmentForm.id ? 'Edit assignment' : 'New assignment'"
      width="620px"
      destroy-on-close
    >
      <el-form
        ref="assignmentFormRef"
        :model="assignmentForm"
        :rules="assignmentRules"
        label-width="150px"
      >
        <el-form-item label="Course" prop="courseId">
          <el-select
            v-model="assignmentForm.courseId"
            placeholder="Choose a course"
            :disabled="!!assignmentForm.id"
          >
            <el-option
              v-for="course in courseOptions"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Assignment name" prop="name">
          <el-input v-model="assignmentForm.name" maxlength="150" show-word-limit />
        </el-form-item>
        <el-form-item label="Type" prop="type">
          <el-select
            v-model="assignmentForm.type"
            placeholder="Choose a type"
            filterable
            allow-create
            default-first-option
          >
            <el-option
            v-for="type in assignmentTypeOptions"
              :key="type"
              :label="type"
              :value="type"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Tutors">
          <el-select
            v-model="assignmentForm.tutorIds"
            multiple
            placeholder="Select tutors"
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option
              v-for="tutor in tutorOptions"
              :key="tutor.id"
              :label="tutor.name"
              :value="tutor.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignmentDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitAssignment">Save</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="typeManagerVisible"
      title="Manage assignment types"
      width="420px"
      destroy-on-close
    >
      <el-form @submit.prevent>
        <el-form-item label="Add type">
          <el-input
            v-model="newType"
            placeholder="Enter type name"
            maxlength="60"
            @keyup.enter.prevent="addType"
          >
            <template #append>
              <el-button type="primary" @click="addType">Add</el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <div v-if="typeManagerList.length" class="type-tag-list">
        <el-tag
          v-for="type in typeManagerList"
          :key="type"
          closable
          class="type-tag"
          @close="removeType(type)"
        >
          {{ type }}
        </el-tag>
      </div>
      <p v-else class="empty-message">No types yet</p>
      <template #footer>
        <el-button text class="reset-button" @click="resetTypeManager">Reset to defaults</el-button>
        <el-button @click="typeManagerVisible = false">Cancel</el-button>
        <el-button type="primary" :disabled="!typeManagerList.length" @click="saveTypeManager">
          Save
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import { useUserStore } from '@/store/user';
import { useDataStore, type Assignment, type AssignmentType } from '@/store/data';
import { appConfig } from '@/config';

const router = useRouter();
const userStore = useUserStore();
const dataStore = useDataStore();

onMounted(async () => {
  await Promise.allSettled([dataStore.fetchCourses(), dataStore.fetchAssignments(), dataStore.fetchUsers()]);
});

const searchQuery = ref('');
const selectedCourseId = ref('');
const typeFilter = ref<AssignmentType | ''>('');
const statusFilter = ref<'missing' | 'draft' | 'published' | ''>('');

const assignmentDialogVisible = ref(false);
const assignmentFormRef = ref<FormInstance>();

const assignmentTypeOptions = computed(() => dataStore.assignmentTypes);
const typeManagerVisible = ref(false);
const typeManagerList = ref<string[]>([]);
const newType = ref('');
const canManageAssignmentTypes = computed(() => userStore.role === 'sc' || userStore.role === 'admin');
const canManageAssignments = computed(() => userStore.role === 'sc' || userStore.role === 'admin');

const assignmentForm = reactive({
  id: '',
  courseId: '',
  name: '',
  type: '' as AssignmentType | '',
  tutorIds: [] as string[],
});

const assignmentRules: FormRules = {
  courseId: [{ required: true, message: 'Please choose a course.', trigger: 'change' }],
  name: [{ required: true, message: 'Please enter an assignment name.', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select an assignment type.', trigger: 'change' }],
};

/* ========= 新增：安全数组（保证下面的 map/filter 永远作用于数组） ========= */
const coursesArr = computed(() =>
  Array.isArray(dataStore.courses) ? dataStore.courses : []
);
const assignmentsArr = computed(() =>
  Array.isArray(dataStore.assignments) ? dataStore.assignments : []
);
const tutorsArr = computed(() =>
  Array.isArray((dataStore as any).tutors) ? (dataStore as any).tutors : []
);
/* ===================================================================== */

watch(
  () => assignmentForm.type,
  (value) => {
    const trimmed = value?.trim();
    if (!trimmed) return;
    if (!dataStore.assignmentTypes.includes(trimmed)) {
      dataStore.setAssignmentTypes([...dataStore.assignmentTypes, trimmed]);
    }
  }
);

/* —— 改 here：原来 watch dataStore.assignments.map(...) —— */
watch(
  () => assignmentsArr.value.map((item) => item.type),
  (types) => {
    const normalized = Array.from(
      new Set(types.map((item) => item?.trim()).filter((item): item is string => !!item))
    ) as AssignmentType[];
    const missing = normalized.filter((item) => !dataStore.assignmentTypes.includes(item));
    if (missing.length) {
      dataStore.setAssignmentTypes([...dataStore.assignmentTypes, ...missing]);
    }
  },
  { immediate: true }
);

/* —— 改 here：courseOptions 里统一用 coursesArr/assignmentsArr —— */
const courseOptions = computed(() => {
  if (userStore.role === 'admin') {
    return coursesArr.value;
  }
  if (userStore.role === 'sc') {
    return coursesArr.value.filter((course) => course.scId === userStore.userInfo?.id);
  }
  if (userStore.role === 'tutor') {
    const tutorId = userStore.userInfo?.id;
    const courseIds = new Set(
      assignmentsArr.value
        .filter((assignment) => assignment.tutorIds.includes(tutorId || ''))
        .map((assignment) => assignment.courseId)
    );
    return coursesArr.value.filter((course) => courseIds.has(course.id));
  }
  return [];
});

watch(
  courseOptions,
  (options) => {
    if (!options.length) {
      selectedCourseId.value = '';
      return;
    }
    if (!selectedCourseId.value || !options.some((c) => c.id === selectedCourseId.value)) {
      selectedCourseId.value = options[0].id;
    }
  },
  { immediate: true }
);

const tutorOptions = computed(() => tutorsArr.value);

const filteredAssignments = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  return assignmentsArr.value.filter((assignment) => {
    if (selectedCourseId.value && assignment.courseId !== selectedCourseId.value) {
      return false;
    }
    if (
      userStore.role === 'tutor' &&
      !(Array.isArray(assignment.tutorIds) && assignment.tutorIds.includes(userStore.userInfo?.id || ''))
    ) {
      return false;
    }
    const matchesQuery = !query || assignment.name.toLowerCase().includes(query);
    const matchesType = !typeFilter.value || assignment.type === typeFilter.value;
    const matchesStatus = !statusFilter.value || assignment.aiDeclarationStatus === statusFilter.value;
    return matchesQuery && matchesType && matchesStatus;
  });
});

function statusTagType(status: string) {
  if (status === 'published') return 'success';
  if (status === 'draft') return 'warning';
  return 'info';
}

function statusLabel(status: string) {
  switch (status) {
    case 'published':
      return 'Published';
    case 'draft':
      return 'Draft';
    default:
      return 'Not created';
  }
}

function resolveTutors(ids: string[] = []) {
  return tutorOptions.value.filter((tutor) => Array.isArray(ids) && ids.includes(tutor.id));
}


function onCourseChange() {
  searchQuery.value = '';
  typeFilter.value = '';
  statusFilter.value = '';
}

function openCreateDialog() {
  resetForm();
  assignmentDialogVisible.value = true;
}

function openEditDialog(assignment: Assignment) {
  assignmentForm.id = assignment.id;
  assignmentForm.courseId = assignment.courseId;
  assignmentForm.name = assignment.name;
  assignmentForm.type = assignment.type;
  assignmentForm.tutorIds = [...assignment.tutorIds];
  assignmentDialogVisible.value = true;
}

function resetForm() {
  assignmentForm.id = '';
  assignmentForm.courseId = selectedCourseId.value || '';
  assignmentForm.name = '';
  assignmentForm.type = '';
  assignmentForm.tutorIds = [];
}

function submitAssignment() {
  assignmentFormRef.value?.validate(async (valid) => {
    if (!valid) return;
    const payload = {
      courseId: assignmentForm.courseId,
      name: assignmentForm.name,
      type: assignmentForm.type as AssignmentType,
      tutorIds: assignmentForm.tutorIds,
    };
    if (assignmentForm.id) {
      await dataStore.updateAssignment(assignmentForm.id, payload);
      ElMessage.success('Assignment updated.');
    } else {
      const created = await dataStore.addAssignment(payload);
      selectedCourseId.value = created.courseId;
      ElMessage.success('Assignment created.');
    }
    assignmentDialogVisible.value = false;
  });
}

function confirmDelete(assignment: Assignment) {
  ElMessageBox.confirm(
    `Delete assignment “${assignment.name}”? Related templates will be removed as well.`,
    'Delete assignment',
    {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
    .then(async () => {
      await dataStore.deleteAssignment(assignment.id);
      ElMessage.success('Assignment deleted.');
    })
    .catch(() => undefined);
}

function goToTemplate(assignment: Assignment) {
  router.push({ name: 'TemplateEditor', params: { assignmentId: assignment.id } });
}

function formatDate(value?: string) {
  if (!value) return '—';
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
.assignments-page { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.subtitle { margin: 4px 0 0; color: #606266; font-size: 14px; }
.filters { padding: 12px 16px; }
.filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.filter-item { width: 240px; }
.tag { margin: 2px; }
.muted { color: #909399; font-size: 13px; }
.timestamp { color: #909399; font-size: 12px; margin-top: 4px; }
.type-tag-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.type-tag { cursor: default; }
.reset-button { margin-right: auto; }
.empty-message { margin: 12px 0; padding: 12px; border: 1px dashed #ccc; background: #fff; text-align: center; color: #666; }
</style>
