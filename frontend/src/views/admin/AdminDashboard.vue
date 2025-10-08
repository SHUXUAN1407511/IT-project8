<template>
  <div class="dashboard">
    <h2>Administrator Overview</h2>

    <el-row :gutter="16" class="cards">
      <el-col :span="8" v-for="card in summaryCards" :key="card.title">
        <el-card shadow="hover">
          <div class="card-title">{{ card.title }}</div>
          <div class="card-value">{{ card.value }}</div>
          <div class="card-extra">{{ card.extra }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="sections">
      <el-col :span="12">
        <el-card shadow="never" class="panel">
          <div class="panel-header">
            <h3>Default Scale – latest version</h3>
            <el-button type="primary" link @click="router.push('/scales')">Open management</el-button>
          </div>
          <el-descriptions :column="1" size="small" border>
            <el-descriptions-item label="Version">v{{ defaultScale?.currentVersion.version }}</el-descriptions-item>
            <el-descriptions-item label="Updated by">{{ defaultScale?.currentVersion.updatedBy }}</el-descriptions-item>
            <el-descriptions-item label="Updated at">{{ formatDate(defaultScale?.currentVersion.updatedAt) }}</el-descriptions-item>
            <el-descriptions-item label="Notes">{{ defaultScale?.currentVersion.notes || '—' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="panel">
          <div class="panel-header">
            <h3>Latest notifications</h3>
            <el-button type="primary" link @click="router.push('/notifications')">View all</el-button>
          </div>
          <el-timeline v-if="recentNotices.length">
            <el-timeline-item
              v-for="notice in recentNotices"
              :key="notice.id"
              :timestamp="formatDate(notice.createdAt)"
              :type="notice.isRead ? 'info' : 'primary'"
            >
              {{ notice.title }}
            </el-timeline-item>
          </el-timeline>
          <div v-else class="empty-message">No notifications</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useDataStore } from '@/store/data';

const router = useRouter();
const dataStore = useDataStore();

const defaultScale = computed(() => dataStore.defaultScale);

const summaryCards = computed(() => [
  {
    title: 'Total users',
    value: dataStore.users.length,
  },
  {
    title: 'Courses',
    value: dataStore.courses.length,
  },
  {
    title: 'Unread notifications',
    value: dataStore.notifications.filter((n) => !n.isRead).length,
  },
]);

const recentNotices = computed(() => dataStore.notifications.slice(0, 3));

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
.dashboard { display: flex; flex-direction: column; gap: 16px; }
.subtitle { color: #606266; }
.cards { margin-top: 8px; }
.card-title { font-size: 14px; color: #606266; }
.card-value { font-size: 28px; font-weight: 600; margin: 8px 0; }
.card-extra { color: #909399; font-size: 12px; }
.sections { margin-top: 8px; }
.panel { height: 100%; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.empty-message { padding: 24px 0; text-align: center; color: #909399; }
</style>
