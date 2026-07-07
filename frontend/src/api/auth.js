import { apiRequest, clearAuthToken, setAuthToken } from './client'

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
  return apiRequest('/create_account', {
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

export const requestRegistrationCode = (payload) => apiRequest('/request_registration_code', {
  method: 'POST',
  body: buildRegistrationPayload(payload),
})

export const verifyRegistrationCode = ({ email, code }) => apiRequest('/verify_registration_code', {
  method: 'POST',
  body: JSON.stringify({
    email,
    code,
  }),
})

export const requestPasswordResetCode = ({ email }) => apiRequest('/request_password_reset_code', {
  method: 'POST',
  body: JSON.stringify({ email }),
})

export const confirmPasswordReset = ({ email, code, newPassword }) => apiRequest('/confirm_password_reset', {
  method: 'POST',
  body: JSON.stringify({
    email,
    code,
    new_password: newPassword,
  }),
})

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

export const getMe = () => apiRequest('/get_me', { requireAuth: true })

export const logout = () => {
  clearAuthToken()
}
