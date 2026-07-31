import { useEffect, useState, useCallback } from 'react'
import { Search, ShieldAlert, Clock, Info, CheckCircle, XCircle } from 'lucide-react'
import alertService, { Alert } from '@services/alertService'
import { useWebSocket } from '@hooks/useWebSocket'
import toast from 'react-hot-toast'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'

const SEVERITY_COLORS = {
  critical: 'bg-red-500/10 text-red-500 border-red-500/20',
  high: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  medium: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  low: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  info: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
}

const STATUS_COLORS = {
  new: 'bg-blue-500/10 text-blue-500',
  open: 'bg-yellow-500/10 text-yellow-500',
  investigating: 'bg-purple-500/10 text-purple-500',
  resolved: 'bg-green-500/10 text-green-500',
  closed: 'bg-gray-500/10 text-gray-400',
}

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const [noteText, setNoteText] = useState('')
  
  // WebSocket Connection
  useWebSocket(useCallback((event: any) => {
    if (event.type === 'alert.new') {
      toast('New Alert Detected', { icon: '🚨' })
      // Fetch full alert details or prepend to list
      alertService.getAlert(event.data.id).then(newAlert => {
        setAlerts(prev => [newAlert, ...prev].slice(0, 50)) // Keep latest 50
        setTotal(prev => prev + 1)
      })
    } else if (event.type === 'alert.updated') {
      setAlerts(prev => prev.map(a => a.id === event.data.id ? { ...a, ...event.data } : a))
      if (selectedAlert?.id === event.data.id) {
        setSelectedAlert(prev => prev ? { ...prev, ...event.data } : null)
      }
    }
  }, [selectedAlert]))

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const data = await alertService.getAlerts({ page, page_size: 20, search })
      setAlerts(data.items)
      setTotal(data.total)
    } catch (err) {
      toast.error('Failed to load alerts')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
  }, [page, search])

  const handleUpdateStatus = async (id: string, status: Alert['status']) => {
    try {
      const updated = await alertService.updateAlert(id, { status })
      setAlerts(prev => prev.map(a => a.id === id ? updated : a))
      if (selectedAlert?.id === id) setSelectedAlert(updated)
      toast.success('Alert status updated')
    } catch {
      toast.error('Failed to update status')
    }
  }

  const handleAddNote = async () => {
    if (!selectedAlert || !noteText.trim()) return
    try {
      const updated = await alertService.addTimelineNote(selectedAlert.id, 'comment', noteText)
      setSelectedAlert(updated)
      setAlerts(prev => prev.map(a => a.id === updated.id ? updated : a))
      setNoteText('')
      toast.success('Note added')
    } catch {
      toast.error('Failed to add note')
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] space-x-6 text-white overflow-hidden pb-6">
      {/* Main List */}
      <div className={`flex flex-col flex-1 bg-dark-300 rounded-lg border border-dark-200 overflow-hidden ${selectedAlert ? 'hidden lg:flex' : 'flex'}`}>
        <div className="p-4 border-b border-dark-200 flex justify-between items-center bg-dark-300">
          <div>
            <h1 className="text-xl font-bold font-heading">Alert Management</h1>
            <p className="text-sm text-gray-400 mt-1">{total} total alerts</p>
          </div>
          <div className="flex gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search IPs or Titles..."
                className="pl-9 pr-4 py-2 bg-dark-400 border border-dark-200 rounded-md text-sm text-white focus:ring-1 focus:ring-brand-500 focus:border-brand-500 w-64 outline-none transition-shadow"
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-auto">
          {loading ? (
             <div className="flex h-full items-center justify-center">
               <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
             </div>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="bg-dark-400/50 text-gray-400 sticky top-0 border-b border-dark-200">
                <tr>
                  <th className="px-4 py-3 font-medium">Severity</th>
                  <th className="px-4 py-3 font-medium">Title & Source</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium hidden md:table-cell">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-200">
                {alerts.map(alert => (
                  <tr 
                    key={alert.id} 
                    onClick={() => setSelectedAlert(alert)}
                    className={`hover:bg-dark-200/50 cursor-pointer transition-colors ${selectedAlert?.id === alert.id ? 'bg-dark-200' : ''}`}
                  >
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${SEVERITY_COLORS[alert.severity]}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-white">{alert.title}</div>
                      <div className="text-xs text-gray-400 mt-0.5">{alert.source} • {alert.src_ip || 'N/A'}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-1 rounded-md text-xs font-medium ${STATUS_COLORS[alert.status]}`}>
                        {alert.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-400 hidden md:table-cell whitespace-nowrap">
                      {new Date(alert.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
                {alerts.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                      <ShieldAlert className="w-12 h-12 mx-auto mb-3 opacity-20" />
                      No alerts found matching your criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
        
        {/* Pagination */}
        <div className="p-4 border-t border-dark-200 flex justify-between items-center bg-dark-300">
          <Button variant="ghost" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
          <span className="text-sm text-gray-400">Page {page}</span>
          <Button variant="ghost" onClick={() => setPage(p => p + 1)} disabled={alerts.length < 20}>Next</Button>
        </div>
      </div>

      {/* Details Slide-over / Pane */}
      {selectedAlert && (
        <div className="flex flex-col w-full lg:w-1/3 bg-dark-300 rounded-lg border border-dark-200 overflow-hidden shrink-0 animate-in slide-in-from-right-8 duration-200">
          <div className="p-4 border-b border-dark-200 flex justify-between items-start bg-dark-300">
            <div>
              <h2 className="text-lg font-bold">{selectedAlert.title}</h2>
              <div className="flex gap-2 mt-2">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${SEVERITY_COLORS[selectedAlert.severity]}`}>
                  {selectedAlert.severity}
                </span>
                <span className={`px-2 py-1 rounded-md text-xs font-medium ${STATUS_COLORS[selectedAlert.status]}`}>
                  {selectedAlert.status}
                </span>
              </div>
            </div>
            <button onClick={() => setSelectedAlert(null)} className="text-gray-400 hover:text-white lg:hidden">
              <XCircle className="w-6 h-6" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* Action Bar */}
            <div className="flex flex-wrap gap-2">
              {selectedAlert.status !== 'investigating' && (
                <Button size="sm" variant="primary" onClick={() => handleUpdateStatus(selectedAlert.id, 'investigating')}>
                  Investigate
                </Button>
              )}
              {selectedAlert.status !== 'resolved' && (
                <Button size="sm" variant="outline" onClick={() => handleUpdateStatus(selectedAlert.id, 'resolved')}>
                  Mark Resolved
                </Button>
              )}
              {selectedAlert.status !== 'closed' && (
                <Button size="sm" variant="danger" onClick={() => handleUpdateStatus(selectedAlert.id, 'closed')}>
                  Close Alert
                </Button>
              )}
            </div>

            {/* Details */}
            <div className="space-y-3 text-sm">
              <h3 className="font-semibold text-gray-300 uppercase tracking-wider text-xs border-b border-dark-200 pb-1">Details</h3>
              <div className="grid grid-cols-2 gap-y-3">
                <div>
                  <span className="text-gray-500 block text-xs mb-1">Source</span>
                  <span>{selectedAlert.source}</span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs mb-1">Risk Score</span>
                  <span className={selectedAlert.risk_score > 70 ? 'text-red-400' : 'text-brand-400'}>
                    {selectedAlert.risk_score.toFixed(1)} / 100
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs mb-1">Source IP / Port</span>
                  <span>{selectedAlert.src_ip || 'N/A'} {selectedAlert.src_port ? `:${selectedAlert.src_port}` : ''}</span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs mb-1">Dest IP / Port</span>
                  <span>{selectedAlert.dst_ip || 'N/A'} {selectedAlert.dst_port ? `:${selectedAlert.dst_port}` : ''}</span>
                </div>
                {selectedAlert.mitre_tactic && (
                  <div className="col-span-2">
                    <span className="text-gray-500 block text-xs mb-1">MITRE ATT&CK</span>
                    <span>{selectedAlert.mitre_tactic} → {selectedAlert.mitre_technique} ({selectedAlert.mitre_technique_id})</span>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="font-semibold text-gray-300 uppercase tracking-wider text-xs border-b border-dark-200 pb-1">Description</h3>
              <p className="text-sm text-gray-400 leading-relaxed bg-dark-400 p-3 rounded-md">
                {selectedAlert.description}
              </p>
            </div>

            {/* Timeline */}
            <div className="space-y-3">
              <h3 className="font-semibold text-gray-300 uppercase tracking-wider text-xs border-b border-dark-200 pb-1">Timeline & Notes</h3>
              <div className="space-y-4">
                {selectedAlert.timeline?.map((entry, i) => (
                  <div key={i} className="flex gap-3 text-sm">
                    <div className="mt-1">
                      {entry.action === 'created' ? <Info className="w-4 h-4 text-blue-400" /> :
                       entry.action === 'updated' ? <Clock className="w-4 h-4 text-yellow-400" /> :
                       <CheckCircle className="w-4 h-4 text-green-400" />}
                    </div>
                    <div className="flex-1 bg-dark-400/50 p-2 rounded-md border border-dark-200/50">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-medium text-brand-300 text-xs">{entry.user || 'System'}</span>
                        <span className="text-[10px] text-gray-500">{new Date(entry.timestamp).toLocaleString()}</span>
                      </div>
                      <p className="text-gray-300 text-xs">
                        {entry.note || (entry.action === 'updated' && entry.changes ? `Updated: ${entry.changes.join(', ')}` : entry.action)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="flex gap-2 mt-4">
                <Input 
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  placeholder="Add an investigation note..."
                  className="text-sm"
                  onKeyDown={e => e.key === 'Enter' && handleAddNote()}
                />
                <Button variant="secondary" onClick={handleAddNote} disabled={!noteText.trim()}>Add</Button>
              </div>
            </div>
            
          </div>
        </div>
      )}
    </div>
  )
}
