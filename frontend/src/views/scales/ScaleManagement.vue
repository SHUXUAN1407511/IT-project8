<template>
  <div class="scale-page">
    <div class="page-header">
      <div>
        <h2>AI Use Scale Management</h2>
      </div>
      <el-space v-if="isAdmin" :size="8">
        <el-button
          type="primary"
          plain
          :disabled="!canEditDefault"
          @click="openLevelDialog('default', null)"
        >
          Add level
        </el-button>
        <el-button type="primary" :disabled="!canEditDefault" @click="saveScale('default')">
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
                <el-button
                  link
                  :disabled="!canEditDefault"
                  @click="openLevelDialog('default', row)"
                >
                  Edit
                </el-button>
                <el-button
                  link
                  type="danger"
                  :disabled="!canEditDefault"
                  @click="removeLevel('default', $index)"
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
          <div class="history-scroll">
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
                    :disabled="!(isAdmin || isSc)"
                    @click="cloneVersion(version, isAdmin ? 'default' : 'personal')"
                  >
                    Clone this version
                  </el-button>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
          <div v-if="!(defaultScale?.history?.length)" class="empty-message">No history yet</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row v-if="isSc" :gutter="16" class="content">
      <el-col :span="24" :lg="16">
        <el-card shadow="never" class="panel">
          <div class="panel-header">
            <h3>My scale levels</h3>
            <div class="panel-meta">
              <div>Last updated {{ formatDate(personalScale?.currentVersion?.updatedAt) }}</div>
              <div>By {{ personalScale?.currentVersion?.updatedBy || '—' }}</div>
            </div>
          </div>
          <el-space :size="8">
            <el-button type="primary" plain @click="openLevelDialog('personal', null)">
              Add level
            </el-button>
            <el-button type="primary" @click="saveScale('personal')">
              Save new version
            </el-button>
          </el-space>

          <el-table
            v-if="personalLevels.length"
            :data="personalLevels"
            border
            size="small"
            empty-text="No levels"
            class="mt-12"
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
                <el-button link @click="openLevelDialog('personal', row)">Edit</el-button>
                <el-button link type="danger" @click="removeLevel('personal', $index)">
                  Remove
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-else class="empty-message">
            <template v-if="personalScale">
              No levels configured. Click “Add level” to create your version.
            </template>
            <template v-else>
              You do not have a personalised scale yet. Modify the default levels and save to create one.
            </template>
          </div>
        </el-card>
      </el-col>

      <el-col :span="24" :lg="8">
        <el-card shadow="never" class="panel history-card">
          <div class="panel-header">
            <h3>My version history</h3>
          </div>
          <div class="history-scroll">
            <el-timeline>
              <el-timeline-item
                v-for="version in personalScale?.history || []"
                :key="version.id"
                :timestamp="formatDate(version.updatedAt)"
              >
                <div class="version-item">
                  <div>
                    <strong>v{{ version.version }}</strong>
                    <span class="muted"> · {{ version.updatedBy }}</span>
                    <p class="muted">{{ version.notes || 'No notes' }}</p>
                  </div>
                  <el-button size="small" @click="cloneVersion(version, 'personal')">
                    Use this version
                  </el-button>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
          <div v-if="!(personalScale?.history?.length)" class="empty-message">
            No personal history yet
          </div>
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

type ScaleScope = 'default' | 'personal';

const dataStore = useDataStore();
const userStore = useUserStore();

onMounted(async () => {
  await dataStore.fetchScales();
});

const normalizedRole = computed(() => {
  const candidates = [
    userStore.userInfo?.role,
    userStore.role,
  ];
  for (const role of candidates) {
    if (role) {
      return String(role).trim().toLowerCase();
    }
  }
  return '';
});

const isAdmin = computed(() => normalizedRole.value === 'admin');
const isSc = computed(() => normalizedRole.value === 'sc');
const defaultScale = computed(() => dataStore.defaultScale);
const personalScale = computed(() => {
  if (!isSc.value) return null;
  const candidates = new Set<string>();
  const username = userStore.userInfo?.username;
  const userId = userStore.userInfo?.id;
  if (username) candidates.add(String(username).trim());
  if (userId) candidates.add(String(userId).trim());
  if (!candidates.size) return null;

  return (
    dataStore.customScales.find((scale) => {
      const ownerId = String(scale.ownerId ?? '').trim();
      return ownerId && candidates.has(ownerId);
    }) || null
  );
});

