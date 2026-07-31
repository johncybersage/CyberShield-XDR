import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuthStore } from '@store/authStore'
interface WSEvent {
  type: string
  data: any
}

export function useWebSocket(onEvent?: (event: WSEvent) => void) {
  const { accessToken } = useAuthStore()
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  const connect = useCallback(() => {
    if (!accessToken) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    // Replace http/https with ws/wss
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    // Get host from api base url, defaulting to window.location.host
    const baseUrl = import.meta.env.VITE_API_URL || '/api/v1'
    let wsUrl = ''
    
    if (baseUrl.startsWith('http')) {
      wsUrl = baseUrl.replace(/^http/, 'ws') + `/ws/events?token=${accessToken}`
    } else {
      wsUrl = `${protocol}//${window.location.host}${baseUrl}/ws/events?token=${accessToken}`
    }

    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        if (event.data === 'pong') return
        const parsed: WSEvent = JSON.parse(event.data)
        if (onEvent) onEvent(parsed)
      } catch (err) {
        console.error('Failed to parse websocket message', err)
      }
    }

    ws.onclose = () => {
      setIsConnected(false)
      // Attempt reconnect after 5s
      setTimeout(connect, 5000)
    }

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error)
      ws.close()
    }
  }, [accessToken, onEvent])

  useEffect(() => {
    connect()
    
    // Keep alive ping
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping')
      }
    }, 30000)

    return () => {
      clearInterval(interval)
      if (wsRef.current) {
        wsRef.current.onclose = null // prevent reconnect on unmount
        wsRef.current.close()
      }
    }
  }, [connect])

  return { isConnected }
}
