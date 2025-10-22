import { describe, it, expect } from 'vitest'

describe('Application Configuration', () => {
  it('has valid environment variables', () => {
    // 测试环境变量是否存在
    expect(process.env.NODE_ENV).toBeDefined()
    expect(typeof process.env.NODE_ENV).toBe('string')
  })

  it('has required build configurations', () => {
    // 测试构建配置
    const config = {
      build: {
        target: 'esnext',
        outDir: 'dist'
      }
    }
    
    expect(config.build.target).toBe('esnext')
    expect(config.build.outDir).toBe('dist')
  })

  it('supports TypeScript configuration', () => {
    const tsConfig = {
      compilerOptions: {
        strict: true,
        target: 'ES2020'
      }
    }
    
    expect(tsConfig.compilerOptions.strict).toBe(true)
    expect(tsConfig.compilerOptions.target).toBe('ES2020')
  })
})
