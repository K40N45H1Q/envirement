<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import AutocompleteInput from '@/components/AutocompleteInput.vue'
import BaseDropdown from '@/components/BaseDropdown.vue'
import PhoneInput from '@/components/PhoneInput.vue'
import CvDocument from '@/cv/CvDocument.vue'
import { getProfile, updateProfile } from '@/api/profile'
import { translate, useI18n } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useJobsStore } from '@/stores/jobs'
import { countryDropdownOptions, countryMeta, getLocalizedCountryLabel } from '@/utils/countries'
import {
  createEmptyEducation,
  createEmptyProfile,
  createEmptyResumeData,
  createEmptyWorkExperience,
  formatDateInput,
  formatDateTypingValue,
  formatDateValue,
  getPhoneDigits,
  isValidDateValue,
  isValidEmail,
  isValidPhone,
  limitText,
  normalizeDateInput,
  parseBirthDate,
  splitTextList,
  toArray,
  toText,
} from '@/utils/cvBuilderHelpers'
import {
  availabilityCatalog,
  DEFAULT_SECTOR_EXPERIENCE,
  displayEducation as displayEducationLabel,
  displayLanguageName as displayLanguageLabel,
  displayPermit as displayPermitLabel,
  displayPreferredEmployment as displayPreferredEmploymentLabel,
  displaySectorExperience as displaySectorExperienceLabel,
  drivingLicenseValues,
  educationCatalog,
  getCatalogEntryLabel,
  languageCatalog,
  languageLevels,
  licenseValues,
  mapCatalogToOptions,
  normalizeLanguageName,
  normalizePermit,
  normalizeSectorExperience,
  permitCatalog,
  preferredEmploymentCatalog,
  sectorExperienceCatalog,
} from '@/utils/cvBuilderOptions'
import { findOccupationSuggestions, resolveOccupation } from '@/utils/occupations'
import { findSkillSuggestions, localizeSkill } from '@/utils/skills'
import { preparePdfCvDocument } from '@/cv/cvLayout'
import { getPrintableStyles } from '@/cv/cvPrintableStyles'
import { createPaginatedCvPdf } from '@/utils/cvPdf'

const emit = defineEmits(['step-change', 'close'])

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

const languageLevelOptions = languageLevels.map((label) => ({ value: label, label }))

const { language } = useI18n()
const router = useRouter()
const sectorExperienceOptions = computed(() => sectorExperienceCatalog.map((entry) => ({
  value: entry.value,
  label: getCatalogEntryLabel(entry, language.value),
})))

const languageOptions = computed(() => mapCatalogToOptions(languageCatalog, language.value))

const licenseOptions = computed(() => {
  const noLicenseLabel = copy.value.noLicense
  return [
    { value: noLicenseLabel, label: noLicenseLabel },
    ...licenseValues.map((label) => ({ value: label, label })),
  ]
})
const permitOptions = computed(() => mapCatalogToOptions(permitCatalog, language.value))
const baseAvailabilityOptions = computed(() => mapCatalogToOptions(availabilityCatalog, language.value)
  .filter((option) => option.value))
const educationOptions = computed(() => mapCatalogToOptions(educationCatalog, language.value))
const preferredEmploymentOptions = computed(() => mapCatalogToOptions(preferredEmploymentCatalog, language.value))
const displayLanguageName = (value) => displayLanguageLabel(value, language.value)
const displaySectorExperience = (value) => displaySectorExperienceLabel(value, language.value)
const displayPermit = (value) => displayPermitLabel(value, language.value)
const displayEducation = (value) => displayEducationLabel(value, language.value)
const displayPreferredEmployment = (value) => displayPreferredEmploymentLabel(value, language.value)
const displayAvailability = (value) => {
  const normalized = toText(value).trim()
  if (isDateAvailability(normalized)) {
    return translate('resumeBuilderPage.dateValue', { value: normalized }, language.value)
  }

  const option = availabilityCatalog.find((entry) => entry.value === normalized)
  return option ? getCatalogEntryLabel(option, language.value) : normalized
}

const copy = computed(() => translate('resumeBuilderPage', {}, language.value))

const genderOptions = computed(() => [
  { value: 'female', label: copy.value.female },
  { value: 'male', label: copy.value.male },
  { value: 'other', label: copy.value.otherGender },
])
const countryOptions = computed(() => countryDropdownOptions)
const citizenshipOptions = computed(() => countryDropdownOptions)

const { state } = useAuth()
const jobsStore = useJobsStore()
const { categoryCounts } = storeToRefs(jobsStore)

const step = ref(1)
const expandedWorkIndex = ref(0)
const expandedEducationIndex = ref(0)
const isLoaded = ref(false)
const isLoading = ref(false)
const isSaving = ref(false)
const isGeneratingPdf = ref(false)
const status = ref('')
const errors = ref({})
const savedSnapshot = ref('')
const firstNameLocked = ref(false)
const lastNameLocked = ref(false)
const avatarFile = ref(null)
const resumeFile = ref(null)
const avatarObjectUrl = ref('')
const selectedSector = ref('')
const selectedSectorExperience = ref(DEFAULT_SECTOR_EXPERIENCE)

const normalizedCountryAliasMap = new Map(
  countryMeta.flatMap((country) => [
    [country.key.toLowerCase(), country.key],
    [country.label.toLowerCase(), country.key],
    [country.canonicalLabel.toLowerCase(), country.key],
    ...country.aliases.map((alias) => [String(alias).toLowerCase(), country.key]),
  ]),
)

const normalizeCitizenship = (value) => {
  const normalized = toText(value).trim().toLowerCase()
  if (!normalized) return ''
  return normalizedCountryAliasMap.get(normalized) || toText(value).trim()
}

const normalizeCountryValue = (value) => {
  const normalized = toText(value).trim().toLowerCase()
  if (!normalized) return ''
  return normalizedCountryAliasMap.get(normalized) || toText(value).trim()
}
const newLanguage = ref('')
const newLanguageLevel = ref(languageLevelOptions[2].value)
const newLicense = ref(copy.value.noLicense)
const newSkillQuery = ref('')
const cvDocumentRef = ref(null)
const avatarInputRef = ref(null)
const resumeInputRef = ref(null)

let savePromise = null
let shouldSaveAgain = false
let isApplyingServerProfile = false
let printFrame = null
let previousBodyOverflow = ''
const LEGACY_CV_DRAFT_STORAGE_KEY = 'cv-builder-draft'

const profile = ref(createEmptyProfile())

