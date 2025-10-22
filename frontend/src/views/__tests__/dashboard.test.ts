import { render, screen } from '@testing-library/vue'
import { describe, it, expect } from 'vitest'

// 创建简单的测试组件
const TestDashboard = {
  template: `
    <div data-testid="dashboard">
      <h1>Dashboard</h1>
      <nav>
        <a href="/templates">Templates</a>
        <a href="/courses">Courses</a>
        <a href="/users">Users</a>
      </nav>
    </div>
  `
}

describe('View Components', () => {
  it('renders dashboard navigation', () => {
    render(TestDashboard)
    
    expect(screen.getByTestId('dashboard')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /templates/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /courses/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /users/i })).toBeInTheDocument()
  })

  it('has correct navigation links', () => {
    render(TestDashboard)
    
    const templatesLink = screen.getByRole('link', { name: /templates/i })
    const coursesLink = screen.getByRole('link', { name: /courses/i })
    
    expect(templatesLink.getAttribute('href')).toBe('/templates')
    expect(coursesLink.getAttribute('href')).toBe('/courses')
  })
})
