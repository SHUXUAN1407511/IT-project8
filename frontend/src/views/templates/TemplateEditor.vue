<template>
  <div class="template-page">
    <div class="page-header">
      <div>
        <h2>AI Use Declaration Template</h2>
        <p class="subtitle" v-if="assignment">{{ assignment.name }} · {{ courseLabel }}</p>
      </div>
      <el-space :size="8" wrap>
        <el-button
          type="primary"
          plain
          :disabled="!editableRows.length"
          @click="exportTemplate('pdf')"
        >
          Export PDF
        </el-button>
        <el-button
          type="primary"
          plain
          :disabled="!editableRows.length"
          @click="exportTemplate('xlsx')"
        >
          Export Excel
        </el-button>
        <el-button
          type="primary"
          :disabled="!canEdit || !editableRows.length"
          @click="saveTemplate(false)"
        >
          Save draft
        </el-button>
        <el-button
          type="success"
          :disabled="!canEdit || !editableRows.length"
          @click="saveTemplate(true)"
        >
          Publish template
        </el-button>
      </el-space>
    </div>

    <el-card class="filters" shadow="never">
      <div class="filter-row">
        <el-select
          v-model="selectedAssignmentId"
          placeholder="Choose assignment"
          filterable
          class="filter-item"
        >
          <el-option
            v-for="item in assignmentOptions"
            :key="item.id"
            :label="`${item.name} · ${item.course}`"
            :value="item.id"
          />
        </el-select>
        <el-select
          v-model="selectedScaleId"
          placeholder="Select AI Use Scale"
          class="filter-item"
          :disabled="!scaleOptions.length"
        >
          <el-option
            v-for="scale in scaleOptions"
            :key="scale.id"
            :label="scale.name"
            :value="scale.id"
          />
        </el-select>
      </div>
    </el-card>

    <el-card v-if="assignment" shadow="never" class="panel">
      <div class="table-toolbar">
        <el-space :size="4">
          <el-button type="primary" text :disabled="!canEdit" @click="addRow">Add row</el-button>
        </el-space>
      </div>
      <el-table
        :data="editableRows"
        empty-text="No rows yet — click Add row"
        row-key="id"
        border
        style="width: 100%"
      >
        <el-table-column label="Index" width="70">
          <template #default="{ $index }">
            <span>{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="General Learning or Assessment Tasks" min-width="240">
          <template #default="{ row }">
            <el-input
              v-model="row.task"
              type="textarea"
              :rows="3"
              :disabled="!canEdit"
            />
          </template>
        </el-table-column>
        <el-table-column label="AI Use Scale Level" width="220">
          <template #default="{ row }">
            <el-select
              v-model="row.levelId"
              :disabled="!canEdit"
              placeholder="Select level"
              @change="(val: string) => onLevelChange(row, val)"
            >
              <el-option
                v-for="level in levelOptions"
                :key="level.id"
                :label="`${level.label} · ${level.title}`"
                :value="level.id"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="Instructions to Students" min-width="260">
          <template #default="{ row }">
            <el-input
              v-model="row.instructions"
              type="textarea"
              :rows="3"
              :disabled="!canEdit"
            />
          </template>
        </el-table-column>
        <el-table-column label="Examples" min-width="260">
          <template #default="{ row }">
            <el-input
              v-model="row.examples"
              type="textarea"
              :rows="3"
              :disabled="!canEdit"
            />
          </template>
        </el-table-column>
        <el-table-column label="AI Generated Content in Submission" min-width="240">
          <template #default="{ row }">
            <el-input
              v-model="row.aiGeneratedContent"
              type="textarea"
              :rows="3"
              :disabled="!canEdit"
            />
          </template>
        </el-table-column>
        <el-table-column label="AI Use Acknowledgement" min-width="260">
          <template #default="{ row }">
            <el-input
              v-model="row.acknowledgement"
              type="textarea"
              :rows="3"
              :disabled="!canEdit"
            />
          </template>
        </el-table-column>
        <el-table-column label="Student Declaration (Please complete this section)">
          <el-table-column label="AI Tools Used (version and link if available)" min-width="220">
            <template #default="{ row }">
              <el-input
                v-model="row.toolsUsed"
                type="textarea"
                :rows="3"
                :disabled="!canEdit"
              />
            </template>
          </el-table-column>
          <el-table-column label="Purpose and Usage" min-width="220">
            <template #default="{ row }">
              <el-input
                v-model="row.purposeAndUsage"
                type="textarea"
                :rows="3"
                :disabled="!canEdit"
              />
            </template>
          </el-table-column>
          <el-table-column label="Key Prompts Used (if any)" min-width="220">
            <template #default="{ row }">
              <el-input
                v-model="row.keyPrompts"
                type="textarea"
                :rows="3"
                :disabled="!canEdit"
              />
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ $index }">
            <el-button
              link
              :disabled="!canEdit || $index === 0"
              @click="moveRow($index, -1)"
            >
              Move up
            </el-button>
            <el-button
              link
              :disabled="!canEdit || $index === editableRows.length - 1"
              @click="moveRow($index, 1)"
            >
              Move down
            </el-button>
            <el-button link type="danger" :disabled="!canEdit" @click="removeRow($index)">
              Remove
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/user';
import {
  useDataStore,
  type Assignment,
  type TemplateRow,
  type ScaleRecord,
} from '@/store/data';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const dataStore = useDataStore();

