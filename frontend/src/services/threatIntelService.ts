import apiClient from './apiClient'

export interface ThreatIntel {
  id: string
  ioc_type: string
  value: string
  abuse_confidence_score: number
  vt_malicious_count: number
  vt_total_count: number
  otx_pulse_count: number
  threat_category: string
  threat_score: number
  is_malicious: boolean
  country_code?: string
  country_name?: string
  asn?: string
  isp?: string
  mitre_techniques?: Record<string, any>
  abuseipdb_data?: Record<string, any>
  virustotal_data?: Record<string, any>
  otx_data?: Record<string, any>
  tags?: Record<string, any>
  description?: string
  last_checked?: string
  source?: string
  created_at: string
  updated_at: string
}

const threatIntelService = {
  async getIOCs(page = 1, search = ''): Promise<ThreatIntel[]> {
    const { data } = await apiClient.get<ThreatIntel[]>('/threat-intel', {
      params: { page, search }
    })
    return data
  },

  async lookupIOC(value: string): Promise<ThreatIntel> {
    const { data } = await apiClient.post<ThreatIntel>('/threat-intel/lookup', null, {
      params: { value }
    })
    return data
  },

  async getIOC(id: string): Promise<ThreatIntel> {
    const { data } = await apiClient.get<ThreatIntel>(`/threat-intel/${id}`)
    return data
  }
}

export default threatIntelService
