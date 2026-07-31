import { useEffect, useState } from 'react'
import { FileText, Download, CheckCircle, RefreshCw, AlertTriangle, FileSpreadsheet, PlusCircle } from 'lucide-react'
import reportService, { Report, ReportCreatePayload } from '@services/reportService'
import toast from 'react-hot-toast'
import Button from '@components/ui/Button'

export default function Reports() {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  
  const [formData, setFormData] = useState<ReportCreatePayload>({
    title: '',
    report_type: 'incident',
    report_format: 'csv',
    period_start: '',
    period_end: ''
  })

  useEffect(() => {
    fetchReports()
    const interval = setInterval(() => {
      setReports(prev => {
        if (prev.some(r => r.status === 'pending' || r.status === 'generating')) {
          fetchReports(false)
        }
        return prev
      })
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchReports = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true)
      const data = await reportService.getReports()
      setReports(data)
    } catch {
      if (showLoading) toast.error('Failed to load reports')
    } finally {
      setLoading(false)
    }
  }

  const handleRequestReport = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.title.trim()) {
      toast.error('Title is required')
      return
    }

    try {
      setIsSubmitting(true)
      const newReport = await reportService.requestReport(formData)
      toast.success('Report generation started')
      setReports(prev => [newReport, ...prev])
      setShowForm(false)
      setFormData({
        title: '',
        report_type: 'incident',
        report_format: 'csv',
        period_start: '',
        period_end: ''
      })
    } catch {
      toast.error('Failed to request report')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDownload = async (id: string, filename: string) => {
    try {
      toast.loading('Downloading...', { id: 'download' })
      await reportService.downloadReport(id, filename)
      toast.success('Download complete', { id: 'download' })
    } catch {
      toast.error('Failed to download report', { id: 'download' })
    }
  }

  const getStatusBadge = (status: string) => {
    if (status === 'completed') return <span className="flex items-center gap-1 text-xs font-bold text-green-500"><CheckCircle className="w-3 h-3" /> Ready</span>
    if (status === 'failed') return <span className="flex items-center gap-1 text-xs font-bold text-red-500"><AlertTriangle className="w-3 h-3" /> Failed</span>
    return <span className="flex items-center gap-1 text-xs font-bold text-blue-500"><RefreshCw className="w-3 h-3 animate-spin" /> Generating</span>
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] space-y-6 text-white pb-6">
      
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold font-heading text-white">Automated Reports</h1>
          <p className="text-gray-400 text-sm mt-1">Generate on-demand CSV data exports for compliance and auditing.</p>
        </div>
        <Button variant="primary" onClick={() => setShowForm(!showForm)}>
          <PlusCircle className="w-4 h-4 mr-2" /> New Report
        </Button>
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        
        {/* Form Panel (Collapsible) */}
        {showForm && (
          <div className="w-1/3 bg-dark-300 rounded-lg border border-dark-200 p-6 overflow-y-auto animate-in slide-in-from-left-4">
            <h2 className="text-lg font-bold mb-6 flex items-center gap-2"><FileText className="w-5 h-5 text-brand-500" /> Configure Report</h2>
            <form onSubmit={handleRequestReport} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Report Title</label>
                <input 
                  type="text" 
                  value={formData.title}
                  onChange={e => setFormData({...formData, title: e.target.value})}
                  className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none"
                  placeholder="e.g. Q3 Incident Summary"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Data Source (Type)</label>
                <select
                  value={formData.report_type}
                  onChange={e => setFormData({...formData, report_type: e.target.value})}
                  className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none"
                >
                  <option value="incident">Incidents & Alerts</option>
                  <option value="threat_intel">Threat Intelligence (IOCs)</option>
                  <option value="asset_inventory">Asset Inventory</option>
                  <option value="executive_summary" disabled>Executive Summary (Coming Soon)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Export Format</label>
                <select
                  value={formData.report_format}
                  onChange={e => setFormData({...formData, report_format: e.target.value})}
                  className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none"
                >
                  <option value="csv">CSV (Excel Compatible)</option>
                  <option value="pdf" disabled>PDF Document (Premium)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Start Date (Optional)</label>
                  <input 
                    type="date" 
                    value={formData.period_start}
                    onChange={e => setFormData({...formData, period_start: e.target.value})}
                    className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none text-gray-300"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">End Date (Optional)</label>
                  <input 
                    type="date" 
                    value={formData.period_end}
                    onChange={e => setFormData({...formData, period_end: e.target.value})}
                    className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none text-gray-300"
                  />
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-3 border-t border-dark-200">
                <Button variant="ghost" type="button" onClick={() => setShowForm(false)}>Cancel</Button>
                <Button variant="primary" type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Queueing...' : 'Generate Report'}
                </Button>
              </div>
            </form>
          </div>
        )}

        {/* History Table */}
        <div className="flex-1 bg-dark-300 rounded-lg border border-dark-200 flex flex-col overflow-hidden">
          <div className="p-4 border-b border-dark-200 bg-dark-400/50 flex justify-between items-center">
            <h2 className="font-medium">Generation History</h2>
            <Button size="sm" variant="ghost" onClick={() => fetchReports(true)}>
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex-1 overflow-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-dark-200 text-xs uppercase tracking-wider text-gray-400 bg-dark-400/30">
                  <th className="p-4 font-medium">Title</th>
                  <th className="p-4 font-medium">Type</th>
                  <th className="p-4 font-medium">Requested</th>
                  <th className="p-4 font-medium">Status</th>
                  <th className="p-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-200">
                {loading && reports.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-gray-500">Loading reports...</td>
                  </tr>
                ) : reports.length > 0 ? (
                  reports.map(report => (
                    <tr key={report.id} className="hover:bg-dark-200/50 transition-colors">
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-dark-400 rounded">
                            <FileSpreadsheet className="w-4 h-4 text-brand-400" />
                          </div>
                          <span className="font-medium text-sm">{report.title}</span>
                        </div>
                      </td>
                      <td className="p-4 text-sm text-gray-400 uppercase">{report.report_type.replace('_', ' ')}</td>
                      <td className="p-4 text-sm text-gray-400">{new Date(report.created_at).toLocaleString()}</td>
                      <td className="p-4">{getStatusBadge(report.status)}</td>
                      <td className="p-4 text-right">
                        <Button 
                          size="sm" 
                          variant="secondary"
                          disabled={report.status !== 'completed'}
                          onClick={() => handleDownload(report.id, `report_${report.id}.${report.report_format}`)}
                        >
                          <Download className="w-4 h-4 mr-2" /> Download
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="p-12 text-center">
                      <FileText className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                      <div className="text-gray-400">No reports generated yet.</div>
                      <Button variant="ghost" className="mt-4 text-brand-400" onClick={() => setShowForm(true)}>
                        Create your first report
                      </Button>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
