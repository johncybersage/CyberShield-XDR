import apiClient from './apiClient'

export interface AuditLog {
  id: string
  user_id?: string
  username?: string
  user_role?: string
  action: string
  resource_type?: string
  resource_id?: string
  ip_address?: string
  user_agent?: string
  request_id?: string
  status: 'success' | 'failure' | 'error'
  details?: Record<string, any>
  error_message?: string
  created_at: string
}

const logService = {
  async getLogs(page = 1, pageSize = 50): Promise<AuditLog[]> {
    const { data } = await apiClient.get<AuditLog[]>('/logs', {
      params: { page, page_size: pageSize }
    })
    return data
  }
}

export default logService
