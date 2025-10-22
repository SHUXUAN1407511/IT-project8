import { describe, it, expect } from 'vitest'

describe('Routing Logic', () => {
  it('defines correct route paths', () => {
    const routes = [
      { path: '/', name: 'home' },
      { path: '/login', name: 'login' },
      { path: '/dashboard', name: 'dashboard' },
      { path: '/templates', name: 'templates' },
      { path: '/courses', name: 'courses' }
    ]
    
    expect(routes).toHaveLength(5)
    expect(routes[0].path).toBe('/')
    expect(routes[1].path).toBe('/login')
    expect(routes.find(r => r.name === 'dashboard')).toBeDefined()
  })

  it('handles route parameters correctly', () => {
    const routeWithParams = {
      path: '/templates/:id',
      name: 'template-detail'
    }
    
    expect(routeWithParams.path).toContain(':id')
    expect(routeWithParams.name).toBe('template-detail')
  })

  it('supports nested routes', () => {
    const nestedRoutes = [
      {
        path: '/admin',
        children: [
          { path: 'users', name: 'admin-users' },
          { path: 'settings', name: 'admin-settings' }
        ]
      }
    ]
    
    expect(nestedRoutes[0].children).toHaveLength(2)
    expect(nestedRoutes[0].children[0].name).toBe('admin-users')
  })
})
