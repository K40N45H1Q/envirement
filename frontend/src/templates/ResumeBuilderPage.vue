<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import AppLayout from '@/components/AppLayout.vue'
import BaseDropdown from '@/components/BaseDropdown.vue'
import Logo from '@/components/Logo.vue'
import PhoneInput from '@/components/PhoneInput.vue'
import { getProfile, updateProfile } from '@/api/profile'
import { translate, useI18n } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useJobsStore } from '@/stores/jobs'

const AUTOSAVE_DELAY = 1200
const GUEST_RESUME_DRAFT_KEY = 'cvhold:createcv:draft'
const MAX_AVATAR_SIZE = 5 * 1024 * 1024
const MAX_RESUME_SIZE = 10 * 1024 * 1024
const AVATAR_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const RESUME_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

const MAX_PRINT_SECTORS = 6
const MAX_PRINT_SKILLS = 10
const MAX_PRINT_LANGUAGES = 5
const MAX_PRINT_LICENSES = 5

const languageLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const languageLevelOptions = languageLevels.map((label) => ({ value: label, label }))

const { language } = useI18n()
const isEnglish = computed(() => language.value === 'en')
const isLatvian = computed(() => language.value === 'lv')

const labelByLocale = (entry) => {
  if (isLatvian.value) return entry.lv ?? entry.en ?? entry.ru
  if (isEnglish.value) return entry.en
  return entry.ru
}

const sectorExperienceCatalog = [
  { value: '1_year', ru: '1+ год', en: '1+ year', lv: '1+ gads' },
  { value: '2_years', ru: '2+ года', en: '2+ years', lv: '2+ gadi' },
  { value: '3_years', ru: '3+ года', en: '3+ years', lv: '3+ gadi' },
  { value: '4_years', ru: '4+ года', en: '4+ years', lv: '4+ gadi' },
  { value: '5_years', ru: '5+ лет', en: '5+ years', lv: '5+ gadi' },
  { value: '7_years', ru: '7+ лет', en: '7+ years', lv: '7+ gadi' },
  { value: '10_years', ru: '10+ лет', en: '10+ years', lv: '10+ gadi' },
]

const languageCatalog = [
  { value: 'english', ru: 'Английский', en: 'English', lv: 'Angļu' },
  { value: 'russian', ru: 'Русский', en: 'Russian', lv: 'Krievu' },
  { value: 'german', ru: 'Немецкий', en: 'German', lv: 'Vācu' },
  { value: 'polish', ru: 'Польский', en: 'Polish', lv: 'Poļu' },
  { value: 'latvian', ru: 'Латышский', en: 'Latvian', lv: 'Latviešu' },
  { value: 'lithuanian', ru: 'Литовский', en: 'Lithuanian', lv: 'Lietuviešu' },
  { value: 'estonian', ru: 'Эстонский', en: 'Estonian', lv: 'Igauņu' },
  { value: 'french', ru: 'Французский', en: 'French', lv: 'Franču' },
]

const licenseValues = ['AM', 'A1', 'A2', 'A', 'B', 'BE', 'C1', 'C1E', 'C', 'CE', 'D1', 'D1E', 'D', 'DE', 'Код 95', 'ADR', 'Forklift', 'VCA']

const permitCatalog = [
  { value: '', ru: 'Выберите', en: 'Choose', lv: 'Izvēlieties' },
  { value: 'eu_citizen', ru: 'гражданин ЕС', en: 'EU citizen', lv: 'ES pilsonis' },
  { value: 'has_visa', ru: 'Есть виза', en: 'Visa available', lv: 'Ir vīza' },
]

const availabilityCatalog = [
  { value: '', ru: 'Выберите', en: 'Choose', lv: 'Izvēlieties' },
  { value: 'Immediate', ru: 'Немедленно', en: 'Immediate', lv: 'Nekavējoties' },
  { value: '1 week notice', ru: 'Через 1 неделю', en: 'In 1 week', lv: 'Pēc 1 nedēļas' },
  { value: '2 weeks notice', ru: 'Через 2 недели', en: 'In 2 weeks', lv: 'Pēc 2 nedēļām' },
  { value: '1 month notice', ru: 'Через 1 месяц', en: 'In 1 month', lv: 'Pēc 1 mēneša' },
  { value: 'By agreement', ru: 'По договорённости', en: 'By agreement', lv: 'Pēc vienošanās' },
]

const educationCatalog = [
  { value: '', ru: 'Выберите', en: 'Choose', lv: 'Izvēlieties' },
  { value: 'primary', ru: 'Начальное', en: 'Primary', lv: 'Pamatizglītība' },
  { value: 'secondary', ru: 'Среднее', en: 'Secondary', lv: 'Vidējā izglītība' },
  { value: 'vocational', ru: 'Профессиональное', en: 'Vocational', lv: 'Profesionālā izglītība' },
  { value: 'bachelor', ru: 'Бакалавр', en: 'Bachelor', lv: 'Bakalaurs' },
  { value: 'master', ru: 'Магистр', en: 'Master', lv: 'Maģistrs' },
  { value: 'phd', ru: 'PhD', en: 'PhD', lv: 'PhD' },
]

const preferredEmploymentCatalog = [
  { value: '', ru: 'Выберите', en: 'Choose', lv: 'Izvēlieties' },
  { value: 'full-time', ru: 'Полная занятость', en: 'Full-time', lv: 'Pilna slodze' },
  { value: 'part-time', ru: 'Частичная занятость', en: 'Part-time', lv: 'Nepilna slodze' },
  { value: 'contract', ru: 'Проект / контракт', en: 'Project / contract', lv: 'Projekts / līgums' },
]

const DEFAULT_SECTOR_EXPERIENCE = sectorExperienceCatalog[0].value

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

const getLocalizedLabel = (catalog, value, fallback = '') => {
  const option = catalog.find((entry) => entry.value === value)
  return option ? labelByLocale(option) : fallback || value
}

const sectorExperienceOptions = computed(() => sectorExperienceCatalog.map((entry) => ({
  value: entry.value,
  label: labelByLocale(entry),
})))

const languageOptions = computed(() => languageCatalog.map((entry) => ({
  value: entry.value,
  label: labelByLocale(entry),
})))

const licenseOptions = computed(() => {
  const noLicenseLabel = copy.value.noLicense
  return [
    { value: noLicenseLabel, label: noLicenseLabel },
    ...licenseValues.map((label) => ({ value: label, label })),
  ]
})
const permitOptions = computed(() => permitCatalog.map((entry) => ({ value: entry.value, label: labelByLocale(entry) })))
const baseAvailabilityOptions = computed(() => availabilityCatalog.map((entry) => ({ value: entry.value, label: labelByLocale(entry) })))
const educationOptions = computed(() => educationCatalog.map((entry) => ({
  value: entry.value,
  label: labelByLocale(entry),
})))
const preferredEmploymentOptions = computed(() => preferredEmploymentCatalog.map((entry) => ({
  value: entry.value,
  label: labelByLocale(entry),
})))

const normalizeSectorExperience = (value) => {
  const normalized = toText(value).trim()
  if (sectorExperienceValues.has(normalized)) return normalized
  return sectorExperienceAliases[normalized] || DEFAULT_SECTOR_EXPERIENCE
}
const normalizeLanguageName = (value) => languageAliases[toText(value).trim()] || toText(value).trim()
const normalizePermit = (value) => {
  const textValue = toText(value).trim()
  if (removedPermitValues.has(textValue)) return ''
  return permitAliases[textValue] || textValue
}
const displayLanguageName = (value) => getLocalizedLabel(languageCatalog, normalizeLanguageName(value), toText(value).trim())
const displaySectorExperience = (value) => getLocalizedLabel(sectorExperienceCatalog, normalizeSectorExperience(value), toText(value).trim())
const displayPermit = (value) => getLocalizedLabel(permitCatalog, normalizePermit(value), toText(value).trim())
const displayEducation = (value) => {
  const normalized = toText(value).trim()
  return getLocalizedLabel(educationCatalog, normalized, normalized)
}
const displayPreferredEmployment = (value) => {
  const normalized = toText(value).trim()
  return getLocalizedLabel(preferredEmploymentCatalog, normalized, normalized)
}
const displayAvailability = (value) => {
  const normalized = toText(value).trim()
  if (isDateAvailability(normalized)) {
    return translate('resumeBuilderPage.dateValue', { value: normalized }, language.value)
  }

  const option = availabilityCatalog.find((entry) => entry.value === normalized)
  return option ? labelByLocale(option) : normalized
}

const copy = computed(() => translate('resumeBuilderPage', {}, language.value))

const cvLanguageOptions = computed(() => [
  { value: 'lv', label: 'Latviešu' },
  { value: 'en', label: 'English' },
  { value: 'ru', label: 'Русский' },
])
const genderOptions = computed(() => [
  { value: '', label: copy.value.choose },
  { value: 'female', label: copy.value.female },
  { value: 'male', label: copy.value.male },
  { value: 'other', label: copy.value.otherGender },
])
const countryOptions = computed(() => [
  { value: 'Latvia', label: copy.value.latvia },
  { value: 'Lithuania', label: copy.value.lithuania },
  { value: 'Estonia', label: copy.value.estonia },
  { value: 'Other', label: copy.value.otherCountry },
])

const { state } = useAuth()
const jobsStore = useJobsStore()
const { categoryCounts } = storeToRefs(jobsStore)

const step = ref(1)
const expandedWorkIndex = ref(0)
const expandedEducationIndex = ref(0)
const isLoaded = ref(false)
const isLoading = ref(false)
const isSaving = ref(false)
const status = ref('')
const errors = ref({})
const savedSnapshot = ref('')
const avatarFile = ref(null)
const resumeFile = ref(null)
const avatarObjectUrl = ref('')
const selectedSector = ref('')
const selectedSectorExperience = ref(DEFAULT_SECTOR_EXPERIENCE)
const newLanguage = ref(languageCatalog[0].value)
const newLanguageLevel = ref(languageLevelOptions[2].value)
const newLicense = ref(copy.value.noLicense)
const cvDocumentRef = ref(null)
const avatarInputRef = ref(null)
const resumeInputRef = ref(null)

let autosaveTimer = null
let savePromise = null
let shouldSaveAgain = false
let isApplyingServerProfile = false
let printFrame = null

const createEmptyWorkExperience = () => ({
  position: '',
  job_category: '',
  company_name: '',
  start_date: '',
  end_date: '',
  current: false,
  country: 'Latvia',
  experience_years: '',
  description: '',
})

const createEmptyEducation = () => ({
  level: '',
  institution: '',
  speciality: '',
  second_speciality: '',
  country: 'Latvia',
  start_date: '',
  end_date: '',
  current: false,
  unfinished: false,
  additional_information: '',
})

const createEmptyResumeData = () => ({
  cv_language: 'lv',
  birth_date: '',
  birth_month: '',
  birth_day: '',
  birth_year: '',
  hide_birth_date: false,
  gender: '',
  hide_gender: false,
  communication_language: 'lv',
  additional_emails: [],
  additional_phones: [],
  no_work_experience: false,
  total_experience_years: '',
  work_experiences: [createEmptyWorkExperience()],
  educations: [createEmptyEducation()],
})

const createEmptyProfile = () => ({
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  summary: '',
  current_role: '',
  skills: '',
  sectors: [],
  languages: [],
  licenses: [],
  mobility: '',
  work_permit: '',
  availability: '',
  salary_expectation: '',
  preferred_employment_type: '',
  education_level: '',
  remote_ready: false,
  resume_name: '',
  resume_url: '',
  avatar_url: '',
  resume_data: createEmptyResumeData(),
})

const profile = ref(createEmptyProfile())

const toText = (value) => (value == null ? '' : String(value))

