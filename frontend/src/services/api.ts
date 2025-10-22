// Mock API service for testing
export const API = {
  login: async (credentials: any) => {
    return { user: { username: credentials.username, role: 'admin' } }
  },
  logout: async () => {
    return { success: true }
  }
}

export default API
