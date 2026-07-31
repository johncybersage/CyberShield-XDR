import { useEffect, useState, useRef } from 'react'
import { Mail, UploadCloud, ShieldAlert, CheckCircle, AlertTriangle, Link as LinkIcon, FileText, Code } from 'lucide-react'
import phishingService, { PhishingAnalysis } from '@services/phishingService'
import toast from 'react-hot-toast'
import Button from '@components/ui/Button'

export default function PhishingDetector() {
  const [analyses, setAnalyses] = useState<PhishingAnalysis[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAnalysis, setSelectedAnalysis] = useState<PhishingAnalysis | null>(null)
  
  // Upload States
  const [activeTab, setActiveTab] = useState<'upload' | 'paste'>('upload')
  const [rawText, setRawText] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchAnalyses()
  }, [])

  const fetchAnalyses = async () => {
    try {
      setLoading(true)
      const data = await phishingService.getAnalyses()
      setAnalyses(data)
      if (data.length > 0 && !selectedAnalysis) setSelectedAnalysis(data[0])
    } catch {
      toast.error('Failed to load phishing history')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    try {
      setIsAnalyzing(true)
      const data = await phishingService.analyzeFile(file)
      toast.success('Email analyzed successfully')
      setAnalyses(prev => [data, ...prev])
      setSelectedAnalysis(data)
    } catch {
      toast.error('Failed to analyze email file')
    } finally {
      setIsAnalyzing(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleTextSubmit = async () => {
    if (!rawText.trim()) return
    try {
      setIsAnalyzing(true)
      const data = await phishingService.analyzeText(rawText)
      toast.success('Email analyzed successfully')
      setAnalyses(prev => [data, ...prev])
      setSelectedAnalysis(data)
      setRawText('')
    } catch {
      toast.error('Failed to analyze raw text')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getVerdictBadge = (verdict: string) => {
    if (verdict === 'phishing') return <span className="px-2 py-0.5 rounded text-xs font-bold uppercase border bg-red-500/10 text-red-500 border-red-500/20">Phishing</span>
    if (verdict === 'suspicious') return <span className="px-2 py-0.5 rounded text-xs font-bold uppercase border bg-yellow-500/10 text-yellow-500 border-yellow-500/20">Suspicious</span>
    if (verdict === 'clean') return <span className="px-2 py-0.5 rounded text-xs font-bold uppercase border bg-green-500/10 text-green-500 border-green-500/20">Clean</span>
    return <span className="px-2 py-0.5 rounded text-xs font-bold uppercase border bg-gray-500/10 text-gray-400 border-gray-500/20">Unknown</span>
  }

  const renderAuthIcon = (status?: boolean) => {
    if (status === true) return <CheckCircle className="w-4 h-4 text-green-500" />
    if (status === false) return <AlertTriangle className="w-4 h-4 text-red-500" />
    return <ShieldAlert className="w-4 h-4 text-gray-500" />
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] space-y-6 text-white pb-6">
      
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold font-heading text-white">Phishing Detector</h1>
          <p className="text-gray-400 text-sm mt-1">AI and heuristic-based email analysis</p>
        </div>
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        {/* Sidebar */}
        <div className="w-1/3 flex flex-col gap-6 overflow-hidden">
          
          {/* Input Area */}
          <div className="bg-dark-300 rounded-lg border border-dark-200 overflow-hidden shrink-0 flex flex-col">
            <div className="flex border-b border-dark-200">
              <button 
                className={`flex-1 py-3 text-sm font-medium ${activeTab === 'upload' ? 'bg-dark-400 text-brand-400 border-b-2 border-brand-500' : 'text-gray-400 hover:bg-dark-400/50'}`}
                onClick={() => setActiveTab('upload')}
              >
                Upload EML
              </button>
              <button 
                className={`flex-1 py-3 text-sm font-medium ${activeTab === 'paste' ? 'bg-dark-400 text-brand-400 border-b-2 border-brand-500' : 'text-gray-400 hover:bg-dark-400/50'}`}
                onClick={() => setActiveTab('paste')}
              >
                Paste Raw
              </button>
            </div>
            
            <div className="p-6">
              {activeTab === 'upload' ? (
                <div 
                  className="border-2 border-dashed border-dark-200 rounded-lg bg-dark-400/50 p-8 text-center hover:border-brand-500 transition-colors cursor-pointer"
                  onDragOver={e => e.preventDefault()}
                  onDrop={e => { e.preventDefault(); if (e.dataTransfer.files[0]) handleFileUpload(e.dataTransfer.files[0]) }}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input type="file" accept=".eml,.txt" className="hidden" ref={fileInputRef} onChange={e => { if (e.target.files?.[0]) handleFileUpload(e.target.files[0]) }} />
                  <UploadCloud className="w-10 h-10 text-gray-500 mx-auto mb-3" />
                  <h3 className="text-sm font-medium">Upload .eml file</h3>
                  {isAnalyzing && <p className="text-xs text-brand-400 mt-2 font-medium animate-pulse">Analyzing...</p>}
                </div>
              ) : (
                <div className="flex flex-col gap-3">
                  <textarea 
                    className="w-full h-32 bg-dark-400 border border-dark-200 rounded-md p-3 text-xs font-mono text-gray-300 focus:ring-1 focus:ring-brand-500 outline-none resize-none"
                    placeholder="Paste raw email headers and body here..."
                    value={rawText}
                    onChange={e => setRawText(e.target.value)}
                  />
                  <Button variant="primary" onClick={handleTextSubmit} disabled={!rawText.trim() || isAnalyzing}>
                    {isAnalyzing ? 'Analyzing...' : 'Analyze Text'}
                  </Button>
                </div>
              )}
            </div>
          </div>

          {/* History */}
          <div className="bg-dark-300 rounded-lg border border-dark-200 flex-1 flex flex-col overflow-hidden">
            <div className="p-3 border-b border-dark-200 bg-dark-400/50">
              <h2 className="font-medium text-sm">Recent Analyses</h2>
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {loading ? (
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
                    <Mail className="w-4 h-4 text-gray-400 shrink-0" />
                    <div className="truncate">
                      <div className="text-sm font-medium truncate text-white">{item.subject || 'No Subject'}</div>
                      <div className="text-xs text-gray-500 truncate">{item.sender || 'Unknown Sender'}</div>
                    </div>
                  </div>
                  <div className="shrink-0 ml-2">
                    <div className={`w-2 h-2 rounded-full ${item.verdict === 'phishing' ? 'bg-red-500' : item.verdict === 'suspicious' ? 'bg-yellow-500' : 'bg-green-500'}`} />
                  </div>
                </button>
              )) : (
                <div className="p-8 text-center text-gray-500 text-sm">No history found.</div>
              )}
            </div>
          </div>
        </div>

        {/* Selected Analysis Details */}
        <div className="flex-1 bg-dark-300 rounded-lg border border-dark-200 overflow-y-auto">
          {selectedAnalysis ? (
            <div className="p-6 space-y-6 animate-in fade-in duration-300">
              
              {/* Header block */}
              <div className="flex justify-between items-start border-b border-dark-200 pb-6">
                <div className="flex-1 mr-4">
                  <div className="mb-3">
                    {getVerdictBadge(selectedAnalysis.verdict)}
                  </div>
                  <h2 className="text-xl font-bold mb-3">{selectedAnalysis.subject || '(No Subject)'}</h2>
                  <div className="space-y-1 text-sm text-gray-300">
                    <div><span className="text-gray-500 w-16 inline-block">From:</span> {selectedAnalysis.sender || 'N/A'}</div>
                    <div><span className="text-gray-500 w-16 inline-block">To:</span> {selectedAnalysis.recipient || 'N/A'}</div>
                    <div><span className="text-gray-500 w-16 inline-block">Date:</span> {new Date(selectedAnalysis.created_at).toLocaleString()}</div>
                  </div>
                </div>

                <div className="flex flex-col items-center justify-center p-4 bg-dark-400 rounded-xl border border-dark-200 min-w-32 shrink-0">
                  <span className="text-xs text-gray-400 uppercase tracking-wider mb-1 font-semibold">Phishing Risk</span>
                  <div className={`text-3xl font-black ${selectedAnalysis.confidence_score >= 70 ? 'text-red-500' : selectedAnalysis.confidence_score >= 30 ? 'text-yellow-500' : 'text-green-500'}`}>
                    {Math.round(selectedAnalysis.confidence_score)}%
                  </div>
                </div>
              </div>

              {/* Authentication & Anomalies */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-dark-400 p-4 rounded-lg border border-dark-200">
                  <h3 className="font-semibold text-gray-300 uppercase tracking-wider text-xs mb-4">Email Authentication</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-2 bg-dark-300 rounded">
                      <span className="text-sm font-medium">SPF</span>
                      <div className="flex items-center gap-2 text-sm">
                        {selectedAnalysis.spf_pass === true ? 'Pass' : selectedAnalysis.spf_pass === false ? 'Fail' : 'None'}
                        {renderAuthIcon(selectedAnalysis.spf_pass)}
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-dark-300 rounded">
                      <span className="text-sm font-medium">DKIM</span>
                      <div className="flex items-center gap-2 text-sm">
                        {selectedAnalysis.dkim_pass === true ? 'Pass' : selectedAnalysis.dkim_pass === false ? 'Fail' : 'None'}
                        {renderAuthIcon(selectedAnalysis.dkim_pass)}
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-dark-300 rounded">
                      <span className="text-sm font-medium">DMARC</span>
                      <div className="flex items-center gap-2 text-sm">
                        {selectedAnalysis.dmarc_pass === true ? 'Pass' : selectedAnalysis.dmarc_pass === false ? 'Fail' : 'None'}
                        {renderAuthIcon(selectedAnalysis.dmarc_pass)}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-dark-400 p-4 rounded-lg border border-dark-200">
                  <h3 className="font-semibold text-gray-300 uppercase tracking-wider text-xs mb-4">Header Anomalies</h3>
                  {selectedAnalysis.header_anomalies && Object.keys(selectedAnalysis.header_anomalies).length > 0 ? (
                    <div className="space-y-2">
                      {Object.entries(selectedAnalysis.header_anomalies).map(([key, value]) => (
                        <div key={key} className="flex gap-2 text-sm text-red-400 bg-red-500/10 p-2 rounded border border-red-500/20">
                          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                          <span>{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500/50" /> No header anomalies detected.
                    </div>
                  )}
                </div>
              </div>

              {/* Extracted URLs */}
              <div className="bg-dark-400 p-4 rounded-lg border border-dark-200">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-300 uppercase tracking-wider text-xs">Extracted URLs ({selectedAnalysis.urls_found})</h3>
                </div>
                {selectedAnalysis.url_details?.urls && selectedAnalysis.url_details.urls.length > 0 ? (
                  <div className="max-h-48 overflow-y-auto space-y-1">
                    {selectedAnalysis.url_details.urls.map((u, i) => (
                      <div key={i} className="text-xs font-mono text-gray-400 bg-dark-500 p-2 rounded border border-dark-300 flex items-start gap-2 break-all">
                        <LinkIcon className="w-3 h-3 mt-0.5 shrink-0" />
                        {u.url}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-gray-500">No URLs found in the email body.</div>
                )}
              </div>

              {/* Raw Data Tabs */}
              <div className="bg-dark-400 rounded-lg border border-dark-200 overflow-hidden">
                <div className="p-3 border-b border-dark-200 flex gap-4 bg-dark-500/50">
                  <div className="text-xs font-semibold uppercase text-gray-300 flex items-center gap-2"><FileText className="w-3 h-3" /> Body Text</div>
                </div>
                <div className="p-4 max-h-64 overflow-y-auto font-mono text-xs text-gray-400 whitespace-pre-wrap">
                  {selectedAnalysis.body_text || 'No body text extracted.'}
                </div>
                <div className="p-3 border-y border-dark-200 flex gap-4 bg-dark-500/50">
                  <div className="text-xs font-semibold uppercase text-gray-300 flex items-center gap-2"><Code className="w-3 h-3" /> Raw Headers</div>
                </div>
                <div className="p-4 max-h-64 overflow-y-auto font-mono text-xs text-gray-400 whitespace-pre-wrap">
                  {selectedAnalysis.raw_headers || 'No headers available.'}
                </div>
              </div>

            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-500 p-8 text-center">
              <Mail className="w-16 h-16 mb-4 opacity-20 text-brand-500" />
              <h3 className="text-xl font-medium text-white mb-2">No Email Selected</h3>
              <p className="max-w-md">Upload an EML file or paste raw email headers to run a phishing analysis.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
