<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { translate, useI18n } from '@/i18n'
import AppLayout from '@/components/AppLayout.vue'
import BaseDropdown from '@/components/BaseDropdown.vue'
import DashboardShell from '@/components/dashboard/DashboardShell.vue'
import MessagesPanel from '@/components/messages/MessagesPanel.vue'
import { resolveApiUrl } from '@/api/client'
import { useAuth } from '@/stores/auth'
import {
  approveResponseChat,
  createJob,
  deleteJob,
  getMyJobs,
  getResponses,
  updateJob,
} from '@/api/jobs'
import { useMessagingStore } from '@/stores/messaging'
import { ApiError } from '@/api/client'
import {
  getLanguageOptions,
  getLicenseOptions,
  languageLevelOptions,
  normalizeLanguages,
  normalizeLicenses,
} from '@/utils/jobRequirements'
import {
  countryByKey,
  countryDropdownOptions,
  getCityOptions,
  resolveCountryMeta,
  salaryCurrencyOptions,
} from '@/utils/countries'
import { inferJobCategory, localizeCategoryConfigs } from '@/utils/jobCategories'
import { analyzeCandidateMatch } from '@/utils/matchScore'
import { normalizeJob } from '@/utils/jobs'

const route = useRoute()
const router = useRouter()
const messaging = useMessagingStore()
const auth = useAuth()
const { language: currentLanguage, t } = useI18n()
const employmentTypeOptions = ['full-time', 'shift', 'contract']

const plans = [
  {
    id: 'basic',
    name: 'Basic',
    price: '99 EUR',
    vacancies: '1 вакансия',
    description: 'Для точечного найма и редких публикаций.',
    features: ['30 дней публикации', 'Базовая карточка вакансии', 'Отклики кандидатов'],
  },
  {
    id: 'standard',
    name: 'Standard',
    price: '149 EUR',
    vacancies: '5 вакансий',
    description: 'Лучший баланс для активного работодателя.',
    features: ['30 дней публикации', 'Кабинет работодателя', 'Сравнение кандидатов'],
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '229 EUR',
    vacancies: '20 вакансий',
    description: 'Для команд с постоянным потоком найма.',
    features: ['Приоритетная выдача', 'Расширенная аналитика', 'Приоритетная поддержка'],
  },
]

const copy = computed(() => translate('employerDashboardPage', {}, currentLanguage.value))

const interpolate = (template, params = {}) => String(template).replace(/\{(\w+)\}/g, (_, key) => String(params[key] ?? ''))

const sections = [
  { id: 'jobs', icon: 'fas fa-briefcase', to: '/dashboard?section=jobs' },
  { id: 'responses', icon: 'fas fa-user-check', to: '/dashboard?section=responses' },
  { id: 'messages', icon: 'fas fa-message', to: '/dashboard?section=messages' },
  { id: 'pricing', icon: 'fas fa-credit-card', to: '/dashboard?section=pricing' },
]

const localizedPlans = computed(() => plans.map((plan) => ({
  ...plan,
  vacancies: copy.value.planMeta[plan.id]?.vacancies || '',
  description: copy.value.planMeta[plan.id]?.description || '',
  features: copy.value.planMeta[plan.id]?.features || [],
})))

const localizedSections = computed(() => sections.map((section) => ({
  ...section,
  label: copy.value.sections[section.id] || section.label,
  to: `${route.path}?section=${section.id}`,
})))

const localizedLanguageOptions = computed(() => getLanguageOptions())
const localizedLicenseOptions = computed(() => getLicenseOptions())
const localizedCategoryOptions = computed(() => ([
  {
    value: '',
    label: copy.value.chooseCategory,
    iconClass: 'fas fa-list',
  },
  ...localizeCategoryConfigs((key) => t(key))
    .filter((category) => category.id !== 'all')
    .map((category) => ({
      value: category.id,
      label: category.label,
      iconClass: category.icon,
    })),
]))
const categoryFieldLabel = computed(() => copy.value.categoryFieldLabel)
const categoryPlaceholder = computed(() => copy.value.chooseCategory)
const localizedEmploymentTypeOptions = computed(() => employmentTypeOptions.map((option) => ({
  id: option,
  label: copy.value.employmentTypes[option],
})))
const localizedExperienceOptions = computed(() => ([
  { value: 'no_experience', label: copy.value.experienceOptions.no_experience },
  { value: '1_year', label: copy.value.experienceOptions['1_year'] },
  { value: '2_years', label: copy.value.experienceOptions['2_years'] },
  { value: '3_years', label: copy.value.experienceOptions['3_years'] },
  { value: '4_years', label: copy.value.experienceOptions['4_years'] },
  { value: '5_years', label: copy.value.experienceOptions['5_years'] },
  { value: '7_years', label: copy.value.experienceOptions['7_years'] },
  { value: '10_years', label: copy.value.experienceOptions['10_years'] },
]))
const localizedEducationOptions = computed(() => ([
  { value: '', label: copy.value.educationPlaceholder },
  { value: 'primary', label: copy.value.educationOptions.primary },
  { value: 'secondary', label: copy.value.educationOptions.secondary },
  { value: 'vocational', label: copy.value.educationOptions.vocational },
  { value: 'bachelor', label: copy.value.educationOptions.bachelor },
  { value: 'master', label: copy.value.educationOptions.master },
  { value: 'phd', label: copy.value.educationOptions.phd },
]))
const validSectionIds = sections.map((section) => section.id)
const normalizeSection = (section) => (validSectionIds.includes(section) ? section : 'jobs')

const blankForm = () => ({
  title: '',
  company: '',
  salary: '',
  salary_currency: 'EUR',
  category: '',
  employment_type: 'full-time',
  experience_level: 'no_experience',
  education_level: '',
  country_key: '',
  location: '',
  description: '',
  languages: [],
  licenses: [],
  has_housing: false,
  has_transport: false,
  logo: null,
  banner: null,
})

