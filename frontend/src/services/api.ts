/**
 * 该文件集中定义前端调后端的 REST 接口封装，按业务域归类，便于后端了解请求路径和数据结构。
 *
 * 后端联调说明（请务必阅读）：
 * - 除登录/注册外，所有接口直接以 `/xxx` 形式调用，`VITE_API_BASE` 会用于拼接后端域名（会自动去掉结尾的 `/api`）。
 * - 登录与注册依旧通过 `/api/auth/login`、`/api/auth/register` 访问，便于兼容现有后端路由。
 * - 返回格式默认遵循 JSON；若出现错误需返回 4xx/5xx，并在响应体中携带 `message` 字段供前端展示。
 * - 前端会在成功登录后把返回的 `token` 写入 `localStorage`，并把 `user` 对象存入状态，所以对应字段必须出现。
 * - 如需对权限做鉴权，请使用 `Authorization: Bearer <token>` 头部；目前前端只负责传递，不会手动拼 Query。
 * - 所有时间字段统一使用 ISO 8601 字符串（例如 `2025-03-01T12:34:56.000Z`），便于前端直接格式化展示。
 */


/*关闭占用  netstat -ano | findstr :5174
            taskkill /PID <PID> /F
            taskkill /IM node.exe /F
*/  

import http, { authHttp } from './http';
// 注册
export const registerUser = async (payload: { username: string; password: string; role: string }) => {
  return authHttp.post('auth/register/', payload)
}

// 登录
export const loginUser = async (payload: { username: string; password: string }) => {
  return authHttp.post('auth/login/', payload)
}


/**
 * 以下部分不用管：前端把查询参数对象转换为 QueryString，自动跳过空值并展开数组。
 */
