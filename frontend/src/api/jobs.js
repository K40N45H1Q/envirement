import { apiRequest } from './client'

export const getJobs = () => apiRequest('/api/get_jobs')
export const getJob = (id) => apiRequest(`/api/jobs/${id}`)

export const getMyJobs = () => apiRequest('/api/my_jobs')
export const getMyApplications = () => apiRequest('/api/my_applications')

export const getResponses = () => apiRequest('/api/responses')

export const deleteResponse = (id) => apiRequest(`/api/responses/${id}`, {
  method: 'DELETE',
})

export const applyToJob = (payload) => apiRequest('/api/apply', {
  method: 'POST',
  body: JSON.stringify(payload),
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
  })
}

export const deleteJob = (id) => apiRequest(`/api/jobs/${id}`, {
  method: 'DELETE',
})
