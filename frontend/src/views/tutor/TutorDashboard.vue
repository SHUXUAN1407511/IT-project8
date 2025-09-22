<!--
Tutor dashboard: View relevant assignments and jump into declaration editing.
-->

<template>
  <div class="dashboard">
    <h2>Tutor Workspace</h2>

    <div class="panel">
      <div class="panel-header">
        <h3>Assignments to tackle</h3>
        <button type="button" @click="router.push('/assignments')">All assignments</button>
      </div>

      <p v-if="!assignedAssignments.length"</p>

      <table v-else class="table">
        <thead>
          <tr>
            <th>Assignment</th>
            <th>Course</th>
            <th>Template status</th>
            <th>Due date</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in assignedAssignments" :key="row.id">
            <td>{{ row.name }}</td>
            <td>{{ row.courseName }}</td>
            <td>{{ statusLabel(row.aiDeclarationStatus) }}</td>
            <td>{{ formatDate(row.dueDate) }}</td>
            <td>
              <button type="button" @click="router.push({ name: 'TemplateEditor', params: { assignmentId: row.id } })">
                Edit template
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/user';
import { useDataStore } from '@/store/data';

const router = useRouter();
const userStore = useUserStore();
const dataStore = useDataStore();

const assignedAssignments = computed(() => {
  const tutorId = userStore.userInfo?.id || '';
  return dataStore.assignments
    .filter((assignment) => assignment.tutorIds.includes(tutorId))
    .map((assignment) => ({
      ...assignment,
      courseName: dataStore.courses.find((course) => course.id === assignment.courseId)?.name || '—',
    }))
    .sort((a, b) => {
      const timeA = a.dueDate ? new Date(a.dueDate).getTime() : Number.POSITIVE_INFINITY;
      const timeB = b.dueDate ? new Date(b.dueDate).getTime() : Number.POSITIVE_INFINITY;
      return timeA - timeB;
    });
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

function formatDate(value?: string) {
  if (!value) return '—';
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 20px; }
.subtitle { color: #555; font-size: 14px; }
.panel { border: 1px solid #ccc; padding: 16px; background: #fff; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.panel button { border: 1px solid #555; background: #fff; padding: 4px 8px; cursor: pointer; }
.empty { color: #777; }
.table { width: 100%; border-collapse: collapse; }
.table th,
.table td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 13px; }
.table tbody tr:nth-child(even) { background: #f9f9f9; }
</style>
