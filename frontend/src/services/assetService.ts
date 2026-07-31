import apiClient from './apiClient'

export interface Asset {
  id: string
  ip_address: string
  hostname?: string
  asset_type: string
  status: string
  risk_score: number
  criticality: string
  owner?: string
  last_seen?: string
}

export interface PaginatedAssets {
  items: Asset[]
  total: number
  page: number
  page_size: number
}

const assetService = {
  async getAssets(params?: Record<string, any>) {
    const { data } = await apiClient.get<PaginatedAssets>('/assets', { params })
    return data
  },
  
  async createAsset(payload: Partial<Asset>) {
    const { data } = await apiClient.post<Asset>('/assets', payload)
    return data
  },
  
  async deleteAsset(id: string) {
    await apiClient.delete(`/assets/${id}`)
  }
}

export default assetService
