import apiClient from './apiClient'

export interface Scan {
  id: string
  target_ip: string
  scan_type: string
  status: string
  risk_score: number
  open_ports_count: number
  vulnerabilities_count: number
  critical_count: number
  high_count: number
  started_at?: string
  completed_at?: string
  created_at: string
  cvss_max: number
  duration_seconds?: number
  findings?: any[]
}

export interface PaginatedScans {
  items: Scan[]
  total: number
  page: number
  page_size: number
}

const scanService = {
  async getScans(params?: Record<string, any>) {
    const { data } = await apiClient.get<PaginatedScans>('/scans', { params })
    return data
  },
  
  async triggerScan(payload: { target_ip: string, scan_type: string, target_ports?: string }) {
    const { data } = await apiClient.post<Scan>('/scans', payload)
    return data
  },
  
  async getScanById(id: string) {
    const { data } = await apiClient.get<Scan>(`/scans/${id}`)
    return data
  }
}

export default scanService