const selectedAssignmentId = ref<string>(route.params.assignmentId as string || '');

const assignmentOptions = computed(() => {
  if (userStore.role === 'admin') {
    return dataStore.assignments.map((assignment) => ({
      id: assignment.id,
      name: assignment.name,
      course: dataStore.courses.find((course) => course.id === assignment.courseId)?.name || '—',
    }));
  }
  if (userStore.role === 'sc') {
    const courseIds = dataStore.courses
      .filter((course) => course.scId === userStore.userInfo?.id)
      .map((course) => course.id);
    return dataStore.assignments
      .filter((assignment) => courseIds.includes(assignment.courseId))
      .map((assignment) => ({
        id: assignment.id,
        name: assignment.name,
        course: dataStore.courses.find((course) => course.id === assignment.courseId)?.name || '—',
      }));
  }
  if (userStore.role === 'tutor') {
    return dataStore.assignments
      .filter((assignment) => assignment.tutorIds.includes(userStore.userInfo?.id || ''))
      .map((assignment) => ({
        id: assignment.id,
        name: assignment.name,
        course: dataStore.courses.find((course) => course.id === assignment.courseId)?.name || '—',
      }));
  }
  return [];
});

watch(
  assignmentOptions,
  (options) => {
    if (!options.length) {
      selectedAssignmentId.value = '';
      return;
    }
    if (!selectedAssignmentId.value || !options.some((item) => item.id === selectedAssignmentId.value)) {
      selectedAssignmentId.value = options[0].id;
    }
  },
  { immediate: true }
);

const assignment = computed<Assignment | undefined>(() =>
  dataStore.assignments.find((item) => item.id === selectedAssignmentId.value)
);

const courseLabel = computed(() => {
  if (!assignment.value) return '';
  const course = dataStore.courses.find((c) => c.id === assignment.value?.courseId);
  return course ? `${course.name} · ${course.term}` : '';
});

const editableRows = ref<TemplateRow[]>([]);

const templateRecord = computed(() =>
  dataStore.templateByAssignment(selectedAssignmentId.value)
);

const scaleOptions = computed<ScaleRecord[]>(() => {
  const options: ScaleRecord[] = [];
  const defaultScale = dataStore.defaultScale;
  if (defaultScale) {
    options.push(defaultScale);
  }
  dataStore.customScales.forEach((scale) => {
    const isOwner = scale.ownerId === userStore.userInfo?.id;
    if (scale.isPublic || isOwner || userStore.role === 'admin') {
      options.push(scale);
    }
  });
  return options;
});

const selectedScaleId = ref('');

function findScaleById(id: string) {
  return scaleOptions.value.find((scale) => scale.id === id);
}

function findScaleContainingLevel(levelId: string) {
  return scaleOptions.value.find((scale) =>
    scale.currentVersion.levels.some((level) => level.id === levelId)
  );
}

const levelOptions = computed(() => findScaleById(selectedScaleId.value)?.currentVersion.levels || []);

watch(
  () => route.params.assignmentId,
  (val) => {
    if (typeof val === 'string') {
      selectedAssignmentId.value = val;
      hydrateTemplate();
    }
  }
);

watch(selectedAssignmentId, (id) => {
  if (id) {
    if (route.params.assignmentId !== id) {
      router.replace({ name: 'TemplateEditor', params: { assignmentId: id } });
    }
    void dataStore.refreshTemplate(id);
  } else if (route.path !== '/templates') {
    router.replace({ path: '/templates' });
  }
  hydrateTemplate();
});

watch(scaleOptions, (options) => {
  if (!options.length) {
    selectedScaleId.value = '';
    return;
  }
  if (!selectedScaleId.value || !findScaleById(selectedScaleId.value)) {
    selectedScaleId.value = options[0].id;
  }
});

watch(selectedScaleId, () => {
  syncRowsWithScale();
});

function hydrateTemplate() {
  if (!assignment.value) {
    editableRows.value = [];
    selectedScaleId.value = scaleOptions.value[0]?.id || '';
    return;
  }
  const record = templateRecord.value;
  if (record) {
    editableRows.value = record.rows.map((row) => withRowDefaults(row));
    const matchedScale = record.rows
      .map((row) => findScaleContainingLevel(row.levelId))
      .find((scale): scale is ScaleRecord => !!scale);
    if (matchedScale) {
      selectedScaleId.value = matchedScale.id;
    }
  } else {
    selectedScaleId.value = scaleOptions.value[0]?.id || '';
    editableRows.value = [];
  }
  syncRowsWithScale();
}

onMounted(async () => {
  await Promise.allSettled([
    dataStore.fetchCourses(),
    dataStore.fetchAssignments(),
    dataStore.fetchUsers(),
    dataStore.fetchScales(),
  ]);
  if (selectedAssignmentId.value) {
    await dataStore.refreshTemplate(selectedAssignmentId.value);
  }
  hydrateTemplate();
});