const activeSection = ref(normalizeSection(typeof route.query.section === 'string' ? route.query.section : 'jobs'))
const jobs = ref([])
const responses = ref([])
const isLoading = ref(false)
const isRefreshing = ref(false)
const isSaving = ref(false)
const isJobModalOpen = ref(false)
const deletingId = ref(null)
const approvingId = ref(null)
const editingId = ref(null)
const form = ref(blankForm())
const status = ref('')
const error = ref('')
const logoPreview = ref('')
const bannerPreview = ref('')
const objectUrl = ref('')
const bannerObjectUrl = ref('')
const newLanguage = ref(localizedLanguageOptions.value[0]?.value || 'English')
const newLanguageLevel = ref(languageLevelOptions[2].value)
const newLicense = ref(copy.value.noLicense)
const expandedResponseJobIds = ref([])
const brokenAvatars = ref(new Set())
const dashboardRefreshTimer = ref(null)

const conversations = computed(() => messaging.conversations)
const isEditing = computed(() => editingId.value !== null)
const employerCompanyName = computed(() => String(auth.user?.company_name || '').trim())
const employerCompanyLogo = computed(() => String(auth.user?.company_logo_url || '').trim())
const approvedCount = computed(() => jobs.value.filter((job) => job.status === 'approved').length)
const subscriptionExpiresAt = computed(() => auth.user?.subscription_expires_at || '')
const hasActiveSubscription = computed(() => {
  if (!auth.user?.subscription_plan || !subscriptionExpiresAt.value) return false
  const expiresAt = new Date(subscriptionExpiresAt.value)
  return !Number.isNaN(expiresAt.getTime()) && expiresAt > new Date()
})
const currentPlanId = computed(() => (hasActiveSubscription.value ? auth.user?.subscription_plan || '' : ''))
const canAddLanguage = computed(() => !form.value.languages.some((language) => (
  language.name === newLanguage.value && language.level === newLanguageLevel.value
)))
const currentPlan = computed(() => localizedPlans.value.find((plan) => plan.id === currentPlanId.value) || null)
const currentPlanName = computed(() => currentPlan.value?.name || copy.value.noActivePlan)
const currentPlanPrice = computed(() => currentPlan.value?.price || '-')
const currentPlanLimit = computed(() => currentPlan.value?.vacancies || '-')
const currentPlanExpires = computed(() => (
  hasActiveSubscription.value
    ? new Intl.DateTimeFormat(currentLanguage.value === 'lv' ? 'lv-LV' : currentLanguage.value === 'en' ? 'en-GB' : 'ru-RU').format(new Date(subscriptionExpiresAt.value))
    : '-'
))
const selectedCountry = computed(() => countryByKey[form.value.country_key] || null)
const cityOptions = computed(() => {
  const availableCities = selectedCountry.value ? getCityOptions(selectedCountry.value.key) : []
  const currentLocation = String(form.value.location || '').trim()
  const knownValues = availableCities.map((city) => city.value)
  const options = [...availableCities]

  if (currentLocation && !knownValues.includes(currentLocation)) {
    options.unshift({ value: currentLocation, label: currentLocation })
  }

  return [{ value: '', label: copy.value.chooseCity }, ...options]
})
const scoredResponses = computed(() => responses.value.map((item) => ({
  ...item,
  matchAnalysis: analyzeCandidateMatch(item, item),
})))

function parseSalaryParts(value = '') {
  const raw = String(value || '').trim()
  if (!raw) return { amount: '', currency: 'EUR' }

  const match = raw.match(/^(.*?)(?:\s+([A-Z]{3}|€|\$))?$/)
  const amount = String(match?.[1] || raw).trim()
  const currencyToken = String(match?.[2] || '').trim().toUpperCase()
  const currency = currencyToken === '€' ? 'EUR' : currencyToken === '$' ? 'USD' : currencyToken || 'EUR'

  return { amount, currency }
}

function formatSalaryValue(amount, currency) {
  const cleanAmount = String(amount || '').trim()
  const cleanCurrency = String(currency || '').trim().toUpperCase()
  return cleanAmount && cleanCurrency ? `${cleanAmount} ${cleanCurrency}` : cleanAmount
}

const groupedResponses = computed(() => {
  const groups = new Map()

  scoredResponses.value.forEach((item) => {
    const key = String(item.job_id)
    if (!groups.has(key)) {
      groups.set(key, {
        job_id: item.job_id,
        job_title: item.job_title,
        job_company: item.job_company,
        job_location: item.job_location,
        job_salary: item.job_salary,
        responses: [],
        counts: {
          strong: 0,
          good: 0,
          partial: 0,
          weak: 0,
          fail: 0,
        },
      })
    }

    const group = groups.get(key)
    group.responses.push(item)
    group.counts[item.matchAnalysis.meta.key] += 1
  })

  return [...groups.values()]
    .map((group) => ({
      ...group,
      responses: group.responses.sort((left, right) => right.matchAnalysis.score - left.matchAnalysis.score),
      badges: [
        { key: 'strong', label: copy.value.matchSummary.strong, count: group.counts.strong },
        { key: 'good', label: copy.value.matchSummary.good, count: group.counts.good },
        { key: 'partial', label: copy.value.matchSummary.partial, count: group.counts.partial },
        { key: 'weak', label: copy.value.matchSummary.weak, count: group.counts.weak },
        { key: 'fail', label: copy.value.failLabel, count: group.counts.fail },
      ].filter((item) => item.count > 0),
    }))
    .sort((left, right) => {
      const leftTop = left.responses[0]?.matchAnalysis.score || 0
      const rightTop = right.responses[0]?.matchAnalysis.score || 0
      return rightTop - leftTop
    })
})