watch(
  [language, () => profile.value.resume_data],
  ([siteLanguage, resumeData]) => {
    if (resumeData) resumeData.cv_language = siteLanguage
  },
  { immediate: true },
)

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

  return Promise.all(images.map(async (image) => {
    if (typeof image.decode === 'function') {
      try {
        await image.decode()
        return
      } catch {
        // Broken images must not block PDF generation.
      }
    }

    if (image.complete) return

    await new Promise((resolve) => {
      image.addEventListener('load', resolve, { once: true })
      image.addEventListener('error', resolve, { once: true })
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

const normalizeCandidateAvailability = (value) => {
  const normalized = toText(value).trim()
  if (normalized === 'Immediate' || (isDateAvailability(normalized) && isValidDateValue(normalized))) {
    return normalized
  }
  return ''
}

const isValidAvailabilityDate = (value) => isValidDateValue(value)

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

const sectorDropdownOptions = computed(() => jobCategoryOptions.value.map(({ hint, ...option }) => option))

const sectorOptionsByValue = computed(() => new Map(
  jobCategoryOptions.value.map((option) => [option.value, option]),
))

const sectorOptionsByLabel = computed(() => new Map(
  jobCategoryOptions.value.map((option) => [option.label.toLowerCase(), option]),
))

const selectedSectorOption = computed(() => sectorOptionsByValue.value.get(selectedSector.value) || null)

const workPositionSuggestions = computed(() => (
  profile.value.resume_data.work_experiences.map((work) => findOccupationSuggestions(work.position, language.value).map((item) => ({
    id: item.id,
    value: item.label,
    label: item.label,
  })))
))

const desiredOccupationSuggestions = computed(() => findOccupationSuggestions(
  profile.value.desired_occupation_label,
  language.value,
).map((item) => ({ id: item.id, value: item.label, label: item.label })))

const skillSuggestions = computed(() => findSkillSuggestions(
  newSkillQuery.value,
  language.value,
  profile.value.skill_ids,
))

const localizeProfileOccupations = (targetProfile, locale = language.value) => {
  targetProfile.resume_data.work_experiences.forEach((work) => {
    const occupation = resolveOccupation(work.occupation_id, work.position, locale)
    if (!occupation) return
    work.occupation_id = occupation.id
    work.position = occupation.label
  })

  const desiredOccupation = resolveOccupation(
    targetProfile.desired_occupation_id,
    targetProfile.desired_occupation_label,
    locale,
  )
  if (!desiredOccupation) return
  targetProfile.desired_occupation_id = desiredOccupation.id
  targetProfile.desired_occupation_label = desiredOccupation.label
}

const availabilityMode = computed({
  get: () => {
    const currentValue = profile.value.availability.trim()
    if (currentValue === 'Immediate') return 'Immediate'
    if (currentValue === '__date__' || currentValue) return '__date__'
    return ''
  },
  set: (value) => {
    profile.value.availability = value
    clearError('availability')
  },
})

const availabilityDateInput = computed({
  get: () => {
    const currentValue = profile.value.availability.trim()
    if (!currentValue || currentValue === 'Immediate' || currentValue === '__date__') return ''
    return formatDateInput(currentValue)
  },
  set: (value) => {
    const normalized = normalizeDateInput(value)
    profile.value.availability = normalized || '__date__'
    clearError('availability')
  },
})

const availabilityLabel = computed(() => {
  const currentValue = profile.value.availability.trim()
  if (!currentValue || currentValue === '__date__') return copy.value.notSpecified
  return displayAvailability(currentValue) || copy.value.notSpecified
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
    occupation_id: toText(entry?.occupation_id),
    position: toText(entry?.position || (index === 0 ? source.current_role : '')),
    job_category: toText(entry?.job_category),
    company_name: toText(entry?.company_name),
    start_date: toText(entry?.start_date),
    end_date: toText(entry?.end_date),
    current: Boolean(entry?.current),
    country: normalizeCountryValue(entry?.country || 'latvia'),
    description: toText(entry?.description),
  }))
  const educations = rawEducations.map((entry, index) => ({
    ...createEmptyEducation(),
    level: toText(entry?.level || (index === 0 ? source.education_level : '')),
    institution: toText(entry?.institution),
    speciality: toText(entry?.speciality),
    second_speciality: toText(entry?.second_speciality),
    country: normalizeCountryValue(entry?.country || 'latvia'),
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
    citizenship: normalizeCitizenship(resumeData.citizenship),
    no_driving_license: Boolean(resumeData.no_driving_license),
    driving_licenses: toArray(resumeData.driving_licenses).map((item) => toText(item)).filter((item) => drivingLicenseValues.includes(item)),
    additional_emails: toArray(resumeData.additional_emails).map((item) => toText(item).trim()).filter(Boolean),
    additional_phones: toArray(resumeData.additional_phones).map((item) => toText(item)).filter(Boolean),
    no_work_experience: Boolean(resumeData.no_work_experience),
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
    residence: toText(source.residence).trim(),
    phone: toText(source.phone),
    summary: toText(source.summary),
    current_role: toText(source.current_role),
    desired_occupation_id: toText(source.desired_occupation_id),
    desired_occupation_label: toText(source.desired_occupation_label),
    skills: toText(source.skills),
    skill_ids: toArray(source.skill_ids ?? source.skill_ids_json),
    sectors: normalizeSectors(source.sectors ?? source.sectors_json),
    languages: normalizeLanguages(source.languages ?? source.languages_json),
    licenses: normalizeLicenses(source.licenses ?? source.licenses_json),
    mobility: toText(source.mobility),
    work_permit: normalizePermit(source.work_permit),
    availability: normalizeCandidateAvailability(source.availability),
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
  residence: profile.value.residence,
  phone: profile.value.phone,
  summary: profile.value.summary,
  current_role: profile.value.current_role,
  desired_occupation_id: profile.value.desired_occupation_id,
  desired_occupation_label: profile.value.desired_occupation_label,
  skills: profile.value.skills,
  skill_ids: profile.value.skill_ids,
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
  profile.value.resume_data.work_experiences[0]?.position,
  profile.value.resume_data.work_experiences[0]?.company_name,
  profile.value.resume_data.educations[0]?.level,
  profile.value.resume_data.educations[0]?.institution,
])

const filledFields = computed(() => progressChecks.value.filter(Boolean).length)
const progress = computed(() => Math.round((filledFields.value / progressChecks.value.length) * 100))

const availableLanguageValues = computed(() => {
  const selectedValues = new Set(profile.value.languages.map((item) => item.name))
  return languageOptions.value
    .map((item) => item.value)
    .filter((value) => !selectedValues.has(value))
})

const canAddLanguage = computed(() => availableLanguageValues.value.includes(newLanguage.value))
const canAddNextLanguage = computed(() => {
  if (!profile.value.languages.length) return false

  const lastIndex = profile.value.languages.length - 1
  const currentValue = toText(profile.value.languages[lastIndex]?.name).trim()
  if (!currentValue) return false

  const selectedValues = new Set(
    profile.value.languages
      .map((item, index) => (index === lastIndex ? '' : toText(item.name).trim()))
      .filter(Boolean),
  )

  return !selectedValues.has(currentValue)
})

const legacyStatusMessage = computed(() => {
  if (isLoading.value) return 'Загрузка профиля...'
  if (isSaving.value) return 'Сохраняем...'
  if (status.value) return status.value
  if (hasUnsavedChanges.value) return 'Есть несохранённые изменения.'
  return ''
})

const cvName = computed(() => fullName.value || 'Кандидат CVHOLD')
const cvRole = computed(() => profile.value.current_role.trim() || 'Специалист')
const cvSkills = computed(() => [...new Set([
  ...profile.value.skill_ids.map((skill) => localizeSkill(skill, language.value)),
  ...splitTextList(profile.value.skills),
])].filter(Boolean))
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
const cvLicenses = computed(() => [...new Set(profile.value.resume_data.driving_licenses)].filter(Boolean))

const cvVisibleSectors = computed(() => cvSectors.value.slice(0, MAX_PRINT_SECTORS))
const cvVisibleSkills = computed(() => cvSkills.value.slice(0, MAX_PRINT_SKILLS))
const cvVisibleLanguages = computed(() => cvLanguages.value.slice(0, MAX_PRINT_LANGUAGES))

const cvMoreSectorsCount = computed(() => Math.max(0, cvSectors.value.length - cvVisibleSectors.value.length))
const cvMoreSkillsCount = computed(() => Math.max(0, cvSkills.value.length - cvVisibleSkills.value.length))
const cvMoreLanguagesCount = computed(() => Math.max(0, cvLanguages.value.length - cvVisibleLanguages.value.length))

const cvId = computed(() => {
  const source = `${profileEmail.value}-${profile.value.phone}-${displayCvName.value}`
  const number = (hashText(source) % 900000) + 100000
  return `CVH-${number}`
})

const legacyCvSummaryParagraphs = computed(() => {
  const summary = profile.value.summary.trim()

  if (summary) {
    return summary
      .split(/\n{2,}/)
      .map((paragraph) => paragraph.trim())
      .filter(Boolean)
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
  profile.value.residence && {
    icon: 'fas fa-location-dot',
    value: profile.value.residence,
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

const cvSectors = computed(() => {
  const sectors = new Map()

  profile.value.resume_data.work_experiences.forEach((work) => {
    const category = toText(work.job_category).trim()
    if (!category) return

    const option = getSectorOption({ id: category, name: category })
    if (option) sectors.set(option.value, option)
  })

  return [...sectors.values()]
})

const cvSummaryParagraphs = computed(() => {
  const summary = profile.value.summary.trim()

  if (summary) {
    return summary
      .split(/\n{2,}/)
      .map((paragraph) => paragraph.trim())
      .filter(Boolean)
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
    icon: 'fas fa-passport',
    label: copy.value.citizenship,
    value: getLocalizedCountryLabel(profile.value.resume_data.citizenship, profile.value.resume_data.citizenship) || copy.value.notSpecified,
  },
  profile.value.resume_data.no_driving_license && {
    icon: 'fas fa-car-side',
    label: copy.value.drivingLicenses,
    value: copy.value.noDrivingLicense,
  },
].filter(Boolean))

const cvWorkExperiences = computed(() => (
  profile.value.resume_data.no_work_experience
    ? []
    : profile.value.resume_data.work_experiences.filter((entry) => (
      entry.position || entry.company_name || entry.description
    ))
))
const educationOrder = new Map(
  educationCatalog.map((entry, index) => [entry.value, index]),
)

const cvEducations = computed(() => profile.value.resume_data.educations
  .filter((entry) => (
    entry.level || entry.institution || entry.speciality
  ))
  .slice()
  .sort((left, right) => {
    const leftRank = educationOrder.get(left.level) ?? -1
    const rightRank = educationOrder.get(right.level) ?? -1
    return rightRank - leftRank
  }))
const categoryLabel = (value) => jobCategoryOptions.value.find((option) => option.value === value)?.label || value
const birthDateInput = computed({
  get: () => {
    const value = toText(profile.value.resume_data.birth_date).trim()
    const parsed = parseBirthDate(value)
    if (!parsed) return value

    const day = String(parsed.getDate()).padStart(2, '0')
    const month = String(parsed.getMonth() + 1).padStart(2, '0')
    const year = String(parsed.getFullYear())
    return `${day}.${month}.${year}`
  },
  set: (value) => {
    const text = formatDateTypingValue(value)
    if (!text) {
      profile.value.resume_data.birth_date = ''
      return
    }

    if (/^\d{2}\.\d{2}\.\d{4}$/.test(text)) {
      const [day, month, year] = text.split('.').map(Number)
      profile.value.resume_data.birth_date = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      return
    }

    profile.value.resume_data.birth_date = text
  },
})

const formatDate = (value) => formatDateValue(value, language.value)

const currentStepHeading = computed(() => {
  if (step.value === 1) return copy.value.step1Heading
  if (step.value === 2) return copy.value.step2Heading
  if (step.value === 3) return copy.value.step3Heading
  if (step.value === 4) return copy.value.step4Heading
  return copy.value.step5Heading
})

const currentStepDescription = computed(() => copy.value.stepDescriptions?.[step.value - 1] || '')
const currentStepIcon = computed(() => ['fa-user', 'fa-briefcase', 'fa-graduation-cap', 'fa-id-card', 'fa-file-pdf'][step.value - 1])
const stepProgress = computed(() => Math.round((step.value / steps.value.length) * 100))

const formatMore = (key, count) => translate(`resumeBuilderPage.${key}`, { count }, language.value)

const canAddEmail = computed(() => {
  const items = profile.value.resume_data.additional_emails
  if (!items.length) return true
  return toText(items[items.length - 1]).trim().length > 0
})

const canAddPhone = computed(() => {
  const items = profile.value.resume_data.additional_phones
  if (!items.length) return true
  return toText(items[items.length - 1]).trim().length > 0
})

const emailHasMissingValue = computed(() => (
  !profileEmail.value.trim()
  || profile.value.resume_data.additional_emails.some((item) => !toText(item).trim())
))

const phoneHasMissingValue = computed(() => (
  !profile.value.phone.trim()
  || profile.value.resume_data.additional_phones.some((item) => !toText(item).trim())
))

const firstNameHasMissingValue = computed(() => !profile.value.first_name.trim())
const lastNameHasMissingValue = computed(() => !profile.value.last_name.trim())
const birthDateHasMissingValue = computed(() => !toText(profile.value.resume_data.birth_date).trim())
const genderHasMissingValue = computed(() => !toText(profile.value.resume_data.gender).trim())

const addEmail = () => {
  if (!canAddEmail.value) return
  profile.value.resume_data.additional_emails.push('')
}
const removeEmail = (index) => profile.value.resume_data.additional_emails.splice(index, 1)
const addPhone = () => {
  if (!canAddPhone.value) return
  profile.value.resume_data.additional_phones.push('')
}
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

const requiredWorkFields = ['position', 'job_category', 'company_name', 'country', 'start_date', 'end_date', 'description']
const workErrorKey = (index, field) => `work_${index}_${field}`
const isWorkFieldMissing = (work, field) => {
  if (field === 'end_date' && work.current) return false
  if (field === 'start_date' || field === 'end_date') return !isValidDateValue(work[field])
  return !toText(work[field]).trim()
}
const isWorkFieldInvalid = (index, field) => Boolean(errors.value[workErrorKey(index, field)])

const clearWorkErrors = (target = errors.value) => {
  Object.keys(target).forEach((key) => {
    if (key.startsWith('work_')) delete target[key]
  })
}

const toggleNoWorkExperience = () => {
  if (!profile.value.resume_data.no_work_experience) return

  const nextErrors = { ...errors.value }
  clearWorkErrors(nextErrors)
  errors.value = nextErrors
  status.value = ''
}

const educationLevelsWithSpeciality = new Set(['vocational', 'bachelor', 'master', 'phd'])
const educationLevelsWithOptionalSpecialities = new Set(['vocational', 'bachelor', 'master', 'phd'])
const requiredEducationFields = ['level', 'institution', 'country', 'start_date', 'end_date']
const educationErrorKey = (index, field) => `education_${index}_${field}`
const isEducationSpecialityRequired = (education) => educationLevelsWithSpeciality.has(toText(education?.level).trim())
const shouldShowEducationSpecialities = (education) => educationLevelsWithOptionalSpecialities.has(toText(education?.level).trim())
const handleEducationLevelChange = (education, index) => {
  clearError(educationErrorKey(index, 'level'))
  if (!shouldShowEducationSpecialities(education)) {
    education.speciality = ''
    education.second_speciality = ''
    clearError(educationErrorKey(index, 'speciality'))
  }
}
const isEducationFieldMissing = (education, field) => {
  if (field === 'speciality') {
    if (!isEducationSpecialityRequired(education)) return false
    return !toText(education[field]).trim()
  }
  if (field === 'end_date' && (education.current || education.unfinished)) return false
  if (field === 'start_date' || field === 'end_date') return !isValidDateValue(education[field])
  return !toText(education[field]).trim()
}
const isEducationFieldInvalid = (index, field) => Boolean(errors.value[educationErrorKey(index, field)])
const clearEducationErrors = (target = errors.value) => {
  Object.keys(target).forEach((key) => {
    if (key.startsWith('education_')) delete target[key]
  })
}

const getErrorMessage = (error, fallback) => (
  error?.response?.data?.message
  || error?.response?.data?.detail
  || error?.message
  || fallback
)

const clearLegacyDraftProfile = () => {
  try {
    for (let index = window.localStorage.length - 1; index >= 0; index -= 1) {
      const key = window.localStorage.key(index)
      if (key === LEGACY_CV_DRAFT_STORAGE_KEY || key?.startsWith(`${LEGACY_CV_DRAFT_STORAGE_KEY}:`)) {
        window.localStorage.removeItem(key)
      }
    }
  } catch {
  }
}

const readFileAsDataUrl = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader()

  reader.onload = () => resolve(toText(reader.result))
  reader.onerror = () => reject(new Error('Failed to read file.'))
  reader.readAsDataURL(file)
})

const applyServerProfile = (rawProfile) => {
  isApplyingServerProfile = true
  const nextProfile = normalizeProfile(rawProfile)
  nextProfile.resume_data.cv_language = language.value
  localizeProfileOccupations(nextProfile, language.value)
  profile.value = nextProfile
  firstNameLocked.value = Boolean(nextProfile.first_name.trim())
  lastNameLocked.value = Boolean(nextProfile.last_name.trim())
  savedSnapshot.value = snapshotProfile()

  window.setTimeout(() => {
    isApplyingServerProfile = false
  }, 0)
}

const loadProfile = async () => {
  isLoading.value = true
  status.value = ''
  clearLegacyDraftProfile()

  if (!isAuthenticated.value) {
    profile.value = createEmptyProfile()
    profile.value.resume_data.cv_language = language.value
    firstNameLocked.value = false
    lastNameLocked.value = false
    savedSnapshot.value = ''
    status.value = copy.value.guestMode
    isLoading.value = false
    isLoaded.value = true
    return
  }

  try {
    const loadedProfile = await getProfile()
    applyServerProfile(loadedProfile)
  } catch (error) {
    profile.value = createEmptyProfile()
    profile.value.resume_data.cv_language = language.value
    firstNameLocked.value = false
    lastNameLocked.value = false
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
  residence: profile.value.residence.trim(),
  phone: profile.value.phone.trim(),
  summary: profile.value.summary.trim(),
  current_role: primaryWorkExperience.value.position.trim(),
  desired_occupation_id: profile.value.desired_occupation_id,
  desired_occupation_label: profile.value.desired_occupation_label.trim(),
  skills: profile.value.skills.trim(),
  skill_ids_json: profile.value.skill_ids,
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
    status.value = copy.value.guestMode
    isSaving.value = false
    return false
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

    if (!profileEmail.value.trim() || !isValidEmail(profileEmail.value)) {
      nextErrors.email = copy.value.emailRequired
      isValid = false
    } else if (profile.value.resume_data.additional_emails.some((item) => !toText(item).trim() || !isValidEmail(item))) {
      nextErrors.email = copy.value.requiredFields
      isValid = false
    } else {
      delete nextErrors.email
    }

    if (!profile.value.phone.trim() || !isValidPhone(profile.value.phone)) {
      nextErrors.phone = copy.value.phoneRequired
      isValid = false
    } else if (profile.value.resume_data.additional_phones.some((item) => !toText(item).trim() || !isValidPhone(item))) {
      nextErrors.phone = copy.value.requiredFields
      isValid = false
    } else {
      delete nextErrors.phone
    }

    const resumeData = profile.value.resume_data
    if (!isValidDateValue(resumeData.birth_date)) {
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

    if (!profile.value.desired_occupation_id) {
      nextErrors.desired_occupation = copy.value.roleRequired
      isValid = false
    } else {
      delete nextErrors.desired_occupation
    }

    delete nextErrors.cv_language

    delete nextErrors.communication_language
  }

  if (stepId === 2) {
    clearWorkErrors(nextErrors)
    delete nextErrors.availability

    if (!profile.value.resume_data.no_work_experience) {
      let firstInvalidWorkIndex = -1

      profile.value.resume_data.work_experiences.forEach((work, index) => {
        requiredWorkFields.forEach((field) => {
          if (!isWorkFieldMissing(work, field)) return
          nextErrors[workErrorKey(index, field)] = copy.value.requiredFields
          if (firstInvalidWorkIndex === -1) firstInvalidWorkIndex = index
          isValid = false
        })
        if (work.position && !work.occupation_id) {
          nextErrors[workErrorKey(index, 'position')] = copy.value.requiredFields
          if (firstInvalidWorkIndex === -1) firstInvalidWorkIndex = index
          isValid = false
        }
        const start = parseBirthDate(work.start_date)
        const end = work.current ? null : parseBirthDate(work.end_date)
        if (start && end && end < start) {
          nextErrors[workErrorKey(index, 'end_date')] = copy.value.requiredFields
          if (firstInvalidWorkIndex === -1) firstInvalidWorkIndex = index
          isValid = false
        }
      })

      if (firstInvalidWorkIndex !== -1) expandedWorkIndex.value = firstInvalidWorkIndex
    }
  }

  if (stepId === 3) {
    clearEducationErrors(nextErrors)
    let firstInvalidEducationIndex = -1

    profile.value.resume_data.educations.forEach((education, index) => {
      requiredEducationFields.forEach((field) => {
        if (!isEducationFieldMissing(education, field)) return
        nextErrors[educationErrorKey(index, field)] = copy.value.requiredFields
        if (firstInvalidEducationIndex === -1) firstInvalidEducationIndex = index
        isValid = false
      })

      if (isEducationFieldMissing(education, 'speciality')) {
        nextErrors[educationErrorKey(index, 'speciality')] = copy.value.requiredFields
        if (firstInvalidEducationIndex === -1) firstInvalidEducationIndex = index
        isValid = false
      } else {
        delete nextErrors[educationErrorKey(index, 'speciality')]
      }
      const start = parseBirthDate(education.start_date)
      const end = education.current || education.unfinished ? null : parseBirthDate(education.end_date)
      if (start && end && end < start) {
        nextErrors[educationErrorKey(index, 'end_date')] = copy.value.requiredFields
        if (firstInvalidEducationIndex === -1) firstInvalidEducationIndex = index
        isValid = false
      }
    })

    if (firstInvalidEducationIndex !== -1) expandedEducationIndex.value = firstInvalidEducationIndex
  }

  if (stepId === 4) {
    const resumeData = profile.value.resume_data

    if (!profile.value.languages.length && newLanguage.value && canAddLanguage.value) {
      addLanguage()
    }

    if (!resumeData.citizenship.trim()) {
      nextErrors.citizenship = copy.value.citizenshipRequired
      isValid = false
    } else {
      delete nextErrors.citizenship
    }

    if (!resumeData.no_driving_license && !resumeData.driving_licenses.length) {
      nextErrors.driving_license = copy.value.drivingLicenseRequired
      isValid = false
    } else {
      delete nextErrors.driving_license
    }

    if (!profile.value.languages.length) {
      nextErrors.languages = copy.value.languagesRequired
      isValid = false
    } else {
      delete nextErrors.languages
    }

    if (availabilityMode.value === '__date__' && !isValidAvailabilityDate(profile.value.availability)) {
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

  if (!validateStep(3)) {
    step.value = 3
    status.value = copy.value.requiredFields
    return false
  }

  if (!validateStep(4)) {
    step.value = 4
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
  if (!profile.value.languages.length) {
    if (!canAddLanguage.value) return

    const nextLanguage = newLanguage.value
    if (!nextLanguage) return

    profile.value.languages.push({
      name: nextLanguage,
      level: newLanguageLevel.value,
    })
    newLanguage.value = ''
    clearError('languages')
    return
  }

  if (!canAddNextLanguage.value) return

  profile.value.languages.push({
    name: '',
    level: languageLevelOptions[2].value,
  })
  clearError('languages')
}

const removeLanguage = (index) => {
  profile.value.languages.splice(index, 1)
  clearError('languages')
}

const languageOptionsForIndex = (index) => {
  const currentValue = toText(profile.value.languages[index]?.name).trim()
  const selectedValues = new Set(
    profile.value.languages
      .map((item, itemIndex) => (itemIndex === index ? '' : toText(item.name).trim()))
      .filter(Boolean),
  )

  return languageOptions.value.filter((option) => option.value === currentValue || !selectedValues.has(option.value))
}

const selectWorkOccupation = (work, option) => {
  work.occupation_id = option?.id || ''
  work.position = option?.label || work.position
  clearError(workErrorKey(profile.value.resume_data.work_experiences.indexOf(work), 'position'))
}

const handleWorkPositionInput = (work, index) => {
  work.occupation_id = ''
  clearError(workErrorKey(index, 'position'))
}

const selectDesiredOccupation = (option) => {
  profile.value.desired_occupation_id = option?.id || ''
  profile.value.desired_occupation_label = option?.label || profile.value.desired_occupation_label
  clearError('desired_occupation')
}

const handleDesiredOccupationInput = () => {
  profile.value.desired_occupation_id = ''
  clearError('desired_occupation')
}

watch([language, isLoaded], ([, loaded]) => {
  if (!loaded || isApplyingServerProfile) return
  localizeProfileOccupations(profile.value, language.value)
}, { immediate: true })

const addSkill = (option) => {
  const id = String(option?.id || option?.value || '').trim()
  if (!id || profile.value.skill_ids.some((skill) => String(skill?.id || skill) === id)) return
  profile.value.skill_ids.push({ id, label: option.label })
  newSkillQuery.value = ''
}

const removeSkill = (index) => profile.value.skill_ids.splice(index, 1)

const toggleLicense = (license) => {
  const licenses = profile.value.resume_data.driving_licenses
  const index = licenses.indexOf(license)
  if (index === -1) {
    licenses.push(license)
    profile.value.resume_data.no_driving_license = false
  } else {
    licenses.splice(index, 1)
  }
  clearError('driving_license')
}

const toggleNoDrivingLicense = () => {
  if (profile.value.resume_data.no_driving_license) profile.value.resume_data.driving_licenses = []
  clearError('driving_license')
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
}

const saveCurrentStep = async () => {
  if (!validateStep(step.value)) {
    status.value = copy.value.requiredFields
    return false
  }

  status.value = ''
  return true
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

defineExpose({ goToStep })

const goNext = async () => {
  const saved = await saveCurrentStep()
  if (!saved || step.value >= steps.value.length) return

  if (step.value === 4) {
    if (!isAuthenticated.value) {
      status.value = copy.value.guestMode
      return
    }

    const persisted = await saveProfile({ silent: false, force: true })
    if (!persisted) return
  }

  step.value += 1
}

const goPrev = () => {
  if (step.value > 1) step.value -= 1
}

const exitBuilder = () => emit('close')

const openProfile = async () => {
  emit('close')
  await router.push('/profile')
}

const handleFinalSave = async () => {
  if (!validateBeforeFinalSave()) return
  await saveProfile({ silent: false, force: true })
}

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

const openPdfPreview = async () => {
  const sourceDocument = cvDocumentRef.value?.$el || cvDocumentRef.value
  if (isGeneratingPdf.value || !sourceDocument) return

  const pdfWindow = window.open('', '_blank')
  if (!pdfWindow) {
    status.value = copy.value.pdfPopupBlocked
    return
  }

  pdfWindow.document.title = copy.value.pdfPreviewTitle
  pdfWindow.document.body.style.cssText = 'margin:0;min-height:100vh;display:grid;place-items:center;background:#f3f6f4;font-family:Arial,sans-serif;color:#17211c;'
  const loadingMessage = pdfWindow.document.createElement('strong')
  loadingMessage.textContent = copy.value.pdfGenerating
  pdfWindow.document.body.appendChild(loadingMessage)
  isGeneratingPdf.value = true
  status.value = ''

  const renderHost = document.createElement('div')
  renderHost.style.cssText = 'position:fixed;left:-10000px;top:0;width:49.625rem;background:#fff;pointer-events:none;'
  const printableClone = sourceDocument.cloneNode(true)
  printableClone.style.transform = 'none'
  printableClone.style.margin = '0'
  renderHost.appendChild(printableClone)
  document.body.appendChild(renderHost)
  // Keep PDF-specific DOM mutations centralized in the CV layout module.
  preparePdfCvDocument(printableClone)

  try {
    const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
      import('html2canvas'),
      import('jspdf'),
    ])

    await waitForImages(printableClone)
    await document.fonts?.ready

    const canvas = await html2canvas(printableClone, {
      scale: 2,
      useCORS: true,
      backgroundColor: null,
      logging: false,
      windowWidth: 1280,
    })
    const pdf = await createPaginatedCvPdf(canvas, printableClone, jsPDF)

    const pdfUrl = URL.createObjectURL(pdf.output('blob'))
    pdfWindow.location.replace(pdfUrl)
    window.setTimeout(() => URL.revokeObjectURL(pdfUrl), 5 * 60 * 1000)
  } catch (error) {
    pdfWindow.close()
    status.value = getErrorMessage(error, copy.value.pdfPrepareError)
  } finally {
    renderHost.remove()
    isGeneratingPdf.value = false
  }
}

const printCv = async () => {
  if (!validateBeforeFinalSave()) return

  if (isAuthenticated.value) {
    const saved = await saveProfile({ silent: true, force: false })
    if (!saved) return
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

watch(step, (value) => {
  emit('step-change', value)
}, { immediate: true })

onMounted(() => {
  previousBodyOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  loadInitialData()
})

onBeforeUnmount(() => {
  document.body.style.overflow = previousBodyOverflow
  removePrintFrame()
  revokeAvatarPreview()
})
</script>

<template>
  <Teleport to="body">
    <div class="cv-builder-overlay">
      <div class="main-card" role="dialog" aria-modal="true" :aria-label="copy.pageTitle">
        <div class="close-wrapper">
          <button type="button" class="close" :aria-label="copy.exit" :title="copy.exit" @click="exitBuilder">
            <i class="fas fa-xmark"></i>
          </button>
        </div>
        <div class="main-card__scroll">

          <template v-if="step === 1">
            <div class="form-stack">
              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-address-card"></i></span>
                  <div><h3>{{ copy.identitySection }}</h3></div>
                </div>

                <div class="form-grid form-grid--fixed-two form-grid--personal form-grid--identity">
                  <div class="avatar-upload">
                    <div class="avatar-upload__preview">
                      <img v-if="avatarPreview" :src="avatarPreview" :alt="copy.avatar" />
                      <span v-else><i class="fas fa-user"></i></span>
                    </div>
                    <div class="avatar-upload__copy">
                      <span class="field-label">{{ copy.avatar }}</span>
                      <small>{{ copy.avatarUploadHint }}</small>
                    </div>
                    <button type="button" class="avatar-upload__button" @click="openAvatarPicker">
                      <i class="fas fa-camera"></i>
                      {{ avatarPreview ? copy.changeAvatar : copy.uploadAvatar }}
                    </button>
                    <input ref="avatarInputRef" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="onAvatarChange" />
                  </div>

                  <label>
                    <span class="field-label" :class="{ 'field-label--error': errors.first_name }">{{ copy.firstName }} <b>*</b></span>
                    <input v-model="profile.first_name" :placeholder="copy.firstNamePlaceholder" :disabled="firstNameLocked" @input="clearError('first_name')" />
                  </label>

                  <label>
                    <span class="field-label" :class="{ 'field-label--error': errors.last_name }">{{ copy.lastName }} <b>*</b></span>
                    <input v-model="profile.last_name" :placeholder="copy.lastNamePlaceholder" :disabled="lastNameLocked" @input="clearError('last_name')" />
                  </label>

                  <label class="entry-wide">
                    <span class="field-label">{{ copy.residence }}</span>
                    <input v-model="profile.residence" :placeholder="copy.residencePlaceholder" />
                  </label>

                  <label class="entry-wide">
                    <span class="field-label" :class="{ 'field-label--error': errors.desired_occupation }">{{ copy.desiredRole }} <b>*</b></span>
                    <AutocompleteInput
                      v-model="profile.desired_occupation_label"
                      :suggestions="desiredOccupationSuggestions"
                      :placeholder="copy.desiredRolePlaceholder"
                      :aria-label="copy.desiredRole"
                      @update:model-value="handleDesiredOccupationInput"
                      @select="selectDesiredOccupation"
                    />
                  </label>

                  <div class="contact-group">
                    <span class="field-label" :class="{ 'field-label--error': errors.email }">Email <b>*</b></span>
                    <label class="contact-row contact-row--addable">
                      <input v-if="!isAuthenticated" v-model="profile.email" type="email" placeholder="email@example.com" />
                      <input v-else :value="profileEmail" disabled />
                      <button type="button" class="contact-add" :disabled="!canAddEmail" :aria-label="copy.addEmail" @click="addEmail"><i class="fas fa-plus"></i></button>
                    </label>
                    <label v-for="(_, index) in profile.resume_data.additional_emails" :key="`email-${index}`" class="contact-row contact-row--removable">
                      <input v-model="profile.resume_data.additional_emails[index]" type="email" :placeholder="`email${index + 2}@example.com`" />
                      <button type="button" class="contact-remove" :aria-label="copy.removeEntry" @click="removeEmail(index)"><i class="far fa-trash-can"></i></button>
                    </label>
                  </div>

                  <div class="contact-group">
                    <span class="field-label" :class="{ 'field-label--error': errors.phone }">{{ copy.phone }} <b>*</b></span>
                    <label class="contact-row contact-row--addable">
                      <PhoneInput v-model="profile.phone" placeholder="2X XXX XXX" :aria-label="copy.phone" />
                      <button type="button" class="contact-add" :disabled="!canAddPhone" :aria-label="copy.addPhone" @click="addPhone"><i class="fas fa-plus"></i></button>
                    </label>
                    <label v-for="(_, index) in profile.resume_data.additional_phones" :key="`phone-${index}`" class="contact-row contact-row--removable">
                      <PhoneInput v-model="profile.resume_data.additional_phones[index]" placeholder="2X XXX XXX" :aria-label="`${copy.phone} ${index + 2}`" />
                      <button type="button" class="contact-remove" :aria-label="copy.removeEntry" @click="removePhone(index)"><i class="far fa-trash-can"></i></button>
                    </label>
                  </div>
                </div>
              </section>

              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-user-shield"></i></span>
                  <div><h3>{{ copy.personalSection }}</h3></div>
                </div>

                <div class="form-grid form-grid--fixed-two">
                  <div class="field-cluster">
                    <label>
                      <span class="field-label" :class="{ 'field-label--error': errors.birth_date }">{{ copy.birthDate }} <b>*</b></span>
                      <input
                        v-model="birthDateInput"
                        type="text"
                        inputmode="numeric"
                        maxlength="10"
                        placeholder="DD.MM.YYYY"
                        @input="clearError('birth_date')"
                      />
                    </label>
                    <label class="checkbox-field"><input v-model="profile.resume_data.hide_birth_date" type="checkbox" /><span>{{ copy.hideInCv }}</span></label>
                  </div>

                  <div class="field-cluster">
                    <label>
                      <span class="field-label" :class="{ 'field-label--error': errors.gender }">{{ copy.gender }} <b>*</b></span>
                      <BaseDropdown v-model="profile.resume_data.gender" full-width overlay :options="genderOptions" :placeholder="copy.choose" @change="clearError('gender')" />
                    </label>
                    <label class="checkbox-field"><input v-model="profile.resume_data.hide_gender" type="checkbox" /><span>{{ copy.hideInCv }}</span></label>
                  </div>
                </div>
              </section>

            </div>
          </template>

          <template v-else-if="step === 2">
            <div class="form-stack">
              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-user-pen"></i></span>
                  <div><h3>{{ copy.aboutMe }}</h3></div>
                </div>

                <label>
                  <span class="field-label">{{ copy.aboutMe }}</span>
                  <textarea v-model="profile.summary" rows="5" :placeholder="copy.aboutMePlaceholder"></textarea>
                </label>
              </section>

              <section
                  v-for="(work, index) in profile.resume_data.work_experiences"
                  :key="`work-${index}`"
                  class="entry-card"
                  :class="{
                    'entry-card--collapsed': expandedWorkIndex !== index,
                    'entry-card--disabled': profile.resume_data.no_work_experience,
                  }"
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
                    <div class="entry-card__actions">
                      <button
                        type="button"
                        class="entry-add entry-add--inline"
                        :aria-label="copy.addWorkExperience"
                        :title="copy.addWorkExperience"
                        @click.stop="addWorkExperience"
                      >
                        <i class="fas fa-plus"></i>
                      </button>
                      <button
                        type="button"
                        class="entry-remove"
                        :aria-label="copy.removeEntry"
                        :title="copy.removeEntry"
                        @click.stop="removeWorkExperience(index)"
                      >
                        <i class="far fa-trash-can"></i>
                      </button>
                    </div>
                  </div>

                  <div v-show="expandedWorkIndex === index" class="entry-card__body entry-card__body--work">
                    <label><span class="field-label" :class="{ 'field-label--error': isWorkFieldInvalid(index, 'position') }">{{ copy.position }} <b>*</b></span><AutocompleteInput v-model="work.position" :suggestions="workPositionSuggestions[index] || []" :aria-label="copy.position" :disabled="profile.resume_data.no_work_experience" @update:model-value="handleWorkPositionInput(work, index)" @select="selectWorkOccupation(work, $event)" /></label>
                    <label class="entry-select"><span class="field-label" :class="{ 'field-label--error': isWorkFieldInvalid(index, 'job_category') }">{{ copy.jobCategory }} <b>*</b></span><BaseDropdown v-model="work.job_category" full-width overlay menu-class="cv-builder-category-menu" :max-menu-height="220" :options="sectorDropdownOptions" :show-selected-hint="false" :placeholder="copy.notSpecified" :disabled="profile.resume_data.no_work_experience" /></label>
                    <label><span class="field-label" :class="{ 'field-label--error': isWorkFieldInvalid(index, 'company_name') }">{{ copy.companyName }} <b>*</b></span><input v-model="work.company_name" :disabled="profile.resume_data.no_work_experience" /></label>
                    <label><span class="field-label" :class="{ 'field-label--error': isWorkFieldInvalid(index, 'country') }">{{ copy.country }} <b>*</b></span><BaseDropdown v-model="work.country" full-width overlay :options="countryOptions" :placeholder="copy.choose" :disabled="profile.resume_data.no_work_experience" /></label>

                    <div class="work-period entry-wide">
                      <label><span class="field-label" :class="{ 'field-label--error': isWorkFieldInvalid(index, 'start_date') }">{{ copy.start }} <b>*</b></span><input :value="formatDateInput(work.start_date)" type="text" inputmode="numeric" maxlength="10" placeholder="DD.MM.YYYY" :disabled="profile.resume_data.no_work_experience" @input="work.start_date = normalizeDateInput($event.target.value)" /></label>
                      <label><span class="field-label" :class="{ 'field-label--error': isWorkFieldInvalid(index, 'end_date') }">{{ copy.end }} <b v-if="!work.current">*</b></span><input :value="formatDateInput(work.end_date)" type="text" inputmode="numeric" maxlength="10" placeholder="DD.MM.YYYY" :disabled="profile.resume_data.no_work_experience || work.current" @input="work.end_date = normalizeDateInput($event.target.value)" /></label>
                    </div>

                    <div class="work-checkboxes entry-wide">
                      <label class="checkbox-field current-field"><input v-model="work.current" type="checkbox" :disabled="profile.resume_data.no_work_experience" @change="toggleCurrentWork(work)" /><span>{{ copy.currentlyWorking }}</span></label>
                      <label
                        v-if="index === 0"
                        class="checkbox-field no-work-toggle"
                        :class="{ 'no-work-toggle--active': profile.resume_data.no_work_experience }"
                      >
                        <input v-model="profile.resume_data.no_work_experience" type="checkbox" @change="toggleNoWorkExperience" />
                        <span>{{ copy.noWorkExperience }}</span>
                      </label>
                    </div>

                    <label class="entry-wide"><span class="field-label" :class="{ 'field-label--error': isWorkFieldInvalid(index, 'description') }">{{ copy.workDescription }} <b>*</b></span><textarea v-model="work.description" rows="5" :placeholder="copy.workDescriptionPlaceholder" :disabled="profile.resume_data.no_work_experience"></textarea></label>
                  </div>
              </section>
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
                  <div class="entry-card__actions">
                    <button
                      type="button"
                      class="entry-add entry-add--inline"
                      :aria-label="copy.addEducation"
                      :title="copy.addEducation"
                      @click.stop="addEducation"
                    >
                      <i class="fas fa-plus"></i>
                    </button>
                    <button
                      type="button"
                      class="entry-remove"
                      :aria-label="copy.removeEntry"
                      :title="copy.removeEntry"
                      @click.stop="removeEducation(index)"
                    >
                      <i class="far fa-trash-can"></i>
                    </button>
                  </div>
                </div>

                <div v-show="expandedEducationIndex === index" class="entry-card__body entry-card__body--education">
                  <label><span class="field-label" :class="{ 'field-label--error': isEducationFieldInvalid(index, 'level') }">{{ copy.educationLevel }} <b>*</b></span><BaseDropdown v-model="education.level" full-width overlay :options="educationOptions" @update:model-value="handleEducationLevelChange(education, index)" /></label>
                  <label><span class="field-label" :class="{ 'field-label--error': isEducationFieldInvalid(index, 'institution') }">{{ copy.institution }} <b>*</b></span><input v-model="education.institution" /></label>
                  <template v-if="shouldShowEducationSpecialities(education)">
                    <label><span class="field-label" :class="{ 'field-label--error': isEducationFieldInvalid(index, 'speciality') }">{{ copy.speciality }} <b v-if="isEducationSpecialityRequired(education)">*</b></span><input v-model="education.speciality" /></label>
                  </template>
                  <label :class="{ 'entry-wide': !shouldShowEducationSpecialities(education) }"><span class="field-label" :class="{ 'field-label--error': isEducationFieldInvalid(index, 'country') }">{{ copy.country }} <b>*</b></span><BaseDropdown v-model="education.country" full-width overlay :options="countryOptions" :placeholder="copy.choose" /></label>
                  <div class="education-period entry-wide">
                    <label><span class="field-label" :class="{ 'field-label--error': isEducationFieldInvalid(index, 'start_date') }">{{ copy.start }} <b>*</b></span><input :value="formatDateInput(education.start_date)" type="text" inputmode="numeric" maxlength="10" placeholder="DD.MM.YYYY" @input="education.start_date = normalizeDateInput($event.target.value)" /></label>
                    <label><span class="field-label" :class="{ 'field-label--error': isEducationFieldInvalid(index, 'end_date') }">{{ copy.end }} <b v-if="!education.current">*</b></span><input :value="formatDateInput(education.end_date)" type="text" inputmode="numeric" maxlength="10" placeholder="DD.MM.YYYY" :disabled="education.current" @input="education.end_date = normalizeDateInput($event.target.value)" /></label>
                  </div>

                  <div class="entry-wide work-checkboxes">
                    <label class="checkbox-field current-field"><input v-model="education.current" type="checkbox" @change="toggleCurrentEducation(education)" /><span>{{ copy.currentlyStudying }}</span></label>
                    <label class="checkbox-field"><input v-model="education.unfinished" type="checkbox" /><span>{{ copy.unfinished }}</span></label>
                  </div>
                </div>
              </section>
            </div>
          </template>

          <template v-else-if="step === 4">
            <div class="form-stack additional-step">
              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-calendar-check"></i></span>
                  <div><h3>{{ copy.availability }}</h3><p>{{ copy.availabilityHint }}</p></div>
                </div>
                <div class="availability-fields" :class="{ 'availability-fields--date': availabilityMode === '__date__' }">
                  <label>
                    <span class="field-label" :class="{ 'field-label--error': errors.availability }">{{ copy.availability }}</span>
                    <BaseDropdown
                      v-model="availabilityMode"
                      full-width
                      overlay
                      :options="baseAvailabilityOptions"
                      :placeholder="copy.notSpecified"
                    />
                  </label>
                  <label v-if="availabilityMode === '__date__'">
                    <span class="field-label" :class="{ 'field-label--error': errors.availability }">{{ copy.availableFrom }}</span>
                    <input
                      v-model="availabilityDateInput"
                      type="text"
                      inputmode="numeric"
                      maxlength="10"
                      placeholder="DD.MM.YYYY"
                    />
                  </label>
                </div>
              </section>

              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-passport"></i></span>
                  <div><h3>{{ copy.citizenshipSection }}</h3><p>{{ copy.citizenshipHint }}</p></div>
                </div>
                <label>
                  <span class="field-label" :class="{ 'field-label--error': errors.citizenship }">{{ copy.citizenship }} <b>*</b></span>
                  <BaseDropdown v-model="profile.resume_data.citizenship" full-width overlay :options="citizenshipOptions" :placeholder="copy.choose" @change="clearError('citizenship')" />
                </label>
              </section>

              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-car-side"></i></span>
                  <div>
                    <h3 :class="{ 'field-label--error': errors.driving_license }">{{ copy.drivingLicenses }}</h3>
                    <p>{{ copy.drivingLicensesHint }}</p>
                  </div>
                </div>

                <div class="license-grid" :class="{ 'license-grid--disabled': profile.resume_data.no_driving_license }">
                  <button
                    v-for="license in drivingLicenseValues"
                    :key="license"
                    type="button"
                    class="license-chip"
                    :class="{ 'license-chip--selected': profile.resume_data.driving_licenses.includes(license) }"
                    :disabled="profile.resume_data.no_driving_license"
                    @click="toggleLicense(license)"
                  >
                    <i :class="profile.resume_data.driving_licenses.includes(license) ? 'fas fa-check' : 'fas fa-plus'"></i>{{ license }}
                  </button>
                </div>

                <label class="checkbox-field no-license-toggle" :class="{ 'no-license-toggle--active': profile.resume_data.no_driving_license }">
                  <input v-model="profile.resume_data.no_driving_license" type="checkbox" @change="toggleNoDrivingLicense" />
                  <span>{{ copy.noDrivingLicense }}</span>
                </label>
              </section>

              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-language"></i></span>
                  <div>
                    <h3 :class="{ 'field-label--error': errors.languages }">{{ copy.languageSkills }}</h3>
                    <p>{{ copy.languageSkillsHint }}</p>
                  </div>
                </div>

                <div class="language-add-row" :class="{ 'language-add-row--with-button': profile.languages.length <= 1 }">
                  <label>
                    <span class="field-label">{{ copy.languageAria }}</span>
                    <BaseDropdown v-if="!profile.languages.length" v-model="newLanguage" full-width overlay :options="languageOptions" :placeholder="copy.notSpecified" />
                    <BaseDropdown v-else v-model="profile.languages[0].name" full-width overlay :options="languageOptionsForIndex(0)" :placeholder="copy.notSpecified" :disabled="profile.languages.length > 1" />
                  </label>
                  <label>
                    <span class="field-label">{{ copy.languageLevel }}</span>
                    <BaseDropdown v-if="!profile.languages.length" v-model="newLanguageLevel" full-width overlay :options="languageLevelOptions" />
                    <BaseDropdown v-else v-model="profile.languages[0].level" full-width overlay :options="languageLevelOptions" :disabled="profile.languages.length > 1" />
                  </label>
                  <button v-if="profile.languages.length <= 1" type="button" class="language-add-button" :disabled="profile.languages.length ? !canAddNextLanguage : !canAddLanguage" :aria-label="copy.addLanguage" @click="addLanguage">
                    <i class="fas fa-plus"></i>
                  </button>
                </div>

                <div v-if="profile.languages.length > 1" class="language-list">
                  <div v-for="(item, index) in profile.languages.slice(1)" :key="`${item.name}-${index + 1}`" class="language-row">
                    <BaseDropdown
                      v-model="item.name"
                      full-width
                      overlay
                      :options="languageOptionsForIndex(index + 1)"
                      :placeholder="copy.notSpecified"
                      :disabled="index + 1 !== profile.languages.length - 1"
                    />
                    <BaseDropdown v-model="item.level" full-width overlay :options="languageLevelOptions" :disabled="index + 1 !== profile.languages.length - 1" />
                    <div class="language-row__actions">
                      <button
                        v-if="index + 1 === profile.languages.length - 1"
                        type="button"
                        class="language-add-button"
                        :disabled="!canAddNextLanguage"
                        :aria-label="copy.addLanguage"
                        @click="addLanguage"
                      >
                        <i class="fas fa-plus"></i>
                      </button>
                      <button type="button" class="entry-remove" :disabled="index + 1 !== profile.languages.length - 1" :aria-label="copy.removeLanguage" @click="removeLanguage(index + 1)"><i class="far fa-trash-can"></i></button>
                    </div>
                  </div>
                </div>
                <p v-if="!profile.languages.length" class="additional-empty">{{ copy.noLanguages }}</p>
              </section>

              <section class="form-panel">
                <div class="form-panel__head">
                  <span><i class="fas fa-tags"></i></span>
                  <div><h3>{{ copy.skills }}</h3></div>
                </div>
                <AutocompleteInput
                  v-model="newSkillQuery"
                  :suggestions="skillSuggestions"
                  :placeholder="copy.skills"
                  :aria-label="copy.skills"
                  @select="addSkill"
                />
                <div v-if="profile.skill_ids.length" class="skill-list">
                  <span v-for="(skill, index) in profile.skill_ids" :key="`${skill.id || skill}-${index}`" class="skill-chip">
                    {{ localizeSkill(skill, language) }}
                    <button type="button" :aria-label="copy.removeEntry" @click="removeSkill(index)"><i class="far fa-trash-can"></i></button>
                  </span>
                </div>
              </section>
            </div>
          </template>

          <template v-else>
            <div class="final-tools no-print">
              <div class="pdf-preview-heading">
                <span><i class="fas fa-file-pdf"></i></span>
                <div><h2>{{ copy.pdfPreviewTitle }}</h2><p>{{ copy.pdfPreviewHint }}</p></div>
              </div>

              <div
                class="pdf-preview-trigger"
                role="button"
                tabindex="0"
                :aria-label="copy.openPdf"
                :class="{ 'pdf-preview-trigger--loading': isGeneratingPdf }"
                @click="openPdfPreview"
                @keydown.enter.prevent="openPdfPreview"
                @keydown.space.prevent="openPdfPreview"
              >
                <div class="pdf-preview-overlay">
                  <i :class="isGeneratingPdf ? 'fas fa-spinner fa-spin' : 'fas fa-up-right-from-square'"></i>
                  <strong>{{ isGeneratingPdf ? copy.pdfGenerating : copy.openPdf }}</strong>
                </div>
                <section class="cv-preview-shell">
                  <div class="cv-preview-scale">
                    <CvDocument
                      ref="cvDocumentRef"
                      class="cv-document--preview"
                      :avatar-preview="avatarPreview"
                      :avatar-initials="avatarInitials"
                      :display-name="displayCvName"
                      :display-role="displayCvRole"
                      :contact-items="cvContactItems"
                      :additional-items="cvAdditionalItems"
                      :summary-paragraphs="cvSummaryParagraphs"
                      :work-experiences="cvWorkExperiences"
                      :more-work-experiences-count="0"
                      :languages="cvVisibleLanguages"
                      :more-languages-count="cvMoreLanguagesCount"
                      :licenses="cvLicenses"
                      :skills="cvVisibleSkills"
                      :more-skills-count="cvMoreSkillsCount"
                      :sectors="cvVisibleSectors"
                      :more-sectors-count="cvMoreSectorsCount"
                      :certificates="profile.licenses"
                      :educations="cvEducations"
                      :more-educations-count="0"
                      :cv-id="cvId"
                      :copy="copy"
                      :format-date="formatDate"
                      :format-more="formatMore"
                      :category-label="categoryLabel"
                      :display-language-name="displayLanguageName"
                      :display-education="displayEducation"
                      :format-country="(country) => getLocalizedCountryLabel(country, country)"
                      :show-education-specialities="shouldShowEducationSpecialities"
                    />
                  </div>
                </section>
              </div>
            </div>
          </template>

          <div class="footer-actions no-print">
            <button
              v-if="step === 1 || step === steps.length"
              type="button"
              class="cv-action-button btn-danger"
              :disabled="isSaving"
              @click="exitBuilder"
            >
              <i class="fas fa-right-from-bracket"></i>{{ copy.exit }}
            </button>

            <button v-if="step > 1" type="button" class="cv-action-button btn-secondary" :disabled="isSaving" @click="goPrev">
              <i class="fas fa-arrow-left"></i>{{ copy.back }}
            </button>

            <button v-if="step < steps.length" type="button" class="cv-action-button btn-primary" :disabled="isSaving" @click="goNext">
              {{ isSaving ? copy.saving : copy.next }}<i class="fas fa-arrow-right-long"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped src="./CVBuilder.css"></style>
