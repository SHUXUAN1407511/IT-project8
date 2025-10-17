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
          :disabled="isExporting || !editableRows.length"
          :loading="isExporting"
          @click="exportTemplate('pdf')"
        >
          Export PDF
        </el-button>
        <el-button
          type="primary"
          plain
          :disabled="isExporting || !editableRows.length"
          :loading="isExporting"
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
      <div v-if="assignment" class="filter-row">
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
      <div v-else-if="assignmentsLoaded" class="filter-empty">
        No assignment selected. Use "Manage template" from an assignment to open its template.
      </div>
      <div v-else class="filter-empty">Loading assignment...</div>
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
              readonly
              class="readonly-area"
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
              readonly
              class="readonly-area"
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
import http from '@/services/http';
import {
  useDataStore,
  type Assignment,
  type TemplateRow,
  type ScaleRecord,
  type ScaleLevel,
} from '@/store/data';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const dataStore = useDataStore();

const asString = (value: unknown) => (value === undefined || value === null ? '' : String(value));

const initialRouteAssignmentId = ref(
  typeof route.params.assignmentId === 'string' ? (route.params.assignmentId as string) : ''
);
const selectedAssignmentId = ref<string>(initialRouteAssignmentId.value);
const assignmentsLoaded = ref(false);

const assignmentOptions = computed(() => {
  const assignments = Array.isArray(dataStore.assignments) ? dataStore.assignments : [];
  const courses = Array.isArray(dataStore.courses) ? dataStore.courses : [];

  const courseNameById = (courseId: unknown) => {
    const targetId = asString(courseId);
    if (!targetId) return '—';
    const course = courses.find((item) => asString(item.id) === targetId);
    return course?.name || '—';
  };

  if (userStore.role === 'admin') {
    return assignments.map((assignment) => {
      const id = asString(assignment.id);
      return {
        id,
        name: assignment.name,
        course: courseNameById(assignment.courseId),
      };
    });
  }

  if (userStore.role === 'sc') {
    const userId = asString(userStore.userInfo?.id);
    const courseIds = courses
      .filter((course) => asString(course.scId) === userId)
      .map((course) => asString(course.id));

    return assignments
      .filter((assignment) => courseIds.includes(asString(assignment.courseId)))
      .map((assignment) => {
        const id = asString(assignment.id);
        return {
          id,
          name: assignment.name,
          course: courseNameById(assignment.courseId),
        };
      });
  }

  if (userStore.role === 'tutor') {
    const tutorId = asString(userStore.userInfo?.id);
    return assignments
      .filter(
        (assignment) =>
          Array.isArray(assignment.tutorIds) &&
          assignment.tutorIds.map((value) => asString(value)).includes(tutorId)
      )
      .map((assignment) => {
        const id = asString(assignment.id);
        return {
          id,
          name: assignment.name,
          course: courseNameById(assignment.courseId),
        };
      });
  }

  return [];
});

watch(
  assignmentOptions,
  (options) => {
    if (!options.length) {
      if (assignmentsLoaded.value) {
        initialRouteAssignmentId.value = '';
        selectedAssignmentId.value = '';
      }
      return;
    }
    const currentId = selectedAssignmentId.value;
    if (currentId && options.some((item) => item.id === currentId)) {
      return;
    }
    const initialId = initialRouteAssignmentId.value;
    if (initialId && options.some((item) => item.id === initialId)) {
      selectedAssignmentId.value = initialId;
      return;
    }
    selectedAssignmentId.value = options[0].id;
  },
  { immediate: true }
);

const assignment = computed<Assignment | undefined>(() => {
  const targetId = selectedAssignmentId.value;
  if (!targetId) return undefined;
  return dataStore.assignments.find((item) => asString(item.id) === targetId);
});

const courseLabel = computed(() => {
  if (!assignment.value) return '';
  const courseId = asString(assignment.value.courseId);
  const course = dataStore.courses.find((c) => asString(c.id) === courseId);
  return course ? `${course.name} · ${course.term}` : '';
});

const editableRows = ref<TemplateRow[]>([]);
const isExporting = ref(false);

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

const sameId = (a: unknown, b: unknown) => asString(a) === asString(b);
const hasNonEmptyText = (value: unknown) =>
  typeof value === 'string' ? value.trim().length > 0 : !!value;

function readLevelInstructions(level: Partial<TemplateRow> | ScaleLevel | undefined | null) {
  if (!level) return '';
  const candidates = [
    (level as ScaleLevel).instructions,
    (level as Record<string, unknown>)?.instructionsToStudents,
    (level as Record<string, unknown>)?.studentInstructions,
    (level as Record<string, unknown>)?.instructions_students,
    (level as Record<string, unknown>)?.instruction,
    (level as Record<string, unknown>)?.description,
  ];
  for (const candidate of candidates) {
    if (hasNonEmptyText(candidate)) {
      return String(candidate);
    }
  }
  return '';
}

