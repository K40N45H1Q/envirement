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

export const getAdminBetaTokens = () => apiRequest('/api/admin/beta-tokens', {
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
