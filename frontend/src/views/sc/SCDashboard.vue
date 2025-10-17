<template>
  <div class="dashboard">
    <h2>Subject Coordinator Overview</h2>

    <el-row :gutter="16" class="cards">
      <el-col :span="12">
        <el-card shadow="hover">
          <div class="card-title">Courses overview</div>
          <div class="card-value">{{ myCourses.length }}</div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <div class="card-title">Templates pending publication</div>
          <div class="card-value">{{ draftTemplates.length }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="sections">
      <el-col :span="24">
        <el-card shadow="never" class="panel">
          <div class="panel-header">
            <h3>Templates to action</h3>
            <el-button type="primary" link @click="router.push('/assignments')">Go to assignment management</el-button>
          </div>
          <el-timeline v-if="draftTemplates.length">
            <el-timeline-item
              v-for="item in draftTemplates"
              :key="item.assignment.id"
              type="warning"
            >
              <div class="timeline-entry">
                <strong>{{ item.assignment.name }}</strong>
                <span class="muted"> · {{ item.course.name }}</span>
                <el-button size="small" link type="primary" @click="toTemplate(item.assignment.id)">Manage template</el-button>
              </div>
            </el-timeline-item>
          </el-timeline>
          <div v-else class="empty-message">No drafts at the moment</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/user';
import { useDataStore } from '@/store/data';

const router = useRouter();
const userStore = useUserStore();
const dataStore = useDataStore();
const coursesArr = computed(() => Array.isArray(dataStore.courses) ? dataStore.courses : []);
const assignmentsArr = computed(() => Array.isArray(dataStore.assignments) ? dataStore.assignments : []);
const normalizeId = (value: unknown) => (value === undefined || value === null ? '' : String(value));

onMounted(async () => {
  await Promise.allSettled([dataStore.fetchCourses(), dataStore.fetchAssignments()]);
});

const myCourses = computed(() =>
  coursesArr.value.filter((course) => normalizeId(course.scId) === normalizeId(userStore.userInfo?.id))
);

const termCount = computed(() => new Set(myCourses.value.map((course) => course.term)).size);

const myAssignments = computed(() =>
  assignmentsArr.value.filter((assignment) =>
    myCourses.value.some((course) => normalizeId(course.id) === normalizeId(assignment.courseId))
  )
);

const draftTemplates = computed(() =>
  myAssignments.value
    .filter((assignment) => assignment.aiDeclarationStatus !== 'published')
    .map((assignment) => ({
      assignment,
      course: myCourses.value.find(
        (course) => normalizeId(course.id) === normalizeId(assignment.courseId)
      )!,
    }))
);

function toTemplate(assignmentId: string | number) {
  router.push({ name: 'TemplateEditor', params: { assignmentId: String(assignmentId) } });
}
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 16px; }
.subtitle { color: #606266; }
.cards { margin-top: 8px; }
.card-title { font-size: 14px; color: #606266; }
.card-value { font-size: 28px; font-weight: 600; margin: 8px 0; }
.card-extra { color: #909399; font-size: 12px; }
.sections { margin-top: 8px; }
.panel { height: 100%; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.timeline-entry { display: flex; align-items: center; gap: 8px; }
.muted { color: #909399; }
.empty-message { padding: 24px 0; text-align: center; color: #909399; }
</style>
