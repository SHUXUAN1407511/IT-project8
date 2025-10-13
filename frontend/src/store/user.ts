import { defineStore } from 'pinia';
import API, { type AccountProfile, type UserRole, type LoginResponse } from '@/services/api';

interface Credentials {
  username: string;
  password: string;
}

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null as AccountProfile | null,
    role: '' as '' | UserRole,
    isAuthenticated: false,
    credentials: null as Credentials | null,
  }),
  getters: {
    currentUser(state) {
      return state.userInfo;
    },
  },
  actions: {
    async login(payload: { username: string; password: string }) {
      const response = await API.auth.login({
        username: payload.username,
        password: payload.password,
      });
      this.applyLoginState(payload, response);
    },
    async register(payload: { username: string; password: string; role: UserRole }) {
      await API.auth.register(payload);
    },
    logout() {
      this.userInfo = null;
      this.role = '';
      this.isAuthenticated = false;
      this.credentials = null;
      localStorage.removeItem('token');
      localStorage.removeItem('username');
    },
    updateProfile(updates: Partial<Omit<AccountProfile, 'id' | 'username' | 'role'>>) {
      if (!this.userInfo) return;
      this.userInfo = { ...this.userInfo, ...updates };
    },
    changePassword(currentPassword: string, newPassword: string) {
      if (!this.credentials) {
        throw new Error('Not signed in.');
      }
      if (this.credentials.password !== currentPassword) {
        throw new Error('Current password is incorrect.');
      }
      this.credentials = { ...this.credentials, password: newPassword };
    },
    applyLoginState(
      payload: { username: string; password: string },
      response: LoginResponse,
    ) {
      const token = response.token;
      if (token) {
        localStorage.setItem('token', token);
      }
      const role = response.user?.role;
      if (!role) {
        throw new Error('Login succeeded but no role was returned.');
      }
      const profile: AccountProfile = {
        id: response.user?.id || `user_${Math.random().toString(36).slice(2, 10)}`,
        username: response.user?.username || payload.username,
        name: response.user?.name || payload.username,
        email: response.user?.email,
        role,
        status: response.user?.status || 'active',
        phone: response.user?.phone,
        organization: response.user?.organization,
        bio: response.user?.bio,
      };
      this.userInfo = profile;
      this.role = role;
      this.isAuthenticated = true;
      this.credentials = { username: payload.username, password: payload.password };
      localStorage.setItem('username', profile.username);
    },
  },
});

export type { UserRole, AccountProfile } from '@/services/api';
