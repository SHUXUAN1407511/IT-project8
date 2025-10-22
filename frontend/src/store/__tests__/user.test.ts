import { describe, it, expect } from 'vitest'

// 模拟 Pinia store
const createMockStore = () => {
  return {
    user: null,
    isLoggedIn: false,
    setUser(userData: any) {
      this.user = userData
      this.isLoggedIn = true
    },
    clearUser() {
      this.user = null
      this.isLoggedIn = false
    }
  }
}

describe('Store Logic Tests', () => {
  it('user store sets user data correctly', () => {
    const userStore = createMockStore()
    const userData = { username: 'testuser', role: 'admin' }
    
    userStore.setUser(userData)
    
    expect(userStore.user).toEqual(userData)
    expect(userStore.isLoggedIn).toBe(true)
  })

  it('user store clears data on logout', () => {
    const userStore = createMockStore()
    const userData = { username: 'testuser', role: 'admin' }
    
    userStore.setUser(userData)
    userStore.clearUser()
    
    expect(userStore.user).toBeNull()
    expect(userStore.isLoggedIn).toBe(false)
  })

  it('handles multiple user roles', () => {
    const roles = ['admin', 'sc', 'tutor']
    const userStore = createMockStore()
    
    roles.forEach(role => {
      userStore.setUser({ username: 'testuser', role })
      expect(userStore.user.role).toBe(role)
      userStore.clearUser()
    })
  })
})
