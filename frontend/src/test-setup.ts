import { config } from '@vue/test-utils'
import { beforeEach } from 'vitest'
import '@testing-library/jest-dom'

// 全局测试配置
beforeEach(() => {
  config.global.mocks = {
    $t: (msg: string) => msg
  }
})