const responseMatchSummary = computed(() => {
  const counters = {
    strong: 0,
    good: 0,
    partial: 0,
    weak: 0,
    fail: 0,
  }

  scoredResponses.value.forEach((item) => {
    counters[item.matchAnalysis.meta.key] += 1
  })

  return [
    { key: 'strong', label: copy.value.matchSummary.strong, count: counters.strong },
    { key: 'good', label: copy.value.matchSummary.good, count: counters.good },
    { key: 'partial', label: copy.value.matchSummary.partial, count: counters.partial },
    { key: 'weak', label: copy.value.matchSummary.weak, count: counters.weak },
    { key: 'fail', label: copy.value.failLabel, count: counters.fail },
  ].filter((item) => item.count > 0)
})

const localizedShellStats = computed(() => ([
  { value: jobs.value.length, label: copy.value.stats.jobs, section: 'jobs' },
  { value: approvedCount.value, label: copy.value.stats.published, section: 'jobs' },
  { value: responses.value.length, label: copy.value.stats.responses, section: 'responses' },
  { value: conversations.value.length, label: copy.value.stats.conversations, section: 'messages' },
]))
const localizedActiveSectionLabel = computed(() => localizedSections.value.find((item) => item.id === activeSection.value)?.label || copy.value.fallbackSection)
const localizedSubmitLabel = computed(() => (isSaving.value ? copy.value.saving : (isEditing.value ? copy.value.saveChanges : copy.value.saveJob)))
const categoryRequiredError = computed(() => copy.value.categoryRequiredError)
const localizedResponseStats = computed(() => ([
  { label: copy.value.activeJobs, value: groupedResponses.value.length },
  { label: copy.value.totalResponses, value: scoredResponses.value.length },
  { label: copy.value.strongMatch, value: scoredResponses.value.filter((item) => item.matchAnalysis.meta.key === 'strong').length },
  { label: copy.value.chatActive, value: scoredResponses.value.filter((item) => item.chat_approved).length },
]))

function localizedResponseCount(count) {
  return interpolate(copy.value.responsesCount, { count })
}

function revokeLogoPreview() {
  if (objectUrl.value) {
    URL.revokeObjectURL(objectUrl.value)
    objectUrl.value = ''
  }
}

function revokeBannerPreview() {
  if (bannerObjectUrl.value) {
    URL.revokeObjectURL(bannerObjectUrl.value)
    bannerObjectUrl.value = ''
  }
}

function resolveAssetUrl(url) {
  if (!url) return ''
  if (/^(https?:|data:|blob:)/.test(url)) return url
  return url.startsWith('/') ? url : `/${url}`
}

function getFirstLetter(value) {
  return String(value || '').trim().match(/\p{L}/u)?.[0]?.toUpperCase() || ''
}

function getFirstTwoLetters(value) {
  const letters = String(value || '').trim().match(/\p{L}/gu) || []
  return letters.slice(0, 2).join('').toUpperCase()
}

function responseAvatarKey(item) {
  return String(item.id || `${item.name || ''}-${item.surname || ''}`)
}

function responseAvatar(item) {
  const avatar = resolveAssetUrl(
    item.avatar_url ||
      item.candidate_avatar_url ||
      item.applicant_avatar_url ||
      item.profile_avatar_url ||
      '',
  )

  if (!avatar || brokenAvatars.value.has(responseAvatarKey(item))) return ''
  return avatar
}

function markAvatarBroken(item) {
  brokenAvatars.value = new Set([...brokenAvatars.value, responseAvatarKey(item)])
}

function responseFullName(item) {
  return [item.name, item.surname].filter(Boolean).join(' ') || copy.value.candidate
}

function responseInitials(item) {
  const firstNameInitial = getFirstLetter(item.name)
  const lastNameInitial = getFirstLetter(item.surname)

  if (firstNameInitial && lastNameInitial && firstNameInitial !== lastNameInitial) {
    return `${firstNameInitial}${lastNameInitial}`
  }

  return getFirstTwoLetters(item.name) || getFirstTwoLetters(item.surname) || 'CV'
}

function responseMessage(item) {
  return item.message || copy.value.noCandidateMessage
}

function responseResumeUrl(item) {
  return resolveApiUrl(item.candidate_resume_url || '')
}

async function setSection(sectionId) {
  activeSection.value = normalizeSection(sectionId)
  await router.replace({
    path: route.path,
    query: { section: activeSection.value },
  })
}

async function fetchDashboardData({ silent = false } = {}) {
  if (silent) {
    if (isRefreshing.value) return
    isRefreshing.value = true
  } else {
    isLoading.value = true
    error.value = ''
  }

  try {
    const [jobsData, responsesData] = await Promise.all([
      getMyJobs(),
      getResponses(),
    ]) 

    jobs.value = Array.isArray(jobsData) ? jobsData.map(normalizeJob) : []
    responses.value = Array.isArray(responsesData) ? responsesData : []
    const loadedResponseJobIds = [...new Set(
      responses.value
        .map((item) => String(item.job_id || ''))
        .filter(Boolean),
    )]

    if (!expandedResponseJobIds.value.length) {
      expandedResponseJobIds.value = loadedResponseJobIds
    } else {
      expandedResponseJobIds.value = [...new Set([
        ...expandedResponseJobIds.value,
        ...loadedResponseJobIds,
      ])]
    }
  } catch {
    if (!silent) {
      error.value = copy.value.dashboardLoadError
      jobs.value = []
      responses.value = []
    }
  } finally {
    if (silent) {
      isRefreshing.value = false
    } else {
      isLoading.value = false
    }
  }
}

async function loadDashboard() {
  await fetchDashboardData()
  await messaging.loadConversations(route.query.application, { silent: true })
}

async function refreshDashboardSilently() {
  if (isSaving.value || deletingId.value || approvingId.value) return

  await fetchDashboardData({ silent: true })

  if (activeSection.value === 'messages') {
    await messaging.loadConversations(route.query.application, { silent: true })
  }
}

