import { translate } from '@/i18n'
import { useUiStore } from '@/stores/ui'

const languageValues = ['English', 'Russian', 'German', 'Polish', 'Latvian', 'Lithuanian', 'Estonian', 'French']
const languageLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const licenseLabels = ['AM', 'A1', 'A2', 'A', 'B', 'BE', 'C1', 'C1E', 'C', 'CE', 'D1', 'D1E', 'D', 'DE', 'Code 95', 'ADR', 'Forklift', 'VCA']

const languageKeyByValue = {
  English: 'registerLanguage.english',
  Russian: 'registerLanguage.russian',
  German: 'registerLanguage.german',
  Polish: 'registerLanguage.polish',
  Latvian: 'registerLanguage.latvian',
  Lithuanian: 'registerLanguage.lithuanian',
  Estonian: 'registerLanguage.estonian',
  French: 'registerLanguage.french',
}

const extraMessages = {
  ru: {
    'registerLanguage.english': 'Английский',
    'registerLanguage.russian': 'Русский',
    'registerLanguage.german': 'Немецкий',
    'registerLanguage.polish': 'Польский',
    'registerLanguage.latvian': 'Латышский',
    'registerLanguage.lithuanian': 'Литовский',
    'registerLanguage.estonian': 'Эстонский',
    'registerLanguage.french': 'Французский',
  },
  en: {
    'registerLanguage.english': 'English',
    'registerLanguage.russian': 'Russian',
    'registerLanguage.german': 'German',
    'registerLanguage.polish': 'Polish',
    'registerLanguage.latvian': 'Latvian',
    'registerLanguage.lithuanian': 'Lithuanian',
    'registerLanguage.estonian': 'Estonian',
    'registerLanguage.french': 'French',
  },
}

const getLanguage = () => {
  try {
    return useUiStore().language
  } catch {
    return 'ru'
  }
}

const t = (key, fallback) => {
  const language = getLanguage()
  return extraMessages[language]?.[key] || translate(key, {}, language) || fallback
}

export const getLanguageOptions = () => languageValues.map((value) => ({
  value,
  label: t(languageKeyByValue[value], value),
}))

export const languageOptions = getLanguageOptions()
export const languageLevelOptions = languageLevels.map((label) => ({ value: label, label }))
export const getLicenseOptions = () => {
  const language = getLanguage()
  const noLicenseLabel = language === 'en' ? 'No license' : 'Нет лицензий'

  return [
    { value: noLicenseLabel, label: noLicenseLabel },
    ...licenseLabels.map((label) => ({ value: label, label })),
  ]
}

export const licenseOptions = getLicenseOptions()

const toText = (value) => (value == null ? '' : String(value))
const noLicenseValues = new Set([
  'no license',
  'нет лицензий',
  'нет лицензии',
  'ÐÐµÑ‚ Ð»Ð¸Ñ†ÐµÐ½Ð·Ð¸Ð¹',
].map((value) => value.toLowerCase()))

export const isNoLicenseValue = (value) => noLicenseValues.has(toText(value).trim().toLowerCase())

const toArray = (value) => {
  if (Array.isArray(value)) return value
  if (typeof value !== 'string') return []

  try {
    const parsed = JSON.parse(value)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export const normalizeLanguages = (value) => toArray(value)
  .map((language) => ({
    name: toText(language?.name).trim(),
    level: toText(language?.level || languageLevelOptions[2].value),
  }))
  .filter((language) => language.name)

export const normalizeLicenses = (value) => toArray(value)
  .map((license) => (typeof license === 'string' ? license : license?.name || license?.title || ''))
  .map((license) => toText(license).trim())
  .filter((license) => license && !isNoLicenseValue(license))
