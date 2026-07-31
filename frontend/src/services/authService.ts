/**
 * CyberShield XDR — Auth API Service
 * Typed wrappers around all authentication endpoints.
 */
import apiClient from './apiClient'
import type { AuthUser } from '@store/authStore'

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  username: string
  full_name: string
  password: string
  confirm_password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: AuthUser
}

export interface ApiError {
  detail: string | Array<{ msg: string; loc: string[] }>
}

const authService = {
  async login(payload: LoginPayload): Promise<TokenResponse> {
    const { data } = await apiClient.post<TokenResponse>('/auth/login', payload)
    return data
  },

  async register(payload: RegisterPayload): Promise<TokenResponse> {
    const { data } = await apiClient.post<TokenResponse>('/auth/register', payload)
    return data
  },

  async logout(): Promise<void> {
    await apiClient.post('/auth/logout')
  },

  async forgotPassword(email: string): Promise<void> {
    await apiClient.post('/auth/forgot-password', { email })
  },

  async resetPassword(token: string, newPassword: string, confirmPassword: string): Promise<void> {
    await apiClient.post('/auth/reset-password', {
      token,
      new_password: newPassword,
      confirm_password: confirmPassword,
    })
  },

  async changePassword(currentPassword: string, newPassword: string, confirmPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    })
  },

  async getMe(): Promise<AuthUser> {
    const { data } = await apiClient.get<AuthUser>('/auth/me')
    return data
  },
}

export default authService

/** Extract a human-readable error message from an Axios error response. */
export function extractErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const resp = (error as { response: { data: ApiError } }).response
    const detail = resp?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map((e) => e.msg).join(', ')
  }
  return 'An unexpected error occurred'
}