function startDashboardRealtime() {
  if (dashboardRefreshTimer.value) return

  dashboardRefreshTimer.value = window.setInterval(() => {
    refreshDashboardSilently()
  }, 5000)
}

function stopDashboardRealtime() {
  if (!dashboardRefreshTimer.value) return

  window.clearInterval(dashboardRefreshTimer.value)
  dashboardRefreshTimer.value = null
}

function resetForm() {
  editingId.value = null
  form.value = {
    ...blankForm(),
    company: employerCompanyName.value,
  }
  logoPreview.value = employerCompanyLogo.value
  bannerPreview.value = ''
  revokeLogoPreview()
  revokeBannerPreview()
}

function openCreateJobModal() {
  resetForm()
  status.value = ''
  error.value = ''
  isJobModalOpen.value = true
}

function closeJobModal() {
  if (isSaving.value) return
  isJobModalOpen.value = false
  error.value = ''
  resetForm()
}

function handleModalKeydown(event) {
  if (event.key === 'Escape' && isJobModalOpen.value) closeJobModal()
}

function addLanguage() {
  if (!canAddLanguage.value) return

  form.value.languages.push({
    name: newLanguage.value,
    level: newLanguageLevel.value,
  })
}

function removeLanguage(index) {
  form.value.languages.splice(index, 1)
}

function addLicense() {
  const value = String(newLicense.value || '').trim()
  if (!value) return
  if (!normalizeLicenses([value]).length) return
  if (form.value.licenses.some((license) => license.toLowerCase() === value.toLowerCase())) return
  form.value.licenses.push(value)
}

function removeLicense(index) {
  form.value.licenses.splice(index, 1)
}

function onLogoChange(event) {
  const file = event.target.files?.[0] || null
  form.value.logo = file
  revokeLogoPreview()

  if (!file) {
    logoPreview.value = ''
    return
  }

  objectUrl.value = URL.createObjectURL(file)
  logoPreview.value = objectUrl.value
}

function onBannerChange(event) {
  const file = event.target.files?.[0] || null
  form.value.banner = file
  revokeBannerPreview()

  if (!file) {
    bannerPreview.value = ''
    return
  }

  bannerObjectUrl.value = URL.createObjectURL(file)
  bannerPreview.value = bannerObjectUrl.value
}

async function editJob(job) {
  const country = resolveCountryMeta(job)
  const salaryParts = parseSalaryParts(job.salary)
  editingId.value = job.id
  form.value = {
    title: job.title,
    company: employerCompanyName.value || job.company,
    salary: salaryParts.amount,
    salary_currency: salaryParts.currency,
    category: job.category || inferJobCategory(job),
    employment_type: job.employment_type || job.employmentType || 'full-time',
    experience_level: job.experience_level || 'no_experience',
    education_level: job.education_level || '',
    country_key: country.countryKey || '',
    location: job.location,
    description: job.description,
    languages: normalizeLanguages(job.languages ?? job.languages_json),
    licenses: normalizeLicenses(job.licenses ?? job.licenses_json),
    has_housing: Boolean(job.has_housing),
    has_transport: Boolean(job.has_transport),
    logo: null,
    banner: null,
  }
  logoPreview.value = job.logo || employerCompanyLogo.value
  bannerPreview.value = job.banner_url || ''
  status.value = ''
  error.value = ''
  await setSection('jobs')
  isJobModalOpen.value = true
}

async function submitJob() {
  status.value = ''
  error.value = ''
  isSaving.value = true

  try {
    const {
      languages,
      licenses,
      salary_currency: _salaryCurrency,
      ...formPayload
    } = form.value
    if (!selectedCountry.value) {
      error.value = copy.value.chooseCountryError
      return
    }
    if (!form.value.category) {
      error.value = categoryRequiredError.value
      return
    }
    if (!String(form.value.company || '').trim()) {
      error.value = copy.value.companyRequired
      return
    }

    const payload = {
      ...formPayload,
      company: String(form.value.company || '').trim(),
      salary: formatSalaryValue(form.value.salary, form.value.salary_currency),
      category: form.value.category,
      country_key: selectedCountry.value.key,
      country_label: selectedCountry.value.label,
      country_flag_code: selectedCountry.value.flagCode,
      languages_json: JSON.stringify(languages),
      licenses_json: JSON.stringify(normalizeLicenses(licenses)),
    }

    if (isEditing.value) {
      await updateJob(editingId.value, payload)
      status.value = copy.value.jobUpdated
    } else {
      await createJob(payload)
      status.value = (!employerCompanyName.value && form.value.company)
        ? `${copy.value.jobSaved} ${copy.value.companyRestored}`
        : copy.value.jobSaved
    }

    await auth.loadUser({ force: true })
    resetForm()
    isJobModalOpen.value = false
    await loadDashboard()
    await setSection('jobs')
  } catch (caughtError) {
    if (caughtError instanceof ApiError) {
      if (caughtError.key === 'missing_company_profile') {
        error.value = copy.value.missingCompanyProfileError
      } else if (caughtError.key === 'subscription_required') {
        error.value = copy.value.subscriptionRequiredError
      } else if (caughtError.key === 'subscription_job_limit_reached') {
        error.value = copy.value.subscriptionJobLimitReachedError
      } else {
        error.value = copy.value.jobSaveError
      }
    } else {
      error.value = copy.value.jobSaveError
    }
  } finally {
    isSaving.value = false
  }
}

async function removeJob(job) {
  if (!window.confirm(interpolate(copy.value.deleteConfirm, { title: job.title }))) return

  deletingId.value = job.id
  status.value = ''
  error.value = ''

  try {
    await deleteJob(job.id)
    if (editingId.value === job.id) resetForm()
    status.value = copy.value.jobDeleted
    await loadDashboard()
  } catch {
    error.value = copy.value.jobDeleteError
  } finally {
    deletingId.value = null
  }
}

