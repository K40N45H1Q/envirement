const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
const STARTUP_RETRY_ATTEMPTS = 6
const STARTUP_RETRY_DELAY_MS = 250
let refreshPromise = null

export class ApiError extends Error {
  constructor(key, status, payload = null) {
    super(key)
    this.name = 'ApiError'
    this.key = key
    this.status = status
    this.payload = payload
  }
}

export const getAuthToken = () => localStorage.getItem('token')

export const setAuthToken = (token) => {
  localStorage.setItem('token', token)
}

export const clearAuthToken = () => {
  localStorage.removeItem('token')
}

export const resolveApiUrl = (value = '') => {
  const raw = String(value || '').trim()
  if (!raw) return ''
  if (/^(https?:|data:|blob:)/i.test(raw)) return raw

  const base = API_BASE_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost')
  return new URL(raw, `${base}/`).toString()
}

const getErrorKey = (payload) => {
  if (!payload) return 'unknown_error'
  if (payload.detail?.error) return payload.detail.error
  if (payload.detail?.key) return payload.detail.key
  if (typeof payload.detail === 'string') return payload.detail
  if (payload.error) return payload.error
  if (payload.key) return payload.key
  return 'unknown_error'
}

const parseResponseBody = (text) => {
  if (!text) return null

  try {
    return JSON.parse(text)
  } catch {
    return {
      detail: text,
    }
  }
}

const refreshAccessToken = async () => {
  if (refreshPromise) return refreshPromise

  refreshPromise = (async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        clearAuthToken()
        return false
      }

      const data = parseResponseBody(await response.text())
      if (!data?.token) {
        clearAuthToken()
        return false
      }

      setAuthToken(data.token)
      return true
    } catch {
      return false
    } finally {
      refreshPromise = null
    }
  })()

  return refreshPromise
}

const wait = (ms) => new Promise((resolve) => {
  window.setTimeout(resolve, ms)
})

const shouldRetryRequest = (method, attempt, error) => {
  if (attempt >= STARTUP_RETRY_ATTEMPTS) return false
  if (!(error instanceof TypeError)) return false

  const normalizedMethod = String(method || 'GET').toUpperCase()
  return normalizedMethod === 'GET'
}

const executeRequest = async (url, options, attempt = 0) => {
  try {
    return await fetch(url, options)
  } catch (error) {
    if (!shouldRetryRequest(options.method, attempt, error)) {
      throw error
    }

    await wait(STARTUP_RETRY_DELAY_MS)
    return executeRequest(url, options, attempt + 1)
  }
}

export const apiRequest = async (path, options = {}) => {
  const token = getAuthToken()
  const headers = new Headers(options.headers || {})
  const skipAuth = options.skipAuth === true
  const requireAuth = options.requireAuth === true
  const suppressUnauthorizedEvent = options.suppressUnauthorizedEvent === true

  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  if (requireAuth && !token) {
    throw new ApiError('unauthorized', 401)
  }

  if (!skipAuth && token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  let response

  try {
    response = await executeRequest(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      credentials: options.credentials || 'include',
    })
  } catch {
    throw new ApiError('network_error', 0)
  }

  const canRefreshSession = (
    response.status === 401
    && Boolean(token)
    && !skipAuth
    && options.retryAuth !== false
    && path !== '/api/login'
    && path !== '/api/refresh'
    && path !== '/api/logout'
  )

  if (canRefreshSession && await refreshAccessToken()) {
    headers.set('Authorization', `Bearer ${getAuthToken()}`)

    try {
      response = await executeRequest(`${API_BASE_URL}${path}`, {
        ...options,
        headers,
        credentials: options.credentials || 'include',
      })
    } catch {
      throw new ApiError('network_error', 0)
    }
  }

  const text = await response.text()
  const data = parseResponseBody(text)

  if (!response.ok) {
    if (response.status === 401) {
      const errorKey = getErrorKey(data)

      if (!suppressUnauthorizedEvent) {
        window.dispatchEvent(new CustomEvent(
          errorKey === 'beta_auth_required' ? 'app:beta-unauthorized' : 'app:unauthorized',
          {
            detail: {
              path,
              status: response.status,
              key: errorKey,
            },
          },
        ))
      }
    }
    throw new ApiError(getErrorKey(data), response.status, data)
  }

  return data
}
