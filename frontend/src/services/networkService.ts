import apiClient from './apiClient'

export interface NetworkAnomaly {
  type: string
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
}

export interface NetworkAnalysis {
  id: string
  filename: string
  file_size: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  total_packets: number
  tcp_count: number
  udp_count: number
  icmp_count: number
  other_count: number
  anomalies_found: number
  anomaly_details?: { anomalies: NetworkAnomaly[] }
  error_message?: string
  created_at: string
}

const networkService = {
  async getAnalyses(page = 1): Promise<NetworkAnalysis[]> {
    const { data } = await apiClient.get<NetworkAnalysis[]>('/network', {
      params: { page }
    })
    return data
  },

  async uploadPcap(file: File): Promise<NetworkAnalysis> {
    const formData = new FormData()
    formData.append('file', file)
    
    const { data } = await apiClient.post<NetworkAnalysis>('/network/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return data
  },

  async getAnalysis(id: string): Promise<NetworkAnalysis> {
    const { data } = await apiClient.get<NetworkAnalysis>(`/network/${id}`)
    return data
  }
}

export default networkService
