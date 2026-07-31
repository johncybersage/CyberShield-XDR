import { useEffect, useState } from 'react'
import { ShieldAlert, Search, Database, Globe, Hash, Shield, AlertTriangle, CheckCircle, Activity } from 'lucide-react'
import threatIntelService, { ThreatIntel } from '@services/threatIntelService'
import toast from 'react-hot-toast'
import Button from '@components/ui/Button'

export default function ThreatIntelligence() {
  const [iocs, setIocs] = useState<ThreatIntel[]>([])
  const [loading, setLoading] = useState(true)
  const [search] = useState('')
  const [lookupValue, setLookupValue] = useState('')
  const [isLookingUp, setIsLookingUp] = useState(false)
  const [selectedIoc, setSelectedIoc] = useState<ThreatIntel | null>(null)

  useEffect(() => {
    fetchIOCs()
  }, [])

  const fetchIOCs = async () => {
    try {
      setLoading(true)
      const data = await threatIntelService.getIOCs(1, search)
      setIocs(data)
      if (data.length > 0 && !selectedIoc) setSelectedIoc(data[0])
    } catch {
      toast.error('Failed to load IOC history')
    } finally {
      setLoading(false)
    }
  }

  const handleLookup = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!lookupValue.trim()) return

    try {
      setIsLookingUp(true)
      const data = await threatIntelService.lookupIOC(lookupValue.trim())
      setSelectedIoc(data)
      setLookupValue('')
      
      // Update history list if it's new
      setIocs(prev => {
        const exists = prev.some(i => i.id === data.id)
        return exists ? prev.map(i => i.id === data.id ? data : i) : [data, ...prev]
      })
      toast.success('IOC lookup complete')
    } catch {
      toast.error('Failed to lookup IOC')
    } finally {
      setIsLookingUp(false)
    }
  }

  const getIocIcon = (type: string) => {
    if (type === 'ip') return <Globe className="w-4 h-4 text-blue-400" />
    if (type.includes('hash')) return <Hash className="w-4 h-4 text-orange-400" />
    return <Database className="w-4 h-4 text-purple-400" />
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] space-y-6 text-white pb-6">
      
      {/* Header & Lookup Bar */}
      <div className="bg-dark-300 p-6 rounded-lg border border-dark-200 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold font-heading">Threat Intelligence</h1>
          <p className="text-sm text-gray-400 mt-1">Enrich indicators of compromise via VT, AbuseIPDB, and OTX</p>
        </div>
        
        <form onSubmit={handleLookup} className="flex gap-2 w-full md:w-auto">
          <div className="relative flex-1 md:w-80">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="IP, Domain, URL, or File Hash..."
              className="w-full pl-9 pr-4 py-2 bg-dark-400 border border-dark-200 rounded-md text-sm text-white focus:ring-1 focus:ring-brand-500 focus:border-brand-500 outline-none transition-shadow"
              value={lookupValue}
              onChange={e => setLookupValue(e.target.value)}
              disabled={isLookingUp}
            />
          </div>
          <Button type="submit" variant="primary" disabled={!lookupValue.trim() || isLookingUp}>
            {isLookingUp ? 'Scanning...' : 'Lookup'}
          </Button>
        </form>
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        {/* History Sidebar */}
        <div className="w-1/3 bg-dark-300 rounded-lg border border-dark-200 flex flex-col overflow-hidden hidden md:flex">
          <div className="p-4 border-b border-dark-200 bg-dark-400/50">
            <h2 className="font-medium">Recent Lookups</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {loading ? (
              <div className="p-4 text-center text-gray-500 text-sm">Loading...</div>
            ) : iocs.length > 0 ? iocs.map(ioc => (
              <button
                key={ioc.id}
                onClick={() => setSelectedIoc(ioc)}
                className={`w-full text-left p-3 rounded-md transition-colors flex items-center justify-between ${
                  selectedIoc?.id === ioc.id ? 'bg-dark-200 border border-dark-100' : 'hover:bg-dark-200/50 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  {getIocIcon(ioc.ioc_type)}
                  <div className="truncate">
                    <div className="text-sm font-medium truncate text-white">{ioc.value}</div>
                    <div className="text-xs text-gray-500 flex items-center gap-2 mt-0.5">
                      <span className="uppercase">{ioc.ioc_type.replace('_', ' ')}</span>
                      <span>•</span>
                      <span>{new Date(ioc.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                <div className="shrink-0 ml-2">
                  <div className={`w-2 h-2 rounded-full ${ioc.is_malicious ? 'bg-red-500' : ioc.threat_score > 0 ? 'bg-yellow-500' : 'bg-green-500'}`} />
                </div>
              </button>
            )) : (
              <div className="p-8 text-center text-gray-500 text-sm">No recent lookups found.</div>
            )}
          </div>
        </div>

        {/* Selected IOC Details */}
        <div className="flex-1 bg-dark-300 rounded-lg border border-dark-200 overflow-y-auto">
          {selectedIoc ? (
            <div className="p-6 space-y-8 animate-in fade-in duration-300">
              
              {/* Top Summary */}
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-0.5 bg-dark-100 border border-dark-200 rounded text-xs font-mono text-gray-400 uppercase">
                      {selectedIoc.ioc_type.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider border ${
                      selectedIoc.is_malicious ? 'bg-red-500/10 text-red-500 border-red-500/20' : 
                      selectedIoc.threat_score > 20 ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' : 
                      'bg-green-500/10 text-green-500 border-green-500/20'
                    }`}>
                      {selectedIoc.is_malicious ? 'Malicious' : selectedIoc.threat_score > 20 ? 'Suspicious' : 'Clean'}
                    </span>
                  </div>
                  <h2 className="text-2xl font-bold font-mono break-all">{selectedIoc.value}</h2>
                  <div className="text-sm text-gray-400 mt-2 flex items-center gap-4">
                    {selectedIoc.country_code && (
                      <span className="flex items-center gap-1">
                        <Globe className="w-4 h-4" /> {selectedIoc.country_name || selectedIoc.country_code}
                      </span>
                    )}
                    {selectedIoc.isp && (
                      <span className="flex items-center gap-1">
                        <Activity className="w-4 h-4" /> {selectedIoc.isp}
                      </span>
                    )}
                  </div>
                </div>

                {/* Risk Score Circle */}
                <div className="flex flex-col items-center justify-center p-4 bg-dark-400 rounded-xl border border-dark-200 shrink-0 min-w-32">
                  <span className="text-xs text-gray-400 uppercase tracking-wider mb-1 font-semibold">Threat Score</span>
                  <div className={`text-4xl font-black ${
                    selectedIoc.threat_score >= 50 ? 'text-red-500' :
                    selectedIoc.threat_score >= 20 ? 'text-yellow-500' :
                    'text-green-500'
                  }`}>
                    {Math.round(selectedIoc.threat_score)}<span className="text-lg text-gray-500 font-normal">/100</span>
                  </div>
                </div>
              </div>

              {/* Feed Engines Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                {/* VirusTotal */}
                <div className="bg-dark-400 p-4 rounded-lg border border-dark-200">
                  <div className="flex items-center gap-2 mb-3 text-gray-300 font-medium">
                    <Shield className="w-5 h-5 text-blue-400" /> VirusTotal
                  </div>
                  {selectedIoc.vt_total_count > 0 ? (
                    <div>
                      <div className="flex justify-between items-end mb-2">
                        <span className="text-sm text-gray-400">Malicious Detections</span>
                        <span className="text-lg font-bold">{selectedIoc.vt_malicious_count} <span className="text-sm font-normal text-gray-500">/ {selectedIoc.vt_total_count}</span></span>
                      </div>
                      <div className="h-2 w-full bg-dark-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${selectedIoc.vt_malicious_count > 0 ? 'bg-red-500' : 'bg-green-500'}`} 
                          style={{ width: `${Math.max(2, (selectedIoc.vt_malicious_count / selectedIoc.vt_total_count) * 100)}%` }}
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500 flex items-center gap-2 mt-4"><CheckCircle className="w-4 h-4 text-green-500/50" /> No data found</div>
                  )}
                </div>

                {/* AbuseIPDB */}
                <div className="bg-dark-400 p-4 rounded-lg border border-dark-200">
                  <div className="flex items-center gap-2 mb-3 text-gray-300 font-medium">
                    <AlertTriangle className="w-5 h-5 text-orange-400" /> AbuseIPDB
                  </div>
                  {(selectedIoc.ioc_type === 'ip' && selectedIoc.abuseipdb_data) ? (
                    <div>
                      <div className="flex justify-between items-end mb-2">
                        <span className="text-sm text-gray-400">Confidence Score</span>
                        <span className="text-lg font-bold">{selectedIoc.abuse_confidence_score}%</span>
                      </div>
                      <div className="h-2 w-full bg-dark-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${selectedIoc.abuse_confidence_score > 50 ? 'bg-red-500' : selectedIoc.abuse_confidence_score > 0 ? 'bg-yellow-500' : 'bg-green-500'}`} 
                          style={{ width: `${Math.max(2, selectedIoc.abuse_confidence_score)}%` }}
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500 flex items-center gap-2 mt-4"><CheckCircle className="w-4 h-4 text-green-500/50" /> Not applicable</div>
                  )}
                </div>

                {/* AlienVault OTX */}
                <div className="bg-dark-400 p-4 rounded-lg border border-dark-200">
                  <div className="flex items-center gap-2 mb-3 text-gray-300 font-medium">
                    <Database className="w-5 h-5 text-purple-400" /> AlienVault OTX
                  </div>
                  {selectedIoc.otx_data ? (
                    <div className="flex items-center justify-between mt-4">
                      <span className="text-sm text-gray-400">Pulses Detected</span>
                      <span className="text-2xl font-bold">{selectedIoc.otx_pulse_count}</span>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500 flex items-center gap-2 mt-4"><CheckCircle className="w-4 h-4 text-green-500/50" /> No data found</div>
                  )}
                </div>

              </div>
              
              {/* Raw JSON Data Preview (For Analysts) */}
              <div className="space-y-3">
                <h3 className="font-semibold text-gray-300 uppercase tracking-wider text-xs border-b border-dark-200 pb-2">Analysis Details</h3>
                <div className="bg-dark-400 p-4 rounded-lg border border-dark-200 font-mono text-xs text-gray-400 overflow-x-auto">
                  Last Checked: {new Date(selectedIoc.last_checked || selectedIoc.created_at).toLocaleString()}<br/>
                  Source: {selectedIoc.source}<br/><br/>
                  {selectedIoc.virustotal_data && selectedIoc.virustotal_data.mock && "Note: API Keys not configured. Displaying mock data.\n"}
                  {JSON.stringify(
                    {
                      category: selectedIoc.threat_category,
                      geo: selectedIoc.country_code ? `${selectedIoc.country_code} - ${selectedIoc.asn}` : 'N/A',
                      vt_stats: selectedIoc.virustotal_data?.last_analysis_stats || {},
                      otx_pulses: selectedIoc.otx_data?.pulse_info?.count || 0
                    },
                    null,
                    2
                  )}
                </div>
              </div>

            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-500 p-8 text-center">
              <ShieldAlert className="w-16 h-16 mb-4 opacity-20 text-brand-500" />
              <h3 className="text-xl font-medium text-white mb-2">No IOC Selected</h3>
              <p className="max-w-md">Select an indicator from the recent lookups list or use the search bar above to query a new IP, Domain, or Hash.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
