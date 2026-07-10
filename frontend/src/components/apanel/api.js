import { apiRequest } from '@/api/client'

export const getAdminSummary = () => apiRequest('/api/admin/summary', {
  requireAuth: true,
})

export const getAdminUsers = (accountType = '') => {
  const query = accountType ? `?account_type=${encodeURIComponent(accountType)}` : ''
  return apiRequest(`/api/admin/users${query}`, {
    requireAuth: true,
  })
}

export const updateAdminUserSubscription = (userId, payload) => apiRequest(`/api/admin/users/${userId}/subscription`, {
  method: 'PATCH',
  requireAuth: true,
  body: JSON.stringify(payload),
})

export const getAdminBetaTokens = () => apiRequest('/api/admin/beta-tokens', {
  requireAuth: true,
})

export const getAdminBetaSettings = () => apiRequest('/api/admin/beta-settings', {
  requireAuth: true,
})

export const getAdminJobs = () => apiRequest('/api/admin/jobs', {
  requireAuth: true,
})

export const getAdminModerationJobs = () => apiRequest('/api/admin/moderation/jobs', {
  requireAuth: true,
})

export const approveAdminJob = (jobId) => apiRequest(`/api/admin/moderation/jobs/${jobId}/approve`, {
  method: 'PATCH',
  requireAuth: true,
})

export const rejectAdminJob = (jobId) => apiRequest(`/api/admin/moderation/jobs/${jobId}/reject`, {
  method: 'PATCH',
  requireAuth: true,
})

export const deleteAdminJob = (jobId) => apiRequest(`/api/admin/jobs/${jobId}`, {
  method: 'DELETE',
  requireAuth: true,
})

export const createAdminBetaToken = ({ note }) => apiRequest('/api/admin/beta-tokens', {
  method: 'POST',
  requireAuth: true,
  body: JSON.stringify({
    note,
  }),
})

export const deleteAdminBetaToken = (tokenId) => apiRequest(`/api/admin/beta-tokens/${tokenId}`, {
  method: 'DELETE',
  requireAuth: true,
})

export const updateAdminBetaSettings = ({ enabled }) => apiRequest('/api/admin/beta-settings', {
  method: 'PATCH',
  requireAuth: true,
  body: JSON.stringify({ enabled }),
})
