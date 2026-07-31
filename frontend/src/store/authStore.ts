/**
 * CyberShield XDR — Authentication Store
 * Zustand store managing auth state with localStorage persistence.
 * Access token kept in memory only; refresh token in httpOnly cookie (set by backend).
 */
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export interface AuthUser {
  id: string
  email: string
  username: string
  full_name: string
  role: 'admin' | 'soc_analyst' | 'viewer'
  avatar_url?: string
}

interface AuthState {
  user: AuthUser | null
  accessToken: string | null
  isAuthenticated: boolean
  isLoading: boolean

  setAuth: (user: AuthUser, accessToken: string) => void
  setUser: (user: AuthUser) => void
  setAccessToken: (token: string) => void
  logout: () => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,

      setAuth: (user, accessToken) =>
        set({ user, accessToken, isAuthenticated: true }),

      setUser: (user) => set({ user }),

      setAccessToken: (accessToken) => set({ accessToken }),

      logout: () =>
        set({ user: null, accessToken: null, isAuthenticated: false }),

      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'cybershield-auth',
      storage: createJSONStorage(() => sessionStorage), // sessionStorage clears on tab close
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
