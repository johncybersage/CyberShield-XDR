import { useEffect, useState } from 'react'
import { ShieldCheck, Server, Users, Activity, CheckCircle, AlertTriangle, AlertCircle } from 'lucide-react'
import logService, { AuditLog } from '@services/logService'
import toast from 'react-hot-toast'

export default function AdminPanel() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLogs()
  }, [])

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const data = await logService.getLogs(1, 50)
      setLogs(data)
    } catch {
      toast.error('Failed to load audit logs. Are you an admin?')
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    if (status === 'success') return <CheckCircle className="w-4 h-4 text-green-500" />
    if (status === 'failure') return <AlertTriangle className="w-4 h-4 text-yellow-500" />
    return <AlertCircle className="w-4 h-4 text-red-500" />
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] space-y-6 text-white pb-6 overflow-hidden">
      
      {/* Header */}
      <div className="flex justify-between items-end shrink-0">
        <div>
          <h1 className="text-2xl font-bold font-heading text-white">Admin Panel</h1>
          <p className="text-gray-400 text-sm mt-1">System configuration and SOC2 compliance tracking.</p>
        </div>
      </div>

      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 shrink-0">
        <div className="bg-dark-300 p-4 rounded-lg border border-dark-200 flex items-center gap-4">
          <div className="p-3 bg-brand-500/20 rounded-lg">
            <Users className="w-6 h-6 text-brand-500" />
          </div>
          <div>
            <div className="text-2xl font-bold">12</div>
            <div className="text-xs text-gray-400 uppercase tracking-wider">Active Users</div>
          </div>
        </div>
        <div className="bg-dark-300 p-4 rounded-lg border border-dark-200 flex items-center gap-4">
          <div className="p-3 bg-green-500/20 rounded-lg">
            <Server className="w-6 h-6 text-green-500" />
          </div>
          <div>
            <div className="text-2xl font-bold">Healthy</div>
            <div className="text-xs text-gray-400 uppercase tracking-wider">System Status</div>
          </div>
        </div>
        <div className="bg-dark-300 p-4 rounded-lg border border-dark-200 flex items-center gap-4">
          <div className="p-3 bg-blue-500/20 rounded-lg">
            <Activity className="w-6 h-6 text-blue-500" />
          </div>
          <div>
            <div className="text-2xl font-bold">{logs.length}+</div>
            <div className="text-xs text-gray-400 uppercase tracking-wider">Audit Events</div>
          </div>
        </div>
        <div className="bg-dark-300 p-4 rounded-lg border border-dark-200 flex items-center gap-4">
          <div className="p-3 bg-purple-500/20 rounded-lg">
            <ShieldCheck className="w-6 h-6 text-purple-500" />
          </div>
          <div>
            <div className="text-2xl font-bold">Strict</div>
            <div className="text-xs text-gray-400 uppercase tracking-wider">Auth Policy</div>
          </div>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="flex-1 bg-dark-300 rounded-lg border border-dark-200 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-dark-200 bg-dark-400/50 flex justify-between items-center">
          <h2 className="font-medium text-sm">Immutable Audit Trail</h2>
        </div>
        <div className="flex-1 overflow-auto">
          <table className="w-full text-left border-collapse whitespace-nowrap">
            <thead className="sticky top-0 bg-dark-400 shadow-sm z-10">
              <tr className="border-b border-dark-200 text-xs uppercase tracking-wider text-gray-400">
                <th className="p-4 font-medium">Timestamp</th>
                <th className="p-4 font-medium">Actor</th>
                <th className="p-4 font-medium">Action</th>
                <th className="p-4 font-medium">Resource</th>
                <th className="p-4 font-medium">IP Address</th>
                <th className="p-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-200 text-sm">
              {loading && logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-gray-500">Loading audit trail...</td>
                </tr>
              ) : logs.length > 0 ? (
                logs.map(log => (
                  <tr key={log.id} className="hover:bg-dark-200/50 transition-colors">
                    <td className="p-4 text-gray-400 font-mono text-xs">{new Date(log.created_at).toLocaleString()}</td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{log.username || 'System'}</span>
                        {log.user_role === 'admin' && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase bg-brand-500/20 text-brand-400">Admin</span>
                        )}
                      </div>
                    </td>
                    <td className="p-4 font-mono text-xs text-brand-300">{log.action}</td>
                    <td className="p-4 text-gray-400 text-xs">
                      {log.resource_type ? `${log.resource_type}:${log.resource_id?.substring(0,8)}` : '-'}
                    </td>
                    <td className="p-4 text-gray-400 font-mono text-xs">{log.ip_address || 'internal'}</td>
                    <td className="p-4">
                      <div className="flex items-center gap-1.5">
                        {getStatusIcon(log.status)}
                        <span className="capitalize">{log.status}</span>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="p-12 text-center text-gray-500">
                    No audit logs available for this viewport.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
