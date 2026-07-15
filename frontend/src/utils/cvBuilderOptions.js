const toText = (value) => (value == null ? '' : String(value))

export const languageLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'Native']

export const sectorExperienceCatalog = [
  { value: '1_year', ru: '1+ год', en: '1+ year', lv: '1+ gads' },
  { value: '2_years', ru: '2+ года', en: '2+ years', lv: '2+ gadi' },
  { value: '3_years', ru: '3+ года', en: '3+ years', lv: '3+ gadi' },
  { value: '4_years', ru: '4+ года', en: '4+ years', lv: '4+ gadi' },
  { value: '5_years', ru: '5+ лет', en: '5+ years', lv: '5+ gadi' },
  { value: '7_years', ru: '7+ лет', en: '7+ years', lv: '7+ gadi' },
  { value: '10_years', ru: '10+ лет', en: '10+ years', lv: '10+ gadi' },
]

export const languageCatalog = [
  { value: 'english', ru: 'Английский', en: 'English', lv: 'Angļu' },
  { value: 'russian', ru: 'Русский', en: 'Russian', lv: 'Krievu' },
  { value: 'german', ru: 'Немецкий', en: 'German', lv: 'Vācu' },
  { value: 'polish', ru: 'Польский', en: 'Polish', lv: 'Poļu' },
  { value: 'latvian', ru: 'Латышский', en: 'Latvian', lv: 'Latviešu' },
  { value: 'lithuanian', ru: 'Литовский', en: 'Lithuanian', lv: 'Lietuviešu' },
  { value: 'estonian', ru: 'Эстонский', en: 'Estonian', lv: 'Igauņu' },
  { value: 'french', ru: 'Французский', en: 'French', lv: 'Franču' },
]

export const licenseValues = ['AM', 'A1', 'A2', 'A', 'B', 'BE', 'C1', 'C1E', 'C', 'CE', 'D1', 'D1E', 'D', 'DE', 'Код 95', 'ADR', 'Forklift', 'VCA']
export const drivingLicenseValues = ['AM', 'A1', 'A2', 'A', 'B', 'BE', 'C1', 'C1E', 'C', 'CE', 'D1', 'D1E', 'D', 'DE']

export const permitCatalog = [
  { value: '', ru: 'Выберите', en: 'Choose', lv: 'Izvēlieties' },
  { value: 'eu_citizen', ru: 'гражданин ЕС', en: 'EU citizen', lv: 'ES pilsonis' },
  { value: 'has_visa', ru: 'Есть виза', en: 'Visa available', lv: 'Ir vīza' },
]

export const availabilityCatalog = [
  { value: '', ru: 'Не указана', en: 'Not specified', lv: 'Nav norādīta' },
  { value: 'Immediate', ru: 'Немедленно', en: 'Immediate', lv: 'Nekavējoties' },
  { value: '__date__', ru: 'Указать дату', en: 'Choose a date', lv: 'Norādīt datumu' },
]

export const educationCatalog = [
  { value: '', ru: 'Выберите', en: 'Choose', lv: 'Izvēlieties' },
  { value: 'primary', ru: 'Основное', en: 'Primary', lv: 'Pamatizglītība' },
  { value: 'secondary', ru: 'Среднее', en: 'Secondary', lv: 'Vidējā izglītība' },
  { value: 'vocational', ru: 'Профессиональное', en: 'Vocational', lv: 'Profesionālā izglītība' },
  { value: 'bachelor', ru: 'Бакалавр', en: 'Bachelor', lv: 'Bakalaurs' },
  { value: 'master', ru: 'Магистр', en: 'Master', lv: 'Maģistrs' },
  { value: 'phd', ru: 'Доктор наук', en: 'PhD', lv: 'PhD' },
]

export const preferredEmploymentCatalog = [
  { value: '', ru: 'Выберите', en: 'Choose', lv: 'Izvēlieties' },
  { value: 'full-time', ru: 'Полная занятость', en: 'Full-time', lv: 'Pilna slodze' },
  { value: 'part-time', ru: 'Частичная занятость', en: 'Part-time', lv: 'Nepilna slodze' },
  { value: 'contract', ru: 'Проект / контракт', en: 'Project / contract', lv: 'Projekts / līgums' },
]