const toArray = (value) => {
  if (Array.isArray(value)) return value
  if (typeof value !== 'string' || !value.trim()) return []

  try {
    const parsed = JSON.parse(value)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

const splitTextList = (value) => toText(value)
  .split(/[,;\s]+/)
  .map((item) => item.trim())
  .filter(Boolean)

const limitText = (value, maxLength = 520, { preserveLineBreaks = false } = {}) => {
  const cleanText = preserveLineBreaks
    ? toText(value).replace(/[^\S\r\n]+/g, ' ').replace(/\r\n?/g, '\n').trim()
    : toText(value).replace(/\s+/g, ' ').trim()
  if (cleanText.length <= maxLength) return cleanText

  const clipped = cleanText.slice(0, maxLength).replace(/[^\S\r\n]+\S*$/, '').trim()
  return `${clipped}…`
}

const hashText = (value) => {
  const text = toText(value) || 'cvhold'
  let hash = 0

  for (let index = 0; index < text.length; index += 1) {
    hash = ((hash << 5) - hash) + text.charCodeAt(index)
    hash |= 0
  }

  return Math.abs(hash)
}

const wait = (delay) => new Promise((resolve) => {
  window.setTimeout(resolve, delay)
})

const waitForImages = (root) => {
  if (!root) return Promise.resolve()

  const images = Array.from(root.querySelectorAll('img'))

  return Promise.all(images.map((image) => {
    if (image.complete) return Promise.resolve()

    return new Promise((resolve) => {
      image.onload = resolve
      image.onerror = resolve
    })
  }))
}

const waitForStylesheets = (printDocument) => {
  if (!printDocument) return Promise.resolve()

  const links = Array.from(printDocument.querySelectorAll('link[rel="stylesheet"]'))

  return Promise.all(links.map((link) => {
    try {
      if (link.sheet) return Promise.resolve()
    } catch {
      // Cross-origin stylesheet access can throw, wait for load/error below.
    }

    return new Promise((resolve) => {
      const done = () => {
        link.removeEventListener('load', done)
        link.removeEventListener('error', done)
        resolve()
      }

      link.addEventListener('load', done, { once: true })
      link.addEventListener('error', done, { once: true })
      window.setTimeout(done, 1600)
    })
  }))
}

const removePrintFrame = () => {
  if (printFrame) {
    printFrame.remove()
    printFrame = null
  }
}

const user = computed(() => state.user)
const isAuthenticated = computed(() => !!user.value)
const fullName = computed(() => `${profile.value.first_name} ${profile.value.last_name}`.trim())
const profileEmail = computed(() => user.value?.email || profile.value.email || '')
const avatarPreview = computed(() => avatarObjectUrl.value || profile.value.avatar_url || '')

const legacyJobCategoryOptions = computed(() => {
  const categoriesFromCounts = (categoryCounts.value || [])
    .filter((category) => category.id && category.id !== 'all')
    .map((category) => ({
      value: category.id,
      label: category.label,
      hint: `${category.count} вакансий`,
      iconClass: category.icon,
    }))

  if (categoriesFromCounts.length) return categoriesFromCounts

  return (jobsStore.categoryConfigs || [])
    .filter((category) => category.id && category.id !== 'all')
    .map((category) => ({
      value: category.id,
      label: category.label,
      hint: 'Сфера деятельности',
      iconClass: category.icon,
    }))
})

const legacySectorDropdownOptions = computed(() => [
  {
    value: '',
    label: 'Выберите сферу деятельности',
    hint: 'Категории как на странице вакансий',
    iconClass: 'fas fa-layer-group',
  },
  ...jobCategoryOptions.value,
])

const legacySectorOptionsByValue = computed(() => new Map(
  legacyJobCategoryOptions.value.map((option) => [option.value, option]),
))

const legacySectorOptionsByLabel = computed(() => new Map(
  legacyJobCategoryOptions.value.map((option) => [option.label.toLowerCase(), option]),
))

const getSectorOption = (sector) => {
  const id = toText(sector?.id || sector?.value)
  const name = toText(sector?.name || sector?.label).trim()
  const byId = id ? sectorOptionsByValue.value.get(id) : null
  const byLabel = name ? sectorOptionsByLabel.value.get(name.toLowerCase()) : null

  return byId || byLabel || null
}

const legacySelectedSectorOption = computed(() => legacySectorOptionsByValue.value.get(selectedSector.value) || null)

const canAddSector = computed(() => {
  const option = selectedSectorOption.value
  if (!option) return false

  return !profile.value.sectors.some((sector) => {
    const sectorOption = getSectorOption(sector)
    return sectorOption?.value === option.value
  })
})

const isDateAvailability = (value) => (
  /^\d{2}\.\d{2}\.\d{4}$/.test(value)
  || /^\d{4}-\d{2}-\d{2}$/.test(value)
)

const legacyAvailabilityDropdownOptions = computed(() => {
  const currentValue = profile.value.availability.trim()
  const exists = baseAvailabilityOptions.value.some((option) => option.value === currentValue)

  if (currentValue && !exists && isDateAvailability(currentValue)) {
    return [
      ...baseAvailabilityOptions,
      { value: currentValue, label: `Дата: ${currentValue}` },
    ]
  }

  return baseAvailabilityOptions
})

const legacyAvailabilityLabel = computed(() => {
  const currentValue = profile.value.availability.trim()
  return availabilityDropdownOptions.value.find((option) => option.value === currentValue)?.label || currentValue
})

const isValidAvailability = (value) => {
  const cleanValue = value.trim()
  if (!cleanValue) return true
  if (baseAvailabilityOptions.value.some((option) => option.value === cleanValue)) return true
  return isDateAvailability(cleanValue)
}

const avatarInitials = computed(() => {
  if (fullName.value) {
    return fullName.value
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0])
      .join('')
      .toUpperCase()
  }

  return (profileEmail.value || 'CV').slice(0, 2).toUpperCase()
})

const legacySteps = [
  { id: 1, title: 'Основное', subtitle: 'Контакты и позиция' },
  { id: 2, title: 'Опыт', subtitle: 'Навыки и условия' },
  { id: 3, title: 'Готовое CV', subtitle: 'Фото, проверка и PDF' },
]

const jobCategoryOptions = computed(() => {
  const categoriesFromCounts = (categoryCounts.value || [])
    .filter((category) => category.id && category.id !== 'all')
    .map((category) => ({
      value: category.id,
      label: category.label,
      hint: `${category.count} ${copy.value.jobsCount}`,
      iconClass: category.icon,
    }))

  if (categoriesFromCounts.length) return categoriesFromCounts

  return (jobsStore.categoryConfigs || [])
    .filter((category) => category.id && category.id !== 'all')
    .map((category) => ({
      value: category.id,
      label: category.label,
      hint: copy.value.sectorHint,
      iconClass: category.icon,
    }))
})

const sectorDropdownOptions = computed(() => [
  {
    value: '',
    label: copy.value.sectorChoose,
    hint: copy.value.sectorListHint,
    iconClass: 'fas fa-layer-group',
  },
  ...jobCategoryOptions.value,
])

const sectorOptionsByValue = computed(() => new Map(
  jobCategoryOptions.value.map((option) => [option.value, option]),
))

const sectorOptionsByLabel = computed(() => new Map(
  jobCategoryOptions.value.map((option) => [option.label.toLowerCase(), option]),
))

const selectedSectorOption = computed(() => sectorOptionsByValue.value.get(selectedSector.value) || null)

const availabilityDropdownOptions = computed(() => {
  const currentValue = profile.value.availability.trim()
  const exists = baseAvailabilityOptions.value.some((option) => option.value === currentValue)

  if (currentValue && !exists && isDateAvailability(currentValue)) {
    return [
      ...baseAvailabilityOptions.value,
      { value: currentValue, label: displayAvailability(currentValue) },
    ]
  }

  return baseAvailabilityOptions.value
})

const availabilityLabel = computed(() => {
  const currentValue = profile.value.availability.trim()
  return availabilityDropdownOptions.value.find((option) => option.value === currentValue)?.label || currentValue
})

const steps = computed(() => copy.value.steps)

const normalizeSectors = (value) => toArray(value)
  .map((sector) => {
    const id = toText(sector?.id || sector?.value).trim()
    const name = toText(sector?.name || sector?.label || sector).trim()
    const byId = id ? sectorOptionsByValue.value.get(id) : null
    const byLabel = name ? sectorOptionsByLabel.value.get(name.toLowerCase()) : null
    const option = byId || byLabel

    if (!option) return null

    return {
      id: option.value,
      name: option.label,
      experience: normalizeSectorExperience(sector?.experience || DEFAULT_SECTOR_EXPERIENCE),
      iconClass: option.iconClass,
    }
  })
  .filter(Boolean)

const normalizeLanguages = (value) => toArray(value)
  .map((language) => ({
    name: normalizeLanguageName(language?.name),
    level: toText(language?.level || languageLevelOptions[2].value),
  }))
  .filter((language) => language.name)

const normalizeLicenses = (value) => toArray(value)
  .map((license) => (typeof license === 'string' ? license : license?.name || license?.title || ''))
  .map((license) => toText(license).trim())
  .filter(Boolean)

const normalizeResumeData = (value, source = {}) => {
  const defaults = createEmptyResumeData()
  const resumeData = value && typeof value === 'object' ? value : {}
  const legacyWorkExperience = resumeData.work_experience && typeof resumeData.work_experience === 'object'
    ? resumeData.work_experience
    : null
  const legacyEducation = resumeData.education && typeof resumeData.education === 'object'
    ? resumeData.education
    : null
  const rawWorkExperiences = Array.isArray(resumeData.work_experiences)
    ? resumeData.work_experiences
    : (legacyWorkExperience ? [legacyWorkExperience] : [])
  const rawEducations = Array.isArray(resumeData.educations)
    ? resumeData.educations
    : (legacyEducation ? [legacyEducation] : [])
  const workExperiences = rawWorkExperiences.map((entry, index) => ({
    ...createEmptyWorkExperience(),
    position: toText(entry?.position || (index === 0 ? source.current_role : '')),
    job_category: toText(entry?.job_category),
    company_name: toText(entry?.company_name),
    start_date: toText(entry?.start_date),
    end_date: toText(entry?.end_date),
    current: Boolean(entry?.current),
    country: toText(entry?.country || 'Latvia'),
    experience_years: toText(entry?.experience_years || (index === 0 ? resumeData.total_experience_years || legacyWorkExperience?.total_years : '')),
    description: toText(entry?.description || (index === 0 ? source.summary : '')),
  }))
  const educations = rawEducations.map((entry, index) => ({
    ...createEmptyEducation(),
    level: toText(entry?.level || (index === 0 ? source.education_level : '')),
    institution: toText(entry?.institution),
    speciality: toText(entry?.speciality),
    second_speciality: toText(entry?.second_speciality),
    country: toText(entry?.country || 'Latvia'),
    start_date: toText(entry?.start_date),
    end_date: toText(entry?.end_date),
    current: Boolean(entry?.current),
    unfinished: Boolean(entry?.unfinished),
    additional_information: toText(entry?.additional_information),
  }))

  return {
    ...defaults,
    cv_language: toText(resumeData.cv_language || defaults.cv_language),
    birth_date: toText(resumeData.birth_date || (
      resumeData.birth_year && resumeData.birth_month && resumeData.birth_day
        ? `${resumeData.birth_year}-${String(resumeData.birth_month).padStart(2, '0')}-${String(resumeData.birth_day).padStart(2, '0')}`
        : ''
    )),
    birth_month: toText(resumeData.birth_month),
    birth_day: toText(resumeData.birth_day),
    birth_year: toText(resumeData.birth_year),
    hide_birth_date: Boolean(resumeData.hide_birth_date),
    gender: toText(resumeData.gender),
    hide_gender: Boolean(resumeData.hide_gender),
    communication_language: toText(resumeData.communication_language || defaults.communication_language),
    additional_emails: toArray(resumeData.additional_emails).map((item) => toText(item).trim()).filter(Boolean),
    additional_phones: toArray(resumeData.additional_phones).map((item) => toText(item)).filter(Boolean),
    no_work_experience: Boolean(resumeData.no_work_experience ?? legacyWorkExperience?.no_experience),
    total_experience_years: toText(resumeData.total_experience_years || legacyWorkExperience?.total_years),
    work_experiences: workExperiences.length ? workExperiences : [createEmptyWorkExperience()],
    educations: educations.length ? educations : [createEmptyEducation()],
  }
}

const normalizeProfile = (value = {}) => {
  const source = value || {}

  return {
    ...createEmptyProfile(),
    ...source,
    email: toText(source.email).trim(),
    first_name: toText(source.first_name).trim(),
    last_name: toText(source.last_name).trim(),
    phone: toText(source.phone),
    summary: toText(source.summary),
    current_role: toText(source.current_role),
    skills: toText(source.skills),
    sectors: normalizeSectors(source.sectors ?? source.sectors_json),
    languages: normalizeLanguages(source.languages ?? source.languages_json),
    licenses: normalizeLicenses(source.licenses ?? source.licenses_json),
    mobility: toText(source.mobility),
    work_permit: normalizePermit(source.work_permit),
    availability: toText(source.availability),
    salary_expectation: toText(source.salary_expectation),
    preferred_employment_type: toText(source.preferred_employment_type),
    education_level: toText(source.education_level),
    remote_ready: Boolean(source.remote_ready),
    resume_name: toText(source.resume_name),
    resume_url: toText(source.resume_url),
    avatar_url: toText(source.avatar_url),
    resume_data: normalizeResumeData(
      typeof source.resume_data_json === 'string'
        ? (() => {
          try { return JSON.parse(source.resume_data_json) } catch { return {} }
        })()
        : (source.resume_data || source.resume_data_json),
      source,
    ),
  }
}

const fileSignature = (file) => {
  if (!file) return null

  return {
    name: file.name,
    size: file.size,
    type: file.type,
    lastModified: file.lastModified,
  }
}

const snapshotProfile = () => JSON.stringify({
  email: profile.value.email,
  first_name: profile.value.first_name,
  last_name: profile.value.last_name,
  phone: profile.value.phone,
  summary: profile.value.summary,
  current_role: profile.value.current_role,
  skills: profile.value.skills,
  sectors: profile.value.sectors,
  languages: profile.value.languages,
  licenses: profile.value.licenses,
  work_permit: profile.value.work_permit,
  availability: profile.value.availability,
  salary_expectation: profile.value.salary_expectation,
  preferred_employment_type: profile.value.preferred_employment_type,
  education_level: profile.value.education_level,
  remote_ready: profile.value.remote_ready,
  resume_name: profile.value.resume_name,
  resume_url: profile.value.resume_url,
  avatar_url: profile.value.avatar_url,
  resume_data: profile.value.resume_data,
  avatarFile: fileSignature(avatarFile.value),
  resumeFile: fileSignature(resumeFile.value),
})

const hasUnsavedChanges = computed(() => isLoaded.value && snapshotProfile() !== savedSnapshot.value)

const progressChecks = computed(() => [
  profile.value.resume_data.cv_language,
  profileEmail.value,
  profile.value.first_name,
  profile.value.last_name,
  profile.value.phone,
  profile.value.resume_data.birth_date,
  profile.value.resume_data.gender,
  profile.value.resume_data.communication_language,
  profile.value.resume_data.work_experiences[0]?.position,
  profile.value.resume_data.work_experiences[0]?.company_name,
  profile.value.resume_data.educations[0]?.level,
  profile.value.resume_data.educations[0]?.institution,
])

const filledFields = computed(() => progressChecks.value.filter(Boolean).length)
const progress = computed(() => Math.round((filledFields.value / progressChecks.value.length) * 100))

