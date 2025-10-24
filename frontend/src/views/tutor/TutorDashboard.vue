<template>
  <div class="dashboard">
    <h2>Tutor Workspace</h2>

    <el-card shadow="never" class="panel">
      <div class="panel-header">
        <h3>To-do list</h3>
        <el-button
          type="primary"
          link
          @click="router.push('/assignments')"
        >
          View all assignments
        </el-button>
      </div>
      <el-table :data="assignedAssignments" border empty-text="No assignments yet">
        <el-table-column prop="name" label="Assignment" min-width="180" />
        <el-table-column prop="courseName" label="Course" min-width="180" />
        <el-table-column label="Template status" width="140">
          <template #default="{ row }">
            <el-tag :type="tagType(row.aiDeclarationStatus)">
              {{ statusLabel(row.aiDeclarationStatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Action" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              @click="router.push({
                name: 'TemplateEditor',
                params: { assignmentId: String(row.id) },
              })"
            >
              Edit template
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/useUserStore';
import { useDataStore } from '@/store/useDataStore';

const router = useRouter();
const userStore = useUserStore();
const dataStore = useDataStore();

onMounted(async () => {
  await dataStore.fetchAssignments();
});

const assignedAssignments = computed(() => {
  const tutorId = String(userStore.userInfo?.id ?? '');
  return dataStore.assignments
    .filter(
      (assignment) =>
        Array.isArray(assignment.tutorIds) &&
        assignment.tutorIds.map((value) => String(value)).includes(tutorId)
    )
    .map((assignment) => ({
      ...assignment,
      id: String(assignment.id),
      courseName:
        assignment.courseName ||
        dataStore.courses.find(
          (course) => String(course.id) === String(assignment.courseId),
        )?.name ||
        '—',
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
});

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

function tagType(status: string) {
  if (status === 'published') {
    return 'success';
  }
  if (status === 'draft') {
    return 'warning';
  }
  return 'info';
}
</script>

<style scoped>
.dashboard {
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
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
</style>
