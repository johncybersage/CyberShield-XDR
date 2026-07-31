import apiClient from './apiClient'

export interface PhishingAnalysis {
  id: string
  subject?: string
  sender?: string
  sender_domain?: string
  recipient?: string
  message_id?: string
  verdict: 'clean' | 'suspicious' | 'phishing' | 'spam' | 'unknown'
  confidence_score: number
  spf_pass?: boolean
  dkim_pass?: boolean
  dmarc_pass?: boolean
  urls_found: number
  url_details?: { urls: Array<{ url: string, is_malicious: boolean }> }
  header_anomalies?: Record<string, string>
  raw_headers?: string
  body_text?: string
  created_at: string
}

const phishingService = {
  async getAnalyses(page = 1, verdict?: string): Promise<PhishingAnalysis[]> {
    const { data } = await apiClient.get<PhishingAnalysis[]>('/phishing', {
      params: { page, verdict }
    })
    return data
  },

  async analyzeFile(file: File): Promise<PhishingAnalysis> {
    const formData = new FormData()
    formData.append('file', file)
    
    const { data } = await apiClient.post<PhishingAnalysis>('/phishing/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return data
  },

  async analyzeText(rawText: string): Promise<PhishingAnalysis> {
    const formData = new FormData()
    formData.append('raw_text', rawText)
    
    const { data } = await apiClient.post<PhishingAnalysis>('/phishing/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return data
  }
}

export default phishingService
