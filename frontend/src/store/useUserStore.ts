import { defineStore } from 'pinia';
import API, { type AccountProfile, type UserRole, type LoginResponse } from '@/services/api';
import { logger } from '@/utils/logger';

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null as AccountProfile | null,
    role: '' as '' | UserRole,
    isAuthenticated: false,
  }),
  getters: {
    currentUser(state) {
      return state.userInfo;
    },
  },
  actions: {
    async login(payload: { username: string; password: string }) {
      const response = (await API.auth.login({
        username: payload.username,
        password: payload.password,
      })) as LoginResponse;
      this.applyLoginState(payload, response);
    },
    async register(payload: { username: string; password: string; role: UserRole }) {
      await API.auth.register(payload);
    },
    async logout() {
      try {
        await API.auth.logout();
      } catch (error) {
        logger.warn('Logout request failed', error);
      }
      this.userInfo = null;
      this.role = '';
      this.isAuthenticated = false;
      localStorage.removeItem('token');
      localStorage.removeItem('username');
    },
    async refreshProfile() {
      if (!this.isAuthenticated) {
        return null;
      }
      const profile = (await API.auth.getProfile()) as AccountProfile;
      const merged = {
        ...(this.userInfo || profile),
        ...profile,
      };
      this.userInfo = merged;
      if (profile.role) {
        this.role = profile.role;
      }
      return this.userInfo;
    },
    async updateProfile(updates: Partial<Omit<AccountProfile, 'id' | 'username' | 'role'>>) {
      if (!this.userInfo) {
        throw new Error('Not signed in.');
      }
      const profile = (await API.auth.updateProfile(updates)) as AccountProfile;
      const merged = {
        ...this.userInfo,
        ...profile,
      };
      this.userInfo = merged;
      if (profile.role) {
        this.role = profile.role;
      }
      return this.userInfo;
    },
    async changePassword(currentPassword: string, newPassword: string) {
      await API.auth.changePassword({ currentPassword, newPassword });
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
      localStorage.setItem('username', profile.username);
    },
  },
});

export type { UserRole, AccountProfile } from '@/services/api';