const canAddLanguage = computed(() => !profile.value.languages.some((language) => (
  language.name === newLanguage.value && language.level === newLanguageLevel.value
)))

const legacyStatusMessage = computed(() => {
  if (isLoading.value) return 'Загрузка профиля...'
  if (isSaving.value) return 'Сохраняем...'
  if (status.value) return status.value
  if (hasUnsavedChanges.value) return 'Есть несохранённые изменения.'
  return ''
})

const cvName = computed(() => fullName.value || 'Кандидат CVHOLD')
const cvRole = computed(() => profile.value.current_role.trim() || 'Специалист')
const cvSkills = computed(() => splitTextList(profile.value.skills))
const legacyCvSectors = computed(() => profile.value.sectors
  .map((sector) => {
    const option = getSectorOption(sector)
    if (!option) return null

    return {
      ...option,
      experience: toText(sector?.experience || DEFAULT_SECTOR_EXPERIENCE),
    }
  })
  .filter(Boolean))
const cvLanguages = computed(() => profile.value.languages.filter((language) => language.name && language.level))
const cvLicenses = computed(() => profile.value.licenses.filter(Boolean))

const cvVisibleSectors = computed(() => cvSectors.value.slice(0, MAX_PRINT_SECTORS))
const cvVisibleSkills = computed(() => cvSkills.value.slice(0, MAX_PRINT_SKILLS))
const cvVisibleLanguages = computed(() => cvLanguages.value.slice(0, MAX_PRINT_LANGUAGES))
const cvVisibleLicenses = computed(() => cvLicenses.value.slice(0, MAX_PRINT_LICENSES))

const cvMoreSectorsCount = computed(() => Math.max(0, cvSectors.value.length - cvVisibleSectors.value.length))
const cvMoreSkillsCount = computed(() => Math.max(0, cvSkills.value.length - cvVisibleSkills.value.length))
const cvMoreLanguagesCount = computed(() => Math.max(0, cvLanguages.value.length - cvVisibleLanguages.value.length))
const cvMoreLicensesCount = computed(() => Math.max(0, cvLicenses.value.length - cvVisibleLicenses.value.length))

const cvId = computed(() => {
  const source = `${profileEmail.value}-${profile.value.phone}-${displayCvName.value}`
  const number = (hashText(source) % 900000) + 100000
  return `CVH-${number}`
})

const cvPublicUrl = computed(() => `cvhold.com/profile/${cvId.value}`)

const legacyCvSummaryParagraphs = computed(() => {
  const summary = profile.value.summary.trim()

  if (summary) {
    return summary
      .split(/\n{2,}/)
      .map((paragraph) => limitText(paragraph, 280, { preserveLineBreaks: true }))
      .filter(Boolean)
      .slice(0, 2)
  }

  const fallbackParts = [
    profile.value.current_role ? `Специалист: ${profile.value.current_role}.` : '',
    cvSectors.value.length ? `Сферы деятельности: ${cvSectors.value.map((sector) => `${sector.label} (${sector.experience})`).join(', ')}.` : '',
    cvSkills.value.length ? `Ключевые навыки: ${cvSkills.value.slice(0, 8).join(', ')}.` : '',
  ].filter(Boolean)

  return [limitText(fallbackParts.join(' ') || 'Профиль кандидата будет сформирован после заполнения основной информации.', 520)]
})

const cvContactItems = computed(() => [
  ...[profileEmail.value, ...profile.value.resume_data.additional_emails].filter(Boolean).map((value) => ({
    icon: 'far fa-envelope',
    value,
  })),
  ...[profile.value.phone, ...profile.value.resume_data.additional_phones].filter(Boolean).map((value) => ({
    icon: 'fas fa-phone',
    value,
  })),
  {
    icon: 'fas fa-globe',
    value: cvPublicUrl.value,
  },
].filter((item) => item.value))

const legacyCvAdditionalItems = computed(() => [
  {
    icon: 'far fa-calendar-check',
    label: 'Готов приступить',
    value: availabilityLabel.value || 'Не указано',
  },
  {
    icon: 'far fa-id-card',
    label: 'Разрешение на работу',
    value: profile.value.work_permit || 'Не указано',
  },
])

const statusMessage = computed(() => {
  if (isLoading.value) return copy.value.loadingProfile
  if (isSaving.value) return copy.value.saving
  if (status.value) return status.value
  if (hasUnsavedChanges.value) return copy.value.unsaved
  return ''
})

const displayCvName = computed(() => fullName.value || copy.value.candidateName)
const primaryWorkExperience = computed(() => profile.value.resume_data.work_experiences[0] || createEmptyWorkExperience())
const primaryEducation = computed(() => profile.value.resume_data.educations[0] || createEmptyEducation())
const displayCvRole = computed(() => primaryWorkExperience.value.position.trim() || copy.value.candidateRole)

const cvSectors = computed(() => profile.value.sectors
  .map((sector) => {
    const option = getSectorOption(sector)
    if (!option) return null

    return {
      ...option,
      experience: displaySectorExperience(sector?.experience || DEFAULT_SECTOR_EXPERIENCE),
    }
  })
  .filter(Boolean))

const cvSummaryParagraphs = computed(() => {
  const summary = primaryWorkExperience.value.description.trim()

  if (summary) {
    return summary
      .split(/\n{2,}/)
      .map((paragraph) => limitText(paragraph, 280, { preserveLineBreaks: true }))
      .filter(Boolean)
      .slice(0, 2)
  }

  const fallbackParts = [
    primaryWorkExperience.value.position ? `${copy.value.summaryRole}: ${primaryWorkExperience.value.position}.` : '',
  ].filter(Boolean)

  return [limitText(fallbackParts.join(' ') || copy.value.summaryFallback, 520)]
})

const cvAdditionalItems = computed(() => [
  !profile.value.resume_data.hide_birth_date && {
    icon: 'far fa-calendar',
    label: copy.value.birthDate,
    value: formatDate(profile.value.resume_data.birth_date),
  },
  !profile.value.resume_data.hide_gender && {
    icon: 'fas fa-user',
    label: copy.value.gender,
    value: genderOptions.value.find((option) => option.value === profile.value.resume_data.gender)?.label || copy.value.notSpecified,
  },
  {
    icon: 'fas fa-globe',
    label: copy.value.communicationLanguage,
    value: cvLanguageOptions.value.find((option) => option.value === profile.value.resume_data.communication_language)?.label || copy.value.notSpecified,
  },
  {
    icon: 'fas fa-location-dot',
    label: copy.value.country,
    value: primaryWorkExperience.value.country || copy.value.notSpecified,
  },
  {
    icon: 'fas fa-user-graduate',
    label: copy.value.education,
    value: displayEducation(primaryEducation.value.level) || copy.value.notSpecified,
  },
].filter(Boolean))

const cvWorkExperiences = computed(() => profile.value.resume_data.work_experiences.filter((entry) => (
  entry.position || entry.company_name || entry.description
)))
const cvEducations = computed(() => profile.value.resume_data.educations.filter((entry) => (
  entry.level || entry.institution || entry.speciality
)))
const categoryLabel = (value) => jobCategoryOptions.value.find((option) => option.value === value)?.label || value
const formatDate = (value) => {
  if (!value) return ''
  const [year, month, day] = value.split('-').map(Number)
  if (!year || !month || !day) return value
  return new Intl.DateTimeFormat(language.value).format(new Date(year, month - 1, day))
}

const currentStepHeading = computed(() => {
  if (step.value === 1) return copy.value.step1Heading
  if (step.value === 2) return copy.value.step2Heading
  if (step.value === 3) return copy.value.step3Heading
  return copy.value.step4Heading
})

const currentStepDescription = computed(() => copy.value.stepDescriptions?.[step.value - 1] || '')
const currentStepIcon = computed(() => ['fa-user', 'fa-briefcase', 'fa-graduation-cap', 'fa-file-pdf'][step.value - 1])
const stepProgress = computed(() => Math.round((step.value / steps.value.length) * 100))

const formatMore = (key, count) => translate(`resumeBuilderPage.${key}`, { count }, language.value)

const addEmail = () => profile.value.resume_data.additional_emails.push('')
const removeEmail = (index) => profile.value.resume_data.additional_emails.splice(index, 1)
const addPhone = () => profile.value.resume_data.additional_phones.push('')
const removePhone = (index) => profile.value.resume_data.additional_phones.splice(index, 1)

const addWorkExperience = () => {
  profile.value.resume_data.work_experiences.push(createEmptyWorkExperience())
  expandedWorkIndex.value = profile.value.resume_data.work_experiences.length - 1
}

const removeWorkExperience = (index) => {
  if (profile.value.resume_data.work_experiences.length === 1) {
    profile.value.resume_data.work_experiences[0] = createEmptyWorkExperience()
    expandedWorkIndex.value = 0
    return
  }
  profile.value.resume_data.work_experiences.splice(index, 1)
  expandedWorkIndex.value = Math.min(index, profile.value.resume_data.work_experiences.length - 1)
}

const addEducation = () => {
  profile.value.resume_data.educations.push(createEmptyEducation())
  expandedEducationIndex.value = profile.value.resume_data.educations.length - 1
}

const removeEducation = (index) => {
  if (profile.value.resume_data.educations.length === 1) {
    profile.value.resume_data.educations[0] = createEmptyEducation()
    expandedEducationIndex.value = 0
    return
  }
  profile.value.resume_data.educations.splice(index, 1)
  expandedEducationIndex.value = Math.min(index, profile.value.resume_data.educations.length - 1)
}

const toggleCurrentWork = (work) => {
  if (work.current) work.end_date = ''
}

const toggleCurrentEducation = (education) => {
  if (education.current) education.end_date = ''
}

const workEntryMeta = (work) => [
  work.company_name,
  work.start_date && `${formatDate(work.start_date)} — ${work.current ? copy.value.present : (formatDate(work.end_date) || '…')}`,
].filter(Boolean).join(' · ')

const educationEntryMeta = (education) => [
  education.institution,
  education.start_date && `${formatDate(education.start_date)} — ${education.current ? copy.value.present : (formatDate(education.end_date) || '…')}`,
].filter(Boolean).join(' · ')

const cvQrCells = computed(() => Array.from({ length: 121 }, (_, index) => {
  const row = Math.floor(index / 11)
  const column = index % 11

  const topLeft = row < 3 && column < 3
  const topRight = row < 3 && column > 7
  const bottomLeft = row > 7 && column < 3

  if (topLeft || topRight || bottomLeft) {
    return true
  }

  return hashText(`${cvId.value}-${index}`) % 3 === 0
}))

const clearAutosaveTimer = () => {
  if (autosaveTimer) {
    window.clearTimeout(autosaveTimer)
    autosaveTimer = null
  }
}

const revokeAvatarPreview = () => {
  if (avatarObjectUrl.value) {
    URL.revokeObjectURL(avatarObjectUrl.value)
    avatarObjectUrl.value = ''
  }
}

const setError = (field, message) => {
  errors.value = { ...errors.value, [field]: message }
}

const clearError = (field) => {
  if (!errors.value[field]) return

  const nextErrors = { ...errors.value }
  delete nextErrors[field]
  errors.value = nextErrors
}

const clearErrors = () => {
  errors.value = {}
}

const getErrorMessage = (error, fallback) => (
  error?.response?.data?.message
  || error?.response?.data?.detail
  || error?.message
  || fallback
)

const readFileAsDataUrl = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader()

  reader.onload = () => resolve(toText(reader.result))
  reader.onerror = () => reject(new Error('Failed to read file.'))
  reader.readAsDataURL(file)
})

const saveGuestDraft = () => {
  if (typeof window === 'undefined') return

  const draft = {
    ...buildPayload(),
    email: profile.value.email.trim(),
    avatar: null,
    resume: null,
    avatar_url: profile.value.avatar_url || avatarPreview.value,
    resume_url: profile.value.resume_url,
    resume_name: profile.value.resume_name,
  }

  window.localStorage.setItem(GUEST_RESUME_DRAFT_KEY, JSON.stringify(draft))
  window.sessionStorage.removeItem(GUEST_RESUME_DRAFT_KEY)
}

const loadGuestDraft = () => {
  if (typeof window === 'undefined') return null

  const rawDraft = window.localStorage.getItem(GUEST_RESUME_DRAFT_KEY)
    || window.sessionStorage.getItem(GUEST_RESUME_DRAFT_KEY)
  if (!rawDraft) return null

  try {
    const draft = JSON.parse(rawDraft)
    window.localStorage.setItem(GUEST_RESUME_DRAFT_KEY, rawDraft)
    window.sessionStorage.removeItem(GUEST_RESUME_DRAFT_KEY)
    return draft
  } catch {
    return null
  }
}

const applyServerProfile = (rawProfile) => {
  isApplyingServerProfile = true
  profile.value = normalizeProfile(rawProfile)
  savedSnapshot.value = snapshotProfile()

  window.setTimeout(() => {
    isApplyingServerProfile = false
  }, 0)
}

const loadProfile = async () => {
  isLoading.value = true
  status.value = ''

  if (!isAuthenticated.value) {
    const guestDraft = loadGuestDraft()
    profile.value = normalizeProfile(guestDraft || {})
    savedSnapshot.value = snapshotProfile()
    status.value = guestDraft
      ? copy.value.guestDraftLoaded
      : copy.value.guestMode
    isLoading.value = false
    isLoaded.value = true
    return
  }

  try {
    const loadedProfile = await getProfile()
    const localDraft = loadGuestDraft()
    applyServerProfile(localDraft || loadedProfile)
    if (localDraft) status.value = copy.value.guestDraftLoaded
  } catch (error) {
    profile.value = createEmptyProfile()
    savedSnapshot.value = snapshotProfile()
    status.value = getErrorMessage(error, copy.value.loadProfileError)
  } finally {
    isLoading.value = false
    isLoaded.value = true
  }
}

