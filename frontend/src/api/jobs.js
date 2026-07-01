import { apiRequest } from './client'

export const getJobs = (params = {}) => {
  const search = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '' && value !== 'all') {
      search.set(key, String(value))
    }
  })

  const query = search.toString()
  return apiRequest(`/api/get_jobs${query ? `?${query}` : ''}`)
}
export const getJob = (id) => apiRequest(`/api/jobs/${id}`)

export const getMyJobs = () => apiRequest('/api/my_jobs', { requireAuth: true })
export const getMyApplications = () => apiRequest('/api/my_applications', { requireAuth: true })

export const getResponses = () => apiRequest('/api/responses', { requireAuth: true })

export const approveResponseChat = (id) => apiRequest(`/api/responses/${id}/approve-chat`, {
  method: 'PATCH',
  requireAuth: true,
})

export const deleteResponse = (id) => apiRequest(`/api/responses/${id}`, {
  method: 'DELETE',
  requireAuth: true,
})

export const getMessageConversations = () => apiRequest('/api/messages/conversations', { requireAuth: true })

export const getMessageThread = (applicationId) => apiRequest(`/api/messages/${applicationId}`, { requireAuth: true })

export const sendMessage = (applicationId, body) => apiRequest(`/api/messages/${applicationId}`, {
  method: 'POST',
  body: JSON.stringify({ body }),
  requireAuth: true,
})

export const deleteMessageConversation = (applicationId) => apiRequest(`/api/messages/${applicationId}`, {
  method: 'DELETE',
  requireAuth: true,
})

export const applyToJob = (payload) => apiRequest('/api/apply', {
  method: 'POST',
  body: JSON.stringify(payload),
  requireAuth: true,
})

export const createJob = (payload) => {
  const formData = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      formData.append(key, value)
    }
  })

  return apiRequest('/api/create_job', {
    method: 'POST',
    body: formData,
    requireAuth: true,
  })
}

export const updateJob = (id, payload) => {
  const formData = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      formData.append(key, value)
    }
  })

  return apiRequest(`/api/jobs/${id}`, {
    method: 'PUT',
    body: formData,
    requireAuth: true,
  })
}

export const deleteJob = (id) => apiRequest(`/api/jobs/${id}`, {
  method: 'DELETE',
  requireAuth: true,
})