function readLevelAcknowledgement(level: Partial<TemplateRow> | ScaleLevel | undefined | null) {
  if (!level) return '';
  const candidates = [
    (level as ScaleLevel).acknowledgement,
    (level as Record<string, unknown>)?.acknowledgementText,
    (level as Record<string, unknown>)?.acknowledgment,
    (level as Record<string, unknown>)?.acknowledgements,
    (level as Record<string, unknown>)?.aiAcknowledgement,
    (level as Record<string, unknown>)?.aiAcknowledgment,
  ];
  for (const candidate of candidates) {
    if (hasNonEmptyText(candidate)) {
      return String(candidate);
    }
  }
  return '';
}

function findScaleById(id: string) {
  return scaleOptions.value.find((scale) => sameId(scale.id, id));
}

function findScaleContainingLevel(levelId: string) {
  return scaleOptions.value.find((scale) =>
    scale.currentVersion?.levels?.some((level) => sameId(level.id, levelId)),
  );
}

const levelOptions = computed(
  () => findScaleById(selectedScaleId.value)?.currentVersion?.levels || [],
);

watch(
  () => route.params.assignmentId,
  (val) => {
    if (val === undefined || val === null || val === '') {
      initialRouteAssignmentId.value = '';
      return;
    }
    const normalized = asString(val);
    initialRouteAssignmentId.value = normalized;
    selectedAssignmentId.value = normalized;
  }
);