const defaultLevels = ref<ScaleLevel[]>(
  (defaultScale.value?.currentVersion?.levels || []).map((level) => normalizeLevel(level)),
);
const personalLevels = ref<ScaleLevel[]>(
  (personalScale.value?.currentVersion?.levels || []).map((level) => normalizeLevel(level)),
);

watch(defaultScale, (scale) => {
  const levels = scale?.currentVersion?.levels;
  if (levels) {
    defaultLevels.value = levels.map((level) => normalizeLevel(level));
  } else {
    defaultLevels.value = [];
  }
});

watch(personalScale, (scale) => {
  const levels = scale?.currentVersion?.levels;
  if (levels) {
    personalLevels.value = levels.map((level) => normalizeLevel(level));
  } else {
    personalLevels.value = [];
  }
});

const canEditDefault = computed(() => isAdmin.value);
const canEditPersonal = computed(() => isSc.value);

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
  scope: 'default' as ScaleScope,
  form: {
    id: generateLevelId('level'),
    label: '',
    title: '',
    instructions: '',
    acknowledgement: '',
  } as ScaleLevel,
});

function targetLevels(scope: ScaleScope) {
  return scope === 'default' ? defaultLevels : personalLevels;
}

function openLevelDialog(scope: ScaleScope, level: ScaleLevel | null) {
  levelDialog.visible = true;
  levelDialog.isEdit = !!level;
  levelDialog.scope = scope;
  levelDialog.form = normalizeLevel(level ? { ...level } : {});
}

function removeLevel(scope: ScaleScope, index: number) {
  if (scope === 'default' && !canEditDefault.value) return;
  if (scope === 'personal' && !canEditPersonal.value) return;
  const buffer = targetLevels(scope);
  buffer.value.splice(index, 1);
}

function saveLevel() {
  const scope = levelDialog.scope;
  const editable = scope === 'default' ? canEditDefault.value : canEditPersonal.value;
  if (!editable) return;

  const label = levelDialog.form.label.trim();
  if (!label) {
    ElMessage.error('Please enter a level key.');
    return;
  }
  const buffer = targetLevels(scope);
  const duplicate = buffer.value.some(
    (item) => item.label === label && item.id !== levelDialog.form.id,
  );
  if (duplicate) {
    ElMessage.error('Level key already exists.');
    return;
  }
  const entry = normalizeLevel({
    ...levelDialog.form,
    label,
    id: levelDialog.form.id || generateLevelId(label),
  });
  const index = buffer.value.findIndex((item) => item.id === entry.id);
  if (levelDialog.isEdit && index >= 0) {
    buffer.value.splice(index, 1, entry);
  } else {
    buffer.value.push(entry);
  }
  levelDialog.visible = false;
}

async function saveScale(scope: ScaleScope) {
  if (scope === 'default') {
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
    return;
  }

  if (!canEditPersonal.value) return;
  const username = userStore.userInfo?.username || 'sc_user';
  const displayName = userStore.userInfo?.name || username;
  const targetScaleId = personalScale.value?.id || 'sc_personal';
  await dataStore.saveScaleVersion(
    {
      scaleId: targetScaleId,
      levels: personalLevels.value,
      updatedBy: displayName,
      notes: 'Updated personal scale',
    },
    {
      ensureRecord: {
        name: `${displayName}'s Scale`,
        ownerType: 'sc',
        ownerId: username,
        isPublic: false,
      },
    },
  );
  ElMessage.success('Your personal scale has been saved.');
}

function cloneVersion(version: ScaleVersion, scope: ScaleScope) {
  const editable = scope === 'default' ? canEditDefault.value : canEditPersonal.value;
  if (!editable) return;

  const levels = (version.levels || []).map((level) => normalizeLevel(level));
  if (!levels.length) {
    ElMessage.warning('No levels found in the selected version.');
    return;
  }
  const buffer = targetLevels(scope);
  buffer.value = levels;
  const label = scope === 'default' ? 'default' : 'personal';
  ElMessage.success(`Loaded v${version.version} into the ${label} editor. Save to create a new version.`);
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
.history-scroll {
  max-height: 240px;
  overflow-y: auto;
  padding-right: 6px;
}
.history-scroll::-webkit-scrollbar {
  width: 6px;
}
.history-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(144, 147, 153, 0.3);
  border-radius: 999px;
}
.history-scroll:hover::-webkit-scrollbar-thumb {
  background-color: rgba(144, 147, 153, 0.6);
}
.version-item { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.mt-12 { margin-top: 12px; }
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
