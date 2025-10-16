import { defineStore } from 'pinia';
import { useUserStore } from '@/store/user';
import { appConfig } from '@/config';
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
  type AIUserScale,
  type PaginatedResponse,
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
    console.warn('[dataStore] Failed to load assignment types from storage:', error);
    return [...appConfig.assignmentTypes] as AssignmentType[];
  }
};

type TemplateCache = Record<string, TemplateRecord | null>;

const DEFAULT_SCALE_ID = 'system_default';

interface NormalizedScaleResult {
  records: ScaleRecord[];
  index: Record<string, AIUserScale>;
  membership: Record<string, string[]>;
}

function toScaleLevel(item: AIUserScale): ScaleLevel {
  const label = (item.level || '').trim() || (item.name || '').trim() || `Level ${item.id}`;
  const title = (item.name || '').trim() || label;
  return {
    id: String(item.id),
    label,
    title,
    description: '',
    aiUsage: '',
    instructions: '',
    acknowledgement: (item.notes || '').trim() || '',
  };
}

function pickLatestTimestamp(items: AIUserScale[]): string {
  const timestamps = items
    .map((item) => item.updated_at || item.created_at)
    .filter((value): value is string => !!value);
  if (!timestamps.length) {
    return new Date().toISOString();
  }
  return timestamps.reduce((latest, current) => (current > latest ? current : latest));
}

function normalizeAiUserScales(items: AIUserScale[]): NormalizedScaleResult {
  const index: Record<string, AIUserScale> = {};
  const membership: Record<string, string[]> = {};
  if (!items.length) {
    return { records: [], index, membership };
  }

  items.forEach((item) => {
    index[String(item.id)] = item;
  });

  const levels = items
    .slice()
    .sort((a, b) => a.id - b.id)
    .map(toScaleLevel);

  membership[DEFAULT_SCALE_ID] = levels.map((level) => level.id);

  const username = items[0]?.username || 'system';
  const normalized: ScaleRecord = {
    id: DEFAULT_SCALE_ID,
    name: 'Default Scale',
    ownerType: 'system',
    ownerId: username,
    isPublic: true,
    currentVersion: {
      id: `${DEFAULT_SCALE_ID}_current`,
      version: 1,
      updatedAt: pickLatestTimestamp(items),
      updatedBy: username,
      notes: '',
      levels,
    },
    history: [],
  };

  return {
    records: [normalized],
    index,
    membership,
  };
}

