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
            :label="scaleDisplayName(scale)"
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/useUserStore';
import API, { type ExportFormat, type ExportTablePayload } from '@/services/api';
import { logger } from '@/utils/logger';
import {
  useDataStore,
  type Assignment,
  type TemplateRow,
  type ScaleRecord,
  type ScaleLevel,
} from '@/store/useDataStore';

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
    if (!targetId) {
      return '';
    }
    const course = courses.find((item) => asString(item.id) === targetId);
    return course?.name || '';
  };

  const resolveCourseName = (assignment: Assignment) => {
    if (assignment.courseName) {
      return assignment.courseName;
    }
    return courseNameById(assignment.courseId) || '—';
  };

  if (userStore.role === 'admin') {
    return assignments.map((assignment) => {
      const id = asString(assignment.id);
      return {
        id,
        name: assignment.name,
        course: resolveCourseName(assignment),
      };
    });
  }

  if (userStore.role === 'sc') {
    const userId = asString(userStore.userInfo?.id);
    const courseIds = courses
      .filter((course) => asString(course.coordinatorId) === userId)
      .map((course) => asString(course.id));

    return assignments
      .filter((assignment) => courseIds.includes(asString(assignment.courseId)))
      .map((assignment) => {
        const id = asString(assignment.id);
        return {
          id,
          name: assignment.name,
          course: resolveCourseName(assignment),
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
          course: resolveCourseName(assignment),
        };
      });
  }

  return [];
});

const hasAssignmentAccess = (assignmentId: string | null | undefined) => {
  if (!assignmentId) {
    return false;
  }
  return assignmentOptions.value.some((option) => option.id === assignmentId);
};

function handleInaccessibleAssignment(notify = false) {
  initialRouteAssignmentId.value = '';
  if (selectedAssignmentId.value) {
    selectedAssignmentId.value = '';
  }
  if (!userStore.isAuthenticated) {
    router.replace({ name: 'Login' });
    return;
  }
  if (notify) {
    ElMessage.warning('You do not have access to that template.');
  }
  const fallbackRoute =
    userStore.role === 'tutor'
      ? { name: 'AssignmentManagement' }
      : { path: '/templates' };
  router.replace(fallbackRoute);
}

