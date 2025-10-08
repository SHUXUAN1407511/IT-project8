import { defineStore } from 'pinia';
import { appConfig } from '@/config';
import type {
  Assignment,
  AssignmentType,
  Course,
  DeclarationStatus,
  ManagedUser,
  NotificationItem,
  ScaleLevel,
  ScaleRecord,
  TemplateRecord,
  TemplateRow,
  UserRole,
} from '@/services/api';
const deepCopy = <T>(value: T): T => JSON.parse(JSON.stringify(value));

const generateId = (prefix: string) => `${prefix}_${Math.random().toString(36).slice(2, 10)}`;

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

export const useDataStore = defineStore('data', {
  state: () => ({
    courses: [] as Course[],
    assignments: [] as Assignment[],
    assignmentTypes: loadAssignmentTypes(),
    templates: [] as TemplateRecord[],
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
      return state.users.filter((user) => user.role === 'tutor' && user.status === 'active');
    },
    coordinators(state) {
      return state.users.filter((user) => user.role === 'sc' && user.status === 'active');
    },
  },
  actions: {
    addCourse(payload: Omit<Course, 'id' | 'createdAt' | 'updatedAt'>) {
      const now = new Date().toISOString();
      const course: Course = {
        ...payload,
        id: generateId('course'),
        createdAt: now,
        updatedAt: now,
      };
      this.courses.push(course);
      return course;
    },
    updateCourse(id: string, updates: Partial<Omit<Course, 'id' | 'createdAt'>>) {
      const course = this.courses.find((item) => item.id === id);
      if (!course) return;
      Object.assign(course, updates);
      course.updatedAt = new Date().toISOString();
    },
    deleteCourse(id: string) {
      this.courses = this.courses.filter((course) => course.id !== id);
      const removedAssignments = this.assignments.filter((assignment) => assignment.courseId === id);
      const assignmentIds = new Set(removedAssignments.map((assignment) => assignment.id));
      this.assignments = this.assignments.filter((assignment) => assignment.courseId !== id);
      this.templates = this.templates.filter((template) => !assignmentIds.has(template.assignmentId));
    },

    addAssignment(payload: Omit<Assignment, 'id' | 'hasTemplate' | 'templateUpdatedAt' | 'aiDeclarationStatus'>) {
      const assignment: Assignment = {
        ...payload,
        id: generateId('assignment'),
        hasTemplate: false,
        aiDeclarationStatus: 'missing',
      };
      this.assignments.push(assignment);
      return assignment;
    },
    updateAssignment(id: string, updates: Partial<Omit<Assignment, 'id'>>) {
      const assignment = this.assignments.find((item) => item.id === id);
      if (!assignment) return;
      Object.assign(assignment, updates);
    },
    deleteAssignment(id: string) {
      this.assignments = this.assignments.filter((assignment) => assignment.id !== id);
      this.templates = this.templates.filter((template) => template.assignmentId !== id);
    },

    saveTemplate(payload: { assignmentId: string; rows: TemplateRow[]; updatedBy: string; publish?: boolean }) {
      const now = new Date().toISOString();
      const existing = this.templates.find((template) => template.assignmentId === payload.assignmentId);
      if (existing) {
        existing.rows = deepCopy(payload.rows);
        existing.updatedAt = now;
        existing.updatedBy = payload.updatedBy;
        if (typeof payload.publish === 'boolean') {
          existing.isPublished = payload.publish;
          existing.lastPublishedAt = payload.publish ? now : existing.lastPublishedAt;
        }
      } else {
        this.templates.push({
          id: generateId('template'),
          assignmentId: payload.assignmentId,
          rows: deepCopy(payload.rows),
          updatedAt: now,
          updatedBy: payload.updatedBy,
          isPublished: payload.publish ?? false,
          lastPublishedAt: payload.publish ? now : undefined,
        });
      }
      const assignment = this.assignments.find((item) => item.id === payload.assignmentId);
      if (assignment) {
        assignment.hasTemplate = true;
        assignment.templateUpdatedAt = now;
        assignment.aiDeclarationStatus = payload.publish ? 'published' : 'draft';
      }
    },
    toggleTemplatePublish(assignmentId: string, publish: boolean, updatedBy: string) {
      const template = this.templates.find((item) => item.assignmentId === assignmentId);
      if (!template) return;
      const now = new Date().toISOString();
      template.isPublished = publish;
      template.updatedAt = now;
      template.updatedBy = updatedBy;
      template.lastPublishedAt = publish ? now : template.lastPublishedAt;
      const assignment = this.assignments.find((item) => item.id === assignmentId);
      if (assignment) {
        assignment.aiDeclarationStatus = publish ? 'published' : 'draft';
      }
    },

    saveScaleVersion(scaleId: string, levels: ScaleLevel[], updatedBy: string, notes?: string) {
      const target = this.scales.find((scale) => scale.id === scaleId);
      if (!target) return;
      target.history.unshift(deepCopy(target.currentVersion));
      target.currentVersion = {
        id: generateId('scale_version'),
        version: target.currentVersion.version + 1,
        updatedAt: new Date().toISOString(),
        updatedBy,
        notes,
        levels: deepCopy(levels),
      };
    },
    createCustomScale(payload: { name: string; ownerId: string; isPublic: boolean; levels: ScaleLevel[]; notes?: string; updatedBy: string }) {
      const scale: ScaleRecord = {
        id: generateId('scale'),
        name: payload.name,
        ownerType: 'sc',
        ownerId: payload.ownerId,
        isPublic: payload.isPublic,
        currentVersion: {
          id: generateId('scale_version'),
          version: 1,
          updatedAt: new Date().toISOString(),
          updatedBy: payload.updatedBy,
          notes: payload.notes,
          levels: deepCopy(payload.levels),
        },
        history: [],
      };
      this.scales.push(scale);
      return scale;
    },
    rollbackScale(scaleId: string, versionId: string, updatedBy: string, notes?: string) {
      const target = this.scales.find((scale) => scale.id === scaleId);
      if (!target) return;
      const version = [target.currentVersion, ...target.history].find((item) => item.id === versionId);
      if (!version) return;
      target.history.unshift(deepCopy(target.currentVersion));
      target.currentVersion = {
        id: generateId('scale_version'),
        version: target.currentVersion.version + 1,
        updatedAt: new Date().toISOString(),
        updatedBy,
        notes: notes || `Rolled back to version ${version.version}`,
        levels: deepCopy(version.levels),
      };
    },
    toggleScalePublic(scaleId: string, isPublic: boolean) {
      const target = this.scales.find((scale) => scale.id === scaleId);
      if (target) {
        target.isPublic = isPublic;
      }
    },

    markNotificationRead(id: string) {
      const notice = this.notifications.find((item) => item.id === id);
      if (notice) {
        notice.isRead = true;
      }
    },
    markAllNotificationsRead() {
      this.notifications.forEach((item) => {
        item.isRead = true;
      });
    },
    createNotification(notification: Omit<NotificationItem, 'id' | 'createdAt' | 'isRead'>) {
      this.notifications.unshift({
        id: generateId('notice'),
        createdAt: new Date().toISOString(),
        isRead: false,
        ...notification,
      });
    },

    createUser(payload: Omit<ManagedUser, 'id' | 'lastLoginAt' | 'status'> & { status?: 'active' | 'inactive' }) {
      const user: ManagedUser = {
        id: generateId('user'),
        username: payload.username,
        name: payload.name,
        email: payload.email,
        role: payload.role,
        phone: payload.phone,
        organization: payload.organization,
        bio: payload.bio,
        status: payload.status || 'active',
        lastLoginAt: new Date().toISOString(),
      };
      this.users.push(user);
      return user;
    },
    updateUser(id: string, updates: Partial<ManagedUser>) {
      const user = this.users.find((item) => item.id === id);
      if (!user) return;
      Object.assign(user, updates);
    },
    toggleUserStatus(id: string, status: 'active' | 'inactive') {
      const user = this.users.find((item) => item.id === id);
      if (user) {
        user.status = status;
      }
    },
    setAssignmentTypes(types: AssignmentType[]) {
      const sanitized = sanitizeAssignmentTypes(types, appConfig.assignmentTypes);
      this.assignmentTypes = sanitized;
      if (typeof window !== 'undefined') {
        try {
          window.localStorage.setItem(
            ASSIGNMENT_TYPES_STORAGE_KEY,
            JSON.stringify(this.assignmentTypes)
          );
        } catch (error) {
          console.warn('[dataStore] Failed to persist assignment types:', error);
        }
      }
    },
    resetAssignmentTypes() {
      this.setAssignmentTypes([...appConfig.assignmentTypes] as AssignmentType[]);
    },
  },
});

export type {
  Course,
  Assignment,
  AssignmentType,
  DeclarationStatus,
  TemplateRecord,
  TemplateRow,
  ScaleRecord,
  ScaleLevel,
  NotificationItem,
  ManagedUser,
} from '@/services/api';
