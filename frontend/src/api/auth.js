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