const loadInitialData = async () => {
  try {
    if (!jobCategoryOptions.value.length && typeof jobsStore.initialize === 'function') {
      await jobsStore.initialize({})
    }
  } catch {
    // Компонент не должен падать, если категории временно недоступны.
  }

  await loadProfile()
}

const buildPayload = () => ({
  first_name: profile.value.first_name.trim(),
  last_name: profile.value.last_name.trim(),
  phone: profile.value.phone.trim(),
  summary: primaryWorkExperience.value.description.trim(),
  current_role: primaryWorkExperience.value.position.trim(),
  skills: profile.value.skills.trim(),
  sectors_json: profile.value.sectors
    .map((sector) => {
      const option = getSectorOption(sector)
      if (!option) return null

      return {
        id: option.value,
        name: option.label,
        experience: toText(sector?.experience || DEFAULT_SECTOR_EXPERIENCE),
        iconClass: option.iconClass,
      }
    })
    .filter(Boolean),
  languages_json: profile.value.languages,
  licenses_json: profile.value.licenses,
  mobility: '',
  preferred_mobility: '',
  work_permit: profile.value.work_permit,
  availability: profile.value.availability.trim(),
  salary_expectation: profile.value.salary_expectation.trim(),
  preferred_employment_type: profile.value.preferred_employment_type,
  education_level: primaryEducation.value.level,
  remote_ready: profile.value.remote_ready,
  avatar: avatarFile.value,
  resume: resumeFile.value,
  resume_data_json: profile.value.resume_data,
})

const performSave = async ({ silent = false, force = false } = {}) => {
  const snapshotBeforeSave = snapshotProfile()
  if (!force && snapshotBeforeSave === savedSnapshot.value) return true

  isSaving.value = true
  if (!silent) status.value = ''

  if (!isAuthenticated.value) {
    try {
      saveGuestDraft()
      savedSnapshot.value = snapshotProfile()
      clearErrors()
      status.value = silent ? '' : copy.value.saveDraftSuccess
      return true
    } catch (error) {
      status.value = getErrorMessage(error, copy.value.saveDraftError)
      return false
    } finally {
      isSaving.value = false
    }
  }

  try {
    const serverProfile = await updateProfile(buildPayload())
    const changedDuringRequest = snapshotProfile() !== snapshotBeforeSave

    if (changedDuringRequest) {
      shouldSaveAgain = true
      if (!silent) status.value = copy.value.saveLatest
      return true
    }

    avatarFile.value = null
    resumeFile.value = null
    revokeAvatarPreview()
    applyServerProfile(serverProfile)
    clearErrors()
    status.value = silent ? '' : copy.value.saveSuccess
    return true
  } catch (error) {
    status.value = getErrorMessage(error, copy.value.saveError)
    return false
  } finally {
    isSaving.value = false
  }
}

const saveProfile = async ({ silent = false, force = false } = {}) => {
  if (!isLoaded.value) return false

  clearAutosaveTimer()

  if (savePromise) {
    shouldSaveAgain = true
    await savePromise
    return saveProfile({ silent, force })
  }

  savePromise = (async () => {
    let success = true
    let firstRun = true

    do {
      shouldSaveAgain = false
      const saved = await performSave({
        silent: firstRun ? silent : true,
        force: firstRun ? force : false,
      })
      success = success && saved
      firstRun = false
    } while (success && shouldSaveAgain && snapshotProfile() !== savedSnapshot.value)

    return success
  })()

  try {
    return await savePromise
  } finally {
    savePromise = null
  }
}

const scheduleAutosave = () => {
  if (!isLoaded.value || isLoading.value || isApplyingServerProfile) return
  if (snapshotProfile() === savedSnapshot.value) return

  clearAutosaveTimer()
  autosaveTimer = window.setTimeout(() => {
    try {
      saveGuestDraft()
      savedSnapshot.value = snapshotProfile()
    } catch (error) {
      status.value = getErrorMessage(error, copy.value.saveDraftError)
    }
  }, AUTOSAVE_DELAY)
}

const validateStep = (stepId) => {
  const nextErrors = { ...errors.value }
  let isValid = true

  if (stepId === 1) {
    if (!profile.value.first_name.trim()) {
      nextErrors.first_name = copy.value.firstNameRequired
      isValid = false
    } else {
      delete nextErrors.first_name
    }

    if (!profile.value.last_name.trim()) {
      nextErrors.last_name = copy.value.lastNameRequired
      isValid = false
    } else {
      delete nextErrors.last_name
    }

    if (!profileEmail.value.trim()) {
      nextErrors.email = copy.value.emailRequired
      isValid = false
    } else {
      delete nextErrors.email
    }

    if (!profile.value.phone.trim()) {
      nextErrors.phone = copy.value.phoneRequired
      isValid = false
    } else {
      delete nextErrors.phone
    }

    const resumeData = profile.value.resume_data
    if (!resumeData.birth_date) {
      nextErrors.birth_date = copy.value.birthDateRequired
      isValid = false
    } else {
      delete nextErrors.birth_date
    }

    if (!resumeData.gender) {
      nextErrors.gender = copy.value.genderRequired
      isValid = false
    } else {
      delete nextErrors.gender
    }
  }

  if (stepId === 2) {
    const availability = profile.value.availability.trim()

    if (!isValidAvailability(availability)) {
      nextErrors.availability = copy.value.availabilityInvalid
      isValid = false
    } else {
      delete nextErrors.availability
    }
  }

  errors.value = nextErrors
  return isValid
}

const validateBeforeFinalSave = () => {
  if (!validateStep(1)) {
    step.value = 1
    status.value = copy.value.requiredFields
    return false
  }

  if (!validateStep(2)) {
    step.value = 2
    status.value = copy.value.requiredFields
    return false
  }

  return true
}

const validateFile = (file, { types, maxSize, label }) => {
  if (!file) return `${label}: ${copy.value.fileNotSelected}.`
  if (!types.includes(file.type)) return `${label}: ${copy.value.fileUnsupported}.`
  if (file.size > maxSize) return `${label}: ${copy.value.fileTooLarge}.`
  return ''
}

const addSector = () => {
  const option = selectedSectorOption.value
  if (!option) return

  if (!canAddSector.value) {
    setError('sectors', copy.value.sectorDuplicate)
    return
  }

  profile.value.sectors.push({
    id: option.value,
    name: option.label,
    experience: selectedSectorExperience.value,
    iconClass: option.iconClass,
  })

  selectedSector.value = ''
  selectedSectorExperience.value = DEFAULT_SECTOR_EXPERIENCE
  clearError('sectors')
}

const removeSector = (index) => {
  profile.value.sectors.splice(index, 1)
  clearError('sectors')
}

const addLanguage = () => {
  if (!canAddLanguage.value) return

  profile.value.languages.push({
    name: newLanguage.value,
    level: newLanguageLevel.value,
  })
}

const removeLanguage = (index) => {
  profile.value.languages.splice(index, 1)
}

const addLicense = () => {
  const value = toText(newLicense.value).trim()
  if (!value) return

  const exists = profile.value.licenses.some((license) => license.toLowerCase() === value.toLowerCase())
  if (exists) {
    setError('licenses', copy.value.licenseDuplicate)
    return
  }

  profile.value.licenses.push(value)
  clearError('licenses')
}

const removeLicense = (index) => {
  profile.value.licenses.splice(index, 1)
  clearError('licenses')
}

const openAvatarPicker = () => {
  avatarInputRef.value?.click()
}

const openResumePicker = () => {
  resumeInputRef.value?.click()
}

const onAvatarChange = async (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  const error = validateFile(file, {
    types: AVATAR_TYPES,
    maxSize: MAX_AVATAR_SIZE,
    label: copy.value.avatarLabel,
  })

  if (error) {
    setError('avatar', error)
    return
  }

  try {
    const avatarDataUrl = await readFileAsDataUrl(file)
    avatarFile.value = isAuthenticated.value ? file : null
    revokeAvatarPreview()
    profile.value.avatar_url = avatarDataUrl

    clearError('avatar')
    scheduleAutosave()
  } catch (error) {
    setError('avatar', getErrorMessage(error, copy.value.saveDraftError))
  }
}

const onResumeChange = (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  const error = validateFile(file, {
    types: RESUME_TYPES,
    maxSize: MAX_RESUME_SIZE,
    label: copy.value.resumeLabel,
  })

  if (error) {
    setError('resume', error)
    return
  }

  resumeFile.value = file
  profile.value.resume_name = file.name
  clearError('resume')
  scheduleAutosave()
}

const saveCurrentStep = async () => {
  if (!validateStep(step.value)) {
    status.value = copy.value.requiredFields
    return false
  }

  try {
    saveGuestDraft()
    savedSnapshot.value = snapshotProfile()
    return true
  } catch (error) {
    status.value = getErrorMessage(error, copy.value.saveDraftError)
    return false
  }
}

const goToStep = async (targetStep) => {
  if (targetStep === step.value) return

  if (targetStep < step.value) {
    step.value = targetStep
    return
  }

  const saved = await saveCurrentStep()
  if (saved) step.value = targetStep
}

const goNext = async () => {
  const saved = await saveCurrentStep()
  if (saved && step.value < steps.value.length) {
    step.value += 1
  }
}

const goPrev = () => {
  if (step.value > 1) step.value -= 1
}

const handleFinalSave = async () => {
  if (!validateBeforeFinalSave()) return
  const saved = await saveProfile({ silent: false, force: true })
  if (saved && isAuthenticated.value) {
    window.localStorage.removeItem(GUEST_RESUME_DRAFT_KEY)
    window.sessionStorage.removeItem(GUEST_RESUME_DRAFT_KEY)
  }
}

