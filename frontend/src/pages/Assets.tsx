import { useState, useEffect } from 'react'
import { Server, Search, Plus, Filter, AlertCircle, RefreshCw } from 'lucide-react'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import assetService, { PaginatedAssets } from '@services/assetService'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

export default function Assets() {
  const [data, setData] = useState<PaginatedAssets | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)

  const fetchAssets = async () => {
    try {
      setLoading(true)
      const res = await assetService.getAssets({ page, page_size: 20, search })
      setData(res)
    } catch (error) {
      toast.error('Failed to fetch assets')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAssets()
  }, [page, search])

  const getRiskBadge = (score: number) => {
    if (score >= 90) return 'badge-critical'
    if (score >= 70) return 'badge-high'
    if (score >= 40) return 'badge-medium'
    return 'badge-low'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Server className="w-6 h-6 text-cyber-400" />
            Network Assets
          </h1>
          <p className="text-sm text-gray-400 mt-1">Manage and monitor discovered infrastructure</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={fetchAssets} disabled={loading}>
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
          <Button variant="primary">
            <Plus className="w-4 h-4 mr-2" />
            Add Asset
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="cyber-card p-4 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input 
            placeholder="Search by IP, hostname..."
            leftIcon={<Search className="w-4 h-4" />}
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        <Button variant="outline">
          <Filter className="w-4 h-4 mr-2" />
          More Filters
        </Button>
      </div>

      {/* Data Table */}
      <div className="cyber-card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-dark-200/50 border-b border-cyber-900/50 text-gray-400">
              <tr>
                <th className="px-6 py-4 font-medium">Asset</th>
                <th className="px-6 py-4 font-medium">IP Address</th>
                <th className="px-6 py-4 font-medium">Type</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">Risk Score</th>
                <th className="px-6 py-4 font-medium">Last Seen</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-900/30">
              {loading && !data ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
                    Loading assets...
                  </td>
                </tr>
              ) : data?.items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                    <AlertCircle className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                    <p className="text-lg font-medium text-gray-400">No assets found</p>
                    <p className="text-sm mt-1">Try adjusting your search or run a discovery scan.</p>
                  </td>
                </tr>
              ) : (
                data?.items.map((asset) => (
                  <tr key={asset.id} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-white">{asset.hostname || 'Unknown Host'}</div>
                      <div className="text-xs text-gray-500">{asset.id.split('-')[0]}</div>
                    </td>
                    <td className="px-6 py-4 font-mono text-cyber-300">{asset.ip_address}</td>
                    <td className="px-6 py-4 capitalize text-gray-300">{asset.asset_type}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${asset.status === 'active' ? 'bg-threat-low/10 text-threat-low border-threat-low/20' : 'bg-gray-800 text-gray-400 border-gray-700'}`}>
                        {asset.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${getRiskBadge(asset.risk_score)}`}>
                        {asset.risk_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-400 text-xs">
                      {asset.last_seen ? format(new Date(asset.last_seen), 'MMM d, HH:mm') : 'Never'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Button variant="ghost" size="sm">View</Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {/* Pagination Footer */}
        {data && data.total > 0 && (
          <div className="px-6 py-4 border-t border-cyber-900/50 flex items-center justify-between">
            <div className="text-sm text-gray-400">
              Showing <span className="text-white font-medium">{(page - 1) * 20 + 1}</span> to{' '}
              <span className="text-white font-medium">{Math.min(page * 20, data.total)}</span> of{' '}
              <span className="text-white font-medium">{data.total}</span> results
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
                Previous
              </Button>
              <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)} disabled={page * 20 >= data.total}>
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
