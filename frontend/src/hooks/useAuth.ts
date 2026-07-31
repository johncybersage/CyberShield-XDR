/**
 * CyberShield XDR — useAuth Hook
 * Convenience hook wrapping the auth store with action helpers.
 *
 * Usage:
 *   const { user, isAdmin, logout } = useAuth()
 */
import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuthStore } from '@store/authStore'
import authService from '@services/authService'

export function useAuth() {
  const { user, accessToken, isAuthenticated, logout: storeLogout } = useAuthStore()
  const navigate = useNavigate()

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch {
      // Logout is best-effort — clear local state regardless
    } finally {
      sessionStorage.removeItem('refresh_token')
      storeLogout()
      navigate('/login', { replace: true })
      toast.success('Logged out successfully')
    }
  }, [storeLogout, navigate])

  return {
    user,
    accessToken,
    isAuthenticated,
    logout,

    // Role helpers
    isAdmin: user?.role === 'admin',
    isAnalyst: user?.role === 'soc_analyst' || user?.role === 'admin',
    isViewer: user?.role === 'viewer',

    // Permission helpers
    canWrite: user?.role === 'admin' || user?.role === 'soc_analyst',
    canAdmin: user?.role === 'admin',
  }
}