watch(
  assignmentOptions,
  (options) => {
    if (!options.length) {
      if (assignmentsLoaded.value) {
        handleInaccessibleAssignment(assignmentsLoaded.value && !!selectedAssignmentId.value);
      } else {
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
  if (!targetId) {
    return undefined;
  }
  return dataStore.assignments.find((item) => asString(item.id) === targetId);
});

const coordinatorOwnerIds = computed(() => {
  const ids = new Set<string>();
  const currentAssignment = assignment.value;
  if (!currentAssignment) {
    return [];
  }
  const courseId = asString(currentAssignment.courseId);
  const course = dataStore.courses.find((c) => asString(c.id) === courseId);
  if (!course) {
    return [];
  }

  const courseCoordinatorId = asString(course.coordinatorId);
  if (courseCoordinatorId) {
    ids.add(courseCoordinatorId);
  }

  const scUser = dataStore.users.find((user) => asString(user.id) === courseCoordinatorId);
  if (scUser?.username) {
    ids.add(scUser.username);
  }

  return Array.from(ids).filter(
    (value): value is string => typeof value === 'string' && value.length > 0,
  );
});

const courseLabel = computed(() => {
  if (!assignment.value) {
    return '';
  }
  const courseId = asString(assignment.value.courseId);
  const course = dataStore.courses.find((c) => asString(c.id) === courseId);
  return course ? `${course.name} · ${course.term}` : '';
});

const editableRows = ref<TemplateRow[]>([]);
const isExporting = ref(false);

const templateRecord = computed(() =>
  dataStore.templateByAssignment(selectedAssignmentId.value)
);

const templateFingerprint = computed(() => rowsFingerprint(templateRecord.value?.rows));
const editableFingerprint = computed(() => rowsFingerprint(editableRows.value));
const hasLocalChanges = computed(() => editableFingerprint.value !== templateFingerprint.value);

const scaleOptions = computed<ScaleRecord[]>(() => {
  const options: ScaleRecord[] = [];
  const defaultScale = dataStore.defaultScale;
  if (defaultScale) {
    options.push(defaultScale);
  }

  const userId = asString(userStore.userInfo?.id);
  const username = userStore.userInfo?.username || '';
  const ownerCandidates = new Set<string>();
  if (userId) ownerCandidates.add(userId);
  if (username) ownerCandidates.add(username);
  coordinatorOwnerIds.value.forEach((id) => ownerCandidates.add(id));

  dataStore.customScales.forEach((scale) => {
    const ownerId = asString(scale.ownerId);
    const ownerMatches = ownerCandidates.has(ownerId);
    const canUse = scale.isPublic || ownerMatches || userStore.role === 'admin';
    if (canUse) {
      options.push(scale);
    }
  });

  return options;
});

const scaleDisplayName = (scale: ScaleRecord) => {
  const ownerId = asString(scale.ownerId);
  const isCoordinatorOwner =
    scale.ownerType === 'sc' && coordinatorOwnerIds.value.includes(ownerId);
  if (isCoordinatorOwner) {
    return 'sc-default scale';
  }
  return scale.name;
};

const selectedScaleId = ref('');
const persistedScaleId = ref('');
const isHydrating = ref(false);

const sameId = (a: unknown, b: unknown) => asString(a) === asString(b);
const hasNonEmptyText = (value: unknown) =>
  typeof value === 'string' ? value.trim().length > 0 : !!value;

const fingerprintRow = (row: TemplateRow) => ({
  id: row.id,
  task: row.task ?? '',
  levelId: row.levelId ?? '',
  instructions: row.instructions ?? '',
  acknowledgement: row.acknowledgement ?? '',
  examples: row.examples ?? '',
  aiGeneratedContent: row.aiGeneratedContent ?? '',
  toolsUsed: row.toolsUsed ?? '',
  purposeAndUsage: row.purposeAndUsage ?? '',
  keyPrompts: row.keyPrompts ?? '',
});

const rowsFingerprint = (rows: TemplateRow[] | undefined | null) =>
  JSON.stringify((rows || []).map((row) => fingerprintRow(row)));

function readLevelInstructions(level: Partial<TemplateRow> | ScaleLevel | undefined | null) {
  if (!level) {
    return '';
  }
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
  if (!level) {
    return '';
  }
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

function findScaleContainingLevel(levelId: string, source?: ScaleRecord[]) {
  const candidates = source ?? scaleOptions.value;
  return candidates.find((scale) =>
    scale.currentVersion?.levels?.some((level) => sameId(level.id, levelId)),
  );
}

function scaleLevelIds(scale?: ScaleRecord | null) {
  return new Set((scale?.currentVersion?.levels || []).map((level) => level.id));
}

function isScaleCompatibleWithRows(
  scaleId: string | null | undefined,
  rows: TemplateRow[] | undefined | null,
) {
  if (!scaleId || !rows) {
    return false;
  }
  const scale = findScaleById(scaleId);
  if (!scale) {
    return false;
  }
  const ids = scaleLevelIds(scale);
  if (!ids.size) {
    return false;
  }
  return rows.every((row) => !row.levelId || ids.has(row.levelId));
}

function inferScaleIdForRows(rows: TemplateRow[] | undefined | null) {
  const dataset = Array.isArray(rows) ? rows : editableRows.value;
  const persisted = persistedScaleId.value;
  const persistedValid = persisted && findScaleById(persisted) ? persisted : '';
  const current = selectedScaleId.value;
  const currentValid = current && findScaleById(current) ? current : '';

  if (!Array.isArray(dataset) || !dataset.length) {
    return (
      persistedValid ||
      currentValid ||
      scaleOptions.value[0]?.id ||
      ''
    );
  }

  const candidates: string[] = [];
  if (persistedValid) {
    candidates.push(persistedValid);
  }
  if (currentValid && currentValid !== persistedValid) {
    candidates.push(currentValid);
  }
  scaleOptions.value.forEach((scale) => {
    if (!candidates.includes(scale.id)) {
      candidates.push(scale.id);
    }
  });

  for (const candidate of candidates) {
    if (isScaleCompatibleWithRows(candidate, dataset)) {
      return candidate;
    }
  }

  const partial = scaleOptions.value.find((scale) => {
    const ids = scaleLevelIds(scale);
    return dataset.some((row) => row.levelId && ids.has(row.levelId));
  });
  return partial?.id || candidates[0] || '';
}

const levelOptions = computed(
  () => findScaleById(selectedScaleId.value)?.currentVersion?.levels || [],
);

const canEdit = computed(() => {
  if (!assignment.value) {
    return false;
  }
  if (!userStore.isAuthenticated) {
    return false;
  }
  if (userStore.role === 'admin') {
    return true;
  }
  if (userStore.role === 'sc') {
    const course = dataStore.courses.find(
      (c) => asString(c.id) === asString(assignment.value?.courseId)
    );
    return course?.coordinatorId === asString(userStore.userInfo?.id);
  }
  if (userStore.role === 'tutor') {
    const tutorId = asString(userStore.userInfo?.id);
    return Array.isArray(assignment.value.tutorIds)
      ? assignment.value.tutorIds.map((value) => asString(value)).includes(tutorId)
      : false;
  }
  return false;
});

const AUTO_REFRESH_INTERVAL = 15000;
let templateSyncTimer: ReturnType<typeof setInterval> | null = null;

function stopTemplateSync() {
  if (templateSyncTimer) {
    clearInterval(templateSyncTimer);
    templateSyncTimer = null;
  }
}

async function triggerTemplateRefresh() {
  const assignmentId = selectedAssignmentId.value;
  if (!assignmentId || hasLocalChanges.value) {
    return;
  }
  try {
    const latest = await dataStore.refreshTemplate(assignmentId);
    const incomingFingerprint = rowsFingerprint(latest?.rows);
    if (incomingFingerprint !== templateFingerprint.value) {
      return;
    }
  } catch (error) {
    logger.warn('[TemplateEditor] Failed to refresh template:', error);
  }
}

function startTemplateSync() {
  if (templateSyncTimer || !selectedAssignmentId.value) {
    return;
  }
  templateSyncTimer = setInterval(() => {
    void triggerTemplateRefresh();
  }, AUTO_REFRESH_INTERVAL);
}

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
    if (!hasAssignmentAccess(id) && assignmentsLoaded.value) {
      handleInaccessibleAssignment(assignmentsLoaded.value);
      return;
    }
    if (asString(route.params.assignmentId) !== id) {
      router.replace({
        name: 'TemplateEditor',
        params: { assignmentId: id },
      });
    }
    if (assignmentsLoaded.value) {
      void dataStore.refreshTemplate(id);
    }
  } else if (route.path !== '/templates') {
    const fallbackRoute =
      userStore.role === 'tutor'
        ? { name: 'AssignmentManagement' }
        : { path: '/templates' };
    router.replace(fallbackRoute);
  }
  hydrateTemplate();
});

