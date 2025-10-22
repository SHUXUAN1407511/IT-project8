import { describe, it, expect, vi, beforeEach } from 'vitest'

// 创建简单的 http service 模拟
const http = {
  async get(url: string) {
    const response = await fetch(url)
    return response.json()
  },
  async post(url: string, data: any) {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    return response.json()
  }
}

// 模拟 fetch
global.fetch = vi.fn()

describe('http service', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('makes GET request successfully', async () => {
    const mockResponse = { data: [{ id: 1, name: 'Test Template' }] }
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const response = await http.get('/api/assignments')
    
    expect(fetch).toHaveBeenCalledWith('/api/assignments')
    expect(response).toEqual(mockResponse)
  })

  it('handles POST request with data', async () => {
    const templateData = { name: 'New Template', type: 'Research' }
    const mockResponse = { id: 1, ...templateData }
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const response = await http.post('/api/assignments', templateData)
    
    expect(fetch).toHaveBeenCalledWith('/api/assignments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(templateData),
    })
    expect(response).toEqual(mockResponse)
  })

  it('handles network errors', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'))
    
    await expect(http.get('/api/assignments')).rejects.toThrow('Network error')
  })
})
