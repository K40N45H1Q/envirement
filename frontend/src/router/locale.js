import { normalizeLanguage } from '@/i18n'

export const SUPPORTED_LOCALES = ['ru', 'en']
const LOCALE_PREFIX_RE = /^\/(ru|en)(?=\/|$)/

export const getLocaleFromPath = (path = '') => {
  const match = String(path || '').match(LOCALE_PREFIX_RE)
  return normalizeLanguage(match?.[1] || 'ru')
}

export const stripLocaleFromPath = (path = '') => {
  const normalizedPath = String(path || '')
  const strippedPath = normalizedPath.replace(LOCALE_PREFIX_RE, '')
  return strippedPath || '/'
}

export const hasLocalePrefix = (path = '') => LOCALE_PREFIX_RE.test(String(path || ''))

export const withLocale = (path = '/', locale = 'ru') => {
  const normalizedLocale = normalizeLanguage(locale)
  const strippedPath = stripLocaleFromPath(path)
  return strippedPath === '/'
    ? `/${normalizedLocale}`
    : `/${normalizedLocale}${strippedPath}`
}

export const localizeFullPath = (fullPath = '/', locale = 'ru') => {
  const [path, hashFragment = ''] = String(fullPath || '/').split('#')
  const [pathname, queryString = ''] = path.split('?')
  const localizedPath = withLocale(pathname || '/', locale)
  const queryPart = queryString ? `?${queryString}` : ''
  const hashPart = hashFragment ? `#${hashFragment}` : ''

  return `${localizedPath}${queryPart}${hashPart}`
}

export const withLocalizedRedirect = (target, locale = 'ru') => {
  if (typeof target === 'string') {
    return localizeFullPath(target, locale)
  }

  return {
    ...target,
    path: withLocale(target.path || '/', locale),
  }
}
