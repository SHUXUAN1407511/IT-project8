import { defineStore } from 'pinia';
import { useUserStore } from '@/store/useUserStore';
import { appConfig } from '@/config';
import { logger } from '@/utils/logger';
import API, {
  type AccountStatus,
  type Assignment,
  type AssignmentFilters,
  type AssignmentType,
  type Course,
  type CourseFilters,
  type CreateAssignmentRequest,
  type CreateCourseRequest,
  type CreateManagedUserRequest,
  type DeclarationStatus,
  type ManagedUser,
  type NotificationItem,
  type SaveScaleVersionRequest,
  type ScaleLevel,
  type ScaleRecord,
  type ScaleVersion,
  type SaveTemplateRequest,
  type TemplateRecord,
  type TemplateRow,
  type UpdateAssignmentRequest,
  type UpdateCourseRequest,
  type UpdateManagedUserRequest,
  type UserRole,
} from '@/services/api';

const ASSIGNMENT_TYPES_STORAGE_KEY = 'assignmentTypes';

const sanitizeAssignmentTypes = (types: unknown, fallback: string[]): AssignmentType[] => {
  if (!Array.isArray(types)) {
    return [...fallback] as AssignmentType[];
  }
  const normalized = types
    .map((item) => (typeof item === 'string' ? item.trim() : ''))
    .filter((item) => item.length > 0);
  const unique = Array.from(new Set(normalized));
  if (!unique.length) {
    return [...fallback] as AssignmentType[];
  }
  return unique as AssignmentType[];
};

const loadAssignmentTypes = (): AssignmentType[] => {
  if (typeof window === 'undefined') {
    return [...appConfig.assignmentTypes] as AssignmentType[];
  }
  try {
    const stored = window.localStorage.getItem(ASSIGNMENT_TYPES_STORAGE_KEY);
    if (!stored) {
      return [...appConfig.assignmentTypes] as AssignmentType[];
    }
    const parsed = JSON.parse(stored);
    return sanitizeAssignmentTypes(parsed, appConfig.assignmentTypes);
  } catch (error) {
    logger.warn('[dataStore] Failed to load assignment types from storage:', error);
    return [...appConfig.assignmentTypes] as AssignmentType[];
  }
};

type TemplateCache = Record<string, TemplateRecord | null>;

const LEVEL_INSTRUCTION_KEYS = [
  'instructions',
  'instructionsToStudents',
  'studentInstructions',
  'instructions_students',
  'instruction',
  'description',
];

const LEVEL_ACKNOWLEDGEMENT_KEYS = [
  'acknowledgement',
  'aiAcknowledgement',
  'aiAcknowledgment',
  'acknowledgementText',
  'acknowledgements',
  'acknowledgment',
];

const hasNonEmptyText = (value: unknown): value is string =>
  typeof value === 'string' && value.trim().length > 0;

function extractLevelField(
  level: ScaleLevel | Record<string, unknown>,
  candidateKeys: string[],
): string {
  const record = level as Record<string, unknown>;
  for (const key of candidateKeys) {
    if (hasNonEmptyText(record[key])) {
      return String(record[key]);
    }
  }
  return '';
}

function normalizeScaleLevel(level: ScaleLevel): ScaleLevel {
  return {
    ...level,
    instructions: extractLevelField(level, LEVEL_INSTRUCTION_KEYS),
    acknowledgement: extractLevelField(level, LEVEL_ACKNOWLEDGEMENT_KEYS),
  };
}

function extractArray<T>(input: unknown, keys: string[] = []): T[] {
  if (Array.isArray(input)) {
    return input as T[];
  }
  if (input && typeof input === 'object') {
    for (const key of keys) {
      const value = (input as Record<string, unknown>)[key];
      if (Array.isArray(value)) {
        return value as T[];
      }
    }
  }
  return [];
}

