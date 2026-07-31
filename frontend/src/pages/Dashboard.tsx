import { useEffect, useState } from 'react'
import { 
  Activity, AlertTriangle, ShieldAlert, Monitor, 
  ArrowUpRight, ArrowDownRight, Minus 
} from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import dashboardService, { DashboardStats, MetricCard } from '@services/dashboardService'
import toast from 'react-hot-toast'

const SEVERITY_COLORS = {
  critical: '#ff3b3b',
  high: '#ff8a00',
  medium: '#f4c150',
  low: '#3273f6',
  info: '#a0aec0',
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const data = await dashboardService.getStats()
      setStats(data)
    } catch (err) {
      toast.error('Failed to load dashboard metrics')
    } finally {
      setLoading(false)
    }
  }

  if (loading || !stats) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
      </div>
    )
  }

  const renderTrend = (card: MetricCard) => {
    if (card.trend === 'up') return <span className="flex items-center text-red-500"><ArrowUpRight className="w-4 h-4 mr-1" />{card.change_pct}%</span>
    if (card.trend === 'down') return <span className="flex items-center text-green-500"><ArrowDownRight className="w-4 h-4 mr-1" />{Math.abs(card.change_pct)}%</span>
    return <span className="flex items-center text-gray-500"><Minus className="w-4 h-4 mr-1" />0%</span>
  }

  const pieData = [
    { name: 'Critical', value: stats.alerts_by_severity.critical, color: SEVERITY_COLORS.critical },
    { name: 'High', value: stats.alerts_by_severity.high, color: SEVERITY_COLORS.high },
    { name: 'Medium', value: stats.alerts_by_severity.medium, color: SEVERITY_COLORS.medium },
    { name: 'Low', value: stats.alerts_by_severity.low, color: SEVERITY_COLORS.low },
    { name: 'Info', value: stats.alerts_by_severity.info, color: SEVERITY_COLORS.info },
  ].filter(d => d.value > 0)

  return (
    <div className="space-y-6 text-white pb-10">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold font-heading text-white">SOC Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Live threat monitoring and system status</p>
        </div>
      </div>

      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {[
          { ...stats.total_assets, icon: Monitor },
          { ...stats.open_alerts, icon: AlertTriangle },
          { ...stats.active_scans, icon: Activity },
          { ...stats.threat_intel_iocs, icon: ShieldAlert },
          { ...stats.risk_score, icon: ShieldAlert }, // Could use a custom icon
        ].map((card, i) => (
          <div key={i} className="bg-dark-300 p-5 rounded-lg border border-dark-200 flex flex-col">
            <div className="flex justify-between items-start mb-4">
              <span className="text-gray-400 text-sm font-medium">{card.label}</span>
              <div className="p-2 bg-dark-200 rounded-lg text-brand-400">
                <card.icon className="w-5 h-5" />
              </div>
            </div>
            <div className="flex items-baseline gap-3">
              <h3 className="text-2xl font-bold">{card.value}</h3>
              {card.change_pct !== undefined && (
                <div className="text-sm font-medium">{renderTrend(card as MetricCard)}</div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <div className="lg:col-span-2 bg-dark-300 p-5 rounded-lg border border-dark-200 h-96 flex flex-col">
          <h3 className="text-lg font-medium mb-4">Alerts Over Time (7 Days)</h3>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.alerts_over_time} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3273f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3273f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" vertical={false} />
                <XAxis dataKey="timestamp" stroke="#a0aec0" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#a0aec0" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1a202c', borderColor: '#2d3748', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area type="monotone" dataKey="value" stroke="#3273f6" strokeWidth={2} fillOpacity={1} fill="url(#colorValue)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Donut Chart */}
        <div className="bg-dark-300 p-5 rounded-lg border border-dark-200 h-96 flex flex-col">
          <h3 className="text-lg font-medium mb-4">Open Alerts by Severity</h3>
          {pieData.length > 0 ? (
            <div className="flex-1 min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="45%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: '#1a202c', borderColor: '#2d3748', color: '#fff', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Legend verticalAlign="bottom" height={36} iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              No open alerts
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Attacked Assets */}
        <div className="bg-dark-300 p-5 rounded-lg border border-dark-200">
          <h3 className="text-lg font-medium mb-4">Top Attacked Assets</h3>
          <div className="space-y-4">
            {stats.top_attacked_assets.length > 0 ? stats.top_attacked_assets.map((item, i) => (
              <div key={i} className="flex items-center justify-between">
                <span className="text-sm text-gray-300">{item.label}</span>
                <div className="flex items-center gap-3 w-1/2">
                  <div className="h-2 w-full bg-dark-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-brand-500 rounded-full" 
                      style={{ width: `${Math.min(100, (item.count / (stats.top_attacked_assets[0]?.count || 1)) * 100)}%` }}
                    />
                  </div>
                  <span className="text-xs font-mono text-gray-400 w-8 text-right">{item.count}</span>
                </div>
              </div>
            )) : (
              <div className="text-gray-500 text-sm text-center py-4">No data available</div>
            )}
          </div>
        </div>

        {/* Recent Alerts Feed */}
        <div className="bg-dark-300 p-5 rounded-lg border border-dark-200">
          <h3 className="text-lg font-medium mb-4">Recent Alerts</h3>
          <div className="space-y-3">
            {stats.recent_alerts.length > 0 ? stats.recent_alerts.map((alert) => (
              <div key={alert.id} className="flex flex-col p-3 bg-dark-200 rounded-lg border border-dark-100">
                <div className="flex justify-between items-start mb-1">
                  <span className="text-sm font-medium truncate pr-2">{alert.title}</span>
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded
                    ${alert.severity === 'critical' ? 'bg-red-500/10 text-red-500' :
                      alert.severity === 'high' ? 'bg-orange-500/10 text-orange-500' :
                      alert.severity === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                      alert.severity === 'low' ? 'bg-blue-500/10 text-blue-500' :
                      'bg-gray-500/10 text-gray-400'
                    }
                  `}>
                    {alert.severity}
                  </span>
                </div>
                <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                  <span>{alert.source}</span>
                  <span>{new Date(alert.created_at).toLocaleString()}</span>
                </div>
              </div>
            )) : (
              <div className="text-gray-500 text-sm text-center py-4">No recent alerts</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