async function approveChat(response) {
  approvingId.value = response.id
  status.value = ''
  error.value = ''

  try {
    await approveResponseChat(response.id)
    await loadDashboard()
    await setSection('messages')
    await messaging.openConversation(response.id)
    status.value = copy.value.chatConfirmed
  } catch {
    error.value = copy.value.chatConfirmError
  } finally {
    approvingId.value = null
  }
}

function openDashboardConversation(applicationId) {
  router.replace({
    path: route.path,
    query: { section: 'messages', application: String(applicationId) },
  })
}

function toggleResponseJob(jobId) {
  const key = String(jobId)
  expandedResponseJobIds.value = expandedResponseJobIds.value.includes(key)
    ? expandedResponseJobIds.value.filter((item) => item !== key)
    : [...expandedResponseJobIds.value, key]
}

function isResponseJobExpanded(jobId) {
  return expandedResponseJobIds.value.includes(String(jobId))
}

function statusLabel(value) {
  return {
    approved: copy.value.statusApproved,
    pending: copy.value.statusPending,
    rejected: copy.value.statusRejected,
  }[value] || copy.value.statusDraft
}

watch(
  () => currentLanguage.value,
  () => {
    const previousLabels = [
      translate('employerDashboardPage.noLicense', {}, 'en'),
      translate('employerDashboardPage.noLicense', {}, 'ru'),
      translate('employerDashboardPage.noLicense', {}, 'lv'),
    ]
    if (previousLabels.includes(newLicense.value)) {
      newLicense.value = copy.value.noLicense
    }
  },
)

watch(
  () => form.value.country_key,
  (nextCountryKey, previousCountryKey) => {
    if (!nextCountryKey || nextCountryKey === previousCountryKey) return

    const availableCities = getCityOptions(nextCountryKey).map((city) => city.value)
    if (availableCities.length && !availableCities.includes(form.value.location)) {
      form.value.location = ''
    }
  },
)

watch(
  () => route.query.section,
  async (section) => {
    activeSection.value = normalizeSection(typeof section === 'string' ? section : 'jobs')

    if (activeSection.value === 'responses') {
      await fetchDashboardData({ silent: true })
    }

    if (activeSection.value === 'messages') {
      await messaging.loadConversations(route.query.application, { silent: true })
    }
  },
)

watch(
  () => route.query.application,
  async (application) => {
    if (activeSection.value !== 'messages') return
    const applicationId = Number(application)
    if (!applicationId || applicationId === messaging.activeApplicationId) return
    const exists = messaging.conversations.some((item) => item.application_id === applicationId)
    if (exists) {
      await messaging.openConversation(applicationId)
    }
  },
)

onMounted(async () => {
  window.addEventListener('keydown', handleModalKeydown)
  if (!auth.user) {
    await auth.loadUser()
  }
  resetForm()
  await loadDashboard()
  startDashboardRealtime()
  messaging.startRealtime()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleModalKeydown)
  revokeLogoPreview()
  stopDashboardRealtime()
  messaging.stopRealtime()
})
</script>