watch(selectedAssignmentId, (id) => {
  if (id) {
    if (asString(route.params.assignmentId) !== id) {
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

watch(
  levelOptions,
  () => {
    syncRowsWithScale();
  },
  { deep: true }
);

function hydrateTemplate() {
  if (!assignment.value) {
    editableRows.value = [];
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
  assignmentsLoaded.value = true;
  if (selectedAssignmentId.value) {
    await dataStore.refreshTemplate(selectedAssignmentId.value);
  }
  hydrateTemplate();
});

watch(templateRecord, (record) => {
  if (record) {
    editableRows.value = record.rows.map((row) => withRowDefaults(row));
  } else {
    editableRows.value = [];
  }
  syncRowsWithScale();
});

const canEdit = computed(() => {
  if (!assignment.value) return false;
  if (!userStore.isAuthenticated) return false;
  if (userStore.role === 'admin') return true;
  if (userStore.role === 'sc') {
    const course = dataStore.courses.find(
      (c) => asString(c.id) === asString(assignment.value?.courseId)
    );
    return course?.scId === asString(userStore.userInfo?.id);
  }
  if (userStore.role === 'tutor') {
    const tutorId = asString(userStore.userInfo?.id);
    return Array.isArray(assignment.value.tutorIds)
      ? assignment.value.tutorIds.map((value) => asString(value)).includes(tutorId)
      : false;
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
      instructions: readLevelInstructions(defaultLevel),
      acknowledgement: readLevelAcknowledgement(defaultLevel),
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
  row.instructions = readLevelInstructions(level);
  row.acknowledgement = readLevelAcknowledgement(level);
}

function syncRowsWithScale() {
  if (!levelOptions.value.length || !editableRows.value.length) return;
  editableRows.value.forEach((row) => {
    const match = findLevel(row.levelId);
    if (match) {
      row.levelLabel = match.label;
      row.instructions = readLevelInstructions(match);
      row.acknowledgement = readLevelAcknowledgement(match);
      return;
    }
    const fallback = levelOptions.value[0];
    if (!fallback) return;
    row.levelId = fallback.id;
    row.levelLabel = fallback.label;
    row.instructions = readLevelInstructions(fallback);
    row.acknowledgement = readLevelAcknowledgement(fallback);
  });
}

function findLevel(levelId?: string) {
  if (!levelId) return levelOptions.value[0];
  return levelOptions.value.find((item) => sameId(item.id, levelId)) || levelOptions.value[0];
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
    instructions:
      hasNonEmptyText(seed.instructions) || !level
        ? seed.instructions ?? ''
        : readLevelInstructions(level),
    acknowledgement:
      hasNonEmptyText(seed.acknowledgement) || !level
        ? seed.acknowledgement ?? ''
        : readLevelAcknowledgement(level),
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
  const targetAssignmentId = asString(assignment.value.id);
  if (!targetAssignmentId) {
    ElMessage.error('Assignment information is incomplete.');
    return;
  }
  await dataStore.saveTemplate(targetAssignmentId, {
    rows: editableRows.value,
    updatedBy: userStore.userInfo.name,
    publish,
  });
  ElMessage.success(publish ? 'Template published.' : 'Draft saved.');
  if (publish) {
    router.replace({ name: 'TemplateEditor', params: { assignmentId: targetAssignmentId } });
  }
}

type ExportFormat = 'pdf' | 'xlsx';

interface ExportColumn {
  label: string;
  pick(row: TemplateRow, index: number): string;
}

interface ExportRequestPayload {
  title: string;
  data: Record<string, string[]>;
}

function buildExportFilename(extension: ExportFormat, timestamp: Date) {
  const rawAssignmentName = assignment.value?.name ?? 'template';
  const safeAssignmentName = rawAssignmentName
    .normalize('NFKC')
    .replace(/[\\/:*?"<>|]+/g, '')
    .replace(/\s+/g, '_');
  const fileDate = timestamp.toISOString().slice(0, 10);
  return `ai_template_${safeAssignmentName}_${fileDate}.${extension}`;
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function buildExportTitle() {
  const titleParts = ['AI Use Declaration Template'];
  if (assignment.value?.name) {
    titleParts.push(assignment.value.name);
  }
  if (courseLabel.value) {
    titleParts.push(courseLabel.value);
  }
  return titleParts.join(' - ').slice(0, 200);
}

function exportColumns(): ExportColumn[] {
  return [
    {
      label: 'Index',
      pick(_row, index) {
        return String(index + 1);
      },
    },
    {
      label: 'Task',
      pick(row) {
        return row.task ?? '';
      },
    },
    {
      label: 'Scale Level',
      pick(row) {
        return row.levelLabel ?? '';
      },
    },
    {
      label: 'Instructions',
      pick(row) {
        return row.instructions ?? '';
      },
    },
    {
      label: 'Examples',
      pick(row) {
        return row.examples ?? '';
      },
    },
    {
      label: 'AI Generated Content',
      pick(row) {
        return row.aiGeneratedContent ?? '';
      },
    },
    {
      label: 'Acknowledgement',
      pick(row) {
        return row.acknowledgement ?? '';
      },
    },
    {
      label: 'Tools Used',
      pick(row) {
        return row.toolsUsed ?? '';
      },
    },
    {
      label: 'Purpose & Usage',
      pick(row) {
        return row.purposeAndUsage ?? '';
      },
    },
    {
      label: 'Key Prompts',
      pick(row) {
        return row.keyPrompts ?? '';
      },
    },
  ];
}

function buildExportRequestPayload(): ExportRequestPayload | null {
  const currentAssignment = assignment.value;
  if (!currentAssignment) return null;
  const columns = exportColumns();
  const rows = editableRows.value;

  const dataEntries = columns.map(({ label, pick }) => {
    const values = rows.map((row, index) => pick(row, index));
    return [label, values] as const;
  });

  return {
    title: buildExportTitle(),
    data: Object.fromEntries(dataEntries),
  };
}

async function exportTemplate(format: ExportFormat) {
  if (!editableRows.value.length) {
    ElMessage.warning('Please add at least one declaration row.');
    return;
  }
  if (!assignment.value) {
    ElMessage.error('Assignment information is missing.');
    return;
  }
  if (isExporting.value) {
    return;
  }

  const now = new Date();
  const payload = buildExportRequestPayload();
  if (!payload) {
    ElMessage.error('Unable to prepare export payload.');
    return;
  }

  const endpoint = format === 'pdf' ? '/export/pdf/' : '/export/excel/';
  const successMessage =
    format === 'pdf'
      ? 'PDF export ready for download.'
      : 'Excel export ready for download.';
  const errorMessage =
    format === 'pdf'
      ? 'Failed to generate PDF export.'
      : 'Failed to generate Excel export.';

  try {
    isExporting.value = true;
    const blob = await http.post<Blob>(endpoint, payload, {
      responseType: 'blob',
    });
    const filename = buildExportFilename(format, now);
    triggerDownload(blob, filename);
    ElMessage.success(successMessage);
  } catch (error) {
    console.error(`Failed to export template ${format}:`, error);
    ElMessage.error(errorMessage);
  } finally {
    isExporting.value = false;
  }
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
.filter-empty { padding: 4px 0; color: #909399; font-size: 14px; }
.panel { display: flex; flex-direction: column; gap: 16px; }
.label { color: #606266; font-size: 13px; margin-right: 4px; }
.table-toolbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.legend { font-size: 13px; color: #606266; display: flex; gap: 8px; align-items: center; }
.mt-6 { margin-top: 6px; }
.readonly-area :deep(.el-textarea__inner) {
  background-color: #f5f7fa;
  color: #606266;
  border-color: transparent;
  box-shadow: none;
  cursor: default;
}
</style>