const buildQuery = (params?: Record<string, unknown>) => {
  if (!params) return '';
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
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

/** 用户角色取值，后端在返回 AccountProfile 时保持一致。 */
export type UserRole = 'admin' | 'sc' | 'tutor';
/** 账号状态枚举，前端只认 active/inactive。 */
export type AccountStatus = 'active' | 'inactive';

/**
 * AccountProfile：后端返回的账号档案信息，id/username/name/email/role/status/phone/organization/bio 均为 string，其中带问号的字段可不返回。
 */
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
/* Auth 认证相关接口                                                          */
/* -------------------------------------------------------------------------- */

/**
 * LoginRequest：用户在登录页面提交时发给后端的数据，包含 string 的 username 和 password。
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * LoginResponse：期望后端返回 JWT 等认证 token（可选），以及登录用户的完整档案信息。
 * 形如：
 * {
 *   "token": "jwt-token",
 *   "user": { "id": "...", "username": "...", "name": "...", "role": "sc", "status": "active", ... },
 *   "message": "login success"
 * }
 * 注意：`user.role` 缺失时前端会判定登录失败。
 */
export interface LoginResponse {
  token?: string;
  user?: AccountProfile;
  message?: string;
}

/**
 * RegisterRequest：注册表单提交时发给后端的数据，包含 string 的 username、password 以及 UserRole 的 role。
 */
export interface RegisterRequest {
  username: string;
  password: string;
  role: UserRole;
}

/**
 * RegisterResponse：注册成功后返回给前端的数据，message 为 string（可选），user 为 AccountProfile（可选）。
 */
export interface RegisterResponse {
  message?: string;
  user?: AccountProfile;
}

/**
 * UpdateProfileRequest：用户在个人资料页修改信息时发给后端的字段，name/email/phone/organization/bio 全部为 string，可选。
 */
export interface UpdateProfileRequest {
  name?: string;
  email?: string;
  phone?: string;
  organization?: string;
  bio?: string;
}

/**
 * ChangePasswordRequest：用户修改密码时发给后端的数据，currentPassword/newPassword 均为 string。
 */
export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

export const AuthAPI = {
  /**
   * POST /auth/login：用户点击登录按钮时调用。
   * 后端需校验用户名密码并返回 LoginResponse。若失败请返回 401，body 中提供 `message`。
   */
  login(payload: LoginRequest) {
    return authHttp.post<LoginResponse>('auth/login/', payload);
  },
  /**
   * POST /auth/logout：用户退出登录时调用。
   * 期望后端清理 token 或 session。成功返回 200，无需响应体；失败请返回 4xx 并包含 `message`。
   */
  logout() {
    return http.post<void>('auth/logout');
  },
  /**
   * GET /auth/me：用于刷新页面后校验登录态。
   * 需从 Authorization 头中解析身份并返回 AccountProfile。若未登录请返回 401。
   */
  getProfile() {
    return http.get<AccountProfile>('/auth/me');
  },
  /**
   * PUT /users/me：用户修改个人资料时调用。
   * 后端需更新数据库并返回最新的 AccountProfile，以便前端立即刷新页面显示。
   */
  updateProfile(payload: UpdateProfileRequest) {
    return http.put<AccountProfile>('/users/me', payload);
  },
  /**
   * POST /users/me/password：用户修改密码时调用。
   * 接口必须验证旧密码是否正确，成功后返回 200；错误时返回 400/403，并携带 `message`。
   */
  changePassword(payload: ChangePasswordRequest) {
    return http.post<void>('/users/me/password', payload);
  },
  /**
   * POST /auth/register：管理员或用户注册时调用。
   * 需创建账号并返回 RegisterResponse，至少包含新用户的基本信息。若用户名重复请返回 400。
   */
  register(payload: RegisterRequest) {
    return authHttp.post<RegisterResponse>('auth/register/', payload);
  },
};

/* -------------------------------------------------------------------------- */
/* Courses 课程管理接口                                                       */
/* -------------------------------------------------------------------------- */

/**
 * Course：课程实体字段说明——后端请与数据库模型对齐。
 * - term：字符串（例：`2025-S1`），不同于后端当前的 `semester`，建议统一字段名为 `term`。
 * - scId：课程对应学科协调员的用户 id。
 * - description：课程简介，可选。
 */
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

/**
 * CourseFilters：课程列表筛选条件，全部可选，keyword/term/scId 均为 string，前端会转成查询参数。
 */
export interface CourseFilters {
  keyword?: string;
  term?: string;
  scId?: string;
}

/**
 * CreateCourseRequest：创建课程时发给后端的数据，含 name/code/term/description/scId，全部为 string。
 */
export type CreateCourseRequest = Pick<Course, 'name' | 'code' | 'term' | 'description' | 'scId'>;
/**
 * UpdateCourseRequest：编辑课程时发给后端的数据，允许更新 Course 中除 id/createdAt/updatedAt 外的字段。
 */
export type UpdateCourseRequest = Partial<Omit<Course, 'id' | 'createdAt' | 'updatedAt'>>;

export const CoursesAPI = {
  /**
   * GET /courses：filters 会转换为查询参数，例如 `/courses?keyword=ai&term=2025-S1&scId=xxx`。
   * 若需要分页，可以扩展响应格式（例如 `{ items: Course[], total: number }`），再同步调整前端解析逻辑。
   */
  list(filters?: CourseFilters) {
    return http.get<Course[]>(`/courses/${buildQuery(filters ? { ...filters } : undefined)}`);
  },
  /**
   * POST /courses：创建课程时调用。
   * 后端需校验 `code` + `term` 不重复，并返回创建后的 Course（包含 id、时间字段）。
   */
  create(payload: CreateCourseRequest) {
    return http.post<Course>('/courses/', payload);
  },
  /**
   * PUT /courses/:id：编辑课程信息时调用。
   * 请根据 id 更新并返回最新 Course。字段未传则不修改。
   */
  update(id: string, payload: UpdateCourseRequest) {
    return http.put<Course>(`/courses/${id}/`, payload);
  },
  /**
   * DELETE /courses/:id：删除课程时调用。
   * 建议返回 200 + `{ "message": "deleted" }`，便于前端提示；若存在外键约束需要阻止删除，请返回 409。
   */
  remove(id: string) {
    return http.delete<void>(`/courses/${id}/`);
  },
};

/* -------------------------------------------------------------------------- */
/* Assignments 作业管理接口                                                    */
/* -------------------------------------------------------------------------- */

/**
 * Assignment：字段说明——请注意与课程关联关系。
 * - courseId：所属课程 id。
 * - tutorIds：分配的导师 id 列表。
 * - aiDeclarationStatus：模板发布状态，用于界面显示标签。
 */
export interface Assignment {
  id: string;
  courseId: string;
  name: string;
  type: AssignmentType;
  description?: string;
  tutorIds: string[];
  hasTemplate: boolean;
  templateUpdatedAt?: string;
  aiDeclarationStatus: DeclarationStatus;
}

/** 作业类型字符串，后端原样返回即可。 */
export type AssignmentType = string;
/** 声明状态取值，后端需返回 missing/draft/published 之一。 */
export type DeclarationStatus = 'missing' | 'draft' | 'published';

/**
 * AssignmentFilters：作业列表筛选条件，可选字段 courseId/keyword/type/status，均为 string。
 */
export interface AssignmentFilters {
  courseId?: string;
  keyword?: string;
  type?: AssignmentType;
  status?: DeclarationStatus;
}

/**
 * CreateAssignmentRequest：创建作业时发送的数据，必填 courseId/name/type/description，tutorIds 可选数组。
 */
export type CreateAssignmentRequest = Pick<Assignment, 'courseId' | 'name' | 'type' | 'description'> & {
  tutorIds?: string[];
};

/**
 * UpdateAssignmentRequest：编辑作业时发送的数据，可更新作业除 id/courseId 外的字段，tutorIds 为可选数组。
 */
export type UpdateAssignmentRequest = Partial<Omit<Assignment, 'id' | 'courseId'>> & {
  tutorIds?: string[];
};

export const AssignmentsAPI = {
  /**
   * GET /assignments：示例 `/assignments?courseId=xxx&type=Essay&status=published`。
   * 若需分页，可扩展响应格式，与课程接口保持一致。
   */
  list(filters?: AssignmentFilters) {
    return http.get<Assignment[]>(`/assignments${buildQuery(filters ? { ...filters } : undefined)}`);
  },
  /**
   * GET /assignments/:id：前端会根据返回的 Assignment 渲染详情页，如遇未找到请返回 404。
   */
  get(id: string) {
    return http.get<Assignment>(`/assignments/${id}`);
  },
  /**
   * POST /assignments：创建作业时调用。
   * 后端需校验课程存在性，并返回新建 Assignment（带 id、hasTemplate=false）。
   */
  create(payload: CreateAssignmentRequest) {
    return http.post<Assignment>('/assignments', payload);
  },
  /**
   * PUT /assignments/:id：编辑作业或导师分配时调用。
   * 需返回更新后的 Assignment，以便前端刷新。
   */
  update(id: string, payload: UpdateAssignmentRequest) {
    return http.put<Assignment>(`/assignments/${id}`, payload);
  },
  /**
   * DELETE /assignments/:id：删除作业时调用。
   * 建议返回 `{ "message": "deleted" }`。如存在模板等依赖，可自行决定是否级联删除或拦截。
   */
  remove(id: string) {
    return http.delete<void>(`/assignments/${id}`);
  },
};

/* -------------------------------------------------------------------------- */
/* Templates 作业模板接口                                                     */
/* -------------------------------------------------------------------------- */

/**
 * TemplateRow：作业模板中的单行配置，所有字段为 string，id/levelId/levelLabel/task/instructions/acknowledgement/examples/aiGeneratedContent/toolsUsed/purposeAndUsage/keyPrompts。
 */
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

/**
 * TemplateRecord：用于模板编辑器。
 * - rows：由前端拖拽生成的结构化条目，请保持数组顺序。
 * - isPublished：true 表示模板已发布，前端会锁定编辑行为。
 * - updatedBy：记录最后一次操作人 id 或姓名。
 */
export interface TemplateRecord {
  id: string;
  assignmentId: string;
  rows: TemplateRow[];
  isPublished: boolean;
  updatedAt: string;
  updatedBy: string;
  lastPublishedAt?: string;
}

/**
 * SaveTemplateRequest：保存模板时发送的数据，assignmentId 为 string，rows 为 TemplateRow[]，publish 为 boolean 可选，true 表示同时发布。
 */
export interface SaveTemplateRequest {
  assignmentId: string;
  rows: TemplateRow[];
  publish?: boolean;
  updatedBy?: string;
  updatedById?: string;
}

export const TemplatesAPI = {
  /**
   * GET /assignments/:assignmentId/template：需返回已保存模板。若尚未创建请返回 404，前端会进入空模板状态。
   */
  getByAssignment(assignmentId: string) {
    return http.get<TemplateRecord>(`/assignments/${assignmentId}/template`);
  },
  /**
   * POST /assignments/:assignmentId/template：保存模板时调用。
   * 后端需覆盖原有模板并返回最新 TemplateRecord；如果 `publish=true`，同时把 `isPublished` 置为 true。
   */
  save(assignmentId: string, payload: SaveTemplateRequest) {
    return http.post<TemplateRecord>(`/assignments/${assignmentId}/template`, payload);
  },
  /**
   * POST /assignments/:assignmentId/template/publish：发布模板时调用。
   * 建议返回最新 TemplateRecord（`isPublished=true`，`lastPublishedAt` 更新），便于前端同步状态。
   */
  publish(assignmentId: string, payload?: { updatedBy?: string; updatedById?: string }) {
    return http.post<void>(`/assignments/${assignmentId}/template/publish`, payload);
  },
  /**
   * POST /assignments/:assignmentId/template/unpublish：撤回模板发布时调用。
   * 建议返回最新 TemplateRecord（`isPublished=false`）。
   */
  unpublish(assignmentId: string) {
    return http.post<void>(`/assignments/${assignmentId}/template/unpublish`);
  },
};

/* -------------------------------------------------------------------------- */
/* Scales 评分量规接口                                                        */
/* -------------------------------------------------------------------------- */

/**
 * ScaleLevel：量规的单个等级配置，id/label/title/instructions/acknowledgement 均为 string，带问号的字段可选。
 */
export interface ScaleLevel {
  id: string;
  label: string;
  title?: string;
  instructions?: string;
  acknowledgement?: string;
}

/**
 * ScaleVersion：量规的一个版本信息，id 为 string，version 为 number，updatedAt/updatedBy/notes 为 string（notes 可选），levels 为 ScaleLevel[]。
 */
export interface ScaleVersion {
  id: string;
  version: number;
  updatedAt: string;
  updatedBy: string;
  notes?: string;
  levels: ScaleLevel[];
}

/**
 * ScaleRecord：量规数据结构说明。
 * - ownerType：`system` 表示平台默认量规；`sc` 表示学科协调员自定义。
 * - history：按照时间倒序保存旧版本，`currentVersion` 为最新版本。
 * - levels：需保留等级顺序，以便前端展示。
 */
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

/**
 * SaveScaleVersionRequest：保存量规新版本时发送的数据，scaleId 为 string，levels 为 ScaleLevel[]，notes 为 string 可选。
 */
export interface SaveScaleVersionRequest {
  scaleId: string;
  levels: ScaleLevel[];
  notes?: string;
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

/* -------------------------------------------------------------------------- */
/* Notifications 通知中心接口                                                 */
/* -------------------------------------------------------------------------- */

/**
 * NotificationItem：后端返回的通知对象，id/title/content/body/createdAt/relatedType/relatedId 为 string，isRead 为 boolean，body/relatedId 可选。
 */
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
  /**
   * GET /notifications：返回用户的通知列表，建议按 `createdAt` 降序排列。
   * 如需分页，可扩展为 `{ items: NotificationItem[], total: number }`。
   */
  list() {
    return http.get<NotificationItem[]>('/notifications');
  },
  /**
   * POST /notifications/:id/read：把单条通知标记为已读。
   * 若通知不存在请返回 404。
   */
  markRead(id: string) {
    return http.post<void>(`/notifications/${id}/read`);
  },
  /**
   * POST /notifications/read-all：将当前用户所有通知标记已读。
   */
  markAllRead() {
    return http.post<void>('/notifications/read-all');
  },
};

/* -------------------------------------------------------------------------- */
/* Admin Users 管理端用户接口                                                 */
/* -------------------------------------------------------------------------- */

/**
 * ManagedUser：后台管理列表中展示的用户信息，字段与 AccountProfile 类似，多了 lastLoginAt（string，可选）。
 */
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

/**
 * CreateManagedUserRequest：管理员新建用户时发给后端的数据，username/name 为必填 string，email/role/phone/organization 均为 string（role 必填）。
 */
export interface CreateManagedUserRequest {
  username: string;
  name: string;
  email?: string;
  role: UserRole;
  phone?: string;
  organization?: string;
  bio?: string;
}

/**
 * UpdateManagedUserRequest：管理员编辑用户时发给后端的数据，继承 CreateManagedUserRequest 的可选字段。
 */
export interface UpdateManagedUserRequest extends Partial<CreateManagedUserRequest> {}

export const AdminUsersAPI = {
  /**
   * GET /admin/users：管理员查看用户列表，支持返回全部或分页。
   * 如果需要分页，可扩展为 `{ items: ManagedUser[], total: number }`。
   */
  list() {
    return http.get<ManagedUser[]>('/admin/users');
  },
  /**
   * POST /admin/users：创建新用户。
   * 后端需设置初始密码策略，并返回创建好的用户（带 `id`、`status`、`lastLoginAt` 等字段）。
   */
  create(payload: CreateManagedUserRequest) {
    return http.post<ManagedUser>('/admin/users', payload);
  },
  /**
   * PUT /admin/users/:id：编辑用户信息。
   * 返回更新后的 ManagedUser；如需限制角色切换，请在后端校验。
   */
  update(id: string, payload: UpdateManagedUserRequest) {
    return http.put<ManagedUser>(`/admin/users/${id}`, payload);
  },
  /**
   * POST /admin/users/:id/status：切换账号启用/停用状态。
   * 返回最新 ManagedUser（`status` 已更新）。若目标用户不存在请返回 404。
   */
  toggleStatus(id: string, status: AccountStatus) {
    return http.post<ManagedUser>(`/admin/users/${id}/status`, { data: { status } });
  },
};

/* -------------------------------------------------------------------------- */
/* API Facade                                                                 */
/* -------------------------------------------------------------------------- */

/** 以下部分不用管：把上面定义的接口聚合成一个对象供前端调用。 */
export const API = {
  auth: AuthAPI,
  courses: CoursesAPI,
  assignments: AssignmentsAPI,
  templates: TemplatesAPI,
  scaleRecords: ScaleRecordsAPI,
  notifications: NotificationsAPI,
  adminUsers: AdminUsersAPI,
};

export default API;
