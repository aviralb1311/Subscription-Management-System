const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const ACCESS_TOKEN_KEY = 'subscription_access_token'
const REFRESH_TOKEN_KEY = 'subscription_refresh_token'

export const authStorage = {
  getAccessToken: () => sessionStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => sessionStorage.getItem(REFRESH_TOKEN_KEY),
  saveTokens(accessToken: string, refreshToken: string) {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    sessionStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  },
  clear() {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY)
    sessionStorage.removeItem(REFRESH_TOKEN_KEY)
  },
}

export async function apiRequest(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers)
  const token = authStorage.getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
  if (response.status === 401) authStorage.clear()
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail || `Request failed (${response.status})`)
  }
  if (response.status === 204) return null
  return response.json()
}

export const api = { getHealth: () => apiRequest('/health') }