const getPrintableStyles = () => `
  @page {
    size: A4;
    margin: 0;
  }

  * {
    box-sizing: border-box !important;
  }

  html,
  body {
    width: 210mm !important;
    height: 297mm !important;
    margin: 0 !important;
    padding: 0 !important;
    background: #fff !important;
    overflow: hidden !important;
  }

  body {
    display: block !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    font-family: Inter, Arial, sans-serif !important;
  }

  .cv-document {
    --cv-green: #149447;
    --cv-green-dark: #0f7f3c;
    --cv-ink: #101828;
    --cv-muted: #667085;
    --cv-line: #d9dee7;
    --cv-soft: #f3fbf6;
    width: 210mm !important;
    min-width: 210mm !important;
    max-width: 210mm !important;
    height: 297mm !important;
    min-height: 297mm !important;
    max-height: 297mm !important;
    margin: 0 !important;
    padding: 10mm 12mm 8mm !important;
    border: 0 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    background: #fff !important;
    color: var(--cv-ink) !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 0 !important;
    font-family: Inter, Arial, sans-serif !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  .cv-header,
  .cv-top,
  .cv-footer {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 9mm !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
  }

  .cv-header > *,
  .cv-top > *,
  .cv-footer > * {
    min-width: 0 !important;
  }

  .cv-header {
    min-height: 12mm !important;
    padding-bottom: 5mm !important;
    border-bottom: 0.35mm solid var(--cv-line) !important;
  }

  .cv-brand {
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
    gap: 3mm !important;
    min-width: 0 !important;
    color: var(--cv-ink) !important;
  }

  .cv-brand__logo,
  .cv-brand__logo svg {
    width: 34mm !important;
    max-width: 34mm !important;
    height: auto !important;
    max-height: 9mm !important;
    display: block !important;
    flex: 0 0 auto !important;
  }

  .cv-brand small {
    display: block !important;
    color: var(--cv-muted) !important;
    font-size: 6.2pt !important;
    line-height: 1 !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    white-space: nowrap !important;
  }

  .cv-verified {
    display: inline-flex !important;
    align-items: center !important;
    gap: 2.5mm !important;
    color: var(--cv-green) !important;
    flex: 0 0 auto !important;
  }

  .cv-top {
    padding: 7mm 0 6mm !important;
    border-bottom: 0.35mm solid var(--cv-line) !important;
    align-items: flex-start !important;
    justify-content: space-between !important;
  }

  .cv-person {
    display: grid !important;
    grid-template-columns: 18mm minmax(0, 1fr) !important;
    gap: 4.2mm !important;
    align-items: start !important;
    flex: 1 1 auto !important;
    min-width: 0 !important;
  }

  .cv-avatar {
    width: 18mm !important;
    height: 18mm !important;
    display: grid !important;
    place-items: center !important;
    overflow: hidden !important;
    border-radius: 50% !important;
    background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%) !important;
    color: #fff !important;
    font-size: 10pt !important;
    line-height: 1 !important;
    font-weight: 900 !important;
  }

  .cv-avatar img {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    display: block !important;
  }

  .cv-person h1 {
    margin: 0 !important;
    color: #05070a !important;
    font-size: 25pt !important;
    line-height: 0.95 !important;
    letter-spacing: -0.055em !important;
    max-width: 126mm !important;
    overflow-wrap: anywhere !important;
  }

  .cv-person p {
    margin: 2mm 0 3.2mm !important;
    color: var(--cv-green) !important;
    font-size: 10.3pt !important;
    line-height: 1.1 !important;
    font-weight: 800 !important;
  }

  .cv-contact-list,
  .cv-list,
  .cv-extra-list {
    margin: 0 !important;
    padding: 0 !important;
    list-style: none !important;
  }

  .cv-contact-list {
    display: grid !important;
    gap: 1.4mm !important;
  }

  .cv-contact-list li {
    display: flex !important;
    align-items: center !important;
    gap: 2mm !important;
    color: var(--cv-ink) !important;
    font-size: 7.7pt !important;
    line-height: 1.2 !important;
    min-width: 0 !important;
  }

  .cv-contact-list span,
  .cv-extra-list span,
  .cv-list li,
  .cv-sector span {
    overflow-wrap: anywhere !important;
  }

  .cv-contact-list i,
  .cv-extra-list i {
    width: 4mm !important;
    color: var(--cv-green) !important;
    text-align: center !important;
    flex: 0 0 auto !important;
  }

  .cv-id {
    display: grid !important;
    justify-items: center !important;
    align-self: flex-start !important;
    gap: 1mm !important;
    color: var(--cv-ink) !important;
    flex: 0 0 auto !important;
  }

  .cv-id small {
    margin-top: 1.2mm !important;
    color: var(--cv-green) !important;
    font-size: 6.2pt !important;
    line-height: 1 !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
  }

  .cv-id > strong {
    font-size: 7.5pt !important;
    line-height: 1 !important;
  }

  .cv-qr {
    position: relative !important;
    width: 24mm !important;
    height: 24mm !important;
    display: grid !important;
    grid-template-columns: repeat(11, 1fr) !important;
    grid-template-rows: repeat(11, 1fr) !important;
    gap: 0.32mm !important;
    padding: 1.4mm !important;
    border: 0.35mm solid var(--cv-line) !important;
    border-radius: 1.4mm !important;
    background: #fff !important;
  }

  .cv-qr-cell {
    background: transparent !important;
    border-radius: 0.15mm !important;
  }

  .cv-qr-cell--active {
    background: #111 !important;
  }

  .cv-qr strong {
    position: absolute !important;
    inset: 50% auto auto 50% !important;
    width: 6.4mm !important;
    height: 6.4mm !important;
    display: grid !important;
    place-items: center !important;
    transform: translate(-50%, -50%) !important;
    border-radius: 1mm !important;
    background: #111 !important;
    color: var(--cv-green) !important;
    font-size: 5.4pt !important;
    line-height: 1 !important;
    font-weight: 900 !important;
  }

  .cv-body {
    display: grid !important;
    grid-template-columns: minmax(0, 1.34fr) minmax(45mm, 0.82fr) !important;
    gap: 7mm !important;
    padding-top: 6mm !important;
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow: hidden !important;
  }

  .cv-main {
    min-height: 0 !important;
    overflow: hidden !important;
    padding-right: 7mm !important;
    border-right: 0.35mm solid var(--cv-line) !important;
  }

  .cv-aside {
    min-height: 0 !important;
    overflow: hidden !important;
  }

  .cv-section {
    padding-bottom: 4mm !important;
    margin-bottom: 4mm !important;
    border-bottom: 0.35mm solid var(--cv-line) !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .cv-section:last-child {
    margin-bottom: 0 !important;
  }

  .cv-section h2 {
    margin: 0 0 2.3mm !important;
    color: var(--cv-ink) !important;
    font-size: 8.2pt !important;
    line-height: 1.1 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
  }

  .cv-section p {
    margin: 0 !important;
    color: var(--cv-ink) !important;
    font-size: 7.6pt !important;
    line-height: 1.4 !important;
  }

  .cv-summary-text {
    display: -webkit-box !important;
    -webkit-line-clamp: 5 !important;
    -webkit-box-orient: vertical !important;
    overflow: hidden !important;
    white-space: pre-line !important;
  }

  .cv-section p + p {
    margin-top: 2mm !important;
  }

  .cv-list {
    display: grid !important;
    gap: 1.45mm !important;
  }

  .cv-list li {
    position: relative !important;
    padding-left: 3.7mm !important;
    color: var(--cv-ink) !important;
    font-size: 7.4pt !important;
    line-height: 1.24 !important;
  }

  .cv-list li::before {
    content: '' !important;
    position: absolute !important;
    top: 3.1mm !important;
    left: 0.55mm !important;
    width: 1mm !important;
    height: 1mm !important;
    border-radius: 50% !important;
    background: var(--cv-green) !important;
  }

  .cv-sector-grid {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 1.8mm !important;
  }

  .cv-sector {
    display: flex !important;
    align-items: center !important;
    gap: 1.8mm !important;
    min-height: 8.5mm !important;
    padding: 1.8mm 2.1mm !important;
    border: 0.35mm solid #d9f2e2 !important;
    border-radius: 2.5mm !important;
    background: var(--cv-soft) !important;
    color: var(--cv-ink) !important;
    font-size: 7pt !important;
    line-height: 1.16 !important;
    font-weight: 800 !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .cv-sector i {
    color: var(--cv-green) !important;
    flex: 0 0 auto !important;
  }

  .cv-extra-list {
    display: grid !important;
    gap: 1.8mm !important;
  }

  .cv-extra-list li {
    display: grid !important;
    grid-template-columns: 4.2mm minmax(0, 1fr) !important;
    gap: 1.7mm !important;
    align-items: start !important;
    color: var(--cv-ink) !important;
    font-size: 7.2pt !important;
    line-height: 1.25 !important;
  }

  .cv-more-item {
    color: var(--cv-muted) !important;
    font-weight: 800 !important;
  }

  .cv-footer {
    margin-top: auto !important;
    padding-top: 3mm !important;
    border-top: 0.35mm solid var(--cv-line) !important;
    color: var(--cv-muted) !important;
    font-size: 6.8pt !important;
    line-height: 1.1 !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .cv-brand--small .cv-brand__logo,
  .cv-brand--small .cv-brand__logo svg {
    width: 26mm !important;
    max-width: 26mm !important;
    max-height: 7mm !important;
  }
`


const buildPrintableDocument = () => {
  const source = cvDocumentRef.value
  if (!source) return null

  removePrintFrame()

  const iframe = document.createElement('iframe')
  iframe.setAttribute('title', 'CVHOLD CV PDF')
  iframe.style.position = 'fixed'
  iframe.style.left = '-10000px'
  iframe.style.top = '0'
  iframe.style.width = '210mm'
  iframe.style.height = '297mm'
  iframe.style.border = '0'
  iframe.style.background = '#fff'
  iframe.style.opacity = '0'
  iframe.style.pointerEvents = 'none'

  document.body.appendChild(iframe)
  printFrame = iframe

  const printWindow = iframe.contentWindow
  const printDocument = printWindow?.document

  if (!printWindow || !printDocument) {
    removePrintFrame()
    return null
  }

  printDocument.open()
  printDocument.write(`
    <!doctype html>
    <html class="cv-print-root">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=794, initial-scale=1">
        <base href="${document.baseURI}">
        <title>${displayCvName.value} — CVHOLD CV</title>
      </head>
      <body class="cv-print-body"></body>
    </html>
  `)
  printDocument.close()

  Array.from(document.querySelectorAll('style, link[rel="stylesheet"]')).forEach((node) => {
    const clonedNode = node.cloneNode(true)
    if (clonedNode.tagName === 'LINK') clonedNode.setAttribute('media', 'all')
    printDocument.head.appendChild(clonedNode)
  })

  const printStyle = printDocument.createElement('style')
  printStyle.textContent = getPrintableStyles()
  printDocument.head.appendChild(printStyle)

  const clone = source.cloneNode(true)
  clone.classList.add('cv-document--print')
  clone.removeAttribute('style')
  printDocument.body.appendChild(clone)

  return {
    iframe,
    printWindow,
    printDocument,
  }
}

const printCv = async () => {
  if (!validateBeforeFinalSave()) return

  try {
    saveGuestDraft()
    savedSnapshot.value = snapshotProfile()
  } catch (error) {
    status.value = getErrorMessage(error, copy.value.saveDraftError)
    return
  }

  await nextTick()

  const printable = buildPrintableDocument()

  if (!printable) {
    status.value = copy.value.pdfPrepareError
    return
  }

  const { iframe, printWindow, printDocument } = printable

  await waitForStylesheets(printDocument)
  await waitForImages(printDocument.body)

  try {
    await printDocument.fonts?.ready
  } catch {
    // PDF не должен блокироваться из-за шрифтов.
  }

  await wait(500)

  const cleanup = () => {
    if (printFrame === iframe) {
      removePrintFrame()
    }

    printWindow.removeEventListener('afterprint', cleanup)
  }

  printWindow.addEventListener('afterprint', cleanup)
  printWindow.focus()
  status.value = copy.value.printHint
  printWindow.print()

  window.setTimeout(cleanup, 8000)
}

watch(
  profile,
  () => {
    scheduleAutosave()
  },
  { deep: true },
)

watch([avatarFile, resumeFile], () => {
  scheduleAutosave()
})

onMounted(loadInitialData)

