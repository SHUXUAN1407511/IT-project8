<!--
SC dashboard: Manage AI Use Scales, courses, assignments, and tutor permissions.
-->

<template>
  <div class="dashboard">
    <h2>Subject Coordinator Overview</h2>
    <section class="info">
      <div class="block">
        <strong>Courses owned:</strong>
        <span>{{ myCourses.length }}</span>
      </div>
      <div class="block">
        <strong>Draft templates:</strong>
        <span>{{ draftTemplates.length }}</span>
      </div>
    </section>

    <section class="drafts">
      <div class="header">
        <h3>Drafts to finish</h3>
        <button type="button" @click="router.push('/assignments')">Open assignments</button>
      </div>
      <p v-if="!draftTemplates.length"</p>
      <ul v-else>
        <li v-for="item in draftTemplates" :key="item.assignment.id">
          <div class="title">{{ item.assignment.name }}</div>
          <div class="course">Course: {{ item.course.name }}</div>
          <button type="button" @click="toTemplate(item.assignment.id)">Edit template</button>
        </li>
      </ul>
    </section>

    <section class="quick-actions">
      <button type="button" @click="router.push({ name: 'TemplateEditor' })">
        Open template editor
      </button>
    </section>
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

const myCourses = computed(() =>
  dataStore.courses.filter((course) => course.scId === userStore.userInfo?.id)
);

const myAssignments = computed(() =>
  dataStore.assignments.filter((assignment) => myCourses.value.some((course) => course.id === assignment.courseId))
);

const draftTemplates = computed(() =>
  myAssignments.value
    .filter((assignment) => assignment.aiDeclarationStatus !== 'published')
    .map((assignment) => ({
      assignment,
      course: myCourses.value.find((course) => course.id === assignment.courseId)!,
    }))
);

function toTemplate(assignmentId: string) {
  router.push({ name: 'TemplateEditor', params: { assignmentId } });
}
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 20px; }
.subtitle { color: #555; font-size: 14px; }
.info { display: flex; gap: 12px; flex-wrap: wrap; }
.block { border: 1px solid #ccc; padding: 12px; background: #fff; min-width: 160px; }
.quick-actions { display: flex; margin-top: 12px; }
.quick-actions button { border: 1px solid #555; background: #fff; padding: 6px 12px; cursor: pointer; }
.drafts { border: 1px solid #ccc; padding: 16px; background: #fff; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.drafts button { border: 1px solid #555; background: #fff; padding: 4px 8px; cursor: pointer; }
.drafts ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px; }
.drafts li { border: 1px solid #eee; padding: 10px; background: #f9f9f9; }
.title { font-weight: 600; margin-bottom: 4px; }
.course { font-size: 13px; color: #666; margin-bottom: 6px; }
.empty { color: #777; }
</style>
