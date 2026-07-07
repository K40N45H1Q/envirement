import { apiRequest } from './client'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export const getBetaBlockedUrl = () => `${API_BASE_URL}/api/beta-auth/status`

export const getBetaStatus = () => apiRequest('/api/beta-auth/status', {
  skipAuth: true,
  suppressUnauthorizedEvent: true,
})

export const loginToBeta = ({ accessToken }) => apiRequest('/api/beta-auth/login', {
  method: 'POST',
  skipAuth: true,
  suppressUnauthorizedEvent: true,
  body: JSON.stringify({ access_token: accessToken }),
})

export const logoutFromBeta = () => apiRequest('/api/beta-auth/logout', {
  method: 'POST',
  skipAuth: true,
  suppressUnauthorizedEvent: true,
})