onBeforeUnmount(() => {
  removePrintFrame()
  clearAutosaveTimer()
  revokeAvatarPreview()
})
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="hero no-print">
        <div class="hero-copy">
          <span class="builder-kicker"><i class="fas fa-wand-magic-sparkles"></i>{{ copy.builderKicker }}</span>
          <div class="title-row">
            <h1>{{ copy.pageTitle }}</h1>
            <span class="hero-progress">{{ stepProgress }}%</span>
          </div>

          <p>{{ copy.pageDescription }}</p>
        </div>

        <div class="steps">
          <button
            v-for="item in steps"
            :key="item.id"
            type="button"
            class="step"
            :class="{ 'step--active': step === item.id, 'step--done': step > item.id }"
            :disabled="isSaving && item.id > step"
            @click="goToStep(item.id)"
          >
            <span class="step-index">{{ item.id }}</span>
            <span class="step-copy">
              <strong>{{ item.title }}</strong>
              <small>{{ item.subtitle }}</small>
            </span>
          </button>
        </div>
      </section>

      <section class="builder">
        <div class="main-card">
          <div class="card-head no-print">
            <span class="card-head__icon"><i class="fas" :class="currentStepIcon"></i></span>
            <div class="card-head__copy">
              <span class="card-head__step">{{ copy.stepLabel }} {{ step }} / {{ steps.length }}</span>
              <h2>{{ currentStepHeading }}</h2>
              <p v-if="currentStepDescription">{{ currentStepDescription }}</p>
              <p v-if="statusMessage" class="hint"><i class="fas fa-cloud-arrow-up"></i>{{ statusMessage }}</p>
            </div>
          </div>

          <template v-if="step === 1">
            <div class="form-stack">
              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-address-card"></i></span>
                  <div><h3>{{ copy.identitySection }}</h3><p>{{ copy.identitySectionHint }}</p></div>
                </div>

                <div class="form-grid">
                  <label>
                    <span class="field-label">{{ copy.firstName }} <b>*</b></span>
                    <input v-model="profile.first_name" :placeholder="copy.firstNamePlaceholder" @input="clearError('first_name')" />
                    <span v-if="errors.first_name" class="field-error">{{ errors.first_name }}</span>
                  </label>

                  <label>
                    <span class="field-label">{{ copy.lastName }} <b>*</b></span>
                    <input v-model="profile.last_name" :placeholder="copy.lastNamePlaceholder" @input="clearError('last_name')" />
                    <span v-if="errors.last_name" class="field-error">{{ errors.last_name }}</span>
                  </label>

                  <div class="contact-group">
                    <span class="field-label">Email <b>*</b></span>
                    <label class="contact-row">
                      <input v-if="!isAuthenticated" v-model="profile.email" type="email" placeholder="email@example.com" />
                      <input v-else :value="profileEmail" disabled />
                    </label>
                    <label v-for="(_, index) in profile.resume_data.additional_emails" :key="`email-${index}`" class="contact-row">
                      <input v-model="profile.resume_data.additional_emails[index]" type="email" :placeholder="`email${index + 2}@example.com`" />
                      <button type="button" class="contact-remove" :aria-label="copy.removeEntry" @click="removeEmail(index)"><i class="far fa-trash-can"></i></button>
                    </label>
                    <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
                    <button type="button" class="contact-add" @click="addEmail"><i class="fas fa-plus"></i>{{ copy.addEmail }}</button>
                  </div>

                  <div class="contact-group">
                    <span class="field-label">{{ copy.phone }} <b>*</b></span>
                    <label class="contact-row"><PhoneInput v-model="profile.phone" placeholder="2X XXX XXX" :aria-label="copy.phone" /></label>
                    <label v-for="(_, index) in profile.resume_data.additional_phones" :key="`phone-${index}`" class="contact-row">
                      <PhoneInput v-model="profile.resume_data.additional_phones[index]" placeholder="2X XXX XXX" :aria-label="`${copy.phone} ${index + 2}`" />
                      <button type="button" class="contact-remove" :aria-label="copy.removeEntry" @click="removePhone(index)"><i class="far fa-trash-can"></i></button>
                    </label>
                    <span v-if="errors.phone" class="field-error">{{ errors.phone }}</span>
                    <button type="button" class="contact-add" @click="addPhone"><i class="fas fa-plus"></i>{{ copy.addPhone }}</button>
                  </div>
                </div>
              </section>

              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-user-shield"></i></span>
                  <div><h3>{{ copy.personalSection }}</h3><p>{{ copy.personalSectionHint }}</p></div>
                </div>

                <div class="form-grid">
                  <div class="field-cluster">
                    <label>
                      <span class="field-label">{{ copy.birthDate }} <b>*</b></span>
                      <input v-model="profile.resume_data.birth_date" type="date" @input="clearError('birth_date')" />
                      <span v-if="errors.birth_date" class="field-error">{{ errors.birth_date }}</span>
                    </label>
                    <label class="checkbox-field"><input v-model="profile.resume_data.hide_birth_date" type="checkbox" /><span>{{ copy.hideInCv }}</span></label>
                  </div>

                  <div class="field-cluster">
                    <label>
                      <span class="field-label">{{ copy.gender }} <b>*</b></span>
                      <BaseDropdown v-model="profile.resume_data.gender" full-width overlay :options="genderOptions" @change="clearError('gender')" />
                      <span v-if="errors.gender" class="field-error">{{ errors.gender }}</span>
                    </label>
                    <label class="checkbox-field"><input v-model="profile.resume_data.hide_gender" type="checkbox" /><span>{{ copy.hideInCv }}</span></label>
                  </div>
                </div>
              </section>

              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-language"></i></span>
                  <div><h3>{{ copy.languageSection }}</h3><p>{{ copy.languageSectionHint }}</p></div>
                </div>
                <div class="form-grid">
                  <label><span class="field-label">{{ copy.cvLanguage }} <b>*</b></span><BaseDropdown v-model="profile.resume_data.cv_language" full-width overlay :options="cvLanguageOptions" /></label>
                  <label><span class="field-label">{{ copy.communicationLanguage }} <b>*</b></span><BaseDropdown v-model="profile.resume_data.communication_language" full-width overlay :options="cvLanguageOptions" /></label>
                </div>
              </section>
            </div>
          </template>

          <template v-else-if="step === 2">
            <div class="form-stack">
              <label class="checkbox-field choice-card">
                <input v-model="profile.resume_data.no_work_experience" type="checkbox" />
                <span><strong>{{ copy.noWorkExperience }}</strong><small>{{ copy.noWorkExperienceHint }}</small></span>
              </label>

              <template v-if="!profile.resume_data.no_work_experience">
                <section
                  v-for="(work, index) in profile.resume_data.work_experiences"
                  :key="`work-${index}`"
                  class="entry-card"
                  :class="{ 'entry-card--collapsed': expandedWorkIndex !== index }"
                >
                  <div class="entry-card__head">
                    <button
                      type="button"
                      class="entry-card__toggle"
                      :aria-expanded="expandedWorkIndex === index"
                      :aria-label="expandedWorkIndex === index ? copy.collapseEntry : copy.expandEntry"
                      @click="expandedWorkIndex = expandedWorkIndex === index ? -1 : index"
                    >
                      <span class="entry-index">{{ index + 1 }}</span>
                      <span class="entry-card__title">
                        <strong>{{ work.position || `${copy.workPlace} ${index + 1}` }}</strong>
                        <small>{{ workEntryMeta(work) || copy.emptyEntryHint }}</small>
                      </span>
                      <i class="fas fa-chevron-down"></i>
                    </button>
                    <button type="button" class="entry-remove" @click="removeWorkExperience(index)"><i class="far fa-trash-can"></i>{{ copy.removeEntry }}</button>
                  </div>

                  <div v-show="expandedWorkIndex === index" class="entry-card__body">
                    <label>{{ copy.position }}<input v-model="work.position" /></label>
                    <label>{{ copy.jobCategory }}<BaseDropdown v-model="work.job_category" full-width overlay :options="sectorDropdownOptions" /></label>
                    <label>{{ copy.companyName }}<input v-model="work.company_name" /></label>
                    <label>{{ copy.country }}<BaseDropdown v-model="work.country" full-width overlay :options="countryOptions" /></label>
                    <label>{{ copy.totalExperience }}<input v-model="work.experience_years" type="number" min="0" :placeholder="copy.yearsPlaceholder" /></label>

                    <div class="grid-two entry-wide">
                      <label>{{ copy.start }}<input v-model="work.start_date" type="date" /></label>
                      <label>{{ copy.end }}<input v-model="work.end_date" type="date" :disabled="work.current" /></label>
                    </div>

                    <label class="checkbox-field current-field entry-wide"><input v-model="work.current" type="checkbox" @change="toggleCurrentWork(work)" /><span>{{ copy.currentlyWorking }}</span></label>
                    <label class="entry-wide">{{ copy.workDescription }}<textarea v-model="work.description" rows="5" :placeholder="copy.workDescriptionPlaceholder"></textarea></label>
                  </div>
                </section>

                <button type="button" class="btn-light entry-add" @click="addWorkExperience"><i class="fas fa-plus"></i>{{ copy.addWorkExperience }}</button>
              </template>
            </div>
          </template>

          <template v-else-if="step === 3">
            <div class="form-stack">
              <section
                v-for="(education, index) in profile.resume_data.educations"
                :key="`education-${index}`"
                class="entry-card"
                :class="{ 'entry-card--collapsed': expandedEducationIndex !== index }"
              >
                <div class="entry-card__head">
                  <button
                    type="button"
                    class="entry-card__toggle"
                    :aria-expanded="expandedEducationIndex === index"
                    :aria-label="expandedEducationIndex === index ? copy.collapseEntry : copy.expandEntry"
                    @click="expandedEducationIndex = expandedEducationIndex === index ? -1 : index"
                  >
                    <span class="entry-index">{{ index + 1 }}</span>
                    <span class="entry-card__title">
                      <strong>{{ education.institution || `${copy.educationPlace} ${index + 1}` }}</strong>
                      <small>{{ educationEntryMeta(education) || copy.emptyEntryHint }}</small>
                    </span>
                    <i class="fas fa-chevron-down"></i>
                  </button>
                  <button type="button" class="entry-remove" @click="removeEducation(index)"><i class="far fa-trash-can"></i>{{ copy.removeEntry }}</button>
                </div>

                <div v-show="expandedEducationIndex === index" class="entry-card__body">
                  <label>{{ copy.educationLevel }}<BaseDropdown v-model="education.level" full-width overlay :options="educationOptions" /></label>
                  <label>{{ copy.institution }}<input v-model="education.institution" /></label>
                  <label>{{ copy.speciality }}<input v-model="education.speciality" /></label>
                  <label>{{ copy.secondSpeciality }}<input v-model="education.second_speciality" /></label>
                  <label>{{ copy.country }}<BaseDropdown v-model="education.country" full-width overlay :options="countryOptions" /></label>

                  <div class="grid-two entry-wide">
                    <label>{{ copy.start }}<input v-model="education.start_date" type="date" /></label>
                    <label>{{ copy.end }}<input v-model="education.end_date" type="date" :disabled="education.current" /></label>
                  </div>

                  <div class="grid-two entry-wide option-row">
                    <label class="checkbox-field current-field"><input v-model="education.current" type="checkbox" @change="toggleCurrentEducation(education)" /><span>{{ copy.currentlyStudying }}</span></label>
                    <label class="checkbox-field"><input v-model="education.unfinished" type="checkbox" /><span>{{ copy.unfinished }}</span></label>
                  </div>

                  <label class="entry-wide">{{ copy.additionalInformation }}<textarea v-model="education.additional_information" rows="5" :placeholder="copy.educationInfoPlaceholder"></textarea></label>
                </div>
              </section>

              <button type="button" class="btn-light entry-add" @click="addEducation"><i class="fas fa-plus"></i>{{ copy.addEducation }}</button>
            </div>
          </template>

          <template v-else>
            <div class="final-tools no-print">
              <div class="review-card">
                <div>
                  <h3>{{ copy.readyCv }}</h3>
                  <p>{{ copy.readyCvDescription }}</p>
                </div>

                <div class="review-actions">
                  <button v-if="isAuthenticated" type="button" class="btn-light" :disabled="isSaving" @click="handleFinalSave">
                    <i class="far fa-floppy-disk"></i>{{ isSaving ? copy.saving : copy.save }}
                  </button>
                  <button type="button" class="btn-primary" :disabled="isSaving" @click="printCv">
                    <i class="fas fa-file-arrow-down"></i>{{ copy.downloadPdf }}
                  </button>
                </div>
              </div>
            </div>

            <section class="cv-preview-shell">
              <article ref="cvDocumentRef" class="cv-document">
                <header class="cv-header">
                  <div class="cv-brand" aria-label="CVHOLD">
                    <Logo class="cv-brand__logo" aria-hidden="true" />
                  </div>
                </header>

                <section class="cv-top">
                  <div class="cv-person">
                    <div class="cv-avatar">
                      <img v-if="avatarPreview" :src="avatarPreview" :alt="displayCvName" />
                      <span v-else>{{ avatarInitials }}</span>
                    </div>

                    <div>
                      <h1>{{ displayCvName }}</h1>
                      <p>{{ displayCvRole }}</p>

                      <ul class="cv-contact-list">
                        <li v-for="(item, index) in cvContactItems" :key="`${item.icon}-${index}`">
                          <i :class="item.icon"></i>
                          <span>{{ item.value }}</span>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <div class="cv-id">
                    <div class="cv-qr" aria-hidden="true">
                      <span
                        v-for="(active, index) in cvQrCells"
                        :key="index"
                        class="cv-qr-cell"
                        :class="{ 'cv-qr-cell--active': active }"
                      ></span>
                      <strong>CV</strong>
                    </div>

                    <small>CVHOLD ID</small>
                    <strong>{{ cvId }}</strong>
                  </div>
                </section>

                <section class="cv-body">
                  <main class="cv-main">
                    <section class="cv-section cv-section--summary">
                      <h2>{{ copy.aboutMe }}</h2>
                      <p
                        v-for="paragraph in cvSummaryParagraphs"
                        :key="paragraph"
                        class="cv-summary-text"
                      >
                        {{ paragraph }}
                      </p>
                    </section>

                    <section v-if="!profile.resume_data.no_work_experience && cvWorkExperiences.length" class="cv-section">
                      <h2>{{ copy.workExperience }}</h2>
                      <div v-for="(work, index) in cvWorkExperiences" :key="`cv-work-${index}`" class="cv-entry">
                        <p class="cv-summary-text">
                          <strong>{{ work.position }}</strong>
                          <span v-if="work.company_name"> · {{ work.company_name }}</span>
                        </p>
                        <p class="cv-summary-text">
                          {{ formatDate(work.start_date) }}
                          —
                          {{ work.current ? copy.present : formatDate(work.end_date) }}
                          <span v-if="work.job_category"> · {{ categoryLabel(work.job_category) }}</span>
                          <span v-if="work.country"> · {{ work.country }}</span>
                          <span v-if="work.experience_years"> · {{ copy.totalExperience }}: {{ work.experience_years }}</span>
                        </p>
                        <p v-if="work.description" class="cv-summary-text">{{ work.description }}</p>
                      </div>
                    </section>

                    <section v-if="cvEducations.length" class="cv-section">
                      <h2>{{ copy.education }}</h2>
                      <div v-for="(education, index) in cvEducations" :key="`cv-education-${index}`" class="cv-entry">
                        <p class="cv-summary-text"><strong>{{ education.institution }}</strong></p>
                        <p class="cv-summary-text">
                          {{ displayEducation(education.level) }}
                          <span v-if="education.speciality"> · {{ education.speciality }}</span>
                          <span v-if="education.second_speciality"> · {{ education.second_speciality }}</span>
                          <span v-if="education.country"> · {{ education.country }}</span>
                          <span v-if="education.start_date || education.end_date"> · {{ formatDate(education.start_date) }}—{{ education.current ? copy.present : formatDate(education.end_date) }}</span>
                        </p>
                        <p v-if="education.additional_information" class="cv-summary-text">{{ education.additional_information }}</p>
                      </div>
                    </section>

                    <section v-if="cvVisibleSectors.length" class="cv-section">
                      <h2>{{ copy.workAreas }}</h2>
                      <div class="cv-sector-grid">
                        <div v-for="sector in cvVisibleSectors" :key="sector.value" class="cv-sector">
                          <i :class="sector.iconClass"></i>
                          <span class="cv-sector__copy">
                            <strong>{{ sector.label }}</strong>
                            <small>{{ sector.experience }}</small>
                          </span>
                        </div>
                        <div v-if="cvMoreSectorsCount" class="cv-sector cv-more-item">
                          <span>{{ formatMore('moreItems', cvMoreSectorsCount) }}</span>
                        </div>
                      </div>
                    </section>

                    <section v-if="cvVisibleSkills.length" class="cv-section">
                      <h2>{{ copy.skills }}</h2>
                      <ul class="cv-list">
                        <li v-for="skill in cvVisibleSkills" :key="skill">{{ skill }}</li>
                        <li v-if="cvMoreSkillsCount" class="cv-more-item">
                          {{ formatMore('moreItems', cvMoreSkillsCount) }}
                        </li>
                      </ul>
                    </section>
                  </main>

                  <aside class="cv-aside">
                    <section v-if="cvVisibleLanguages.length" class="cv-section">
                      <h2>{{ copy.languages }}</h2>
                      <ul class="cv-list">
                        <li v-for="language in cvVisibleLanguages" :key="`${language.name}-${language.level}`">
                          {{ displayLanguageName(language.name) }} — {{ language.level }}
                        </li>
                        <li v-if="cvMoreLanguagesCount" class="cv-more-item">
                          {{ formatMore('moreItems', cvMoreLanguagesCount) }}
                        </li>
                      </ul>
                    </section>

                    <section v-if="cvVisibleLicenses.length" class="cv-section">
                      <h2>{{ copy.certificatesAndLicenses }}</h2>
                      <ul class="cv-list">
                        <li v-for="license in cvVisibleLicenses" :key="license">{{ license }}</li>
                        <li v-if="cvMoreLicensesCount" class="cv-more-item">
                          {{ formatMore('moreItems', cvMoreLicensesCount) }}
                        </li>
                      </ul>
                    </section>

                    <section class="cv-section">
                      <h2>{{ copy.additionalDetails }}</h2>
                      <ul class="cv-extra-list">
                        <li v-for="item in cvAdditionalItems" :key="item.label">
                          <i :class="item.icon"></i>
                          <span>{{ item.label }}: {{ item.value }}</span>
                        </li>
                      </ul>
                    </section>
                  </aside>
                </section>

                <footer class="cv-footer">
                  <div class="cv-brand cv-brand--small" aria-label="CVHOLD">
                    <Logo class="cv-brand__logo" aria-hidden="true" />
                  </div>

                  <span>{{ copy.cvFooterTagline }}</span>
                  <span>www.cvhold.com</span>
                </footer>
              </article>
            </section>
          </template>

          <div class="footer-actions no-print">
            <button type="button" class="btn-light" :disabled="step === 1 || isSaving" @click="goPrev">
              <i class="fas fa-arrow-left"></i>{{ copy.back }}
            </button>

            <span class="footer-step">{{ step }} / {{ steps.length }}</span>

            <button v-if="step < 4" type="button" class="btn-primary" :disabled="isSaving" @click="goNext">
              {{ isSaving ? copy.saving : copy.next }}<i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>

        <aside class="sidebar no-print">
          <div class="side-card profile-card">
            <input
              ref="avatarInputRef"
              class="upload-card__input"
              type="file"
              accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
              @change="onAvatarChange"
            />
            <div class="profile-card__top">
              <button type="button" class="profile-avatar profile-avatar--button" :aria-label="copy.uploadAvatar" @click="openAvatarPicker">
                <img v-if="avatarPreview" class="profile-avatar__image" :src="avatarPreview" :alt="copy.avatar" />
                <span v-else>{{ avatarInitials }}</span>
              </button>

              <div>
                <strong>{{ fullName || copy.yourName }}</strong>
                <p>{{ primaryWorkExperience.position || copy.profession }}</p>
              </div>
            </div>

            <div class="profile-meta">
              <span><i class="far fa-envelope"></i>{{ profileEmail || 'email@example.com' }}</span>
              <span><i class="fas fa-phone"></i>{{ profile.phone || '+000 00 000 000' }}</span>
              <button type="button" class="text-link-button" @click="openAvatarPicker">
                {{ avatarPreview ? copy.changeAvatar : copy.uploadAvatar }}
              </button>
              <span v-if="errors.avatar" class="field-error">{{ errors.avatar }}</span>
            </div>
          </div>

          <div class="side-card">
            <div class="side-card__head">
              <strong>{{ copy.profileCompletion }}</strong>
              <span class="shield">✓</span>
            </div>

            <div class="progress-value">{{ progress }}%</div>

            <div class="progress-track" role="progressbar" :aria-valuenow="progress" aria-valuemin="0" aria-valuemax="100">
              <span class="progress-bar" :style="{ width: `${progress}%` }"></span>
            </div>

            <p>{{ copy.profileCompletionDescription }}</p>
          </div>

          <div class="side-card side-card--dashed">
            <h3>{{ copy.strongCvTitle }}</h3>

            <div class="feature">
              <span class="feature-icon">1</span>
              <div class="feature-text">
                <strong>{{ copy.strongCvClearRoleTitle }}</strong>
                <small>{{ copy.strongCvClearRoleText }}</small>
              </div>
            </div>

            <div class="feature">
              <span class="feature-icon">2</span>
              <div class="feature-text">
                <strong>{{ copy.strongCvExperienceTitle }}</strong>
                <small>{{ copy.strongCvExperienceText }}</small>
              </div>
            </div>

            <div class="feature">
              <span class="feature-icon">3</span>
              <div class="feature-text">
                <strong>{{ copy.readyCv }}</strong>
                <small>{{ copy.strongCvReadyCvText }}</small>
              </div>
            </div>
          </div>
        </aside>
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.page {
  width: min(100%, var(--shell-max-width));
  box-sizing: border-box;
  margin: 0 auto;
  padding: 2rem var(--shell-gutter) 4rem;
  display: grid;
  gap: 1.25rem;
}

