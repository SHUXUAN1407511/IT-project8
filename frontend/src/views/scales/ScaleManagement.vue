<template>
  <div class="scale-page">
    <h2>AI Use Scale Management</h2>

    <el-row :gutter="16">
      <el-col :span="24" :lg="12">
        <el-card shadow="never" class="panel">
          <div class="panel-header">
            <h3>Default scale</h3>
            <el-button class="outlined-button" :disabled="!canEditDefault" @click="saveDefaultScale">
              Save new version
            </el-button>
          </div>

          <el-table
            v-if="defaultLevels.length"
            :data="defaultLevels"
            border
            size="small"
            empty-text="No levels"
          >
            <el-table-column prop="label" label="Level" width="80" />
            <el-table-column prop="title" label="Title" min-width="120" />
            <el-table-column prop="description" label="Description" min-width="160" show-overflow-tooltip />
            <el-table-column label="Instructions" min-width="220">
              <template #default="{ row }">
                <el-input
                  v-model="row.instructions"
                  :disabled="!canEditDefault"
                  type="textarea"
                  :rows="3"
                />
              </template>
            </el-table-column>
            <el-table-column label="Acknowledgement" min-width="220">
              <template #default="{ row }">
                <el-input
                  v-model="row.acknowledgement"
                  :disabled="!canEditDefault"
                  type="textarea"
                  :rows="3"
                />
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="120" fixed="right">
              <template #default="{ row, $index }">
                <el-button link :disabled="!canEditDefault" @click="openLevelDialog(row)">Edit</el-button>
                <el-button
                  link
                  type="danger"
                  :disabled="!canEditDefault || defaultLevels.length <= 1"
                  @click="removeLevel($index)"
                >
                  Remove
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="panel-footer">
            <el-button class="outlined-button" :disabled="!canEditDefault" @click="saveDefaultScale">
              Add level
            </el-button>
            <span class="updated-at">Latest version: {{ formatDate(defaultScale?.currentVersion.updatedAt) }}</span>
          </div>

          <el-divider />

          <h4>Version history</h4>
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
                <el-button
                  size="small"
                  :disabled="!canEditDefault"
                  @click="rollbackScale(defaultScale?.id || '', version.id)"
                >
                  Clone this version
                </el-button>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

    </el-row>

    <el-dialog v-model="levelDialog.visible" title="Edit scale level" width="520px">
      <el-form :model="levelDialog.form" label-width="96px">
        <el-form-item label="Level key">
          <el-input v-model="levelDialog.form.label" :disabled="levelDialog.isEdit" />
        </el-form-item>
        <el-form-item label="Title">
          <el-input v-model="levelDialog.form.title" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input type="textarea" :rows="2" v-model="levelDialog.form.description" />
        </el-form-item>
        <el-form-item label="Instructions">
          <el-input type="textarea" :rows="3" v-model="levelDialog.form.instructions" />
        </el-form-item>
        <el-form-item label="Acknowledgement">
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
import { computed, reactive, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/user';
import { useDataStore, type ScaleLevel } from '@/store/data';

const dataStore = useDataStore();
const userStore = useUserStore();

const defaultScale = computed(() => dataStore.defaultScale);
const defaultLevels = ref<ScaleLevel[]>(defaultScale.value ? defaultScale.value.currentVersion.levels.map((level) => ({ ...level })) : []);

watch(defaultScale, (scale) => {
  if (scale) {
    defaultLevels.value = scale.currentVersion.levels.map((level) => ({ ...level }));
  }
});

const canEditDefault = computed(() => userStore.role === 'admin');

function generateLevelId(seed: string) {
  const normalized = seed.trim().toLowerCase().replace(/\s+/g, '_') || 'level';
  return `level_${normalized}_${Math.random().toString(36).slice(2, 8)}`;
}

const levelDialog = reactive({
  visible: false,
  isEdit: false,
  form: {
    id: generateLevelId('level'),
    label: '',
    title: '',
    description: '',
    instructions: '',
    acknowledgement: '',
  } as ScaleLevel,
});

function openLevelDialog(level: ScaleLevel | null) {
  levelDialog.visible = true;
  levelDialog.isEdit = !!level;
  levelDialog.form = level
    ? { ...level }
    : {
        id: generateLevelId('level'),
        label: '',
        title: '',
        description: '',
        instructions: '',
        acknowledgement: '',
      };
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
  const entry: ScaleLevel = {
    ...levelDialog.form,
    label,
    id: levelDialog.form.id || generateLevelId(label),
  };
  const index = defaultLevels.value.findIndex((item) => item.id === entry.id);
  if (levelDialog.isEdit && index >= 0) {
    defaultLevels.value.splice(index, 1, entry);
  } else {
    defaultLevels.value.push(entry);
  }
  levelDialog.visible = false;
}

function saveDefaultScale() {
  if (!canEditDefault.value || !defaultScale.value) return;
  dataStore.saveScaleVersion(defaultScale.value.id, defaultLevels.value, userStore.userInfo?.name || 'Admin', 'Updated default scale');
  ElMessage.success('Default scale saved as a new version.');
}

function rollbackScale(scaleId: string, versionId: string) {
  if (!canEditDefault.value) return;
  dataStore.rollbackScale(scaleId, versionId, userStore.userInfo?.name || 'Admin');
  const latest = dataStore.scales.find((scale) => scale.id === scaleId);
  if (latest && scaleId === defaultScale.value?.id) {
    defaultLevels.value = latest.currentVersion.levels.map((level) => ({ ...level }));
  }
  ElMessage.success('New version cloned from history.');
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
.scale-page { display: flex; flex-direction: column; gap: 16px; }
.panel { display: flex; flex-direction: column; gap: 12px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.panel-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 8px; }
.updated-at { color: #909399; font-size: 13px; }
.version-item { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.muted { color: #909399; font-size: 13px; }
.empty-message { margin: 12px 0; padding: 12px; border: 1px dashed #ccc; background: #fff; text-align: center; color: #666; }
.outlined-button { border: 1px solid #222; background: #fff; color: #222; }
.outlined-button:hover,
.outlined-button:focus { background: #f5f5f5; border-color: #111; color: #111; }
.outlined-button:disabled { border-color: #ccc; color: #bbb; background: #fafafa; }
.text-button { color: #222; font-weight: 500; }
.text-button:disabled { color: #bbb; }
</style>
