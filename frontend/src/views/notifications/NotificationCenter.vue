<template>
  <div class="notification-page">
    <div class="page-header">
      <div>
        <h2>Notification Centre</h2>
      </div>
      <div class="actions">
        <el-button
          @click="filter = 'all'"
          :type="filter === 'all' ? 'primary' : 'default'"
        >
          All
        </el-button>
        <el-button
          @click="filter = 'unread'"
          :type="filter === 'unread' ? 'primary' : 'default'"
        >
          Unread
        </el-button>
        <el-button type="primary" plain :disabled="!hasUnread" @click="markAll">
          Mark all as read
        </el-button>
      </div>
    </div>

    <el-card shadow="never">
      <el-timeline>
        <el-timeline-item
          v-for="notice in filteredNotices"
          :key="notice.id"
          :timestamp="formatDate(notice.createdAt)"
          :type="notice.isRead ? 'info' : 'primary'"
        >
          <div class="notice">
            <div class="notice-header">
              <h4>{{ notice.title }}</h4>
              <div class="tags">
                <el-tag size="small" :type="tagType(notice.relatedType)">
                  {{ typeLabel(notice.relatedType) }}
                </el-tag>
                <el-tag
                  v-if="!notice.isRead"
                  size="small"
                  type="danger"
                >Unread</el-tag>
              </div>
            </div>
            <p class="content">{{ notice.content || notice.body }}</p>
            <div class="footer">
              <el-button size="small" link type="primary" @click="navigate(notice)">
                Open related page
              </el-button>
              <el-button size="small" link @click="markRead(notice.id)" v-if="!notice.isRead">
                Mark as read
              </el-button>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
      <div v-if="!filteredNotices.length" class="empty-message">No notifications</div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useDataStore } from '@/store/useDataStore';
import type { NotificationItem } from '@/services/api';

const dataStore = useDataStore();
const router = useRouter();

const filter = ref<'all' | 'unread'>('all');

onMounted(async () => {
  await dataStore.fetchNotifications();
});

const filteredNotices = computed(() => {
  if (filter.value === 'unread') {
    return dataStore.notifications.filter((notice) => !notice.isRead);
  }
  return dataStore.notifications;
});

const hasUnread = computed(() => dataStore.notifications.some((notice) => !notice.isRead));

async function markRead(id: string) {
  await dataStore.markNotificationRead(id);
}

async function markAll() {
  await dataStore.markAllNotificationsRead();
}

function navigate(notice: NotificationItem) {
  if (notice.relatedType === 'scale') {
    router.push({ path: '/scales' });
  } else if (notice.relatedType === 'assignment' && notice.relatedId) {
    router.push({
      name: 'TemplateEditor',
      params: { assignmentId: String(notice.relatedId) },
    });
  } else if (notice.relatedType === 'course') {
    router.push({ path: '/courses' });
  }
}

function tagType(type: string | undefined) {
  switch (type) {
    case 'scale':
      return 'warning';
    case 'assignment':
      return 'success';
    case 'course':
      return 'info';
    default:
      return 'primary';
  }
}

function typeLabel(type: string | undefined) {
  switch (type) {
    case 'scale':
      return 'Scale update';
    case 'assignment':
      return 'Assignment';
    case 'course':
      return 'Course';
    default:
      return 'System';
  }
}

function formatDate(value: string) {
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
.notification-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.subtitle {
  color: #606266;
}
.actions {
  display: flex;
  gap: 8px;
}
.notice {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.notice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.tags {
  display: flex;
  gap: 8px;
  align-items: center;
}
.content {
  color: #303133;
  margin: 0;
}
.footer {
  display: flex;
  gap: 12px;
}
.empty-message {
  padding: 24px 0;
  text-align: center;
  color: #909399;
}
</style>
