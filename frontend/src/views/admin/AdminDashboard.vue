<!--
Admin dashboard: Entry points for scale management, notifications, and overview.
-->

<template>
  <div class="dashboard">
    <h2>Admin Overview</h2>

    <section class="summary">
      <div
        v-for="card in summaryCards"
        :key="card.title"
        class="summary-item"
      >
        <strong>{{ card.title }}</strong>
        <span class="value">{{ card.value }}</span>
        <span class="note">{{ card.extra }}</span>
      </div>
    </section>

    <section class="notice">
      <h3>Recent Notifications</h3>
      <p v-if="!recentNotices.length">No notifications.</p>
      <ul v-else>
        <li v-for="notice in recentNotices" :key="notice.id">
          <div class="title">{{ notice.title }}</div>
          <div class="time">{{ formatDate(notice.createdAt) }}</div>
        </li>
      </ul>
      <button type="button" @click="router.push('/notifications')">View All Notifications</button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useDataStore } from '@/store/data';

const router = useRouter();
const dataStore = useDataStore();

const summaryCards = computed(() => [
  {
    title: 'Total Users',
    value: dataStore.users.length,
    extra: 'Admin / SC / Tutor',
  },
  {
    title: 'Courses',
    value: dataStore.courses.length,
  },
  {
    title: 'Unread Notifications',
    value: dataStore.notifications.filter((n) => !n.isRead).length,
  },
]);

const recentNotices = computed(() => dataStore.notifications.slice(0, 3));

function formatDate(value?: string) {
  if (!value) return '—';
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 20px; }
.summary { display: flex; gap: 12px; flex-wrap: wrap; }
.summary-item { border: 1px solid #ccc; padding: 12px; width: 200px; background: #fafafa; }
.summary-item .value { font-size: 24px; display: block; margin: 6px 0; }
.summary-item .note { font-size: 12px; color: #666; }
.notice { border: 1px solid #ccc; padding: 16px; background: #fff; }
.notice button { margin-top: 8px; padding: 6px 10px; border: 1px solid #333; background: #fff; cursor: pointer; }
.notice ul { margin: 0; padding-left: 16px; }
.notice li { margin-bottom: 8px; }
.notice .title { font-weight: 600; font-size: 14px; }
.notice .time { font-size: 12px; color: #777; }
</style>
