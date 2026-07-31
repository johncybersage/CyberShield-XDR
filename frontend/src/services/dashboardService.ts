import apiClient from './apiClient'

export interface MetricCard {
  label: string
  value: number | string
  change_pct: number
  trend: 'up' | 'down' | 'neutral'
}

export interface SeverityBreakdown {
  critical: number
  high: number
  medium: number
  low: number
  info: number
}

export interface TimeSeriesPoint {
  timestamp: string
  value: number
}

export interface TopItem {
  label: string
  count: number
  percentage: number
}

export interface RecentAlert {
  id: string
  title: string
  severity: string
  source: string
  created_at: string
  status: string
}

export interface DashboardStats {
  total_assets: MetricCard
  open_alerts: MetricCard
  active_scans: MetricCard
  threat_intel_iocs: MetricCard
  risk_score: MetricCard

  alerts_by_severity: SeverityBreakdown
  assets_by_status: Record<string, number>

  alerts_over_time: TimeSeriesPoint[]
  scans_over_time: TimeSeriesPoint[]

  top_attacked_assets: TopItem[]
  top_threat_countries: TopItem[]
  top_mitre_techniques: TopItem[]

  recent_alerts: RecentAlert[]
}

const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    const { data } = await apiClient.get<DashboardStats>('/dashboard')
    return data
  }
}

export default dashboardService
