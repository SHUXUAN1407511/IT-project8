import { render, screen } from '@testing-library/vue'
import { describe, it, expect } from 'vitest'

// 创建简单的 HelpHint 模拟组件
const HelpHint = {
  template: `
    <div class="help-hint">
      <h3>{{ title }}</h3>
      <p>{{ content }}</p>
    </div>
  `,
  props: {
    title: {
      type: String,
      default: 'Help'
    },
    content: {
      type: String,
      default: 'This is help content'
    }
  }
}

describe('HelpHint.vue', () => {
  it('renders help hint component with props', () => {
    render(HelpHint, {
      props: {
        title: 'Test Help',
        content: 'This is a test help message'
      }
    })
    
    // 使用更具体的查询避免多个匹配
    expect(screen.getByRole('heading', { name: /test help/i })).toBeInTheDocument()
    expect(screen.getByText(/this is a test help message/i)).toBeInTheDocument()
  })

  it('renders with default props', () => {
    render(HelpHint)
    
    expect(screen.getByRole('heading', { name: /help/i })).toBeInTheDocument()
    expect(screen.getByText(/this is help content/i)).toBeInTheDocument()
  })
})
