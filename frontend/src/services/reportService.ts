import apiClient from './apiClient'

export interface Report {
  id: string
  title: string
  report_type: 'executive_summary' | 'vulnerability' | 'incident' | 'weekly' | 'monthly' | 'threat_intel' | 'malware' | 'phishing' | 'asset_inventory'
  report_format: 'pdf' | 'csv' | 'excel' | 'json'
  status: 'pending' | 'generating' | 'completed' | 'failed'
  period_start?: string
  period_end?: string
  parameters?: Record<string, any>
  file_size?: number
  download_url?: string
  created_at: string
}

export interface ReportCreatePayload {
  title: string
  report_type: string
  report_format: string
  period_start?: string
  period_end?: string
}

const reportService = {
  async getReports(page = 1): Promise<Report[]> {
    const { data } = await apiClient.get<Report[]>('/reports', {
      params: { page }
    })
    return data
  },

  async requestReport(payload: ReportCreatePayload): Promise<Report> {
    const { data } = await apiClient.post<Report>('/reports', payload)
    return data
  },

  async downloadReport(id: string, filename: string): Promise<void> {
    const response = await apiClient.get(`/reports/${id}/download`, {
      responseType: 'blob'
    })
    
    // Create blob link to download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
  }
}

export default reportService
