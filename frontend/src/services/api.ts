import http, { authHttp } from './http';

const buildQuery = (params?: Record<string, unknown>) => {
  if (!params) {
    return '';
  }
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') {
      return;
    }
    if (Array.isArray(value)) {
      value.forEach((item) => searchParams.append(key, String(item)));
    } else {
      searchParams.append(key, String(value));
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : '';
};

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type UserRole = 'admin' | 'sc' | 'tutor';
export type AccountStatus = 'active' | 'inactive';

export interface AccountProfile {
  id: string;
  username: string;
  name: string;
  email?: string;
  role: UserRole;
  status: AccountStatus;
  phone?: string;
  organization?: string;
  bio?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token?: string;
  user?: AccountProfile;
  message?: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  role: UserRole;
}

export interface RegisterResponse {
  message?: string;
  data?: AccountProfile;
  user?: AccountProfile;
}

export interface UpdateProfileRequest {
  name?: string;
  email?: string;
  phone?: string;
  organization?: string;
  bio?: string;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

export interface PasswordResetRequestPayload {
  email?: string;
  username?: string;
}

export interface PasswordResetConfirmPayload {
  token: string;
  newPassword: string;
}

export const AuthAPI = {
  login(payload: LoginRequest) {
    return authHttp.post<LoginResponse>('auth/login/', payload);
  },
  logout() {
    return authHttp.post<void>('auth/logout/');
  },
  getProfile() {
    return http.get<AccountProfile>('/auth/me');
  },
  updateProfile(payload: UpdateProfileRequest) {
    return http.put<AccountProfile>('/users/me', payload);
  },
  changePassword(payload: ChangePasswordRequest) {
    return http.post<void>('/users/me/password', payload);
  },
  register(payload: RegisterRequest) {
    return authHttp.post<RegisterResponse>('auth/register/', payload);
  },
  requestPasswordReset(payload: PasswordResetRequestPayload) {
    return authHttp.post<void>('auth/password/reset/', payload);
  },
  confirmPasswordReset(payload: PasswordResetConfirmPayload) {
    return authHttp.post<void>('auth/password/reset/confirm/', payload);
  },
};

export interface Course {
  id: string;
  name: string;
  code: string;
  term: string;
  description?: string;
  coordinatorId: string;
  coordinatorName?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CourseFilters {
  keyword?: string;
  term?: string;
  coordinatorId?: string;
}

export type CreateCourseRequest = Pick<
  Course,
  'name' | 'code' | 'term' | 'description' | 'coordinatorId'
>;
export type UpdateCourseRequest = Partial<Omit<Course, 'id' | 'createdAt' | 'updatedAt'>>;

export const CoursesAPI = {
  list(filters?: CourseFilters) {
    return http.get<Course[]>(`/courses/${buildQuery(filters ? { ...filters } : undefined)}`);
  },
  create(payload: CreateCourseRequest) {
    return http.post<Course>('/courses/', payload);
  },
  update(id: string, payload: UpdateCourseRequest) {
    return http.put<Course>(`/courses/${id}/`, payload);
  },
  remove(id: string) {
    return http.delete<void>(`/courses/${id}/`);
  },
};

export interface Assignment {
  id: string;
  courseId: string;
  courseName?: string;
  courseCode?: string;
  courseTerm?: string;
  name: string;
  type: AssignmentType;
  description?: string;
  tutorIds: string[];
  hasTemplate: boolean;
  templateUpdatedAt?: string;
  aiDeclarationStatus: DeclarationStatus;
}

export type AssignmentType = string;
export type DeclarationStatus = 'missing' | 'draft' | 'published';

export interface AssignmentFilters {
  courseId?: string;
  keyword?: string;
  type?: AssignmentType;
  status?: DeclarationStatus;
}

export type CreateAssignmentRequest = Pick<
  Assignment,
  'courseId' | 'name' | 'type' | 'description'
> & {
  tutorIds?: string[];
};

export type UpdateAssignmentRequest = Partial<Omit<Assignment, 'id' | 'courseId'>> & {
  tutorIds?: string[];
};

export const AssignmentsAPI = {
  list(filters?: AssignmentFilters) {
    return http.get<Assignment[]>(
      `/assignments${buildQuery(filters ? { ...filters } : undefined)}`,
    );
  },
  get(id: string) {
    return http.get<Assignment>(`/assignments/${id}`);
  },
  create(payload: CreateAssignmentRequest) {
    return http.post<Assignment>('/assignments', payload);
  },
  update(id: string, payload: UpdateAssignmentRequest) {
    return http.put<Assignment>(`/assignments/${id}`, payload);
  },
  remove(id: string) {
    return http.delete<void>(`/assignments/${id}`);
  },
};

export interface TemplateRow {
  id: string;
  task: string;
  levelId: string;
  levelLabel: string;
  instructions: string;
  acknowledgement: string;
  examples: string;
  aiGeneratedContent: string;
  toolsUsed: string;
  purposeAndUsage: string;
  keyPrompts: string;
}

export interface TemplateRecord {
  id: string;
  assignmentId: string;
  rows: TemplateRow[];
  isPublished: boolean;
  updatedAt: string;
  updatedBy: string;
  lastPublishedAt?: string;
}

export interface SaveTemplateRequest {
  assignmentId: string;
  rows: TemplateRow[];
  publish?: boolean;
  updatedBy?: string;
  updatedById?: string;
}

export const TemplatesAPI = {
  getByAssignment(assignmentId: string) {
    return http.get<TemplateRecord>(`/assignments/${assignmentId}/template`);
  },
  save(assignmentId: string, payload: SaveTemplateRequest) {
    return http.post<TemplateRecord>(`/assignments/${assignmentId}/template`, payload);
  },
  publish(assignmentId: string, payload?: { updatedBy?: string; updatedById?: string }) {
    return http.post<void>(`/assignments/${assignmentId}/template/publish`, payload);
  },
  unpublish(assignmentId: string) {
    return http.post<void>(`/assignments/${assignmentId}/template/unpublish`);
  },
};

export interface ScaleLevel {
  id: string;
  label: string;
  title?: string;
  instructions?: string;
  acknowledgement?: string;
}

export interface ScaleVersion {
  id: string;
  version: number;
  updatedAt: string;
  updatedBy: string;
  notes?: string;
  levels: ScaleLevel[];
}

export interface ScaleRecord {
  id: string;
  name: string;
  ownerType: 'system' | 'sc';
  ownerId?: string;
  isPublic: boolean;
  currentVersion: ScaleVersion | null;
  history: ScaleVersion[];
}

export interface CreateScaleRecordRequest {
  name: string;
  ownerType: 'system' | 'sc';
  ownerId?: string;
  isPublic?: boolean;
}

export interface SaveScaleVersionRequest {
  scaleId: string;
  levels: ScaleLevel[];
  notes?: string;
  updatedById?: string;
}

export const ScaleRecordsAPI = {
  list(params?: { ownerType?: string; ownerId?: string; isPublic?: string | number }) {
    return http.get<PaginatedResponse<ScaleRecord> | ScaleRecord[]>('/scale-records/', {
      params,
    });
  },
  create(payload: CreateScaleRecordRequest) {
    return http.post<ScaleRecord>('/scale-records/', payload);
  },
  saveVersion(payload: SaveScaleVersionRequest & { updatedBy?: string }) {
    return http.post<ScaleRecord>('/scale-records/save_version/', payload);
  },
};

export interface NotificationItem {
  id: string;
  title: string;
  content: string;
  body?: string;
  createdAt: string;
  isRead: boolean;
  relatedType: string;
  relatedId?: string;
}

export const NotificationsAPI = {
  list() {
    return http.get<NotificationItem[]>('/notifications');
  },
  markRead(id: string) {
    return http.post<void>(`/notifications/${id}/read`);
  },
  markAllRead() {
    return http.post<void>('/notifications/read-all');
  },
};

export interface ManagedUser {
  id: string;
  username: string;
  name: string;
  email?: string;
  role: UserRole;
  status: AccountStatus;
  phone?: string;
  organization?: string;
  bio?: string;
  lastLoginAt?: string;
}

export interface CreateManagedUserRequest {
  username: string;
  name: string;
  email?: string;
  role: UserRole;
  phone?: string;
  organization?: string;
  bio?: string;
}

export interface UpdateManagedUserRequest extends Partial<CreateManagedUserRequest> {}

export const AdminUsersAPI = {
  list() {
    return http.get<ManagedUser[]>('/admin/users');
  },
  create(payload: CreateManagedUserRequest) {
    return http.post<ManagedUser>('/admin/users', payload);
  },
  update(id: string, payload: UpdateManagedUserRequest) {
    return http.put<ManagedUser>(`/admin/users/${id}`, payload);
  },
  toggleStatus(id: string, status: AccountStatus) {
    return http.post<ManagedUser>(`/admin/users/${id}/status`, { data: { status } });
  },
};

export type ExportFormat = 'pdf' | 'xlsx';

export interface ExportTablePayload {
  title: string;
  data: Record<string, unknown[]>;
}

export const ExportAPI = {
  download(format: ExportFormat, payload: ExportTablePayload) {
    const endpoint = format === 'pdf' ? '/export/pdf/' : '/export/excel/';
    return http.post<Blob>(endpoint, payload, { responseType: 'blob' });
  },
};

export const API = {
  auth: AuthAPI,
  courses: CoursesAPI,
  assignments: AssignmentsAPI,
  templates: TemplatesAPI,
  scaleRecords: ScaleRecordsAPI,
  notifications: NotificationsAPI,
  adminUsers: AdminUsersAPI,
  exporter: ExportAPI,
};

export default API;