<template>
  <AppLayout>
    <DashboardShell
      :sections="localizedSections"
      :active-section="activeSection"
      :eyebrow="copy.shellEyebrow"
      :title="localizedActiveSectionLabel"
      :description="copy.shellDescription"
      :stats="localizedShellStats"
      @select-section="setSection"
      @stat-click="setSection"
    >
      <template #actions>
        <button
          v-if="activeSection === 'jobs'"
          type="button"
          class="btn-primary dashboard-cta"
          @click="openCreateJobModal"
        >
          <i class="fas fa-plus"></i>
          {{ copy.createJob }}
        </button>
      </template>

      <p v-if="status" class="status success">{{ status }}</p>
      <p v-if="error" class="status danger">{{ error }}</p>
      <p v-if="isLoading" class="state">{{ copy.loadingDashboard }}</p>

      <template v-if="!isLoading">
        <section v-if="activeSection === 'jobs'" class="jobs-grid">
          <Teleport to="body">
            <Transition name="job-modal-fade">
              <div v-if="isJobModalOpen" class="job-modal" role="dialog" aria-modal="true" @click.self="closeJobModal">
                <form class="panel form-panel job-modal__card" @submit.prevent="submitJob">
                  <button
                    type="button"
                    class="job-modal__close"
                    :aria-label="copy.closeJobModal"
                    :disabled="isSaving"
                    @click="closeJobModal"
                  >
                    <i class="fas fa-xmark"></i>
                  </button>
                  <div class="job-modal__scroll">
            <div class="panel-heading">
              <div>
                <p class="eyebrow compact">{{ isEditing ? copy.editingEyebrow : copy.newJobEyebrow }}</p>
                <h2>{{ isEditing ? copy.updateJob : copy.createJob }}</h2>
              </div>
            </div>

            <p v-if="error" class="status danger">{{ error }}</p>

            <div class="fields-row">
              <label>
                {{ copy.title }}
                <input v-model="form.title" required :placeholder="copy.titlePlaceholder" />
              </label>
              <label>
                {{ copy.company }}
                <input
                  v-model="form.company"
                  required
                  :readonly="Boolean(employerCompanyName)"
                  :disabled="Boolean(employerCompanyName)"
                  :placeholder="copy.company"
                />
              </label>
            </div>

            <div class="fields-row">
              <label>
                {{ copy.salaryAmount }}
                <input v-model="form.salary" required :placeholder="copy.salaryAmountPlaceholder" />
              </label>
              <label>
                {{ copy.salaryCurrency }}
                <BaseDropdown
                  v-model="form.salary_currency"
                  :aria-label="copy.salaryCurrency"
                  full-width
                  :options="salaryCurrencyOptions"
                />
              </label>
            </div>

            <div class="fields-row">
              <label>
                {{ copy.country }}
                <BaseDropdown
                v-model="form.country_key"
                :aria-label="copy.countryAria"
                full-width
                :options="countryDropdownOptions"
                />
              </label>
              <label>
                {{ copy.city }}
                <BaseDropdown
                v-model="form.location"
                  :aria-label="copy.cityAria"
                  full-width
                  :options="cityOptions"
                />
              </label>
            </div>
            <label>
              {{ categoryFieldLabel }}
              <BaseDropdown
                v-model="form.category"
                :aria-label="categoryFieldLabel"
                :placeholder="categoryPlaceholder"
                full-width
                :options="localizedCategoryOptions"
              />
            </label>
            
            <div class="fields-row">
              <label>
                {{ copy.requiredLanguage }}
                <BaseDropdown
                  v-model="newLanguage"
                  :aria-label="copy.requiredLanguage"
                  full-width
                  :options="localizedLanguageOptions"
                />
              </label>

              <label>
                {{ copy.requiredLanguageLevel }}
                <BaseDropdown
                  v-model="newLanguageLevel"
                  :aria-label="copy.requiredLanguageLevel"
                  full-width
                  :options="languageLevelOptions"
                />
              </label>
            </div>
            <button
              type="button"
              class="btn-secondary"
              :disabled="!canAddLanguage"
              @click="addLanguage"
            >
              {{ copy.addLanguage }}
            </button>
            <div class="section">
              <div class="chips">
                <span
                  v-for="(language, index) in form.languages"
                  :key="`${language.name}-${language.level}-${index}`"
                  class="chip"
                >
                  <span>{{ language.name }}</span>
                  <b>{{ language.level }}</b>
                  <button type="button" @click="removeLanguage(index)">×</button>
                </span>
              </div>
            </div>
            
            <div class="upload-grid">
              <label class="upload-card">
                <span class="upload-title">{{ copy.vacancyPhoto }}</span>
                <span class="upload-copy">{{ copy.vacancyPhotoHint }}</span>
                <span class="upload-button">{{ copy.chooseFile }}</span>
                <span class="upload-filename">{{ form.logo?.name || copy.noFileSelected }}</span>
                <input type="file" accept="image/*" @change="onLogoChange" />
              </label>
              
              <div class="preview-card">
                <img v-if="logoPreview" :src="logoPreview" :alt="copy.vacancyPreview" />
                <div v-else class="preview-placeholder">
                  <i class="fas fa-image"></i>
                  <span>{{ copy.vacancyPreview }}</span>
                </div>
              </div>
            </div>

            <div class="upload-grid">
              <label class="upload-card">
                <span class="upload-title">{{ copy.vacancyBanner }}</span>
                <span class="upload-copy">{{ copy.vacancyBannerHint }}</span>
                <span class="upload-button">{{ copy.chooseFile }}</span>
                <span class="upload-filename">{{ form.banner?.name || copy.noFileSelected }}</span>
                <input type="file" accept="image/*" @change="onBannerChange" />
              </label>

              <div class="preview-card preview-card--banner">
                <img v-if="bannerPreview" :src="bannerPreview" :alt="copy.vacancyBannerPreview" />
                <div v-else class="preview-placeholder">
                  <i class="fas fa-panorama"></i>
                  <span>{{ copy.vacancyBannerPreview }}</span>
                </div>
              </div>
            </div>
            <div class="attribute-grid">
              <label class="attribute-card" :class="{ 'attribute-card--active': form.has_housing }">
                <input v-model="form.has_housing" type="checkbox" />
                <i class="fas fa-house"></i>
                <span>
                  <strong>{{ copy.hasHousing }}</strong>
                  <small>{{ copy.hasHousingHint }}</small>
                </span>
              </label>

              <label class="attribute-card" :class="{ 'attribute-card--active': form.has_transport }">
                <input v-model="form.has_transport" type="checkbox" />
                <i class="fas fa-bus"></i>
                <span>
                  <strong>{{ copy.hasTransport }}</strong>
                  <small>{{ copy.hasTransportHint }}</small>
                </span>
              </label>
            </div>
            <div class="section">
              <label class="section-label">{{ copy.licenses }}</label>

              <div class="chips">
                <span v-for="(license, index) in form.licenses" :key="`${license}-${index}`" class="chip">
                  <span>{{ license }}</span>
                  <button type="button" @click="removeLicense(index)">×</button>
                </span>
              </div>

              <div class="inline-add inline-add--dropdown">
                <BaseDropdown
                  v-model="newLicense"
                  :aria-label="copy.licenseAria"
                  full-width
                  :options="localizedLicenseOptions"
                />
                <button type="button" class="btn-secondary" @click="addLicense">{{ copy.add }}</button>
              </div>
            </div>
            <div class="field-grid">
              <div class="field-group field-group--full">
                <span class="field-label">{{ copy.employmentType }}</span>
                <div class="stack-options">
                  <button
                    v-for="option in localizedEmploymentTypeOptions"
                    :key="option.id"
                    type="button"
                    class="filter-chip"
                    :class="{ 'filter-chip--active': form.employment_type === option.id }"
                    @click="form.employment_type = option.id"
                    >
                    {{ option.label }}
                  </button>
                </div>
              </div>
            </div>

            <div class="field-grid">
              <label>
                {{ copy.minimumExperience }}
                <BaseDropdown
                  v-model="form.experience_level"
                  :aria-label="copy.minimumExperience"
                  full-width
                  :options="localizedExperienceOptions"
                />
              </label>

              <label>
                {{ copy.educationRequirement }}
                <BaseDropdown
                  v-model="form.education_level"
                  :aria-label="copy.educationRequirement"
                  full-width
                  :options="localizedEducationOptions"
                />
              </label>
            </div>

            <label>
              {{ copy.description }}
              <textarea v-model="form.description" rows="6" required :placeholder="copy.descriptionPlaceholder"></textarea>
            </label>



            <div class="form-actions">
              <button class="btn-primary" type="submit" :disabled="isSaving">{{ localizedSubmitLabel }}</button>
            </div>
                  </div>
                </form>
              </div>
            </Transition>
          </Teleport>

          <section class="panel jobs-panel">
            <div class="panel-heading">
              <div>
                <p class="eyebrow compact">{{ copy.publications }}</p>
                <h2>{{ copy.myJobs }}</h2>
              </div>
            </div>

            <p v-if="!jobs.length" class="state">{{ copy.noJobsYet }}</p>

            <article v-for="job in jobs" :key="job.id" class="job-row">
              <div class="company-logo" :style="{ background: job.color }">
                <img v-if="job.logo" :src="job.logo" :alt="job.company" />
                <span v-else>{{ job.initials }}</span>
              </div>

              <div class="job-body">
                <div class="job-top">
                  <div class="job-heading">
                    <h3>{{ job.title }}</h3>
                    <div class="job-company">{{ job.company }} · {{ job.location }}</div>
                  </div>
                  <span class="badge" :class="job.status">{{ statusLabel(job.status) }}</span>
                </div>

                <div class="job-tags">
                  <span v-if="job.has_housing" class="job-tag"><i class="fas fa-house"></i> {{ copy.housingTag }}</span>
                  <span v-if="job.has_transport" class="job-tag"><i class="fas fa-bus"></i> {{ copy.transportTag }}</span>
                  <span v-for="language in job.languages" :key="`${job.id}-${language.name}-${language.level}`" class="job-tag">
                    <i class="fas fa-language"></i> {{ language.name }} · {{ language.level }}
                  </span>
                  <span v-for="license in job.licenses" :key="`${job.id}-${license}`" class="job-tag">
                    <i class="fas fa-id-card"></i> {{ license }}
                  </span>
                </div>

                <p class="job-description">{{ job.description }}</p>

                <div class="job-footer">
                  <strong class="job-salary">{{ job.salary }}</strong>
                  <div class="job-buttons">
                    <RouterLink v-if="job.status === 'approved'" :to="`/jobs/${job.id}`" class="text-button">{{ copy.open }}</RouterLink>
                    <button type="button" class="text-button" @click="editJob(job)">{{ copy.edit }}</button>
                    <button type="button" class="text-button danger" :disabled="deletingId === job.id" @click="removeJob(job)">
                      {{ deletingId === job.id ? copy.deleting : copy.delete }}
                    </button>
                  </div>
                </div>
              </div>
            </article>
          </section>
        </section>

        <section v-if="activeSection === 'responses'" class="panel responses-panel">
          <div class="panel-heading responses-heading">
            <div>
              <p class="eyebrow compact">{{ copy.responsesEyebrow }}</p>
              <h2>{{ copy.candidatesByJobs }}</h2>
              <p class="responses-subtitle">{{ copy.responsesSubtitle }}</p>
            </div>
          </div>

          <p v-if="!responses.length" class="state">{{ copy.noResponsesYet }}</p>

          <template v-else>

            <div v-if="responseMatchSummary.length" class="response-summary">
              <span
                v-for="item in responseMatchSummary"
                :key="item.key"
                class="response-summary__pill"
                :class="`response-summary__pill--${item.key}`"
              >
                {{ item.label }} · {{ item.count }}
              </span>
            </div>

            <div class="responses-list">
              <article
                v-for="group in groupedResponses"
                :key="group.job_id"
                class="response-vacancy-card"
              >
                <div class="response-vacancy-card__top">
                  <div class="response-vacancy-card__copy">
                    <h3>{{ group.job_title }}</h3>
                    <div class="response-vacancy-card__meta">
                      <span><i class="fas fa-location-dot"></i>{{ group.job_location || copy.locationMissing }}</span>
                      <span><i class="fas fa-euro-sign"></i>{{ group.job_salary || copy.salaryNegotiable }}</span>
                      <span><i class="fas fa-users"></i>{{ localizedResponseCount(group.responses.length) }}</span>
                    </div>
                  </div>

                  <button
                    type="button"
                    class="response-vacancy-card__toggle"
                    @click="toggleResponseJob(group.job_id)"
                  >
                    {{ isResponseJobExpanded(group.job_id) ? copy.hideResponses : copy.showResponses }}
                  </button>
                </div>

                <div class="response-inline-pills">
                  <span
                    v-for="item in group.badges"
                    :key="`${group.job_id}-${item.key}`"
                    class="response-summary__pill"
                    :class="`response-summary__pill--${item.key}`"
                  >
                    {{ item.label }} · {{ item.count }}
                  </span>

                  <span
                    v-for="item in group.responses"
                    :key="`pill-${item.id}`"
                    class="response-candidate-pill"
                    :class="`response-candidate-pill--${item.matchAnalysis.meta.key}`"
                  >
                    {{ responseFullName(item) }} · {{ item.matchAnalysis.score }}
                  </span>
                </div>

                <div v-if="isResponseJobExpanded(group.job_id)" class="response-candidate-list">
                  <article
                    v-for="item in group.responses"
                    :key="item.id"
                    class="response-candidate-row"
                  >
                    <div class="response-avatar">
                      <img
                        v-if="responseAvatar(item)"
                        :src="responseAvatar(item)"
                        :alt="responseFullName(item)"
                        @error="markAvatarBroken(item)"
                      />
                      <span v-else>{{ responseInitials(item) }}</span>
                    </div>

                    <div class="response-candidate-row__body">
                      <div class="response-header">
                        <div class="response-title-block">
                          <p class="response-kicker">{{ copy.candidateKicker }}</p>
                          <h3>{{ responseFullName(item) }}</h3>
                          <p class="response-match-profile">
                            <span class="response-traffic-dot" :class="`response-traffic-dot--${item.matchAnalysis.trafficLight}`"></span>
                            {{ item.matchAnalysis.profile }}
                          </p>
                        </div>

                        <div class="response-score-chip" :class="`response-score-chip--${item.matchAnalysis.meta.key}`">
                          {{ item.matchAnalysis.meta.label }} · {{ item.matchAnalysis.score }}
                        </div>
                      </div>

                      <p class="response-message">{{ responseMessage(item) }}</p>

                      <div class="response-details">
                        <span v-if="item.phone" class="response-detail">
                          <i class="fas fa-phone"></i>
                          {{ item.phone }}
                        </span>
                        <span v-if="item.email" class="response-detail">
                          <i class="fas fa-envelope"></i>
                          {{ item.email }}
                        </span>
                        <span v-if="item.nationality" class="response-detail">
                          <i class="fas fa-globe"></i>
                          {{ item.nationality }}
                        </span>
                        <a
                          v-if="item.candidate_resume_url"
                          class="response-detail response-resume-link"
                          :href="responseResumeUrl(item)"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <i class="fas fa-file-pdf"></i>
                          {{ copy.openResumePdf }}
                        </a>
                        <a
                          v-if="item.candidate_resume_url"
                          class="response-detail response-resume-link"
                          :href="responseResumeUrl(item)"
                          :download="item.candidate_resume_name || true"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <i class="fas fa-download"></i>
                          {{ copy.downloadResumePdf }}
                        </a>
                      </div>

                      <div v-if="item.matchAnalysis.failedGates.length" class="response-failed-gates">
                        <span
                          v-for="(gate, gateIndex) in item.matchAnalysis.failedGates"
                          :key="`${item.id}-gate-${gateIndex}`"
                          class="response-failed-gates__pill"
                        >
                          {{ gate }}
                        </span>
                      </div>

                      <div class="response-breakdown">
                        <article
                          v-for="part in item.matchAnalysis.breakdown"
                          :key="`${item.id}-${part.key}`"
                          class="response-breakdown-card"
                          :class="`response-breakdown-card--${part.meta.key}`"
                        >
                          <div class="response-breakdown-card__head">
                            <span>{{ part.label }}</span>
                            <strong>{{ part.score }}</strong>
                          </div>

                          <p
                            v-for="(detail, detailIndex) in part.details"
                            :key="`${item.id}-${part.key}-${detailIndex}`"
                            class="response-breakdown-card__detail"
                          >
                            {{ detail }}
                          </p>
                        </article>
                      </div>
                    </div>

                    <div class="response-actions">
                      <span class="badge response-status" :class="item.chat_approved ? 'approved' : 'pending'">
                        {{ item.chat_approved ? copy.chatActive : copy.chatWaiting }}
                      </span>

                      <button
                        v-if="!item.chat_approved"
                        type="button"
                        class="response-action-button"
                        :disabled="approvingId === item.id"
                        @click="approveChat(item)"
                      >
                        <i class="fas fa-message"></i>
                        {{ approvingId === item.id ? copy.confirming : copy.confirmChat }}
                      </button>

                      <button
                        v-else
                        type="button"
                        class="response-action-button"
                        @click="openDashboardConversation(item.id)"
                      >
                        <i class="fas fa-arrow-up-right-from-square"></i>
                        {{ copy.openMessages }}
                      </button>
                    </div>
                  </article>
                </div>
              </article>
            </div>
          </template>
        </section>

        <section v-if="activeSection === 'messages'" class="message-shell">
          <MessagesPanel embedded @open="openDashboardConversation" />
        </section>

        <section v-if="activeSection === 'pricing'" class="pricing-layout">
          <article class="panel current-plan">
            <div class="panel-heading">
              <div>
                <p class="eyebrow compact">{{ copy.currentPlan }}</p>
                <h2>{{ currentPlanName }}</h2>
              </div>
              <span v-if="hasActiveSubscription" class="plan-badge">{{ copy.active }}</span>
            </div>

            <div class="current-plan-grid">
              <div class="current-plan-card">
                <span>{{ copy.cost }}</span>
                <strong>{{ currentPlanPrice }}</strong>
              </div>
              <div class="current-plan-card">
                <span>{{ copy.limit }}</span>
                <strong>{{ currentPlanLimit }}</strong>
              </div>
              <div class="current-plan-card">
                <span>{{ copy.renewal }}</span>
                <strong>{{ currentPlanExpires }}</strong>
              </div>
            </div>
          </article>

          <section class="pricing-grid">
            <article
              v-for="plan in localizedPlans"
              :key="plan.id"
              class="plan-card"
              :class="{ 'plan-card--current': plan.id === currentPlanId }"
            >
              <div class="plan-card__top">
                <div>
                  <p class="eyebrow compact">{{ plan.id === currentPlanId ? copy.yourPlan : copy.available }}</p>
                  <h3>{{ plan.name }}</h3>
                </div>
                <span v-if="plan.id === currentPlanId" class="plan-badge">{{ copy.current }}</span>
              </div>

              <strong class="plan-price">{{ plan.price }}</strong>
              <p class="plan-limit">{{ plan.vacancies }}</p>
              <p class="pricing-copy">{{ plan.description }}</p>

              <ul class="plan-features">
                <li v-for="feature in plan.features" :key="feature">
                  <i class="fas fa-check"></i>
                  <span>{{ feature }}</span>
                </li>
              </ul>

              <button type="button" :class="plan.id === currentPlanId ? 'btn-secondary' : 'btn-primary'">
                {{ plan.id === currentPlanId ? copy.renew : copy.choosePlan }}
              </button>
            </article>
          </section>
        </section>
      </template>
    </DashboardShell>
  </AppLayout>
</template>

<style scoped src="../styles/pages/employer-dashboard.css"></style>
