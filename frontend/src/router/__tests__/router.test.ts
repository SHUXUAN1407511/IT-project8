import { describe, it, expect } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'

describe('Router Configuration', () => {
  it('creates router instance successfully', () => {
    const routes = [
      { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
      { path: '/login', name: 'login', component: { template: '<div>Login</div>' } },
      { path: '/dashboard', name: 'dashboard', component: { template: '<div>Dashboard</div>' } }
    ]
    
    const router = createRouter({
      history: createWebHistory(),
      routes,
    })
    
    expect(router).toBeDefined()
    expect(router.getRoutes().length).toBe(3)
  })

  it('has correct route paths', () => {
    const routes = [
      { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
      { path: '/login', name: 'login', component: { template: '<div>Login</div>' } }
    ]
    
    const router = createRouter({
      history: createWebHistory(),
      routes,
    })
    
    const routePaths = router.getRoutes().map(route => route.path)
    expect(routePaths).toContain('/')
    expect(routePaths).toContain('/login')
  })
})
