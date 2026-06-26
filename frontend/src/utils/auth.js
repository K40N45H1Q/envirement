export const ACCOUNT_LABELS = {
  user: 'Candidate',
  employer: 'Employer',
  admin: 'Platform admin',
}

export const isEmployerAccount = (accountType) => ['employer', 'admin'].includes(accountType)

export const defaultRouteForAccount = (accountType) => {
  if (isEmployerAccount(accountType)) return '/employer-dashboard'
  return '/dashboard'
}

export const canAccessRoute = (accountType, allowedTypes = []) => {
  if (!allowedTypes.length) return true
  return allowedTypes.includes(accountType)
}
