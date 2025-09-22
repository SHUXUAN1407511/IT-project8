/**
 * API
 */
import http from './http';

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

/* -------------------------------------------------------------------------- */
/* Auth                                                                       */
/* -------------------------------------------------------------------------- */

export interface LoginRequest {
  username: string;
  password: string;
  role?: UserRole;
}

export interface LoginResponse {
  token?: string;
  user?: AccountProfile;
  message?: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  role?: UserRole;
}

export interface RegisterResponse {
  message?: string;
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

/**
 * AuthAPI — 负责认证和账号管理。
 * 建议返回 JSON；当鉴权失败时请返回 401/403，并携带 `{ message: string }`。
 * 登录/注销用于登录页，资料接口支撑设置页。
 */
export const AuthAPI = {
  /**
   * POST /auth/login
   * 请求体：{ username: string; password: string }
   * 成功 200：{ token: string; user: AccountProfile }
   * 提示：前端会本地存储 token，并在 http.ts 中追加 `Authorization: Bearer <token>`。
   */
  login(payload: LoginRequest) {
    return http.post<LoginResponse>('/login', { data: payload });
  },
  /**
   * POST /auth/logout
   * 请求体：无
   * 成功 204（推荐）或 200：空响应
   * 提示：后端需吊销 token，前端随后清理本地状态。
   */
  logout() {
    return http.post<void>('/auth/logout');
  },
  /**
   * GET /auth/me
   * 请求体：无
   * 成功 200：AccountProfile（当前用户）
   * 提示：用于应用刷新时基于 token 恢复用户信息。
   */
  getProfile() {
    return http.get<AccountProfile>('/auth/me');
  },
  /**
   * PUT /users/me
   * 请求体：UpdateProfileRequest（支持部分字段更新）
   * 成功 200：更新后的 AccountProfile
   */
  updateProfile(payload: UpdateProfileRequest) {
    return http.put<AccountProfile>('/users/me', { data: payload });
  },
  /**
   * POST /users/me/password
   * 请求体：{ currentPassword: string; newPassword: string }
   * 成功 204（推荐）或 200：空响应
   * 提示：前端会将 400/422 的错误信息展示给用户。
   */
  changePassword(payload: ChangePasswordRequest) {
    return http.post<void>('/users/me/password', { data: payload });
  },
  register(payload: RegisterRequest) {
    return http.post<RegisterResponse>('/register', { data: payload });
  }
};

/* -------------------------------------------------------------------------- */
/* Courses                                                                    */
/* -------------------------------------------------------------------------- */

export interface Course {
  id: string;
  name: string;
  code: string;
  term: string;
  description?: string;
  scId: string;
  createdAt: string;
  updatedAt: string;
}

export interface CourseFilters {
  keyword?: string;
  term?: string;
  scId?: string;
}

export type CreateCourseRequest = Pick<Course, 'name' | 'code' | 'term' | 'description' | 'scId'>;
export type UpdateCourseRequest = Partial<Omit<Course, 'id' | 'createdAt' | 'updatedAt'>>;

/* -------------------------------------------------------------------------- */
/* Assignments                                                                */
/* -------------------------------------------------------------------------- */

export type AssignmentType = string;
export type DeclarationStatus = 'missing' | 'draft' | 'published';

export interface Assignment {
  id: string;
  courseId: string;
  name: string;
  type: AssignmentType;
  description?: string;
  dueDate?: string;
  tutorIds: string[];
  hasTemplate: boolean;
  templateUpdatedAt?: string;
  aiDeclarationStatus: DeclarationStatus;
}

export interface AssignmentFilters {
  courseId?: string;
  keyword?: string;
  type?: AssignmentType;
  status?: DeclarationStatus;
}

export type CreateAssignmentRequest = Pick<Assignment, 'courseId' | 'name' | 'type' | 'description'> & {
  tutorIds?: string[];
  dueDate?: string;
};

export type UpdateAssignmentRequest = Partial<Omit<Assignment, 'id' | 'courseId'>> & {
  tutorIds?: string[];
  dueDate?: string;
};

/* -------------------------------------------------------------------------- */
/* Templates                                                                  */
/* -------------------------------------------------------------------------- */

export interface TemplateRow {
  id: string;
  levelId: string;
  levelLabel: string;
  instructions: string;
  acknowledgement: string;
  additionalNotes?: string;
  examples?: string;
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
}

/* -------------------------------------------------------------------------- */
/* AI User Scale                                                              */
/* -------------------------------------------------------------------------- */

export interface ScaleLevel {
  id: string;
  label: string;
  title: string;
  description: string;
  instructions: string;
  acknowledgement: string;
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
  currentVersion: ScaleVersion;
  history: ScaleVersion[];
}

export interface ScaleFilters {
  ownerId?: string;
  includeSystem?: boolean;
  includePublic?: boolean;
}

export interface CreateCustomScaleRequest {
  name: string;
  ownerId: string;
  isPublic: boolean;
  levels: ScaleLevel[];
  notes?: string;
}

export interface UpdateScaleVersionRequest {
  scaleId: string;
  levels: ScaleLevel[];
  notes?: string;
}

/* -------------------------------------------------------------------------- */
/* Notifications                                                              */
/* -------------------------------------------------------------------------- */

export interface NotificationItem {
  id: string;
  title: string;
  content: string;
  relatedType: 'scale' | 'assignment' | 'course' | 'system';
  relatedId?: string;
  createdAt: string;
  isRead: boolean;
}

/* -------------------------------------------------------------------------- */
/* Admin                                                                      */
/* -------------------------------------------------------------------------- */

export interface ManagedUser extends AccountProfile {
  lastLoginAt?: string;
}

export interface CreateUserRequest {
  username: string;
  name: string;
  email: string;
  role: UserRole;
  phone?: string;
  organization?: string;
  bio?: string;
  status?: AccountStatus;
}

export type UpdateUserRequest = Partial<Omit<CreateUserRequest, 'username' | 'role'>> & {
  role?: UserRole;
  status?: AccountStatus;
};

/* -------------------------------------------------------------------------- */
/* Tools。                                                                    */
/* -------------------------------------------------------------------------- */

// buildUrl 用于拼接查询字符串：跳过空值，并把数组展开成重复键。
function buildUrl(path: string, params?: Record<string, unknown>) {
  if (!params) return path;
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    if (Array.isArray(value)) {
      value.forEach((item) => search.append(key, String(item)));
    } else {
      search.append(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

/* -------------------------------------------------------------------------- */
/* API                                                                        */
/* -------------------------------------------------------------------------- */

/**
 * CoursesAPI — 课程管理相关接口。
 * 所有 Course.createdAt/updatedAt 字段均使用 ISO-8601 字符串。
 * SC/Admin 负责创建和维护课程，导师使用筛选后的列表。
 */
export const CoursesAPI = {
  /**
   * GET /courses
   * 查询参数：{ keyword?: string; term?: string; scId?: string }
   * 成功 200：Course[]
   * 提示：keyword 会匹配课程名称或课程代码。
   * 场景：课程页首次加载或执行筛选搜索。
   */
  list(filters?: CourseFilters) {
    return http.get<Course[]>(buildUrl('/courses', filters as Record<string, unknown> | undefined));
  },
  /**
   * POST /courses
   * 请求体：{ name, code, term, description?, scId }
   * 成功 201（推荐）或 200：Course
   * 提示：id/createdAt/updatedAt 由后端生成。
   * 场景：SC/Admin 通过弹窗创建课程。
   */
  create(payload: CreateCourseRequest) {
    return http.post<Course>('/courses', { data: payload });
  },
  /**
   * PUT /courses/{id}
   * 请求体：UpdateCourseRequest（允许部分更新）
   * 成功 200：Course
   * 场景：编辑课程详情，包括课程协调人变更。
   */
  update(id: string, payload: UpdateCourseRequest) {
    return http.put<Course>(`/courses/${id}`, { data: payload });
  },
  /**
   * DELETE /courses/{id}
   * 成功 204（推荐）或 200：空响应
   * 提示：前端假设课程下的作业/模板由后端负责清理。
   * 场景：管理员或协调人删除课程。
   */
  remove(id: string) {
    return http.delete<void>(`/courses/${id}`);
  }
};

/**
 * AssignmentsAPI — 作业与 AI 申报相关接口。
 * SC 负责按课程管理作业，导师通过搜索/类型/状态过滤查看列表。
 */
export const AssignmentsAPI = {
  /**
   * GET /assignments
   * 查询参数：{ courseId?: string; keyword?: string; type?: string; status?: 'missing' | 'draft' | 'published' }
   * 成功 200：Assignment[]
   * 提示：tutorIds 必须是字符串数组；aiDeclarationStatus 控制界面徽标。
   * 场景：作业页加载或筛选时使用；导师会携带类型/状态过滤条件。
   */
  list(filters?: AssignmentFilters) {
    return http.get<Assignment[]>(buildUrl('/assignments', filters as Record<string, unknown> | undefined));
  },
  /**
   * POST /assignments
   * 请求体：{ courseId, name, type, description?, tutorIds?, dueDate? }
   * 成功 201（推荐）或 200：Assignment（id/hasTemplate/aiDeclarationStatus 由后端返回）
   * 场景：SC 新建作业；默认 hasTemplate=false、aiDeclarationStatus='missing'。
   */
  create(payload: CreateAssignmentRequest) {
    return http.post<Assignment>('/assignments', { data: payload });
  },
  /**
   * PUT /assignments/{id}
   * 请求体：UpdateAssignmentRequest
   * 成功 200：Assignment
   * 提示：允许部分更新；若提供 dueDate，需返回 ISO-8601 字符串。
   * 场景：SC 编辑作业信息或同步发布状态。
   */
  update(id: string, payload: UpdateAssignmentRequest) {
    return http.put<Assignment>(`/assignments/${id}`, { data: payload });
  },
  /**
   * DELETE /assignments/{id}
   * 成功 204（推荐）或 200：空响应
   * 提示：前端期望关联模板由后端一并删除。
   * 场景：SC 删除作业并等待后端清理。
   */
  remove(id: string) {
    return http.delete<void>(`/assignments/${id}`);
  }
};

/**
 * TemplatesAPI — 作业 AI 申报模板相关接口。
 * SC/导师在编辑页维护模板（草稿/发布/下线）。
 */
export const TemplatesAPI = {
  /**
   * GET /assignments/{assignmentId}/template
   * 成功 200：TemplateRecord
   * 提示：若模板不存在请返回 404，前端会给出提示。
   * 场景：模板编辑器初始加载。
   */
  getByAssignment(assignmentId: string) {
    return http.get<TemplateRecord>(`/assignments/${assignmentId}/template`);
  },
  /**
   * PUT /assignments/{assignmentId}/template
   * 请求体：{ assignmentId, rows: TemplateRow[], publish?: boolean }
   * 成功 200：TemplateRecord（最新模板数据）
   * 场景：保存草稿或发布；当 publish=true 时，后端需将 assignment.aiDeclarationStatus 改为 'published'。
   */
  save(assignmentId: string, payload: SaveTemplateRequest) {
    return http.put<TemplateRecord>(`/assignments/${assignmentId}/template`, { data: payload });
  },
  /**
   * POST /assignments/{assignmentId}/template/publish
   * 请求体：无
   * 成功 200：TemplateRecord（isPublished=true，lastPublishedAt 已更新）
   * 场景：执行发布操作；后端需记录 lastPublishedAt 与 updatedBy。
   */
  publish(assignmentId: string) {
    return http.post<TemplateRecord>(`/assignments/${assignmentId}/template/publish`);
  },
  /**
   * POST /assignments/{assignmentId}/template/unpublish
   * 请求体：无
   * 成功 200：TemplateRecord（isPublished=false）
   * 场景：执行下线操作；后端需将 assignment.aiDeclarationStatus 调整为 'draft'。
   */
  unpublish(assignmentId: string) {
    return http.post<TemplateRecord>(`/assignments/${assignmentId}/template/unpublish`);
  },
  /**
   * GET /assignments/{assignmentId}/template/export?format=pdf|xlsx
   * 成功 200：Blob（文件流）
   * 提示：前端会以二进制方式下载该响应。
   * 场景：在模板编辑器中导出 PDF/XLSX。
   */
  export(assignmentId: string, format: 'pdf' | 'xlsx') {
    return http.get<Blob>(buildUrl(`/assignments/${assignmentId}/template/export`, { format }));
  }
};

/**
 * ScalesAPI — 量表管理（系统版与自定义版）。
 * 管理员维护系统量表，SC 负责创建、保存和回滚自定义版本。
 */
export const ScalesAPI = {
  /**
   * GET /scales
   * 查询参数：{ ownerId?: string; includeSystem?: boolean; includePublic?: boolean }
   * 成功 200：ScaleRecord[]
   * 场景：量表管理列表；includeSystem=true 时请求系统量表。
   */
  list(filters?: ScaleFilters) {
    return http.get<ScaleRecord[]>(buildUrl('/scales', filters as Record<string, unknown> | undefined));
  },
  /**
   * POST /scales/custom
   * 请求体：{ name, ownerId, isPublic, levels: ScaleLevel[], notes? }
   * 成功 201（推荐）或 200：ScaleRecord
   * 场景：SC 创建自定义量表；ownerId 为当前用户。
   */
  createCustom(payload: CreateCustomScaleRequest) {
    return http.post<ScaleRecord>('/scales/custom', { data: payload });
  },
  /**
   * POST /scales/{scaleId}/versions
   * 请求体：{ scaleId, levels: ScaleLevel[], notes?: string }
   * 成功 200：ScaleRecord（currentVersion 与 history 已更新）
   * 场景：保存新版本；后端需将旧版本插入 history[0]。
   */
  saveVersion(payload: UpdateScaleVersionRequest) {
    return http.post<ScaleRecord>(`/scales/${payload.scaleId}/versions`, { data: payload });
  },
  /**
   * POST /scales/{scaleId}/versions/{versionId}/rollback
   * 请求体：{ notes?: string }
   * 成功 200：ScaleRecord（生成新的 currentVersion，并调整 history）
   * 场景：回滚会创建一个新版本；notes 可默认为“回滚至版本 x”。
   */
  rollback(scaleId: string, versionId: string, notes?: string) {
    return http.post<ScaleRecord>(`/scales/${scaleId}/versions/${versionId}/rollback`, { data: { notes } });
  },
  /**
   * POST /scales/{scaleId}/visibility
   * 请求体：{ isPublic: boolean }
   * 成功 200：ScaleRecord（isPublic 已更新）
   * 场景：管理员或 SC 在公开与私有之间切换可见性。
   */
  toggleVisibility(scaleId: string, isPublic: boolean) {
    return http.post<ScaleRecord>(`/scales/${scaleId}/visibility`, { data: { isPublic } });
  }
};

/**
 * NotificationsAPI — 通知中心相关接口。
 * 用于系统提醒（模板发布、量表更新等）；所有请求均需已登录。
 */
export const NotificationsAPI = {
  /**
   * GET /notifications
   * 成功 200：NotificationItem[]（按 createdAt 降序）
   * 场景：通知中心首次加载；isRead 控制角标状态。
   */
  list() {
    return http.get<NotificationItem[]>('/notifications');
  },
  /**
   * POST /notifications/{id}/read
   * 成功 204（推荐）或 200：空响应
   * 场景：用户打开通知；后端需要将 isRead 设为 true。
   */
  markRead(id: string) {
    return http.post<void>(`/notifications/${id}/read`);
  },
  /**
   * POST /notifications/read-all
   * 成功 204（推荐）或 200：空响应
   * 场景：“全部标记为已读”；后端需为该用户批量更新通知。
   */
  markAllRead() {
    return http.post<void>('/notifications/read-all');
  }
};

/**
 * AdminUsersAPI — 管理员专用的用户管理接口。
 */
export const AdminUsersAPI = {
  /**
   * GET /admin/users
   * 查询参数：{ role?: 'admin' | 'sc' | 'tutor'; status?: 'active' | 'inactive' }
   * 成功 200：ManagedUser[]
   * 场景：管理员按角色或状态筛选用户列表。
   */
  list(params?: { role?: UserRole; status?: AccountStatus }) {
    return http.get<ManagedUser[]>(buildUrl('/admin/users', params));
  },
  /**
   * POST /admin/users
   * 请求体：{ username, name, email, role, phone?, organization?, bio?, status? }
   * 成功 201（推荐）或 200：ManagedUser
   * 场景：管理员创建新用户；如有需要后端可返回初始密码。
   */
  create(payload: CreateUserRequest) {
    return http.post<ManagedUser>('/admin/users', { data: payload });
  },
  /**
   * PUT /admin/users/{id}
   * 请求体：UpdateUserRequest
   * 成功 200：ManagedUser
   * 场景：管理员更新用户资料或角色权限。
   */
  update(id: string, payload: UpdateUserRequest) {
    return http.put<ManagedUser>(`/admin/users/${id}`, { data: payload });
  },
  /**
   * POST /admin/users/{id}/status
   * 请求体：{ status: 'active' | 'inactive' }
   * 成功 200：ManagedUser（状态已更新）
   * 场景：管理员切换账号启用/停用并刷新列表。
   */
  toggleStatus(id: string, status: AccountStatus) {
    return http.post<ManagedUser>(`/admin/users/${id}/status`, { data: { status } });
  }
};

export const API = {
  auth: AuthAPI,
  courses: CoursesAPI,
  assignments: AssignmentsAPI,
  templates: TemplatesAPI,
  scales: ScalesAPI,
  notifications: NotificationsAPI,
  adminUsers: AdminUsersAPI,
};

export default API;
