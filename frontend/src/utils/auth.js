export const ACCOUNT_LABELS = {
  user: 'Кандидат',
  employer: 'Работодатель',
  admin: 'Администратор',
}

export const isEmployerAccount = (accountType) => ['employer', 'admin'].includes(accountType)

export const defaultRouteForAccount = (accountType) => {
  if (accountType === 'admin') return '/admin'
  if (isEmployerAccount(accountType)) return '/dashboard?section=jobs'
  return '/dashboard'
}

export const canAccessRoute = (accountType, allowedTypes = []) => {
  if (!allowedTypes.length) return true
  return allowedTypes.includes(accountType)
}
