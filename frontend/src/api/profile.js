import { apiRequest } from './client'

export const getProfile = () => apiRequest('/api/profile')

export const updateProfile = (payload) => {
  const formData = new FormData()

  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return

    if (Array.isArray(value) || (typeof value === 'object' && !(value instanceof File))) {
      formData.append(key, JSON.stringify(value))
      return
    }

    formData.append(key, value)
  })

  return apiRequest('/api/profile', {
    method: 'PUT',
    body: formData,
  })
}
