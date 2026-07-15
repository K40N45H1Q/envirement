import occupationsDirectory from '@/data/occupationsDirectory'

const SUPPORTED_LOCALES = new Set(['ru', 'en', 'lv'])

const normalizeLocale = (locale) => {
  const value = String(locale || '').trim().toLowerCase()
  return SUPPORTED_LOCALES.has(value) ? value : 'ru'
}

const normalizeText = (value = '') => String(value)
  .toLowerCase()
  .normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '')
  .trim()

const collectOccupationItems = (items = [], locale = 'ru', bucket = []) => {
  for (const item of items) {
    if (!item?.title) continue

    if (Array.isArray(item.occupations)) {
      collectOccupationItems(item.occupations, locale, bucket)
      continue
    }

    const label = String(item.title[locale] || item.title.ru || item.title.en || item.title.lv || '').trim()
    if (!label) continue

    bucket.push({
      id: String(item.id || label),
      label,
      searchLabel: normalizeText(label),
    })
  }

  return bucket
}

export const getOccupationOptions = (locale = 'ru') => {
  const resolvedLocale = normalizeLocale(locale)
  const seen = new Set()

  return collectOccupationItems(occupationsDirectory, resolvedLocale)
    .filter((item) => {
      if (seen.has(item.label)) return false
      seen.add(item.label)
      return true
    })
    .sort((left, right) => left.label.localeCompare(right.label))
}

export const getOccupationById = (id = '', locale = 'ru') => {
  const normalizedId = String(id || '').trim()
  if (!normalizedId) return null

  return getOccupationOptions(locale).find((option) => option.id === normalizedId) || null
}

export const findOccupationSuggestions = (query = '', locale = 'ru', limit = 8) => {
  const normalizedQuery = normalizeText(query)
  if (!normalizedQuery) return []

  const exactPrefixMatches = []
  const containsMatches = []

  for (const option of getOccupationOptions(locale)) {
    if (option.searchLabel.startsWith(normalizedQuery)) {
      exactPrefixMatches.push(option)
      continue
    }

    if (option.searchLabel.includes(normalizedQuery)) {
      containsMatches.push(option)
    }
  }

  return [...exactPrefixMatches, ...containsMatches].slice(0, limit)
}

export const findOccupationByLabel = (label = '', locale = 'ru') => {
  const normalizedLabel = normalizeText(label)
  return getOccupationOptions(locale).find((option) => option.searchLabel === normalizedLabel) || null
}

export const resolveOccupation = (id = '', label = '', locale = 'ru') => {
  const resolvedLocale = normalizeLocale(locale)
  const matchById = getOccupationById(id, resolvedLocale)
  if (matchById) return matchById

  for (const sourceLocale of SUPPORTED_LOCALES) {
    const sourceMatch = findOccupationByLabel(label, sourceLocale)
    if (!sourceMatch) continue
    return getOccupationById(sourceMatch.id, resolvedLocale) || sourceMatch
  }

  return null
}