watch(templateRecord, (record) => {
  if (record) {
    editableRows.value = record.rows.map((row) => withRowDefaults(row));
  } else if (!assignment.value) {
    editableRows.value = [];
  }
  syncRowsWithScale();
});

const canEdit = computed(() => {
  if (!assignment.value) return false;
  if (!userStore.isAuthenticated) return false;
  if (userStore.role === 'admin') return true;
  if (userStore.role === 'sc') {
    return assignment.value && dataStore.courses.find((c) => c.id === assignment.value?.courseId)?.scId === userStore.userInfo?.id;
  }
  if (userStore.role === 'tutor') {
    return assignment.value.tutorIds.includes(userStore.userInfo?.id || '');
  }
  return false;
});

function addRow() {
  const defaultLevel = levelOptions.value[0];
  if (!defaultLevel) {
    ElMessage.warning('The selected scale has no available levels yet.');
    return;
  }
  editableRows.value.push(
    withRowDefaults({
      id: generateRowId(),
      levelId: defaultLevel.id,
      levelLabel: defaultLevel.label,
      instructions: defaultLevel.instructions ?? '',
      acknowledgement: defaultLevel.acknowledgement ?? '',
    }),
  );
}

function removeRow(index: number) {
  editableRows.value.splice(index, 1);
}

function moveRow(index: number, step: number) {
  const targetIndex = index + step;
  if (targetIndex < 0 || targetIndex >= editableRows.value.length) return;
  const [row] = editableRows.value.splice(index, 1);
  editableRows.value.splice(targetIndex, 0, row);
}

function onLevelChange(row: TemplateRow, levelId: string) {
  const level = findLevel(levelId);
  if (!level) return;
  row.levelLabel = level.label;
  row.instructions = level.instructions ?? '';
  row.acknowledgement = level.acknowledgement ?? '';
}

function syncRowsWithScale() {
  if (!levelOptions.value.length || !editableRows.value.length) return;
  editableRows.value.forEach((row) => {
    const match = findLevel(row.levelId);
    if (match) {
      row.levelLabel = match.label;
      return;
    }
    const fallback = levelOptions.value[0];
    if (!fallback) return;
    row.levelId = fallback.id;
    row.levelLabel = fallback.label;
    row.instructions = fallback.instructions ?? '';
    row.acknowledgement = fallback.acknowledgement ?? '';
  });
}

function findLevel(levelId?: string) {
  if (!levelId) return levelOptions.value[0];
  return levelOptions.value.find((item) => item.id === levelId) || levelOptions.value[0];
}

function withRowDefaults(seed: Partial<TemplateRow>): TemplateRow {
  const level = findLevel(seed.levelId);
  const levelLabel = level?.label ?? seed.levelLabel ?? '';
  const legacy = seed as TemplateRow & { additionalNotes?: string };
  return {
    id: seed.id || generateRowId(),
    task: seed.task ?? '',
    levelId: level?.id || '',
    levelLabel,
    instructions: seed.instructions ?? level?.instructions ?? '',
    acknowledgement: seed.acknowledgement ?? level?.acknowledgement ?? '',
    examples: seed.examples ?? '',
    aiGeneratedContent: seed.aiGeneratedContent ?? legacy.additionalNotes ?? '',
    toolsUsed: seed.toolsUsed ?? '',
    purposeAndUsage: seed.purposeAndUsage ?? '',
    keyPrompts: seed.keyPrompts ?? '',
  };
}

async function saveTemplate(publish: boolean) {
  if (!assignment.value || !userStore.userInfo) {
    ElMessage.error('Assignment or user info is missing.');
    return;
  }
  if (!editableRows.value.length) {
    ElMessage.warning('Please add at least one declaration row.');
    return;
  }
  await dataStore.saveTemplate(assignment.value.id, {
    rows: editableRows.value,
    updatedBy: userStore.userInfo.name,
    publish,
  });
  ElMessage.success(publish ? 'Template published.' : 'Draft saved.');
  if (publish) {
    router.replace({ name: 'TemplateEditor', params: { assignmentId: assignment.value.id } });
  }
}

function exportTemplate(format: 'pdf' | 'xlsx') {
  if (!editableRows.value.length) return;
  const label = format === 'pdf' ? 'PDF' : 'Excel';
  ElMessage.info(`Generating ${label} export (demo only).`);
}

function generateRowId() {
  return `row_${Math.random().toString(36).slice(2, 10)}`;
}
</script>

<style scoped>
.template-page { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
.subtitle { margin: 4px 0 0; color: #606266; font-size: 14px; }
.filters { padding: 12px 16px; }
.filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.filter-item { width: 280px; }
.panel { display: flex; flex-direction: column; gap: 16px; }
.label { color: #606266; font-size: 13px; margin-right: 4px; }
.table-toolbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.legend { font-size: 13px; color: #606266; display: flex; gap: 8px; align-items: center; }
.mt-6 { margin-top: 6px; }
</style>
