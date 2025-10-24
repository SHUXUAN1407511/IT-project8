<template>
  <div class="courses-page">
    <div class="page-header">
      <div>
        <h2>Course Management</h2>
      </div>
      <el-button
        type="primary"
        v-permission="['admin', 'sc']"
        @click="openCreateCourse"
      >
        New course
      </el-button>
    </div>

    <el-card class="filters" shadow="never">
      <div class="filter-row">
        <el-input
          v-model="searchQuery"
          placeholder="Search by course name or code"
          clearable
          class="filter-item"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="termFilter"
          placeholder="Filter by term"
          clearable
          class="filter-item"
        >
          <el-option
            v-for="term in termOptions"
            :key="term"
            :label="term"
            :value="term"
          />
        </el-select>
        <el-select
          v-if="isAdmin"
          v-model="coordinatorFilter"
          placeholder="Filter by coordinator"
          clearable
          class="filter-item"
        >
          <el-option
            v-for="sc in coordinatorOptions"
            :key="sc.id"
            :label="sc.name"
            :value="sc.id"
          />
        </el-select>
      </div>
    </el-card>

    <el-card shadow="never">
      <el-table
        :data="sortedCourses"
        stripe
        border
        @sort-change="onSortChange"
        height="460"
        empty-text="No courses yet"
      >
        <el-table-column
          prop="name"
          label="Course"
          min-width="220"
          sortable="custom"
        >
          <template #default="{ row }">
            <div class="course-name">
              <span class="name">{{ row.name }}</span>
              <span class="code">{{ row.code }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="term"
          label="Term"
          width="140"
          sortable="custom"
        />
        <el-table-column
          prop="description"
          label="Description"
          min-width="260"
          show-overflow-tooltip
        />
        <el-table-column
          prop="coordinator"
          label="Coordinator"
          width="160"
        >
          <template #default="{ row }">
            {{ resolveCoordinator(row.coordinatorId)?.name || '—' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="updatedAt"
          label="Last updated"
          width="180"
          sortable="custom"
        >
          <template #default="{ row }">
            {{ formatDate(row.updatedAt) }}
          </template>
        </el-table-column>
        <el-table-column
          label="Actions"
          width="180"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              @click="openEditCourse(row)"
            >
              Edit
            </el-button>
            <el-button
              link
              type="danger"
              v-permission="['admin', 'sc']"
              @click="confirmRemoveCourse(row)"
            >
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="courseDialogVisible"
      :title="courseForm.id ? 'Edit course' : 'New course'"
      width="520px"
      destroy-on-close
    >
      <el-form
        ref="courseFormRef"
        :model="courseForm"
        :rules="courseRules"
        label-width="110px"
      >
        <el-form-item label="Course name" prop="name">
          <el-input v-model="courseForm.name" maxlength="80" show-word-limit />
        </el-form-item>
        <el-form-item label="Course code" prop="code">
          <el-input v-model="courseForm.code" maxlength="20" show-word-limit />
        </el-form-item>
        <el-form-item label="Year / term" prop="term">
          <div class="term-selects">
            <el-select
              v-model="courseYear"
              placeholder="Select year"
              class="term-item"
              style="width: 100%;"
            >
              <el-option
                v-for="year in yearOptions"
                :key="year"
                :label="year"
                :value="year"
              />
            </el-select>
            <el-select
              v-model="courseSeason"
              placeholder="Select term"
              class="term-item"
              style="width: 100%;"
            >
              <el-option
                v-for="season in seasonOptions"
                :key="season"
                :label="season"
                :value="season"
              />
            </el-select>
          </div>
        </el-form-item>
        <el-form-item label="Coordinator" prop="coordinatorId">
          <el-select
            v-model="courseForm.coordinatorId"
            :disabled="!isAdmin"
            placeholder="Choose a coordinator"
          >
            <el-option
              v-for="coordinator in coordinatorOptions"
              :key="coordinator.id"
              :value="coordinator.id"
              :label="coordinator.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input
            v-model="courseForm.description"
            type="textarea"
            :rows="3"
            maxlength="160"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="courseDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitCourse">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus';
import { useUserStore } from '@/store/useUserStore';
import { useDataStore, type Course } from '@/store/useDataStore';
import { Search } from '@element-plus/icons-vue';

const dataStore = useDataStore();
const userStore = useUserStore();
const coursesArr = computed(() =>
  Array.isArray(dataStore.courses) ? dataStore.courses : [],
);



const searchQuery = ref('');
const termFilter = ref('');
const coordinatorFilter = ref('');
const sortState = ref<{
  prop: keyof Course | '';
  order: 'ascending' | 'descending' | null;
}>({
  prop: '',
  order: null,
});

const isAdmin = computed(() => userStore.role === 'admin');
const currentUserCoordinatorKeys = computed(() => {
  const keys = new Set<string>();
  if (userStore.userInfo?.id) {
    keys.add(String(userStore.userInfo.id));
  }
  if (userStore.userInfo?.username) {
    keys.add(String(userStore.userInfo.username));
  }
  return Array.from(keys);
});

onMounted(async () => {
  await Promise.allSettled([dataStore.fetchCourses(), dataStore.fetchUsers()]);
});

const coordinatorOptions = computed(() => {
  const list = dataStore.coordinators;
  if (list.length) {
    return list;
  }
  if (userStore.role === 'sc' && userStore.userInfo) {
    return [
      {
        id: userStore.userInfo.id,
        name: userStore.userInfo.name,
        username: userStore.userInfo.username,
        email: userStore.userInfo.email || '',
        role: 'sc',
        status: 'active',
      },
    ];
  }
  return list;
});

const termOptions = computed(() => {
  const terms = new Set<string>();
  coursesArr.value.forEach((course) => terms.add(course.term));
  return Array.from(terms.values()).sort();
});

const filteredCourses = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  return coursesArr.value.filter((course) => {
    const matchesQuery =
      !query ||
      course.name.toLowerCase().includes(query) ||
      course.code.toLowerCase().includes(query);
    const matchesTerm = !termFilter.value || course.term === termFilter.value;
    const matchesCoordinator =
      !coordinatorFilter.value || course.coordinatorId === coordinatorFilter.value;
    if (!isAdmin.value && userStore.userInfo?.id) {
      const matchesCurrentUser =
        currentUserCoordinatorKeys.value.length === 0 ||
        currentUserCoordinatorKeys.value.includes(course.coordinatorId);
      return matchesQuery && matchesTerm && matchesCurrentUser;
    }
    return matchesQuery && matchesTerm && matchesCoordinator;
  });
});

const sortedCourses = computed(() => {
  if (!sortState.value.prop || !sortState.value.order) {
    return filteredCourses.value;
  }
  const prop = sortState.value.prop;
  const order = sortState.value.order === 'ascending' ? 1 : -1;
  return [...filteredCourses.value].sort((a, b) => {
    const av = (a as any)[prop];
    const bv = (b as any)[prop];
    if (av === bv) {
      return 0;
    }
    return av > bv ? order : -order;
  });
});

const courseDialogVisible = ref(false);
const courseFormRef = ref<FormInstance>();

const currentYear = new Date().getFullYear();
const yearOptions = Array.from({ length: 11 }, (_, i) => String(currentYear - 5 + i));
const seasonOptions = ['S1', 'S2', 'Summer', 'Winter'];

const courseForm = reactive({
  id: '',
  name: '',
  code: '',
  term: '',
  coordinatorId: '',
  description: '',
});

const courseYear = ref(String(currentYear));
const courseSeason = ref('');

watch([courseYear, courseSeason], ([year, season]) => {
  if (year && season) {
    courseForm.term = `${year} ${season}`;
  } else {
    courseForm.term = '';
  }
  courseFormRef.value?.validateField?.('term');
});
const courseRules: FormRules = {
  name: [
    { required: true, message: 'Please enter a course name.', trigger: 'blur' },
  ],
  code: [
    { required: true, message: 'Please enter a course code.', trigger: 'blur' },
  ],
  term: [
    { required: true, message: 'Please select the year and term.', trigger: 'change' },
  ],
  coordinatorId: [
    { required: true, message: 'Please choose a coordinator.', trigger: 'change' },
  ],
};

function resetCourseForm() {
  courseForm.id = '';
  courseForm.name = '';
  courseForm.code = '';
  courseForm.term = '';
  courseYear.value = String(currentYear);
  courseSeason.value = '';
  courseForm.coordinatorId = isAdmin.value ? '' : userStore.userInfo?.id || '';
  courseForm.description = '';
}

function resolveCoordinator(coordinatorId: string) {
  return coordinatorOptions.value.find((option) => option.id === coordinatorId);
}

function onSortChange({
  prop,
  order,
}: { prop: keyof Course; order: 'ascending' | 'descending' | null }) {
  sortState.value = { prop, order };
}

function openCreateCourse() {
  resetCourseForm();
  courseDialogVisible.value = true;
}

function openEditCourse(course: Course) {
  courseForm.id = course.id;
  courseForm.name = course.name;
  courseForm.code = course.code;
  const [yearPart = '', seasonPart = ''] = (course.term || '').split(' ');
  courseYear.value = yearOptions.includes(yearPart) ? yearPart : String(currentYear);
  courseSeason.value = seasonOptions.includes(seasonPart) ? seasonPart : '';
  courseForm.term = courseSeason.value ? `${courseYear.value} ${courseSeason.value}` : '';
  courseForm.coordinatorId = course.coordinatorId;
  courseForm.description = course.description || '';
  courseDialogVisible.value = true;
}

function getApiErrorMessage(err: any) {
  const data = err?.response?.data;
  if (!data) {
    return 'Request failed.';
  }
  if (typeof data === 'string') {
    return data;
  }

  if (Array.isArray(data?.non_field_errors) && data.non_field_errors.length) {
    return data.non_field_errors[0];
  }

  for (const key of ['code', 'term', 'name', 'coordinatorId', 'description']) {
    const arr = (data as any)?.[key];
    if (Array.isArray(arr) && arr.length) {
      return arr[0];
    }
  }

  return 'Request failed.';
}


function submitCourse() {
  courseFormRef.value?.validate(async (valid) => {
    if (!valid) {
      return;
    }
    const payload = {
      name: courseForm.name,
      code: courseForm.code,
      term: courseForm.term,
      coordinatorId: courseForm.coordinatorId,
      description: courseForm.description,
    };
    try {
      if (courseForm.id) {
        await dataStore.updateCourse(courseForm.id, payload);
        ElMessage.success('Course updated.');
      } else {
        await dataStore.addCourse(payload as any);
        ElMessage.success('Course created.');
      }
      courseDialogVisible.value = false;
    } catch (err: any) {
      ElMessage.error(getApiErrorMessage(err));
    }
  });
}

function confirmRemoveCourse(course: Course) {
  ElMessageBox.confirm(
    `Delete course “${course.name}”? Related assignments and templates will also be removed.`,
    'Delete course',
    {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
    .then(async () => {
      await dataStore.deleteCourse(course.id);
      ElMessage.success('Course deleted.');
    })
    .catch(() => undefined);
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
.courses-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}
.subtitle {
  margin: 4px 0 0;
  color: #606266;
  font-size: 14px;
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
  width: 240px;
}
.course-name {
  display: flex;
  flex-direction: column;
}
.course-name .name {
  font-weight: 600;
}
.course-name .code {
  color: #909399;
  font-size: 12px;
}
.term-selects {
  display: flex;
  gap: 8px;
  width: 100%;
}
.term-item {
  flex: 1 1 160px;
}
</style>