export const useDataStore = defineStore('data', {
  state: () => ({
    courses: [] as Course[],
    assignments: [] as Assignment[],
    assignmentTypes: loadAssignmentTypes(),
    templateCache: {} as TemplateCache,
    scales: [] as ScaleRecord[],
    notifications: [] as NotificationItem[],
    users: [] as ManagedUser[],
  }),
  getters: {
    defaultScale(state) {
      return state.scales.find((scale) => scale.ownerType === 'system');
    },
    customScales(state) {
      return state.scales.filter((scale) => scale.ownerType === 'sc');
    },
    tutors(state) {
      const arr = Array.isArray(state.users) ? state.users : [];
      return arr.filter((user) => user.role === 'tutor' && user.status === 'active');
    },
    coordinators(state) {
      const arr = Array.isArray(state.users) ? state.users : [];
      return arr.filter((user) => user.role === 'sc' && user.status === 'active');
    },
    templateByAssignment: (state) =>
      (assignmentId: string) => state.templateCache[assignmentId] || null,
  },
  actions: {
    setAssignmentTypes(types: AssignmentType[]) {
      const sanitized = sanitizeAssignmentTypes(types, appConfig.assignmentTypes);
      this.assignmentTypes = sanitized;
      if (typeof window !== 'undefined') {
        try {
          window.localStorage.setItem(
            ASSIGNMENT_TYPES_STORAGE_KEY,
            JSON.stringify(this.assignmentTypes),
          );
        } catch (error) {
          logger.warn('[dataStore] Failed to persist assignment types:', error);
        }
      }
    },
    resetAssignmentTypes() {
      this.setAssignmentTypes([...appConfig.assignmentTypes] as AssignmentType[]);
    },

    async fetchCourses(filters?: CourseFilters) {
      const d = (await API.courses.list(filters)) as Course[] | Record<string, unknown>;
      this.courses = extractArray<Course>(d, ['courses', 'results']);
      return this.courses;
    },
    async addCourse(payload: CreateCourseRequest) {
      const course = (await API.courses.create(payload)) as Course;
      this.upsertCourse(course);
      return course;
    },
    async updateCourse(id: string, payload: UpdateCourseRequest) {
      const course = (await API.courses.update(id, payload)) as Course;
      this.upsertCourse(course);
      return course;
    },
    async deleteCourse(id: string) {
      await API.courses.remove(id);
      this.courses = this.courses.filter((course) => course.id !== id);
      const remainingCourseIds = new Set(this.courses.map((course) => course.id));
      this.assignments = this.assignments.filter((assignment) => {
        const keep = remainingCourseIds.has(assignment.courseId);
        if (!keep) {
          delete this.templateCache[assignment.id];
        }
        return keep;
      });
    },

    async fetchAssignments(filters?: AssignmentFilters) {
      const d = (await API.assignments.list(filters)) as Assignment[] | Record<string, unknown>;
      this.assignments = extractArray<Assignment>(d, ['assignments', 'results']);
      this.pruneTemplateCache(new Set(this.assignments.map((assignment) => assignment.id)));
      return this.assignments;
    },
    async fetchAssignment(id: string) {
      const assignment = (await API.assignments.get(id)) as Assignment;
      this.upsertAssignment(assignment);
      return assignment;
    },
    async addAssignment(payload: CreateAssignmentRequest) {
      const userStore = useUserStore();
      const role = (userStore.role || userStore.userInfo?.role || '').toString().toLowerCase();
      if (!['admin', 'sc'].includes(role)) {
        logger.warn('[dataStore] addAssignment ignored for role:', role || 'unknown');
        throw new Error('You do not have permission to create assignments.');
      }
      const assignment = (await API.assignments.create(payload)) as Assignment;
      this.upsertAssignment(assignment);
      return assignment;
    },
    async updateAssignment(id: string, payload: UpdateAssignmentRequest) {
      const userStore = useUserStore();
      const role = (userStore.role || userStore.userInfo?.role || '').toString().toLowerCase();
      if (!['admin', 'sc'].includes(role)) {
        logger.warn(
          '[dataStore] updateAssignment ignored for role:',
          role || 'unknown',
        );
        throw new Error('You do not have permission to update assignments.');
      }
      const assignment = (await API.assignments.update(id, payload)) as Assignment;
      this.upsertAssignment(assignment);
      return assignment;
    },
    async deleteAssignment(id: string) {
      const userStore = useUserStore();
      const role = (userStore.role || userStore.userInfo?.role || '').toString().toLowerCase();
      if (!['admin', 'sc'].includes(role)) {
        logger.warn(
          '[dataStore] deleteAssignment ignored for role:',
          role || 'unknown',
        );
        throw new Error('You do not have permission to delete assignments.');
      }
      await API.assignments.remove(id);
      this.assignments = this.assignments.filter((assignment) => assignment.id !== id);
      delete this.templateCache[id];
    },

    async fetchTemplate(assignmentId: string) {
      const template = (await API.templates.getByAssignment(assignmentId)) as TemplateRecord;
      this.templateCache[assignmentId] = template;
      return template;
    },
    async saveTemplate(
      assignmentId: string,
      payload: Omit<SaveTemplateRequest, 'assignmentId'> & {
        updatedBy?: string;
        updatedById?: string;
      },
    ) {
      const template = (await API.templates.save(assignmentId, {
        assignmentId,
        rows: payload.rows,
        publish: payload.publish,
        updatedBy: payload.updatedBy,
        updatedById: payload.updatedById,
      })) as TemplateRecord;
      this.templateCache[assignmentId] = {
        ...template,
        updatedBy: payload.updatedBy ?? template.updatedBy,
      };
      await this.fetchAssignment(assignmentId);
      return this.templateCache[assignmentId];
    },
    async publishTemplate(
      assignmentId: string,
      payload?: { updatedBy?: string; updatedById?: string },
    ) {
      await API.templates.publish(assignmentId, payload);
      return this.refreshTemplate(assignmentId);
    },
    async unpublishTemplate(assignmentId: string) {
      await API.templates.unpublish(assignmentId);
      return this.refreshTemplate(assignmentId);
    },
    async refreshTemplate(assignmentId: string) {
      try {
        const template = (await API.templates.getByAssignment(
          assignmentId,
        )) as TemplateRecord;
        this.templateCache[assignmentId] = template;
      } catch (error) {
        this.templateCache[assignmentId] = null;
      }
      await this.fetchAssignment(assignmentId);
      return this.templateCache[assignmentId];
    },

    async fetchScales(params?: { ownerType?: string; ownerId?: string }) {
      const response = (await API.scaleRecords.list(params)) as
        | ScaleRecord[]
        | { results?: ScaleRecord[] };
      let items: ScaleRecord[] = [];
      if (Array.isArray(response)) {
        items = response;
      } else if (Array.isArray(response.results)) {
        items = response.results ?? [];
      }

      const normalizeVersion = (version: ScaleVersion | null | undefined): ScaleVersion | null => {
        if (!version) {
          return null;
        }
        return {
          ...version,
          levels: (version.levels || []).map((level) => normalizeScaleLevel(level)),
        };
      };

      this.scales = items.map((record) => {
        const currentVersion = normalizeVersion(record.currentVersion);
        const history = (record.history || [])
          .map((entry: ScaleVersion | null | undefined) => normalizeVersion(entry))
          .filter((entry): entry is ScaleVersion => !!entry);
        return {
          ...record,
          currentVersion,
          history,
        };
      });

      return this.scales;
    },
    async ensureScaleRecord(options: {
      name: string;
      ownerType: 'system' | 'sc';
      ownerId?: string;
      isPublic?: boolean;
    }) {
      const record = (await API.scaleRecords.create({
        name: options.name,
        ownerType: options.ownerType,
        ownerId: options.ownerId,
        isPublic: options.isPublic ?? (options.ownerType === 'system'),
      })) as ScaleRecord;
      await this.fetchScales({
        ownerType: options.ownerType,
        ownerId: options.ownerId,
      });
      return record;
    },
    async saveScaleVersion(
      payload: SaveScaleVersionRequest & { updatedBy?: string; updatedById?: string },
      options?: {
        ensureRecord?: {
          name: string;
          ownerType: 'system' | 'sc';
          ownerId?: string;
          isPublic?: boolean;
        };
      },
    ) {
      const userStore = useUserStore();
      const role = (userStore.role || userStore.userInfo?.role || '').toString().toLowerCase();
      if (!['admin', 'sc'].includes(role)) {
        logger.warn('[dataStore] saveScaleVersion denied for role:', role || 'unknown');
        throw new Error('You do not have permission to modify AI use scales.');
      }

      const safeLevels = payload.levels.map((level) => normalizeScaleLevel(level));

      try {
        let targetScaleId = payload.scaleId;
        if (
          options?.ensureRecord &&
          (
            !targetScaleId ||
            targetScaleId === 'system_default' ||
            !this.scales.find((scale) => scale.id === targetScaleId)
          )
        ) {
          const record = await this.ensureScaleRecord(options.ensureRecord);
          targetScaleId = record.id;
        }

        await API.scaleRecords.saveVersion({
          ...payload,
          scaleId: targetScaleId,
          levels: safeLevels.map((level) => ({
            id: level.id,
            label: level.label,
            title: level.title,
            instructions: level.instructions,
            acknowledgement: level.acknowledgement,
          })),
          updatedById: payload.updatedById,
        });
        const records = await this.fetchScales();
        return records.find((scale) => scale.id === targetScaleId);
      } catch (error) {
        logger.warn(
          '[dataStore] Failed to save scale version via scale-records API:',
          error,
        );
        throw error;
      }
    },

    async fetchNotifications() {
      const notifications = (await API.notifications.list()) as NotificationItem[];
      this.notifications = notifications;
      return notifications;
    },
    async markNotificationRead(id: string) {
      await API.notifications.markRead(id);
      this.notifications = this.notifications.map((notice) =>
        notice.id === id ? { ...notice, isRead: true } : notice
      );
    },
    async markAllNotificationsRead() {
      await API.notifications.markAllRead();
      this.notifications = this.notifications.map((notice) => ({ ...notice, isRead: true }));
    },

    async fetchUsers() {
      const d = (await API.adminUsers.list()) as ManagedUser[] | Record<string, unknown>;
      this.users = extractArray<ManagedUser>(d, ['users', 'results']);
      return this.users;
    },
    async createUser(payload: CreateManagedUserRequest) {
      const user = (await API.adminUsers.create(payload)) as ManagedUser;
      this.upsertUser(user);
      return user;
    },
    async updateUser(id: string, updates: UpdateManagedUserRequest) {
      const user = (await API.adminUsers.update(id, updates)) as ManagedUser;
      this.upsertUser(user);
      return user;
    },
    async toggleUserStatus(id: string, status: AccountStatus) {
      const user = (await API.adminUsers.toggleStatus(id, status)) as ManagedUser;
      this.upsertUser(user);
      return user;
    },

    upsertCourse(course: Course) {
      const index = this.courses.findIndex((item) => item.id === course.id);
      if (index >= 0) this.courses.splice(index, 1, course);
      else this.courses.push(course);
    },
    upsertAssignment(assignment: Assignment) {
      const index = this.assignments.findIndex((item) => item.id === assignment.id);
      if (index >= 0) this.assignments.splice(index, 1, assignment);
      else this.assignments.push(assignment);
    },
    upsertScale(scale: ScaleRecord) {
      const index = this.scales.findIndex((item) => item.id === scale.id);
      if (index >= 0) this.scales.splice(index, 1, scale);
      else this.scales.push(scale);
    },
    upsertUser(user: ManagedUser) {
      const index = this.users.findIndex((item) => item.id === user.id);
      if (index >= 0) this.users.splice(index, 1, user);
      else this.users.push(user);
    },
    pruneTemplateCache(validAssignmentIds: Set<string>) {
      Object.keys(this.templateCache).forEach((assignmentId) => {
        if (!validAssignmentIds.has(assignmentId)) {
          delete this.templateCache[assignmentId];
        }
      });
    },
  },
});

export type {
  Course,
  Assignment,
  AssignmentType,
  AssignmentFilters,
  DeclarationStatus,
  TemplateRecord,
  TemplateRow,
  ScaleRecord,
  ScaleLevel,
  NotificationItem,
  ManagedUser,
  UserRole,
} from '@/services/api';
