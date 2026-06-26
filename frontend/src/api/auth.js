import { apiRequest, clearAuthToken, setAuthToken } from './client'

export const createAccount = ({ email, password, accountType = 'user' }) => {
  return apiRequest('/create_account', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password,
      account_type: accountType,
    }),
  })
}

export const login = async ({ email, password }) => {
  const data = await apiRequest('/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })

  if (!data?.token) {
    throw new Error('no_token_received')
  }

  setAuthToken(data.token)
  return data
}

export const getMe = () => apiRequest('/get_me')

export const logout = () => {
  clearAuthToken()
}