watch(scaleOptions, (options) => {
  if (!options.length) {
    selectedScaleId.value = '';
    persistedScaleId.value = '';
    return;
  }

  const rows = templateRecord.value?.rows || editableRows.value;
  const inferred = inferScaleIdForRows(rows as TemplateRow[]);

  if (inferred) {
    if (inferred !== selectedScaleId.value) {
      isHydrating.value = true;
      selectedScaleId.value = inferred;
      isHydrating.value = false;
    }
    persistedScaleId.value = inferred;
    return;
  }

  if (!selectedScaleId.value || !findScaleById(selectedScaleId.value)) {
    const fallback = options[0]?.id;
    if (fallback) {
      isHydrating.value = true;
      selectedScaleId.value = fallback;
      isHydrating.value = false;
      persistedScaleId.value = fallback;
    }
  }
});

watch(
  selectedScaleId,
  (newVal, oldVal) => {
    const allowFallback = !isHydrating.value && !!oldVal && newVal !== oldVal;
    if (newVal && findScaleById(newVal)) {
      persistedScaleId.value = newVal;
    } else if (!newVal) {
      persistedScaleId.value = '';
    }
    syncRowsWithScale({ allowFallback });
  }
);

watch(
  levelOptions,
  () => {
    syncRowsWithScale({ allowFallback: false });
  },
  { deep: true }
);

function hydrateTemplate() {
  isHydrating.value = true;
  if (!assignment.value) {
    editableRows.value = [];
    isHydrating.value = false;
    return;
  }
  const record = templateRecord.value;
  const candidateScaleId = inferScaleIdForRows(record?.rows || []);
  if (candidateScaleId) {
    selectedScaleId.value = candidateScaleId;
    persistedScaleId.value = candidateScaleId;
  } else if (!selectedScaleId.value && scaleOptions.value.length) {
    selectedScaleId.value = scaleOptions.value[0].id;
    persistedScaleId.value = scaleOptions.value[0].id;
  }

  if (record) {
    editableRows.value = record.rows.map((row) => withRowDefaults(row));
  } else {
    editableRows.value = [];
  }

  isHydrating.value = false;
  syncRowsWithScale({ allowFallback: false });
}

onMounted(async () => {
  await Promise.allSettled([
    dataStore.fetchCourses(),
    dataStore.fetchAssignments(),
    dataStore.fetchUsers(),
    dataStore.fetchScales(),
  ]);
  assignmentsLoaded.value = true;
  if (selectedAssignmentId.value && hasAssignmentAccess(selectedAssignmentId.value)) {
    await dataStore.refreshTemplate(selectedAssignmentId.value);
  } else if (!hasAssignmentAccess(selectedAssignmentId.value)) {
    handleInaccessibleAssignment(!!selectedAssignmentId.value);
  }
  hydrateTemplate();
});

watch(templateRecord, (record) => {
  isHydrating.value = true;
  const rows = record?.rows || [];
  const targetScaleId = inferScaleIdForRows(rows as TemplateRow[]);
  if (targetScaleId) {
    selectedScaleId.value = targetScaleId;
    persistedScaleId.value = targetScaleId;
  } else if (!selectedScaleId.value && scaleOptions.value.length) {
    const fallback = scaleOptions.value[0].id;
    selectedScaleId.value = fallback;
    persistedScaleId.value = fallback;
  }

  if (record) {
    editableRows.value = record.rows.map((row) => withRowDefaults(row));
  } else {
    editableRows.value = [];
  }

  isHydrating.value = false;
  syncRowsWithScale({ allowFallback: false });
});

