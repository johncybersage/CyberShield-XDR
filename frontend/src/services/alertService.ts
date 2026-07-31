import apiClient from './apiClient'

export interface Alert {
  id: string
  title: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  status: 'new' | 'open' | 'investigating' | 'resolved' | 'closed'
  source: string
  src_ip?: string
  dst_ip?: string
  src_port?: number
  dst_port?: number
  protocol?: string
  mitre_tactic?: string
  mitre_technique?: string
  mitre_technique_id?: string
  risk_score: number
  confidence: number
  ai_summary?: string
  ai_recommendations?: string
  notes?: string
  timeline?: Array<{
    timestamp: string
    action: string
    note?: string
    user?: string
    changes?: string[]
  }>
  tags?: Record<string, string>
  is_false_positive: boolean
  asset_id?: string
  assigned_to_id?: string
  created_at: string
  updated_at: string
}

export interface AlertListResponse {
  items: Alert[]
  total: number
  page: number
  page_size: number
}

export interface AlertListParams {
  page?: number
  page_size?: number
  severity?: string
  status?: string
  source?: string
  search?: string
  asset_id?: string
  sort_by?: string
  sort_dir?: 'asc' | 'desc'
}

const alertService = {
  async getAlerts(params: AlertListParams = {}): Promise<AlertListResponse> {
    const { data } = await apiClient.get<AlertListResponse>('/alerts', { params })
    return data
  },

  async getAlert(id: string): Promise<Alert> {
    const { data } = await apiClient.get<Alert>(`/alerts/${id}`)
    return data
  },

  async updateAlert(id: string, updates: Partial<Alert>): Promise<Alert> {
    const { data } = await apiClient.patch<Alert>(`/alerts/${id}`, updates)
    return data
  },

  async addTimelineNote(id: string, action: string, note: string): Promise<Alert> {
    const { data } = await apiClient.post<Alert>(`/alerts/${id}/timeline`, { action, note })
    return data
  },

  async deleteAlert(id: string): Promise<void> {
    await apiClient.delete(`/alerts/${id}`)
  }
}

export default alertService
