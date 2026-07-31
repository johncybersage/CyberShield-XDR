import apiClient from './apiClient'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatResponse {
  response: string
  model_used: string
  is_mock: boolean
}

const aiService = {
  async chat(messages: ChatMessage[], contextAlertId?: string): Promise<ChatResponse> {
    const { data } = await apiClient.post<ChatResponse>('/ai/chat', {
      messages,
      context_alert_id: contextAlertId
    })
    return data
  }
}

export default aiService
