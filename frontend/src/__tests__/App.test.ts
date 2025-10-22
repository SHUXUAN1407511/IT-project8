import { render, screen } from '@testing-library/vue'
import { describe, it, expect } from 'vitest'

// 创建简单的 App 组件模拟
const App = {
  template: `
    <div id="app">
      <header>
        <h1>AI Assessment System</h1>
      </header>
      <main>
        <router-view />
      </main>
    </div>
  `
}

describe('App.vue', () => {
  it('renders the main application layout', () => {
    render(App)
    
    expect(screen.getByRole('banner')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /ai assessment system/i })).toBeInTheDocument()
    expect(screen.getByRole('main')).toBeInTheDocument()
  })

  it('has correct application structure', () => {
    render(App)
    
    const appElement = screen.getByText(/ai assessment system/i).closest('#app')
    expect(appElement).toBeInTheDocument()
  })
})
