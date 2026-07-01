<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import AppLayout from '@/components/AppLayout.vue'
import BaseDropdown from '@/components/BaseDropdown.vue'
import Logo from '@/components/Logo.vue'
import { getProfile, updateProfile } from '@/api/profile'
import { useAuth } from '@/stores/auth'
import { useJobsStore } from '@/stores/jobs'

const AUTOSAVE_DELAY = 1200
const GUEST_RESUME_DRAFT_KEY = 'cvhold:resume-builder:draft'
const MAX_AVATAR_SIZE = 5 * 1024 * 1024
const MAX_RESUME_SIZE = 10 * 1024 * 1024
const AVATAR_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const RESUME_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

const sectorExperienceOptions = [
  { value: '1+ год', label: '1+ год' },
  { value: '2+ года', label: '2+ года' },
  { value: '3+ года', label: '3+ года' },
  { value: '4+ года', label: '4+ года' },
  { value: '5+ лет', label: '5+ лет' },
  { value: '7+ лет', label: '7+ лет' },
  { value: '10+ лет', label: '10+ лет' },
]

const DEFAULT_SECTOR_EXPERIENCE = sectorExperienceOptions[0].value
const MAX_PRINT_SECTORS = 6
const MAX_PRINT_SKILLS = 10
const MAX_PRINT_LANGUAGES = 5
const MAX_PRINT_LICENSES = 5

const languageNames = [
  'Английский',
  'Русский',
  'Немецкий',
  'Польский',
  'Латышский',
  'Литовский',
  'Эстонский',
  'Французский',
]

const languageLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const languageOptions = languageNames.map((label) => ({ value: label, label }))
const languageLevelOptions = languageLevels.map((label) => ({ value: label, label }))
const licenseOptions = [
  'AM',
  'A1',
  'A2',
  'A',
  'B',
  'BE',
  'C1',
  'C1E',
  'C',
  'CE',
  'D1',
  'D1E',
  'D',
  'DE',
  'Код 95',
  'ADR',
  'Forklift',
  'VCA',
].map((label) => ({ value: label, label }))

const permitOptions = [
  { value: '', label: 'Выберите' },
  { value: 'EU гражданин', label: 'EU гражданин' },
  { value: 'Есть виза', label: 'Есть виза' },
  { value: 'Нужен sponsorship', label: 'Нужен sponsorship' },
]

const baseAvailabilityOptions = [
  { value: '', label: 'Выберите' },
  { value: 'Immediate', label: 'Немедленно' },
  { value: '1 week notice', label: 'Через 1 неделю' },
  { value: '2 weeks notice', label: 'Через 2 недели' },
  { value: '1 month notice', label: 'Через 1 месяц' },
  { value: 'By agreement', label: 'По договорённости' },
]

const { state } = useAuth()
const jobsStore = useJobsStore()
const { categoryCounts } = storeToRefs(jobsStore)

const step = ref(1)
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
const newLanguage = ref(languageOptions[0].value)
const newLanguageLevel = ref(languageLevelOptions[2].value)
const newLicense = ref(licenseOptions[4].value)
const cvDocumentRef = ref(null)

let autosaveTimer = null
let savePromise = null
let shouldSaveAgain = false
let isApplyingServerProfile = false
let printFrame = null

