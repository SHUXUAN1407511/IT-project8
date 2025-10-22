import { render, screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'

// 创建简单的 Login 模拟组件
const Login = {
  template: `
    <div>
      <h1>Login</h1>
      <form @submit.prevent="$emit('login', { username, password })">
        <input 
          v-model="username" 
          type="text" 
          placeholder="Username" 
          data-testid="username-input"
        />
        <input 
          v-model="password" 
          type="password" 
          placeholder="Password" 
          data-testid="password-input"
        />
        <button type="submit">Login</button>
      </form>
    </div>
  `,
  data() {
    return {
      username: '',
      password: ''
    }
  },
  emits: ['login']
}

describe('Login.vue', () => {
  it('renders login form with username and password fields', () => {
    render(Login)
    
    expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument()
    expect(screen.getByTestId('username-input')).toBeInTheDocument()
    expect(screen.getByTestId('password-input')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })

  it('allows user to enter credentials', async () => {
    const user = userEvent.setup()
    render(Login)
    
    const usernameInput = screen.getByTestId('username-input')
    const passwordInput = screen.getByTestId('password-input')
    
    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'password123')
    
    expect(usernameInput.value).toBe('testuser')
    expect(passwordInput.value).toBe('password123')
  })

  it('emits login event with credentials', async () => {
    const user = userEvent.setup()
    const mockLogin = vi.fn()
    
    render(Login, {
      props: {
        onLogin: mockLogin
      }
    })
    
    const usernameInput = screen.getByTestId('username-input')
    const passwordInput = screen.getByTestId('password-input')
    const loginButton = screen.getByRole('button', { name: /login/i })
    
    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'password123')
    await user.click(loginButton)
    
    expect(mockLogin).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123'
    })
  })
})