export const useDataStore = defineStore('data', {
  state: () => ({
    courses: [] as Course[],
    assignments: [] as Assignment[],
    assignmentTypes: loadAssignmentTypes(),
    templateCache: {} as TemplateCache,
    scales: [] as ScaleRecord[],
    scaleIndex: {} as Record<string, AIUserScale>,
    scaleMembership: {} as Record<string, string[]>,
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
    templateByAssignment: (state) => (assignmentId: string) => state.templateCache[assignmentId] || null,
  },
  actions: {
    setAssignmentTypes(types: AssignmentType[]) {
      const sanitized = sanitizeAssignmentTypes(types, appConfig.assignmentTypes);
      this.assignmentTypes = sanitized;
      if (typeof window !== 'undefined') {
        try {
          window.localStorage.setItem(ASSIGNMENT_TYPES_STORAGE_KEY, JSON.stringify(this.assignmentTypes));
        } catch (error) {
          console.warn('[dataStore] Failed to persist assignment types:', error);
        }
      }
    },
    resetAssignmentTypes() {
      this.setAssignmentTypes([...appConfig.assignmentTypes] as AssignmentType[]);
    },

    async fetchCourses(filters?: CourseFilters) {
      const d = await API.courses.list(filters);
      this.courses = Array.isArray(d) ? d
                    : Array.isArray(d?.courses) ? d.courses
                    : Array.isArray(d?.results) ? d.results
                    : [];
      return this.courses;
    },
    async addCourse(payload: CreateCourseRequest) {
      const course = await API.courses.create(payload);
      this.upsertCourse(course);
      return course;
    },
    async updateCourse(id: string, payload: UpdateCourseRequest) {
      const course = await API.courses.update(id, payload);
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
      const d = await API.assignments.list(filters);
      this.assignments = Array.isArray(d) ? d
                      : Array.isArray(d?.assignments) ? d.assignments
                      : Array.isArray(d?.results) ? d.results
                      : [];
      this.pruneTemplateCache(new Set(this.assignments.map((assignment) => assignment.id)));
      return this.assignments;
    },
    async fetchAssignment(id: string) {
      const assignment = await API.assignments.get(id);
      this.upsertAssignment(assignment);
      return assignment;
    },
    async addAssignment(payload: CreateAssignmentRequest) {
      const assignment = await API.assignments.create(payload);
      this.upsertAssignment(assignment);
      return assignment;
    },
    async updateAssignment(id: string, payload: UpdateAssignmentRequest) {
      const assignment = await API.assignments.update(id, payload);
      this.upsertAssignment(assignment);
      return assignment;
    },
    async deleteAssignment(id: string) {
      await API.assignments.remove(id);
      this.assignments = this.assignments.filter((assignment) => assignment.id !== id);
      delete this.templateCache[id];
    },

    async fetchTemplate(assignmentId: string) {
      const template = await API.templates.getByAssignment(assignmentId);
      this.templateCache[assignmentId] = template;
      return template;
    },
    async saveTemplate(
      assignmentId: string,
      payload: Omit<SaveTemplateRequest, 'assignmentId'> & { updatedBy?: string }
    ) {
      const template = await API.templates.save(assignmentId, {
        assignmentId,
        rows: payload.rows,
        publish: payload.publish,
      });
      this.templateCache[assignmentId] = {
        ...template,
        updatedBy: payload.updatedBy ?? template.updatedBy,
      };
      await this.fetchAssignment(assignmentId);
      return this.templateCache[assignmentId];
    },
    async publishTemplate(assignmentId: string) {
      await API.templates.publish(assignmentId);
      return this.refreshTemplate(assignmentId);
    },
    async unpublishTemplate(assignmentId: string) {
      await API.templates.unpublish(assignmentId);
      return this.refreshTemplate(assignmentId);
    },
    async refreshTemplate(assignmentId: string) {
      try {
        const template = await API.templates.getByAssignment(assignmentId);
        this.templateCache[assignmentId] = template;
      } catch (error) {
        this.templateCache[assignmentId] = null;
      }
      await this.fetchAssignment(assignmentId);
      return this.templateCache[assignmentId];
    },

    async fetchScales(params?: { username?: string }) {
      const response = await API.scales.list(params);
      const paged = Array.isArray(response) ? null : (response as PaginatedResponse<AIUserScale>);
      const items = Array.isArray(response)
        ? response
        : Array.isArray(paged?.results)
          ? paged?.results ?? []
          : [];
      const normalized = normalizeAiUserScales(items);
      this.scales = normalized.records;
      this.scaleIndex = normalized.index;
      this.scaleMembership = normalized.membership;
      return this.scales;
    },
    async saveScaleVersion(payload: SaveScaleVersionRequest & { updatedBy?: string }) {
      const userStore = useUserStore();
      const fallbackUsername =
        userStore.userInfo?.username || localStorage.getItem('username') || 'system';

      const membership = new Set(this.scaleMembership[payload.scaleId] || []);
      const seen = new Set<string>();

      const createTasks: Promise<unknown>[] = [];
      const updateTasks: Promise<unknown>[] = [];

      payload.levels.forEach((level) => {
        const rawId = level.id ? String(level.id) : '';
        const label = (level.label || '').trim();
        let name = (level.title || '').trim();
        const notes = (level.acknowledgement || '').trim();

        if (!label) {
          return;
        }
        if (!name) {
          name = label;
        }

        if (/^\d+$/.test(rawId)) {
          seen.add(rawId);
          const existing = this.scaleIndex[rawId];
          const username = existing?.username || fallbackUsername;
          const payloadData = {
            username,
            level: label,
            name,
            notes,
          };
          if (
            !existing ||
            existing.level !== payloadData.level ||
            existing.name !== payloadData.name ||
            (existing.notes || '') !== payloadData.notes
          ) {
            updateTasks.push(API.scales.update(rawId, payloadData));
          }
        } else {
          createTasks.push(
            API.scales.create({
              username: fallbackUsername,
              level: label,
              name,
              notes,
            }),
          );
        }
      });

      const deletions = Array.from(membership).filter((id) => !seen.has(id));
      const deleteTasks = deletions.map((id) => API.scales.remove(id));

      await Promise.all([...updateTasks, ...createTasks, ...deleteTasks]);
      const records = await this.fetchScales();
      return records.find((scale) => scale.id === payload.scaleId);
    },

    async fetchNotifications() {
      const notifications = await API.notifications.list();
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
      const d = await API.adminUsers.list();
      this.users = Array.isArray(d) ? d
                : Array.isArray(d?.users) ? d.users
                : Array.isArray(d?.results) ? d.results
                : [];
      return this.users;
    },
    async createUser(payload: CreateManagedUserRequest) {
      const user = await API.adminUsers.create(payload);
      this.upsertUser(user);
      return user;
    },
    async updateUser(id: string, updates: UpdateManagedUserRequest) {
      const user = await API.adminUsers.update(id, updates);
      this.upsertUser(user);
      return user;
    },
    async toggleUserStatus(id: string, status: AccountStatus) {
      const user = await API.adminUsers.toggleStatus(id, status);
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