watch(
  [selectedAssignmentId, canEdit],
  ([assignmentId, editable]) => {
    stopTemplateSync();
    if (assignmentId && editable) {
      startTemplateSync();
    }
  },
  { immediate: true }
);

onBeforeUnmount(() => {
  stopTemplateSync();
});

function addRow() {
  const defaultLevel = findLevel(undefined, { allowFallback: true });
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
  if (targetIndex < 0 || targetIndex >= editableRows.value.length) {
    return;
  }
  const [row] = editableRows.value.splice(index, 1);
  editableRows.value.splice(targetIndex, 0, row);
}

function onLevelChange(row: TemplateRow, levelId: string) {
  const level = findLevel(levelId, { allowFallback: true });
  if (!level) {
    return;
  }
  row.levelLabel = level.label;
  row.instructions = readLevelInstructions(level);
  row.acknowledgement = readLevelAcknowledgement(level);
}

type SyncOptions = { allowFallback?: boolean };

function syncRowsWithScale(options: SyncOptions = {}) {
  const allowFallback = !!options.allowFallback;
  if (!levelOptions.value.length || !editableRows.value.length) {
    return;
  }
  editableRows.value.forEach((row) => {
    const match = findLevel(row.levelId, { allowFallback: false });
    if (match) {
      row.levelLabel = match.label;
      row.instructions = readLevelInstructions(match);
      row.acknowledgement = readLevelAcknowledgement(match);
      return;
    }
    if (!allowFallback) {
      return;
    }
    const fallback = findLevel(undefined, { allowFallback: true });
    if (!fallback) {
      return;
    }
    row.levelId = fallback.id;
    row.levelLabel = fallback.label;
    row.instructions = readLevelInstructions(fallback);
    row.acknowledgement = readLevelAcknowledgement(fallback);
  });
}

type FindLevelOptions = { allowFallback?: boolean };

function findLevel(levelId?: string, options: FindLevelOptions = {}) {
  const allowFallback = options.allowFallback !== false;
  if (!levelId) {
    return allowFallback ? levelOptions.value[0] : undefined;
  }
  const match = levelOptions.value.find((item) => sameId(item.id, levelId));
  if (match) {
    return match;
  }
  return allowFallback ? levelOptions.value[0] : undefined;
}

function withRowDefaults(seed: Partial<TemplateRow>): TemplateRow {
  const level = findLevel(seed.levelId, { allowFallback: false });
  const levelLabel = level?.label ?? seed.levelLabel ?? '';
  const legacy = seed as TemplateRow & { additionalNotes?: string };
  return {
    id: seed.id || generateRowId(),
    task: seed.task ?? '',
    levelId: level?.id || (seed.levelId ?? ''),
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
  const actorId = asString(userStore.userInfo.id);
  const actorName = userStore.userInfo.name || userStore.userInfo.username || '';
  await dataStore.saveTemplate(targetAssignmentId, {
    rows: editableRows.value,
    updatedBy: actorName,
    updatedById: actorId,
    publish,
  });
  ElMessage.success(publish ? 'Template published.' : 'Draft saved.');
  if (publish) {
    router.replace({ name: 'TemplateEditor', params: { assignmentId: targetAssignmentId } });
  }
}

interface ExportColumn {
  label: string;
  pick(row: TemplateRow, index: number): string;
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

function buildExportRequestPayload(): ExportTablePayload | null {
  const currentAssignment = assignment.value;
  if (!currentAssignment) {
    return null;
  }
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
    const blob = await API.exporter.download(format, payload);
    const filename = buildExportFilename(format, now);
    triggerDownload(blob, filename);
    ElMessage.success(successMessage);
  } catch (error) {
    logger.error(`Failed to export template ${format}:`, error);
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
.template-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.subtitle {
  margin: 4px 0 0;
  color: #606266;
  font-size: 14px;
}
.filters {
  padding: 12px 16px;
}
.filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}
.filter-item {
  width: 280px;
}
.filter-empty {
  padding: 4px 0;
  color: #909399;
  font-size: 14px;
}
.panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.label {
  color: #606266;
  font-size: 13px;
  margin-right: 4px;
}
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.legend {
  font-size: 13px;
  color: #606266;
  display: flex;
  gap: 8px;
  align-items: center;
}
.mt-6 {
  margin-top: 6px;
}
.readonly-area :deep(.el-textarea__inner) {
  background-color: #f5f7fa;
  color: #606266;
  border-color: transparent;
  box-shadow: none;
  cursor: default;
}
</style>
