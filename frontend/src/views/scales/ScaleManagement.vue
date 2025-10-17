<template>
  <div class="scale-page">
    <div class="page-header">
      <div>
        <h2>AI Use Scale Management</h2>
      </div>
      <el-space :size="8">
        <el-button
          type="primary"
          plain
          :disabled="!canEditDefault"
          @click="openLevelDialog(null)"
        >
          Add level
        </el-button>
        <el-button type="primary" :disabled="!canEditDefault" @click="saveDefaultScale">
          Save new version
        </el-button>
      </el-space>
    </div>

    <el-row :gutter="16" class="content">
      <el-col :span="24" :lg="16">
        <el-card shadow="never" class="panel">
          <div class="panel-header">
            <h3>Default scale levels</h3>
            <div class="panel-meta">
              <div>Last updated {{ formatDate(defaultScale?.currentVersion?.updatedAt) }}</div>
              <div>By {{ defaultScale?.currentVersion?.updatedBy || '—' }}</div>
            </div>
          </div>

          <el-table
            v-if="defaultLevels.length"
            :data="defaultLevels"
            border
            size="small"
            empty-text="No levels"
          >
            <el-table-column label="Level" width="120" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="cell-text" :title="row.label || '—'">
                  {{ row.label || '—' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="AI Assessment Scale" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="cell-text" :title="row.title || '—'">
                  {{ row.title || '—' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="Instructions to Students" min-width="240">
              <template #default="{ row }">
                <span
                  :class="['cell-text', { muted: !row.instructions } ]"
                  :title="row.instructions || '—'"
                >
                  {{ row.instructions || '—' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="AI Acknowledgement" min-width="240">
              <template #default="{ row }">
                <span
                  :class="['cell-text', { muted: !row.acknowledgement } ]"
                  :title="row.acknowledgement || '—'"
                >
                  {{ row.acknowledgement || '—' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="140" fixed="right">
              <template #default="{ row, $index }">
                <el-button link :disabled="!canEditDefault" @click="openLevelDialog(row)">Edit</el-button>
                <el-button
                  link
                  type="danger"
                  :disabled="!canEditDefault"
                  @click="removeLevel($index)"
                >
                  Remove
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-else class="empty-message">No levels configured</div>
        </el-card>
      </el-col>

      <el-col :span="24" :lg="8">
        <el-card shadow="never" class="panel history-card">
          <div class="panel-header">
            <h3>Version history</h3>
          </div>
          <el-timeline>
            <el-timeline-item
              v-for="version in defaultScale?.history || []"
              :key="version.id"
              :timestamp="formatDate(version.updatedAt)"
            >
              <div class="version-item">
                <div>
                  <strong>v{{ version.version }}</strong>
                  <span class="muted"> · {{ version.updatedBy }}</span>
                  <p class="muted">{{ version.notes || 'No notes' }}</p>
                </div>
                <el-button size="small" :disabled="!canEditDefault" @click="rollbackScale(version)">
                  Clone this version
                </el-button>
              </div>
            </el-timeline-item>
          </el-timeline>
          <div v-if="!(defaultScale?.history?.length)" class="empty-message">No history yet</div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog
      v-model="levelDialog.visible"
      :title="levelDialog.isEdit ? 'Edit scale level' : 'Add scale level'"
      width="700px"
    >
      <el-form :model="levelDialog.form" label-width="150px">
        <el-form-item label="Level">
          <el-input v-model="levelDialog.form.label" />
        </el-form-item>
        <el-form-item label="AI Assessment Scale">
          <el-input v-model="levelDialog.form.title" />
        </el-form-item>
        <el-form-item label="Instructions to Students">
          <el-input type="textarea" :rows="3" v-model="levelDialog.form.instructions" />
        </el-form-item>
        <el-form-item label="AI Acknowledgement">
          <el-input type="textarea" :rows="3" v-model="levelDialog.form.acknowledgement" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="levelDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="saveLevel">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/user';
import { useDataStore, type ScaleLevel, type ScaleVersion } from '@/store/data';

const dataStore = useDataStore();
const userStore = useUserStore();

onMounted(async () => {
  await dataStore.fetchScales();
});
const defaultScale = computed(() => dataStore.defaultScale);
const defaultLevels = ref<ScaleLevel[]>(
  (defaultScale.value?.currentVersion?.levels || []).map((level) => normalizeLevel(level)),
);

watch(defaultScale, (scale) => {
  const levels = scale?.currentVersion?.levels;
  if (levels) {
    defaultLevels.value = levels.map((level) => normalizeLevel(level));
  } else {
    defaultLevels.value = [];
  }
});

const canEditDefault = computed(() => userStore.role === 'admin' || userStore.role === 'sc');

function generateLevelId(seed: string) {
  const normalized = seed.trim().toLowerCase().replace(/\s+/g, '_') || 'level';
  return `level_${normalized}_${Math.random().toString(36).slice(2, 8)}`;
}

function normalizeLevel(seed: Partial<ScaleLevel> = {}): ScaleLevel {
  return {
    id: seed.id || generateLevelId('level'),
    label: seed.label || '',
    title: seed.title || '',
    instructions: seed.instructions ?? '',
    acknowledgement: seed.acknowledgement ?? '',
  };
}

const levelDialog = reactive({
  visible: false,
  isEdit: false,
  form: {
    id: generateLevelId('level'),
    label: '',
    title: '',
    instructions: '',
    acknowledgement: '',
  } as ScaleLevel,
});

function openLevelDialog(level: ScaleLevel | null) {
  levelDialog.visible = true;
  levelDialog.isEdit = !!level;
  levelDialog.form = normalizeLevel(level ? { ...level } : {});
}

function removeLevel(index: number) {
  if (!canEditDefault.value) return;
  defaultLevels.value.splice(index, 1);
}

function saveLevel() {
  const label = levelDialog.form.label.trim();
  if (!label) {
    ElMessage.error('Please enter a level key.');
    return;
  }
  const duplicate = defaultLevels.value.some((item) => item.label === label && item.id !== levelDialog.form.id);
  if (duplicate) {
    ElMessage.error('Level key already exists.');
    return;
  }
  const entry = normalizeLevel({
    ...levelDialog.form,
    label,
    id: levelDialog.form.id || generateLevelId(label),
  });
  const index = defaultLevels.value.findIndex((item) => item.id === entry.id);
  if (levelDialog.isEdit && index >= 0) {
    defaultLevels.value.splice(index, 1, entry);
  } else {
    defaultLevels.value.push(entry);
  }
  levelDialog.visible = false;
}

async function saveDefaultScale() {
  if (!canEditDefault.value) return;
  const targetScaleId = defaultScale.value?.id || 'system_default';
  await dataStore.saveScaleVersion(
    {
      scaleId: targetScaleId,
      levels: defaultLevels.value,
      updatedBy: userStore.userInfo?.name || userStore.userInfo?.username || 'Coordinator',
      notes: 'Updated default scale',
    },
    {
      ensureRecord: {
        name: 'Default Scale',
        ownerType: 'system',
        ownerId: 'system',
        isPublic: true,
      },
    },
  );
  ElMessage.success('Default scale saved as a new version.');
}

function rollbackScale(version: ScaleVersion) {
  if (!canEditDefault.value) return;
  const levels = version.levels?.length
    ? version.levels.map((level) => normalizeLevel(level))
    : [];
  if (!levels.length) {
    ElMessage.warning('No levels found in the selected version.');
    return;
  }
  defaultLevels.value = levels;
  ElMessage.success(`Loaded v${version.version} into the editor. Save to create a new version.`);
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
.scale-page { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px; }
.subtitle { color: #606266; margin: 4px 0 0; max-width: 520px; }
.content { margin-top: 4px; }
.panel { display: flex; flex-direction: column; gap: 16px; height: 100%; }
.panel-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.panel-meta { font-size: 12px; color: #909399; text-align: right; display: flex; flex-direction: column; gap: 4px; }
.history-card { min-height: 100%; }
.version-item { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.cell-text {
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
  max-width: 100%;
  min-height: 22px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.muted { color: #909399; font-size: 13px; }
.empty-message { padding: 24px 0; text-align: center; color: #909399; }
</style>