.hero,
.main-card,
.side-card {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.25rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.hero {
  padding: 1.6rem;
  display: grid;
  gap: 1.3rem;
}

.hero-copy {
  display: grid;
  gap: 0.85rem;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.title-row h1,
.card-head h2,
.review-card h3,
.side-card h3 {
  margin: 0;
  color: var(--text-primary);
}

.title-row h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.08;
}

.hero-copy p,
.hint,
.profile-meta,
.side-card p,
.feature small {
  color: var(--text-muted);
  line-height: 1.65;
}

.steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.85rem;
}

.step {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.85rem;
  align-items: center;
  padding: 1rem 1.05rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.step:hover {
  border-color: color-mix(in srgb, var(--brand-base) 24%, var(--border-subtle));
}

.step-copy,
.main-card,
.section {
  display: grid;
}

.step-copy {
  gap: 0.15rem;
}

.step strong,
.step small {
  display: block;
}

.step small {
  color: var(--text-muted);
}

.step-index {
  width: 2.5rem;
  height: 2.5rem;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: #fff;
  border: 0.0625rem solid var(--border-subtle);
  color: var(--text-primary);
  font-weight: 800;
}

.step--active,
.step--done {
  border-color: color-mix(in srgb, var(--brand-base) 26%, var(--border-subtle));
  background: color-mix(in srgb, var(--brand-soft) 44%, white);
}

.step--active .step-index,
.step--done .step-index {
  background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%);
  border-color: transparent;
  color: #fff;
}

.builder {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 23rem;
  gap: 1.25rem;
  align-items: start;
}

.main-card,
.side-card {
  padding: 1.35rem;
}

.main-card {
  min-width: 0;
  gap: 1.35rem;
  height: 100%;
}

.card-head {
  display: grid;
  gap: 0.4rem;
}

.form-stack,
.form-panel {
  display: grid;
  gap: 1rem;
}

.form-panel,
.entry-card {
  min-width: 0;
  padding: 1.1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
}