const createEmptyProfile = () => ({
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
  resume_name: '',
  resume_url: '',
  avatar_url: '',
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
  .split(/[,;\n]+/)
  .map((item) => item.trim())
  .filter(Boolean)

const limitText = (value, maxLength = 520) => {
  const cleanText = toText(value).replace(/\s+/g, ' ').trim()
  if (cleanText.length <= maxLength) return cleanText

  const clipped = cleanText.slice(0, maxLength).replace(/\s+\S*$/, '').trim()
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
const profileEmail = computed(() => user.value?.email || '')
const avatarPreview = computed(() => avatarObjectUrl.value || profile.value.avatar_url || '')

const jobCategoryOptions = computed(() => {
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

const sectorDropdownOptions = computed(() => [
  {
    value: '',
    label: 'Выберите сферу деятельности',
    hint: 'Категории как на странице вакансий',
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

const getSectorOption = (sector) => {
  const id = toText(sector?.id || sector?.value)
  const name = toText(sector?.name || sector?.label).trim()
  const byId = id ? sectorOptionsByValue.value.get(id) : null
  const byLabel = name ? sectorOptionsByLabel.value.get(name.toLowerCase()) : null

  return byId || byLabel || null
}

const selectedSectorOption = computed(() => sectorOptionsByValue.value.get(selectedSector.value) || null)

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

const availabilityDropdownOptions = computed(() => {
  const currentValue = profile.value.availability.trim()
  const exists = baseAvailabilityOptions.some((option) => option.value === currentValue)

  if (currentValue && !exists && isDateAvailability(currentValue)) {
    return [
      ...baseAvailabilityOptions,
      { value: currentValue, label: `Дата: ${currentValue}` },
    ]
  }

  return baseAvailabilityOptions
})

const availabilityLabel = computed(() => {
  const currentValue = profile.value.availability.trim()
  return availabilityDropdownOptions.value.find((option) => option.value === currentValue)?.label || currentValue
})

const isValidAvailability = (value) => {
  const cleanValue = value.trim()
  if (!cleanValue) return true
  if (baseAvailabilityOptions.some((option) => option.value === cleanValue)) return true
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

const steps = [
  { id: 1, title: 'Основное', subtitle: 'Контакты и позиция' },
  { id: 2, title: 'Опыт', subtitle: 'Навыки и условия' },
  { id: 3, title: 'Готовое CV', subtitle: 'Фото, проверка и PDF' },
]

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
      experience: toText(sector?.experience || DEFAULT_SECTOR_EXPERIENCE),
      iconClass: option.iconClass,
    }
  })
  .filter(Boolean)

const normalizeLanguages = (value) => toArray(value)
  .map((language) => ({
    name: toText(language?.name).trim(),
    level: toText(language?.level || languageLevelOptions[2].value),
  }))
  .filter((language) => language.name)

const normalizeLicenses = (value) => toArray(value)
  .map((license) => (typeof license === 'string' ? license : license?.name || license?.title || ''))
  .map((license) => toText(license).trim())
  .filter(Boolean)

const normalizeProfile = (value = {}) => {
  const source = value || {}

  return {
    ...createEmptyProfile(),
    ...source,
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
    work_permit: toText(source.work_permit),
    availability: toText(source.availability),
    resume_name: toText(source.resume_name),
    resume_url: toText(source.resume_url),
    avatar_url: toText(source.avatar_url),
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
  resume_name: profile.value.resume_name,
  resume_url: profile.value.resume_url,
  avatar_url: profile.value.avatar_url,
  avatarFile: fileSignature(avatarFile.value),
  resumeFile: fileSignature(resumeFile.value),
})

const hasUnsavedChanges = computed(() => isLoaded.value && snapshotProfile() !== savedSnapshot.value)

const progressChecks = computed(() => [
  profile.value.first_name,
  profile.value.last_name,
  profile.value.phone,
  profile.value.current_role,
  profile.value.summary,
  profile.value.skills,
  profile.value.sectors.length,
  profile.value.languages.length,
  profile.value.work_permit,
  profile.value.availability,
  profile.value.avatar_url || avatarFile.value,
  profile.value.resume_name || resumeFile.value,
])

const filledFields = computed(() => progressChecks.value.filter(Boolean).length)
const progress = computed(() => Math.round((filledFields.value / progressChecks.value.length) * 100))

const canAddLanguage = computed(() => !profile.value.languages.some((language) => (
  language.name === newLanguage.value && language.level === newLanguageLevel.value
)))

const statusMessage = computed(() => {
  if (isLoading.value) return 'Загрузка профиля...'
  if (isSaving.value) return 'Сохраняем...'
  if (status.value) return status.value
  if (hasUnsavedChanges.value) return 'Есть несохранённые изменения.'
  return ''
})

const cvName = computed(() => fullName.value || 'Кандидат CVHOLD')
const cvRole = computed(() => profile.value.current_role.trim() || 'Специалист')
const cvSkills = computed(() => splitTextList(profile.value.skills))
const cvSectors = computed(() => profile.value.sectors
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
  const source = `${profileEmail.value}-${profile.value.phone}-${cvName.value}`
  const number = (hashText(source) % 900000) + 100000
  return `CVH-${number}`
})

const cvPublicUrl = computed(() => `cvhold.com/profile/${cvId.value}`)

const cvSummaryParagraphs = computed(() => {
  const summary = profile.value.summary.trim()

  if (summary) {
    return summary
      .split(/\n{2,}/)
      .map((paragraph) => limitText(paragraph, 280))
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
  {
    icon: 'far fa-envelope',
    value: profileEmail.value,
  },
  {
    icon: 'fas fa-phone',
    value: profile.value.phone,
  },
  {
    icon: 'fas fa-globe',
    value: cvPublicUrl.value,
  },
].filter((item) => item.value))

const cvAdditionalItems = computed(() => [
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

const saveGuestDraft = () => {
  if (typeof window === 'undefined') return

  const draft = {
    ...buildPayload(),
    avatar: null,
    resume: null,
    avatar_url: profile.value.avatar_url,
    resume_url: profile.value.resume_url,
    resume_name: profile.value.resume_name,
  }

  window.localStorage.setItem(GUEST_RESUME_DRAFT_KEY, JSON.stringify(draft))
}

const loadGuestDraft = () => {
  if (typeof window === 'undefined') return null

  const rawDraft = window.localStorage.getItem(GUEST_RESUME_DRAFT_KEY)
  if (!rawDraft) return null

  try {
    return JSON.parse(rawDraft)
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
      ? 'Черновик резюме загружен из этого браузера.'
      : 'Гостевой режим: черновик будет сохраняться только в этом браузере.'
    isLoading.value = false
    isLoaded.value = true
    return
  }

  try {
    const loadedProfile = await getProfile()
    applyServerProfile(loadedProfile)
  } catch (error) {
    profile.value = createEmptyProfile()
    savedSnapshot.value = snapshotProfile()
    status.value = getErrorMessage(error, 'Не удалось загрузить профиль.')
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
  summary: profile.value.summary.trim(),
  current_role: profile.value.current_role.trim(),
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
  avatar: avatarFile.value,
  resume: resumeFile.value,
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
      status.value = silent ? '' : 'Черновик сохранен в этом браузере.'
      return true
    } catch (error) {
      status.value = getErrorMessage(error, 'Не удалось сохранить черновик локально.')
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
      if (!silent) status.value = 'Сохраняем последние изменения...'
      return true
    }

    avatarFile.value = null
    resumeFile.value = null
    revokeAvatarPreview()
    applyServerProfile(serverProfile)
    clearErrors()
    status.value = silent ? '' : 'Профиль успешно сохранён.'
    return true
  } catch (error) {
    status.value = getErrorMessage(error, 'Не удалось сохранить профиль.')
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
    saveProfile({ silent: true })
  }, AUTOSAVE_DELAY)
}

const validateStep = (stepId) => {
  const nextErrors = { ...errors.value }
  let isValid = true

  if (stepId === 1) {
    if (!profile.value.first_name.trim()) {
      nextErrors.first_name = 'Укажите имя.'
      isValid = false
    } else {
      delete nextErrors.first_name
    }

    if (!profile.value.last_name.trim()) {
      nextErrors.last_name = 'Укажите фамилию.'
      isValid = false
    } else {
      delete nextErrors.last_name
    }

    if (!profile.value.current_role.trim()) {
      nextErrors.current_role = 'Укажите желаемую позицию.'
      isValid = false
    } else {
      delete nextErrors.current_role
    }
  }

  if (stepId === 2) {
    const availability = profile.value.availability.trim()

    if (!isValidAvailability(availability)) {
      nextErrors.availability = 'Выберите доступность из списка.'
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
    status.value = 'Проверьте обязательные поля.'
    return false
  }

  if (!validateStep(2)) {
    step.value = 2
    status.value = 'Проверьте обязательные поля.'
    return false
  }

  return true
}

const validateFile = (file, { types, maxSize, label }) => {
  if (!file) return `${label}: файл не выбран.`
  if (!types.includes(file.type)) return `${label}: неподдерживаемый формат файла.`
  if (file.size > maxSize) return `${label}: файл слишком большой.`
  return ''
}

const addSector = () => {
  const option = selectedSectorOption.value
  if (!option) return

  if (!canAddSector.value) {
    setError('sectors', 'Такая сфера уже добавлена.')
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
    setError('licenses', 'Такая лицензия или сертификат уже добавлены.')
    return
  }

  profile.value.licenses.push(value)
  clearError('licenses')
}

const removeLicense = (index) => {
  profile.value.licenses.splice(index, 1)
  clearError('licenses')
}

const onAvatarChange = (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  const error = validateFile(file, {
    types: AVATAR_TYPES,
    maxSize: MAX_AVATAR_SIZE,
    label: 'Аватар',
  })

  if (error) {
    setError('avatar', error)
    return
  }

  avatarFile.value = file
  revokeAvatarPreview()
  avatarObjectUrl.value = URL.createObjectURL(file)
  clearError('avatar')
  scheduleAutosave()
}

const onResumeChange = (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  const error = validateFile(file, {
    types: RESUME_TYPES,
    maxSize: MAX_RESUME_SIZE,
    label: 'CV',
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
    status.value = 'Проверьте обязательные поля.'
    return false
  }

  return saveProfile({ silent: false })
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
  if (saved && step.value < steps.length) {
    step.value += 1
  }
}

const goPrev = () => {
  if (step.value > 1) step.value -= 1
}

const handleFinalSave = async () => {
  if (!validateBeforeFinalSave()) return
  await saveProfile({ silent: false, force: true })
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
        <title>${cvName.value} — CVHOLD CV</title>
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

  const saved = await saveProfile({ silent: false, force: true })
  if (!saved) return

  await nextTick()

  const printable = buildPrintableDocument()

  if (!printable) {
    status.value = 'Не удалось подготовить CV к PDF.'
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
  status.value = 'Откройте системное окно печати и выберите «Сохранить в PDF».'
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
          <div class="title-row">
            <h1>Резюме кандидата</h1>
          </div>

          <p>
            Заполните профиль по шагам: основная информация, опыт и навыки, затем реальные файлы.
            Всё сохраняется в аккаунт и используется в откликах на вакансии.
          </p>
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
            <h2 v-if="step === 1">Шаг 1. Основная информация</h2>
            <h2 v-else-if="step === 2">Шаг 2. Опыт и навыки</h2>
            <h2 v-else>Шаг 3. Фото, CV и финальная проверка</h2>
            <p v-if="statusMessage" class="hint">{{ statusMessage }}</p>
          </div>

          <template v-if="step === 1">
            <div class="grid-two">
              <label>
                Имя
                <input v-model="profile.first_name" placeholder="Иван" @input="clearError('first_name')" />
                <span v-if="errors.first_name" class="field-error">{{ errors.first_name }}</span>
              </label>

              <label>
                Фамилия
                <input v-model="profile.last_name" placeholder="Иванов" @input="clearError('last_name')" />
                <span v-if="errors.last_name" class="field-error">{{ errors.last_name }}</span>
              </label>

              <label>
                Email
                <input :value="profileEmail" disabled />
              </label>

              <label>
                Телефон
                <input v-model="profile.phone" placeholder="+371 2X XXX XXX" />
              </label>

              <label class="grid-span-2">
                Желаемая позиция
                <input
                  v-model="profile.current_role"
                  placeholder="Например, Сварщик MIG/MAG"
                  @input="clearError('current_role')"
                />
                <span v-if="errors.current_role" class="field-error">{{ errors.current_role }}</span>
              </label>

              <label class="grid-span-2">
                Ключевые навыки
                <input v-model="profile.skills" placeholder="MIG/MAG, TIG, монтаж, чтение чертежей" />
              </label>
            </div>

            <label>
              О себе
              <textarea
                v-model="profile.summary"
                rows="6"
                placeholder="Кратко опишите ваш опыт, сильные стороны и формат работы, который ищете."
              ></textarea>
            </label>
          </template>

          <template v-else-if="step === 2">
            <div class="section">
              <label class="section-label">Сферы деятельности</label>

              <div class="chips sector-chips">
                <span
                  v-for="(sector, index) in profile.sectors"
                  :key="`${sector.id || sector.name}-${index}`"
                  class="chip sector-chip"
                >
                  <span class="sector-chip__icon">
                    <i :class="getSectorOption(sector)?.iconClass"></i>
                  </span>
                  <span class="sector-chip__copy">
                    <strong>{{ getSectorOption(sector)?.label }}</strong>
                    <small>{{ sector.experience || DEFAULT_SECTOR_EXPERIENCE }}</small>
                  </span>
                  <button type="button" @click="removeSector(index)">×</button>
                </span>
              </div>

              <div class="inline-add sector-add">
                <BaseDropdown
                  v-model="selectedSector"
                  aria-label="Сфера деятельности"
                  class="sector-dropdown"
                  :options="sectorDropdownOptions"
                  full-width
                  :show-selected-hint="false"
                  @change="clearError('sectors')"
                />

                <BaseDropdown
                  v-model="selectedSectorExperience"
                  aria-label="Опыт в сфере"
                  class="sector-dropdown sector-dropdown--experience"
                  :options="sectorExperienceOptions"
                  full-width
                />

                <button type="button" class="ghost-button" :disabled="!canAddSector" @click="addSector">
                  Добавить
                </button>
              </div>

              <span v-if="errors.sectors" class="field-error">{{ errors.sectors }}</span>
            </div>

            <div class="section">
              <label class="section-label">Языки</label>

              <div class="chips">
                <span
                  v-for="(language, index) in profile.languages"
                  :key="`${language.name}-${language.level}-${index}`"
                  class="chip"
                >
                  <span>{{ language.name }}</span>
                  <b>{{ language.level }}</b>
                  <button type="button" @click="removeLanguage(index)">×</button>
                </span>
              </div>

              <div class="grid-two">
                <BaseDropdown
                  v-model="newLanguage"
                  aria-label="Язык"
                  full-width
                  :options="languageOptions"
                />

                <BaseDropdown
                  v-model="newLanguageLevel"
                  aria-label="Уровень языка"
                  full-width
                  :options="languageLevelOptions"
                />
              </div>

              <button
                type="button"
                class="ghost-button ghost-button--small"
                :disabled="!canAddLanguage"
                @click="addLanguage"
              >
                Добавить язык
              </button>
            </div>

            <div class="grid-two">
              <label>
                Разрешение на работу
                <BaseDropdown
                  v-model="profile.work_permit"
                  aria-label="Разрешение на работу"
                  full-width
                  :options="permitOptions"
                />
              </label>

              <label>
                Доступность
                <BaseDropdown
                  v-model="profile.availability"
                  aria-label="Доступность"
                  full-width
                  :options="availabilityDropdownOptions"
                  @change="clearError('availability')"
                />
                <span v-if="errors.availability" class="field-error">{{ errors.availability }}</span>
              </label>
            </div>

            <div class="section">
              <label class="section-label">Права, лицензии и сертификаты</label>

              <div class="chips">
                <span v-for="(license, index) in profile.licenses" :key="`${license}-${index}`" class="chip">
                  <span>{{ license }}</span>
                  <button type="button" @click="removeLicense(index)">×</button>
                </span>
              </div>

              <div class="inline-add inline-add--dropdown">
                <BaseDropdown
                  v-model="newLicense"
                  aria-label="Категория прав, лицензия или сертификат"
                  full-width
                  :options="licenseOptions"
                  @change="clearError('licenses')"
                />
                <button type="button" class="ghost-button" @click="addLicense">Добавить</button>
              </div>

              <span v-if="errors.licenses" class="field-error">{{ errors.licenses }}</span>
            </div>
          </template>

          <template v-else>
            <div class="final-tools no-print">

              <div class="review-card">
                <div>
                  <h3>Готовое CV</h3>
                  <p>
                    CV собирается автоматически из данных профиля. Проверьте результат ниже и сохраните PDF.
                  </p>
                </div>

                <div class="review-actions">
                  <button type="button" class="btn-light" :disabled="isSaving" @click="handleFinalSave">
                    {{ isSaving ? 'Сохраняем...' : 'Сохранить' }}
                  </button>
                  <button type="button" class="btn-primary" :disabled="isSaving" @click="printCv">
                    Скачать PDF
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
                      <img v-if="avatarPreview" :src="avatarPreview" :alt="cvName" />
                      <span v-else>{{ avatarInitials }}</span>
                    </div>

                    <div>
                      <h1>{{ cvName }}</h1>
                      <p>{{ cvRole }}</p>

                      <ul class="cv-contact-list">
                        <li v-for="item in cvContactItems" :key="item.value">
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
                      <h2>О себе</h2>
                      <p
                        v-for="paragraph in cvSummaryParagraphs"
                        :key="paragraph"
                        class="cv-summary-text"
                      >
                        {{ paragraph }}
                      </p>
                    </section>

                    <section v-if="cvVisibleSectors.length" class="cv-section">
                      <h2>Сферы деятельности</h2>
                      <div class="cv-sector-grid">
                        <div v-for="sector in cvVisibleSectors" :key="sector.value" class="cv-sector">
                          <i :class="sector.iconClass"></i>
                          <span class="cv-sector__copy">
                            <strong>{{ sector.label }}</strong>
                            <small>{{ sector.experience }}</small>
                          </span>
                        </div>
                        <div v-if="cvMoreSectorsCount" class="cv-sector cv-more-item">
                          <span>+ ещё {{ cvMoreSectorsCount }}</span>
                        </div>
                      </div>
                    </section>

                    <section v-if="cvVisibleSkills.length" class="cv-section">
                      <h2>Навыки</h2>
                      <ul class="cv-list">
                        <li v-for="skill in cvVisibleSkills" :key="skill">{{ skill }}</li>
                        <li v-if="cvMoreSkillsCount" class="cv-more-item">
                          + ещё {{ cvMoreSkillsCount }}
                        </li>
                      </ul>
                    </section>
                  </main>

                  <aside class="cv-aside">
                    <section v-if="cvVisibleLanguages.length" class="cv-section">
                      <h2>Языки</h2>
                      <ul class="cv-list">
                        <li v-for="language in cvVisibleLanguages" :key="`${language.name}-${language.level}`">
                          {{ language.name }} — {{ language.level }}
                        </li>
                        <li v-if="cvMoreLanguagesCount" class="cv-more-item">
                          + ещё {{ cvMoreLanguagesCount }}
                        </li>
                      </ul>
                    </section>

                    <section v-if="cvVisibleLicenses.length" class="cv-section">
                      <h2>Сертификаты и лицензии</h2>
                      <ul class="cv-list">
                        <li v-for="license in cvVisibleLicenses" :key="license">{{ license }}</li>
                        <li v-if="cvMoreLicensesCount" class="cv-more-item">
                          + ещё {{ cvMoreLicensesCount }}
                        </li>
                      </ul>
                    </section>

                    <section class="cv-section">
                      <h2>Дополнительно</h2>
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

                  <span>Verified • Secure • Professional</span>
                  <span>www.cvhold.com</span>
                </footer>
              </article>
            </section>
          </template>

          <div class="footer-actions no-print">
            <button type="button" class="btn-light" :disabled="step === 1 || isSaving" @click="goPrev">
              Назад
            </button>

            <button v-if="step < 3" type="button" class="btn-primary" :disabled="isSaving" @click="goNext">
              {{ isSaving ? 'Сохраняем...' : 'Далее' }}
            </button>
          </div>
        </div>

        <aside class="sidebar no-print">
          <div class="side-card profile-card">
            <div class="profile-card__top">
              <div class="profile-avatar">
                <img v-if="avatarPreview" class="profile-avatar__image" :src="avatarPreview" alt="Аватар" />
                <span v-else>{{ avatarInitials }}</span>
              </div>

              <div>
                <strong>{{ fullName || 'Ваше имя' }}</strong>
                <p>{{ profile.current_role || 'Профессия' }}</p>
              </div>
            </div>

            <div class="profile-meta">
              <span>{{ profileEmail || 'email@example.com' }}</span>
              <span>{{ profile.phone || '+000 00 000 000' }}</span>
            </div>
          </div>

          <div class="side-card">
            <div class="side-card__head">
              <strong>Заполненность профиля</strong>
              <span class="shield">✓</span>
            </div>

            <div class="progress-value">{{ progress }}%</div>

            <div class="progress-track">
              <span class="progress-bar" :style="{ width: `${progress}%` }"></span>
            </div>

            <p>Готовый профиль ускоряет отклик на вакансии и делает кандидата понятнее работодателю.</p>
          </div>

          <div class="side-card side-card--dashed">
            <h3>Что должно быть в хорошем CV</h3>

            <div class="feature">
              <span class="feature-icon">1</span>
              <div class="feature-text">
                <strong>Понятная роль</strong>
                <small>Укажите специализацию и сильные стороны в нескольких словах.</small>
              </div>
            </div>

            <div class="feature">
              <span class="feature-icon">2</span>
              <div class="feature-text">
                <strong>Сферы деятельности и опыт</strong>
                <small>Добавьте направления работы, опыт по каждой сфере и языки.</small>
              </div>
            </div>

            <div class="feature">
              <span class="feature-icon">3</span>
              <div class="feature-text">
                <strong>Готовое CV</strong>
                <small>На последнем шаге профиль собирается в аккуратное резюме для PDF.</small>
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
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
  gap: 1.35rem;
  height: 100%;
}

.card-head {
  display: grid;
  gap: 0.4rem;
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

.upload-card__title {
  color: var(--text-primary);
  font-weight: 700;
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

.avatar__image,
.profile-avatar__image {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover;
  display: block;
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
    grid-template-columns: 1fr;
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
  .steps,
  .grid-two,
  .inline-add,
  .upload-grid,
  .sector-add {
    grid-template-columns: 1fr;
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
