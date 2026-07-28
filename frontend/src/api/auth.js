import { apiRequest, clearAuthToken } from './client'

export const createAccount = ({
  fullName,
  email,
  phone,
  password,
  accountType = 'candidate',
  companyName = '',
  companyCountry = '',
  companyIndustry = '',
  companyRegistrationNumber = '',
}) => {
  return apiRequest('/api/create_account', {
    method: 'POST',
    body: JSON.stringify({
      full_name: fullName,
      email,
      phone,
      password,
      account_type: accountType,
      company_name: companyName,
      company_country: companyCountry,
      company_industry: companyIndustry,
      company_registration_number: companyRegistrationNumber,
    }),
  })
}

const buildRegistrationPayload = ({
  fullName,
  email,
  phone,
  password,
  accountType = 'candidate',
  companyName = '',
  companyCountry = '',
  companyIndustry = '',
  companyRegistrationNumber = '',
}) => JSON.stringify({
  full_name: fullName,
  email,
  phone,
  password,
  account_type: accountType,
  company_name: companyName,
  company_country: companyCountry,
  company_industry: companyIndustry,
  company_registration_number: companyRegistrationNumber,
})

export const requestRegistrationLink = (payload) => apiRequest('/api/request_registration_link', {
  method: 'POST',
  body: buildRegistrationPayload(payload),
})

export const getRegistrationOptions = () => apiRequest('/api/registration_options', {
  retryAuth: false,
  suppressUnauthorizedEvent: true,
})

export const requestPasswordResetLink = ({ email }) => apiRequest('/api/request_password_reset_link', {
  method: 'POST',
  body: JSON.stringify({ email }),
})

export const completeEmailLinkAuth = ({ accessToken, refreshToken, expiresIn, type }) => apiRequest('/api/auth/email-link', {
  method: 'POST',
  skipAuth: true,
  retryAuth: false,
  body: JSON.stringify({
    access_token: accessToken,
    refresh_token: refreshToken,
    expires_in: expiresIn,
    type,
  }),
})

export const updateRecoveryPassword = ({ newPassword }) => apiRequest('/api/auth/recovery-password', {
  method: 'POST',
  requireAuth: true,
  body: JSON.stringify({
    new_password: newPassword,
  }),
})

export const login = async ({ email, password }) => {
  const data = await apiRequest('/api/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })

  if (!data?.user) {
    throw new Error('no_user_received')
  }

  clearAuthToken()
  return data
}

export const getMe = () => apiRequest('/api/get_me', { requireAuth: true })

export const deleteAccount = () => apiRequest('/api/account', {
  method: 'DELETE',
  requireAuth: true,
})

export const logout = () => {
  clearAuthToken()
  return apiRequest('/api/logout', {
    method: 'POST',
    skipAuth: true,
    retryAuth: false,
    suppressUnauthorizedEvent: true,
  }).catch(() => {})
}