.form-panel__head {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.form-panel__head > span,
.entry-index {
  width: 2.25rem;
  height: 2.25rem;
  display: grid;
  flex: 0 0 2.25rem;
  place-items: center;
  border-radius: 50%;
  background: #fff;
  border: 0.0625rem solid var(--border-subtle);
  color: var(--brand-strong);
  font-weight: 800;
}

.form-panel__head h3,
.form-panel__head p {
  margin: 0;
}

.form-panel__head p,
.entry-card__title small {
  color: var(--text-muted);
}

.form-grid,
.entry-card__body {
  min-width: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.entry-card {
  display: grid;
  gap: 1rem;
}

.entry-card--collapsed {
  gap: 0;
}

.entry-card__head {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.entry-card__toggle {
  min-width: 0;
  flex: 1;
  display: grid;
  grid-template-columns: 2.25rem minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.75rem;
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.entry-card__title {
  min-width: 0;
  display: grid;
  gap: 0.15rem;
}

.entry-card__title strong,
.entry-card__title small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.entry-card__toggle > i {
  transition: transform 0.2s ease;
}

.entry-card__toggle[aria-expanded='true'] > i {
  transform: rotate(180deg);
}

.entry-remove {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--text-muted);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.entry-wide {
  grid-column: 1 / -1;
}

.entry-add {
  justify-self: start;
}

.checkbox-field,
.choice-card {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.checkbox-field input[type='checkbox'],
.choice-card input[type='checkbox'] {
  width: 1.15rem;
  min-width: 1.15rem;
  height: 1.15rem;
  min-height: 1.15rem;
  margin: 0;
  flex: 0 0 1.15rem;
}

.choice-card > span {
  display: grid;
  gap: 0.15rem;
}

.choice-card small {
  color: var(--text-muted);
  font-weight: 400;
}

.contact-group {
  min-width: 0;
  display: grid;
  align-content: start;
  gap: 0.65rem;
}

.contact-row {
  min-width: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.5rem;
}

.contact-row > :first-child {
  min-width: 0;
}

.contact-remove,
.contact-add {
  border: 0;
  background: transparent;
  color: var(--brand-strong);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.contact-remove {
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  border-radius: 0.65rem;
  color: var(--text-muted);
}

.contact-add {
  width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0;
}

.grid-two,
.inline-add,
.upload-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.grid-span-2 {
  grid-column: 1 / -1;
}

.section {
  gap: 0.85rem;
}

.section-label {
  font-weight: 700;
  color: var(--text-primary);
}

label {
  display: grid;
  gap: 0.45rem;
  color: var(--text-primary);
  font-weight: 600;
}

.toggle-field {
  align-content: start;
}

.toggle-switch {
  gap: 0.7rem;
}

.toggle-switch__control {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: 3.5rem;
  height: 2rem;
}

.toggle-switch__control input[type="checkbox"] {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  min-width: 100%;
  min-height: 100%;
  margin: 0;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
}

.toggle-switch__track {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 999px;
  background: color-mix(in srgb, var(--border-subtle) 78%, white);
  border: 0.0625rem solid color-mix(in srgb, var(--border-strong) 55%, white);
  box-shadow: inset 0 0.0625rem 0.2rem rgba(15, 23, 42, 0.08);
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.toggle-switch__thumb {
  position: absolute;
  top: 0.1875rem;
  left: 0.1875rem;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0.2rem 0.55rem rgba(15, 23, 42, 0.16);
  transition: transform 0.2s ease;
}

.toggle-switch__control input[type="checkbox"]:checked + .toggle-switch__track {
  background: linear-gradient(135deg, var(--brand-base), var(--brand-strong));
  border-color: color-mix(in srgb, var(--brand-strong) 70%, white);
  box-shadow: 0 0 0 0.1875rem rgba(20, 184, 87, 0.12);
}

.toggle-switch__control input[type="checkbox"]:checked + .toggle-switch__track .toggle-switch__thumb {
  transform: translateX(1.5rem);
}

.toggle-switch__control input[type="checkbox"]:focus-visible + .toggle-switch__track {
  outline: 0.1875rem solid rgba(20, 184, 87, 0.2);
  outline-offset: 0.125rem;
}

input,
textarea {
  width: 100%;
  min-width: 0;
  min-height: 3.2rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

textarea {
  min-height: 8rem;
  resize: vertical;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: var(--brand-strong);
  box-shadow: 0 0 0 0.1875rem rgba(20, 184, 87, 0.12);
}

.sector-dropdown {
  min-width: 10rem;
}

.sector-add {
  grid-template-columns: minmax(0, 1fr) minmax(11rem, 12rem) auto;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.sector-chips:empty {
  display: none;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 2.8rem;
  padding: 0.7rem 0.85rem;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 14%, var(--border-subtle));
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
  color: var(--brand-strong);
}

.sector-chip {
  padding-left: 0.65rem;
}

.sector-chip__copy {
  display: grid;
  gap: 0.08rem;
}

.sector-chip__copy strong,
.sector-chip__copy small {
  line-height: 1.2;
}

.sector-chip__copy strong {
  font-size: 0.88rem;
}

.sector-chip__copy small {
  color: color-mix(in srgb, var(--brand-strong) 82%, white);
  font-size: 0.72rem;
  font-weight: 800;
}

.sector-chip__icon {
  width: 1.9rem;
  height: 1.9rem;
  display: inline-grid;
  place-items: center;
  border-radius: 0.55rem;
  background: #fff;
  color: var(--brand-strong);
}

.chip button,
.ghost-button,
.btn-light,
.btn-primary {
  border: 0;
  cursor: pointer;
  font: inherit;
}

.chip button {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.5rem;
  background: #fff;
  color: var(--text-muted);
}

.ghost-button,
.btn-light,
.btn-primary {
  min-height: 3.1rem;
  padding: 0 1.2rem;
  border-radius: 0.875rem;
  font-weight: 700;
}

.ghost-button {
  border: 0.0625rem dashed color-mix(in srgb, var(--brand-base) 24%, var(--border-subtle));
  background: #fff;
  color: var(--brand-strong);
}

.ghost-button--small {
  width: fit-content;
}

.btn-light {
  border: 0.0625rem solid var(--border-subtle);
  background: #fff;
  color: var(--text-primary);
}

.btn-primary {
  background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%);
  color: #fff;
  box-shadow: 0 0.75rem 1.5rem rgba(20, 184, 87, 0.18);
}

.upload-card {
  display: grid;
  gap: 0.65rem;
  padding: 1.1rem;
  border: 0.0625rem dashed color-mix(in srgb, var(--brand-base) 22%, var(--border-subtle));
  border-radius: 1rem;
  background: color-mix(in srgb, var(--brand-soft) 38%, white);
  cursor: pointer;
}

.upload-card__input {
  display: none;
}

.upload-card__title {
  color: var(--text-primary);
  font-weight: 700;
}

.upload-card__button {
  width: fit-content;
}

.avatar,
.profile-avatar {
  width: 5.2rem;
  height: 5.2rem;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 50%;
  background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%);
  color: #fff;
  font-size: 1.3rem;
  font-weight: 800;
  flex: 0 0 5.2rem;
}

.profile-avatar--button {
  border: 0;
  padding: 0;
  box-shadow: 0 0 0 0 transparent;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.profile-avatar--button:hover,
.profile-avatar--button:focus-visible {
  transform: translateY(-0.0625rem);
  box-shadow: 0 0 0 0.1875rem rgba(20, 184, 87, 0.14);
}

.avatar__image,
.profile-avatar__image {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover;
  display: block;
}

.text-link-button {
  width: fit-content;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--brand-strong);
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

.review-card {
  display: grid;
  gap: 1rem;
  padding: 1.1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 84%, white);
}

.review-card p {
  margin: 0.4rem 0 0;
  color: var(--text-muted);
  line-height: 1.55;
}

.review-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  
}

.final-tools {
  display: grid;
  gap: 1rem;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 0.4rem;
}

.footer-actions .btn-light,
.footer-actions .btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 3rem;
  height: 3rem;
  padding: 0 1.35rem;
}

.sidebar {
  display: grid;
  gap: 1rem;
  position: sticky;
  top: 5.75rem;
}

.profile-card {
  display: grid;
  gap: 0.9rem;
}

.profile-card__top {
  display: grid;
  grid-template-columns: 5.2rem minmax(0, 1fr);
  gap: 0.9rem;
  align-items: center;
}

.profile-card__top p {
  margin: 0.25rem 0 0;
}

.profile-meta {
  display: grid;
  gap: 0.35rem;
}

.side-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.shield {
  width: 2.2rem;
  height: 2.2rem;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: color-mix(in srgb, var(--brand-soft) 70%, white);
  color: var(--brand-strong);
  font-weight: 800;
}

.progress-value {
  margin-top: 0.9rem;
  color: var(--brand-strong);
  font-size: 2.2rem;
  font-weight: 800;
}

.progress-track {
  height: 0.7rem;
  margin-top: 0.8rem;
  overflow: hidden;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--surface-secondary) 90%, black 4%);
}

.progress-bar {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #0fb152 0%, #17c660 100%);
}

.side-card--dashed {
  border-style: dashed;
}

.feature {
  display: grid;
  grid-template-columns: 3rem minmax(0, 1fr);
  gap: 0.9rem;
  align-items: center;
  padding: 0.85rem 0;
}

.feature + .feature {
  border-top: 0.0625rem solid var(--border-subtle);
}

.feature-icon {
  width: 3rem;
  height: 3rem;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: color-mix(in srgb, var(--brand-soft) 70%, white);
  color: var(--brand-strong);
  font-weight: 800;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.field-error {
  color: #b42318;
  font-size: 0.86rem;
  font-weight: 700;
  line-height: 1.4;
}

.upload-card--error {
  border-color: #b42318;
}

.cv-preview-shell {
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.25rem;
  background: color-mix(in srgb, var(--surface-secondary) 70%, white);
  overflow: auto;
}

.cv-document {
  --cv-green: #149447;
  --cv-green-dark: #0f7f3c;
  --cv-ink: #101828;
  --cv-muted: #667085;
  --cv-line: #d9dee7;
  --cv-soft: #f3fbf6;
  width: min(100%, 49.625rem);
  height: 70.1875rem;
  margin: 0 auto;
  padding: 1.45rem 1.7rem 1.15rem;
  background: #fff;
  color: var(--cv-ink);
  border-radius: 0.8rem;
  box-shadow: 0 1.5rem 3rem rgba(16, 24, 40, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: Inter, Arial, sans-serif;
}

.cv-header,
.cv-top,
.cv-footer {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex: 0 0 auto;
  min-width: 0;
}

.cv-header {
  min-height: 2.9rem;
  padding-bottom: 0.85rem;
  border-bottom: 0.0625rem solid var(--cv-line);
}

.cv-brand {
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  flex-wrap: nowrap;
  gap: 0.55rem;
  min-width: 0;
  color: var(--cv-ink);
}

.cv-brand__logo,
.cv-brand__logo svg {
  width: 8.2rem;
  max-width: 8.2rem;
  max-height: 2.15rem;
  height: auto;
  display: block;
  flex: 0 0 auto;
}

.cv-brand small {
  display: block;
  color: var(--cv-muted);
  font-size: 0.55rem;
  line-height: 1;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.cv-verified {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--cv-green);
  flex: 0 0 auto;
}

.cv-verified-icon {
  width: 1.7rem;
  height: 1.7rem;
  display: grid;
  place-items: center;
  border: 0.1rem solid var(--cv-green);
  border-radius: 50%;
  font-size: 0.78rem;
  line-height: 1;
  font-weight: 900;
}

.cv-verified strong {
  display: block;
  font-size: 0.68rem;
  line-height: 1.1;
  white-space: nowrap;
}

.cv-verified small {
  display: block;
  margin-top: 0.08rem;
  color: var(--cv-muted);
  font-size: 0.66rem;
  line-height: 1.1;
  white-space: nowrap;
}

.cv-top {
  padding: 1rem 0 0.95rem;
  border-bottom: 0.0625rem solid var(--cv-line);
  align-items: flex-start;
}

.cv-person {
  display: grid;
  grid-template-columns: 4.25rem minmax(0, 1fr);
  gap: 0.85rem;
  align-items: start;
  min-width: 0;
}

.cv-avatar {
  width: 4.25rem;
  height: 4.25rem;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 50%;
  background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%);
  color: #fff;
  font-size: 1.05rem;
  line-height: 1;
  font-weight: 900;
}

.cv-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cv-person h1 {
  margin: 0;
  color: #05070a;
  font-size: clamp(2rem, 4vw, 2.45rem);
  line-height: 0.95;
  letter-spacing: -0.055em;
  overflow-wrap: anywhere;
}

.cv-person p {
  margin: 0.4rem 0 0.7rem;
  color: var(--cv-green);
  font-size: 0.95rem;
  line-height: 1.1;
  font-weight: 800;
}

.cv-contact-list,
.cv-list,
.cv-extra-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.cv-contact-list {
  display: grid;
  gap: 0.3rem;
}

.cv-contact-list li {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--cv-ink);
  font-size: 0.74rem;
  line-height: 1.22;
  min-width: 0;
}

.cv-contact-list span,
.cv-extra-list span,
.cv-list li,
.cv-sector span {
  overflow-wrap: anywhere;
}

.cv-contact-list i,
.cv-extra-list i {
  width: 0.95rem;
  color: var(--cv-green);
  text-align: center;
  flex: 0 0 auto;
}

.cv-id {
  display: grid;
  justify-items: center;
  gap: 0.18rem;
  color: var(--cv-ink);
  flex: 0 0 auto;
}

.cv-id small {
  margin-top: 0.18rem;
  color: var(--cv-green);
  font-size: 0.6rem;
  line-height: 1;
  font-weight: 900;
  text-transform: uppercase;
}

.cv-id > strong {
  font-size: 0.72rem;
  line-height: 1;
}

.cv-qr {
  position: relative;
  width: 5.7rem;
  height: 5.7rem;
  display: grid;
  grid-template-columns: repeat(11, 1fr);
  grid-template-rows: repeat(11, 1fr);
  gap: 0.075rem;
  padding: 0.32rem;
  border: 0.0625rem solid var(--cv-line);
  border-radius: 0.32rem;
  background: #fff;
}

.cv-qr-cell {
  background: transparent;
  border-radius: 0.035rem;
}

.cv-qr-cell--active {
  background: #111;
}

.cv-qr strong {
  position: absolute;
  inset: 50% auto auto 50%;
  width: 1.48rem;
  height: 1.48rem;
  display: grid;
  place-items: center;
  transform: translate(-50%, -50%);
  border-radius: 0.22rem;
  background: #111;
  color: var(--cv-green);
  font-size: 0.5rem;
  line-height: 1;
  font-weight: 900;
}

.cv-body {
  display: grid;
  grid-template-columns: minmax(0, 1.34fr) minmax(12.5rem, 0.82fr);
  gap: 1.25rem;
  padding-top: 1rem;
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
}

.cv-main {
  min-height: 0;
  overflow: hidden;
  padding-right: 1.25rem;
  border-right: 0.0625rem solid var(--cv-line);
}

.cv-aside {
  min-height: 0;
  overflow: hidden;
}

.cv-section {
  padding-bottom: 0.72rem;
  margin-bottom: 0.72rem;
  border-bottom: 0.0625rem solid var(--cv-line);
  break-inside: avoid;
  page-break-inside: avoid;
}

.cv-section:last-child {
  margin-bottom: 0;
}

.cv-section h2 {
  margin: 0 0 0.48rem;
  color: var(--cv-ink);
  font-size: 0.78rem;
  line-height: 1.1;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.cv-section p {
  margin: 0;
  color: var(--cv-ink);
  font-size: 0.72rem;
  line-height: 1.42;
}

.cv-summary-text {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: pre-line;
}

.cv-section p + p {
  margin-top: 0.42rem;
}

.cv-list {
  display: grid;
  gap: 0.3rem;
}

.cv-list li {
  position: relative;
  padding-left: 0.78rem;
  color: var(--cv-ink);
  font-size: 0.7rem;
  line-height: 1.24;
}

.cv-list li::before {
  content: '';
  position: absolute;
  top: 0.42rem;
  left: 0.12rem;
  width: 0.22rem;
  height: 0.22rem;
  border-radius: 50%;
  background: var(--cv-green);
}

.cv-sector-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.36rem;
}

.cv-sector {
  display: flex;
  align-items: center;
  gap: 0.36rem;
  min-height: 1.95rem;
  padding: 0.38rem 0.45rem;
  border: 0.0625rem solid #d9f2e2;
  border-radius: 0.5rem;
  background: var(--cv-soft);
  color: var(--cv-ink);
  font-size: 0.66rem;
  line-height: 1.16;
  font-weight: 800;
  break-inside: avoid;
  page-break-inside: avoid;
}

.cv-sector i {
  color: var(--cv-green);
  flex: 0 0 auto;
}

.cv-sector__copy {
  display: grid;
  gap: 0.08rem;
}

.cv-sector__copy strong,
.cv-sector__copy small {
  line-height: 1.12;
}

.cv-sector__copy small {
  color: #557567;
  font-size: 0.58rem;
  font-weight: 700;
}

.cv-extra-list {
  display: grid;
  gap: 0.38rem;
}

.cv-extra-list li {
  display: grid;
  grid-template-columns: 0.95rem minmax(0, 1fr);
  gap: 0.34rem;
  align-items: start;
  color: var(--cv-ink);
  font-size: 0.69rem;
  line-height: 1.25;
}

.cv-more-item {
  color: var(--cv-muted) !important;
  font-weight: 800 !important;
}

.cv-footer {
  margin-top: auto;
  padding-top: 0.55rem;
  border-top: 0.0625rem solid var(--cv-line);
  color: var(--cv-muted);
  font-size: 0.63rem;
  line-height: 1.1;
  break-inside: avoid;
  page-break-inside: avoid;
}

.cv-brand--small .cv-brand__logo {
  width: 6.3rem;
  max-width: 6.3rem;
  max-height: 1.6rem;
}

.feature-text {
  display: flex;
  flex-direction: column;
}

@media (max-width: 72rem) {
  .builder {
    grid-template-columns: minmax(0, 1fr);
  }

  .sidebar {
    position: static;
  }

  .cv-body {
    grid-template-columns: 1fr;
  }

  .cv-main {
    padding-right: 0;
    border-right: 0;
  }
}

@media (max-width: 56rem) {
  .grid-two,
  .inline-add,
  .upload-grid,
  .sector-add {
    grid-template-columns: 1fr;
  }

  .form-grid,
  .entry-card__body {
    grid-template-columns: minmax(0, 1fr);
  }

  .steps {
    display: flex;
    gap: 0.75rem;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;
  }

  .steps::-webkit-scrollbar {
    display: none;
  }

  .step {
    min-width: 12.5rem;
    scroll-snap-align: start;
  }

  .footer-actions,
  .review-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .main-card,
  .side-card,
  .hero {
    padding: 1rem;
  }

  .ghost-button,
  .btn-light,
  .btn-primary,
  .sector-dropdown {
    width: 100%;
  }

  .cv-preview-shell {
    padding: 0;
    border: 0;
    background: transparent;
  }

  .cv-document {
    padding: 1.35rem;
    border-radius: 1rem;
  }

  .cv-header,
  .cv-top,
  .cv-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .cv-person {
    grid-template-columns: 1fr;
  }

  .cv-brand {
    flex-wrap: wrap;
  }

  .cv-brand__logo {
    width: 7.4rem;
  }

  .cv-id {
    justify-items: start;
  }

  .cv-sector-grid {
    grid-template-columns: 1fr;
  }
}

@media print {
  @page {
    size: A4;
    margin: 0;
  }

  :global(html),
  :global(body) {
    width: 210mm;
    height: 297mm;
    margin: 0 !important;
    padding: 0 !important;
    background: #fff !important;
    overflow: hidden !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  .no-print,
  .sidebar,
  .hero,
  .card-head,
  .footer-actions,
  .final-tools {
    display: none !important;
  }

  .page,
  .builder,
  .main-card,
  .cv-preview-shell {
    display: block !important;
    width: 210mm !important;
    max-width: 210mm !important;
    min-width: 210mm !important;
    height: 297mm !important;
    max-height: 297mm !important;
    min-height: 297mm !important;
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    background: #fff !important;
    overflow: hidden !important;
  }

  .cv-document {
    width: 210mm !important;
    min-width: 210mm !important;
    max-width: 210mm !important;
    height: 297mm !important;
    min-height: 297mm !important;
    max-height: 297mm !important;
    margin: 0 !important;
    padding: 10mm 12mm 8mm !important;
    border: 0 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    background: #fff !important;
    color: #101828 !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  .cv-header,
  .cv-top,
  .cv-section,
  .cv-footer,
  .cv-sector {
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .cv-header,
  .cv-top,
  .cv-footer {
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-between !important;
    gap: 9mm !important;
  }

  .cv-header,
  .cv-footer {
    align-items: center !important;
  }

  .cv-top {
    align-items: flex-start !important;
  }

  .cv-brand {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
  }

  .cv-brand__logo,
  .cv-brand__logo svg {
    width: 34mm !important;
    max-width: 34mm !important;
    max-height: 9mm !important;
  }

  .cv-brand--small .cv-brand__logo,
  .cv-brand--small .cv-brand__logo svg {
    width: 26mm !important;
    max-width: 26mm !important;
    max-height: 7mm !important;
  }

  .cv-person {
    grid-template-columns: 18mm minmax(0, 1fr) !important;
  }

  .cv-id {
    justify-items: center !important;
    align-self: flex-start !important;
  }

  .cv-body {
    display: grid !important;
    grid-template-columns: minmax(0, 1.34fr) minmax(45mm, 0.82fr) !important;
  }

  .cv-main {
    padding-right: 7mm !important;
    border-right: 0.35mm solid #d9dee7 !important;
  }

  .cv-sector-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }

  .cv-footer {
    margin-top: auto !important;
  }
}
</style>
