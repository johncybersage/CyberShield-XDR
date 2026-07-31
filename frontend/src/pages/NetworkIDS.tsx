import { useEffect, useState, useRef } from 'react'
import { Activity, AlertTriangle, ShieldAlert, CheckCircle, RefreshCw, BarChart2, Radio } from 'lucide-react'
import networkService, { NetworkAnalysis } from '@services/networkService'
import toast from 'react-hot-toast'
import Button from '@components/ui/Button'

export default function NetworkIDS() {
  const [analyses, setAnalyses] = useState<NetworkAnalysis[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAnalysis, setSelectedAnalysis] = useState<NetworkAnalysis | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchAnalyses()
    // Poll for updates every 5s if there are pending/running tasks
    const interval = setInterval(() => {
      setAnalyses(prev => {
        if (prev.some(a => a.status === 'pending' || a.status === 'running')) {
          fetchAnalyses(false)
        }
        return prev
      })
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchAnalyses = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true)
      const data = await networkService.getAnalyses()
      setAnalyses(data)
      
      setSelectedAnalysis(prev => {
        if (!prev) return data.length > 0 ? data[0] : null
        return data.find(a => a.id === prev.id) || prev
      })
    } catch {
      if (showLoading) toast.error('Failed to load network analyses')
    } finally {
      setLoading(false)
    }
  }

  const handleFileDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) handleUpload(file)
  }

  const handleUpload = async (file: File) => {
    if (!file.name.endsWith('.pcap') && !file.name.endsWith('.pcapng')) {
      toast.error('Only .pcap or .pcapng files are supported')
      return
    }
    if (file.size > 50 * 1024 * 1024) {
      toast.error('File exceeds 50MB limit')
      return
    }

    try {
      setIsUploading(true)
      const data = await networkService.uploadPcap(file)
      toast.success('PCAP uploaded for analysis')
      setAnalyses(prev => [data, ...prev])
      setSelectedAnalysis(data)
    } catch {
      toast.error('PCAP upload failed')
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const getStatusIcon = (status: string) => {
    if (status === 'completed') return <CheckCircle className="w-4 h-4 text-green-500" />
    if (status === 'failed') return <AlertTriangle className="w-4 h-4 text-red-500" />
    return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />
  }

  const getSeverityBadge = (severity: string) => {
    if (severity === 'critical') return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-500 text-white">Critical</span>
    if (severity === 'high') return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-500/20 text-red-500 border border-red-500/30">High</span>
    if (severity === 'medium') return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-yellow-500/20 text-yellow-500 border border-yellow-500/30">Medium</span>
    return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-gray-500/20 text-gray-400 border border-gray-500/30">Low</span>
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] space-y-6 text-white pb-6">
      
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold font-heading text-white">Network IDS</h1>
          <p className="text-gray-400 text-sm mt-1">PCAP Anomaly Detection & Protocol Analysis</p>
        </div>
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        {/* Sidebar */}
        <div className="w-1/3 flex flex-col gap-6 overflow-hidden">
          
          {/* Upload Dropzone */}
          <div 
            className="border-2 border-dashed border-dark-200 rounded-lg bg-dark-300 p-8 text-center hover:border-brand-500 transition-colors cursor-pointer shrink-0 group relative overflow-hidden"
            onDragOver={e => e.preventDefault()}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="absolute inset-0 bg-brand-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
            <input 
              type="file" 
              accept=".pcap,.pcapng"
              className="hidden" 
              ref={fileInputRef} 
              onChange={e => e.target.files?.[0] && handleUpload(e.target.files[0])} 
            />
            <Radio className="w-12 h-12 text-gray-500 mx-auto mb-4 group-hover:text-brand-400 transition-colors" />
            <h3 className="text-lg font-medium mb-1">Upload PCAP</h3>
            <p className="text-sm text-gray-400">Drag & drop .pcap (Max 50MB)</p>
            {isUploading && <p className="text-sm text-brand-400 mt-2 font-medium animate-pulse">Uploading...</p>}
          </div>

          {/* Analysis History */}
          <div className="bg-dark-300 rounded-lg border border-dark-200 flex-1 flex flex-col overflow-hidden hidden md:flex">
            <div className="p-4 border-b border-dark-200 bg-dark-400/50 flex justify-between items-center">
              <h2 className="font-medium text-sm">Capture History</h2>
              <Button size="sm" variant="ghost" onClick={() => fetchAnalyses(true)}>
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {loading && analyses.length === 0 ? (
                <div className="p-4 text-center text-gray-500 text-sm">Loading...</div>
              ) : analyses.length > 0 ? analyses.map(item => (
                <button
                  key={item.id}
                  onClick={() => setSelectedAnalysis(item)}
                  className={`w-full text-left p-3 rounded-md transition-colors flex items-center justify-between ${
                    selectedAnalysis?.id === item.id ? 'bg-dark-200 border border-dark-100' : 'hover:bg-dark-200/50 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3 overflow-hidden">
                    <Activity className="w-4 h-4 text-gray-400 shrink-0" />
                    <div className="truncate">
                      <div className="text-sm font-medium truncate text-white">{item.filename}</div>
                      <div className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                        {new Date(item.created_at).toLocaleTimeString()} · {(item.file_size / 1024 / 1024).toFixed(2)} MB
                      </div>
                    </div>
                  </div>
                  <div className="shrink-0 ml-2">
                    {getStatusIcon(item.status)}
                  </div>
                </button>
              )) : (
                <div className="p-8 text-center text-gray-500 text-sm">No analysis history found.</div>
              )}
            </div>
          </div>
        </div>

        {/* Selected Analysis Details */}
        <div className="flex-1 bg-dark-300 rounded-lg border border-dark-200 overflow-y-auto relative">
          {selectedAnalysis ? (
            <div className="p-6 space-y-6 animate-in fade-in duration-300">
              
              {/* Header block */}
              <div className="flex justify-between items-start border-b border-dark-200 pb-6">
                <div>
                  <div className="flex gap-2 mb-2">
                    <span className="px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider bg-dark-400 border border-dark-200 text-gray-300">
                      {selectedAnalysis.status}
                    </span>
                    {selectedAnalysis.anomalies_found > 0 && (
                      <span className="px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider bg-red-500/10 border border-red-500/20 text-red-500 flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3" /> {selectedAnalysis.anomalies_found} Anomalies
                      </span>
                    )}
                  </div>
                  <h2 className="text-2xl font-bold font-mono text-white">{selectedAnalysis.filename}</h2>
                  <div className="text-sm text-gray-400 mt-2 flex items-center gap-4">
                    <span>Uploaded: {new Date(selectedAnalysis.created_at).toLocaleString()}</span>
                    <span>Size: {(selectedAnalysis.file_size / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                </div>
              </div>

              {selectedAnalysis.status === 'pending' || selectedAnalysis.status === 'running' ? (
                <div className="py-20 text-center flex flex-col items-center">
                  <div className="relative mb-6">
                    <Activity className="w-16 h-16 text-brand-500 animate-pulse" />
                    <div className="absolute inset-0 border-t-2 border-brand-500 rounded-full animate-spin" />
                  </div>
                  <h3 className="text-xl font-medium">Parsing Packets...</h3>
                  <p className="text-gray-400 mt-2">The IDS engine is inspecting protocols and payloads.</p>
                </div>
              ) : selectedAnalysis.status === 'failed' ? (
                <div className="py-20 text-center flex flex-col items-center">
                  <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />
                  <h3 className="text-xl font-medium">Analysis Failed</h3>
                  <p className="text-red-400 mt-2 font-mono text-sm max-w-lg">{selectedAnalysis.error_message}</p>
                </div>
              ) : (
                <div className="space-y-6">
                  
                  {/* Stats Cards */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-dark-400 p-4 rounded-lg border border-dark-200">
                      <div className="text-xs text-gray-400 uppercase tracking-wider font-semibold mb-1">Total Packets</div>
                      <div className="text-2xl font-bold text-white">{selectedAnalysis.total_packets.toLocaleString()}</div>
                    </div>
                    <div className="bg-dark-400 p-4 rounded-lg border border-dark-200">
                      <div className="text-xs text-brand-400 uppercase tracking-wider font-semibold mb-1">TCP Flows</div>
                      <div className="text-2xl font-bold text-white">{selectedAnalysis.tcp_count.toLocaleString()}</div>
                    </div>
                    <div className="bg-dark-400 p-4 rounded-lg border border-dark-200">
                      <div className="text-xs text-purple-400 uppercase tracking-wider font-semibold mb-1">UDP Flows</div>
                      <div className="text-2xl font-bold text-white">{selectedAnalysis.udp_count.toLocaleString()}</div>
                    </div>
                    <div className="bg-dark-400 p-4 rounded-lg border border-dark-200">
                      <div className="text-xs text-green-400 uppercase tracking-wider font-semibold mb-1">ICMP / Other</div>
                      <div className="text-2xl font-bold text-white">{(selectedAnalysis.icmp_count + selectedAnalysis.other_count).toLocaleString()}</div>
                    </div>
                  </div>

                  {/* Protocol Distribution Bar */}
                  <div className="bg-dark-400 p-5 rounded-lg border border-dark-200">
                    <h3 className="font-semibold text-gray-300 uppercase tracking-wider text-xs mb-4 flex items-center gap-2">
                      <BarChart2 className="w-4 h-4" /> Protocol Distribution
                    </h3>
                    <div className="h-4 w-full bg-dark-500 rounded-full overflow-hidden flex">
                      <div className="h-full bg-brand-500 transition-all" style={{ width: `${(selectedAnalysis.tcp_count / Math.max(1, selectedAnalysis.total_packets)) * 100}%` }} title="TCP" />
                      <div className="h-full bg-purple-500 transition-all" style={{ width: `${(selectedAnalysis.udp_count / Math.max(1, selectedAnalysis.total_packets)) * 100}%` }} title="UDP" />
                      <div className="h-full bg-green-500 transition-all" style={{ width: `${((selectedAnalysis.icmp_count + selectedAnalysis.other_count) / Math.max(1, selectedAnalysis.total_packets)) * 100}%` }} title="Other" />
                    </div>
                    <div className="flex gap-4 mt-3 text-xs text-gray-400">
                      <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-brand-500" /> TCP ({Math.round((selectedAnalysis.tcp_count / Math.max(1, selectedAnalysis.total_packets)) * 100)}%)</div>
                      <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-purple-500" /> UDP ({Math.round((selectedAnalysis.udp_count / Math.max(1, selectedAnalysis.total_packets)) * 100)}%)</div>
                      <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-green-500" /> Other ({Math.round(((selectedAnalysis.icmp_count + selectedAnalysis.other_count) / Math.max(1, selectedAnalysis.total_packets)) * 100)}%)</div>
                    </div>
                  </div>

                  {/* Anomalies Table */}
                  <div className="bg-dark-400 rounded-lg border border-dark-200 overflow-hidden">
                    <div className="p-4 border-b border-dark-200 bg-dark-500/30 flex items-center gap-2">
                      <ShieldAlert className={`w-4 h-4 ${selectedAnalysis.anomalies_found > 0 ? 'text-red-400' : 'text-gray-400'}`} />
                      <h3 className="font-semibold text-gray-300 uppercase tracking-wider text-xs">Detected Anomalies</h3>
                    </div>
                    
                    {selectedAnalysis.anomaly_details?.anomalies && selectedAnalysis.anomaly_details.anomalies.length > 0 ? (
                      <div className="divide-y divide-dark-200">
                        {selectedAnalysis.anomaly_details.anomalies.map((anomaly, idx) => (
                          <div key={idx} className="p-4 flex flex-col md:flex-row gap-4 items-start md:items-center hover:bg-dark-300/50 transition-colors">
                            <div className="shrink-0 w-24">
                              {getSeverityBadge(anomaly.severity)}
                            </div>
                            <div className="flex-1">
                              <div className="font-mono text-sm text-red-300 mb-1">{anomaly.type}</div>
                              <div className="text-sm text-gray-400">{anomaly.description}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-8 text-center text-gray-500 text-sm flex flex-col items-center justify-center">
                        <CheckCircle className="w-8 h-8 text-green-500/50 mb-3" />
                        No malicious signatures or anomalies detected in this capture.
                      </div>
                    )}
                  </div>

                </div>
              )}
            </div>
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500 p-8 text-center">
              <Activity className="w-16 h-16 mb-4 opacity-20 text-brand-500" />
              <h3 className="text-xl font-medium text-white mb-2">Network IDS Dashboard</h3>
              <p className="max-w-md text-sm">Select a PCAP from the history queue or upload a new packet capture to begin deep packet inspection.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