export const DEFAULT_SECTOR_EXPERIENCE = sectorExperienceCatalog[0].value

const sectorExperienceValues = new Set(sectorExperienceCatalog.map((entry) => entry.value))

const sectorExperienceAliases = {
  '1+ год': '1_year',
  '1+ year': '1_year',
  '2+ года': '2_years',
  '2+ years': '2_years',
  '3+ года': '3_years',
  '3+ years': '3_years',
  '4+ года': '4_years',
  '4+ years': '4_years',
  '5+ лет': '5_years',
  '5+ years': '5_years',
  '7+ лет': '7_years',
  '7+ years': '7_years',
  '10+ лет': '10_years',
  '10+ years': '10_years',
}

const languageAliases = {
  english: 'english',
  'Английский': 'english',
  English: 'english',
  russian: 'russian',
  'Русский': 'russian',
  Russian: 'russian',
  german: 'german',
  'Немецкий': 'german',
  German: 'german',
  polish: 'polish',
  'Польский': 'polish',
  Polish: 'polish',
  latvian: 'latvian',
  'Латышский': 'latvian',
  Latvian: 'latvian',
  lithuanian: 'lithuanian',
  'Литовский': 'lithuanian',
  Lithuanian: 'lithuanian',
  estonian: 'estonian',
  'Эстонский': 'estonian',
  Estonian: 'estonian',
  french: 'french',
  'Французский': 'french',
  French: 'french',
}

const permitAliases = {
  eu_citizen: 'eu_citizen',
  'гражданин ЕС': 'eu_citizen',
  'EU гражданин': 'eu_citizen',
  'EU citizen': 'eu_citizen',
  has_visa: 'has_visa',
  'Есть виза': 'has_visa',
  'Visa available': 'has_visa',
}

const removedPermitValues = new Set([
  'needs_sponsorship',
  'Нужен sponsorship',
  'Needs sponsorship',
])

export const getCatalogEntryLabel = (entry, locale) => {
  if (locale === 'lv') return entry.lv ?? entry.en ?? entry.ru
  if (locale === 'en') return entry.en
  return entry.ru
}

export const mapCatalogToOptions = (catalog, locale) => (
  catalog.map((entry) => ({
    value: entry.value,
    label: getCatalogEntryLabel(entry, locale),
  }))
)

export const getLocalizedCatalogLabel = (catalog, value, locale, fallback = '') => {
  const option = catalog.find((entry) => entry.value === value)
  return option ? getCatalogEntryLabel(option, locale) : fallback || value
}

export const normalizeSectorExperience = (value) => {
  const normalized = toText(value).trim()
  if (sectorExperienceValues.has(normalized)) return normalized
  return sectorExperienceAliases[normalized] || DEFAULT_SECTOR_EXPERIENCE
}

export const normalizeLanguageName = (value) => languageAliases[toText(value).trim()] || toText(value).trim()

export const normalizePermit = (value) => {
  const textValue = toText(value).trim()
  if (removedPermitValues.has(textValue)) return ''
  return permitAliases[textValue] || textValue
}

export const displayLanguageName = (value, locale) => (
  getLocalizedCatalogLabel(languageCatalog, normalizeLanguageName(value), locale, toText(value).trim())
)

export const displaySectorExperience = (value, locale) => (
  getLocalizedCatalogLabel(sectorExperienceCatalog, normalizeSectorExperience(value), locale, toText(value).trim())
)

export const displayPermit = (value, locale) => (
  getLocalizedCatalogLabel(permitCatalog, normalizePermit(value), locale, toText(value).trim())
)

export const displayEducation = (value, locale) => {
  const normalized = toText(value).trim()
  return getLocalizedCatalogLabel(educationCatalog, normalized, locale, normalized)
}

export const displayPreferredEmployment = (value, locale) => {
  const normalized = toText(value).trim()
  return getLocalizedCatalogLabel(preferredEmploymentCatalog, normalized, locale, normalized)
}
