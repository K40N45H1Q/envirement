<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/i18n'
import AppLayout from '@/components/AppLayout.vue'
import BaseDropdown from '@/components/BaseDropdown.vue'
import DashboardShell from '@/components/dashboard/DashboardShell.vue'
import MessagesPanel from '@/components/messages/MessagesPanel.vue'
import {
  approveResponseChat,
  createJob,
  deleteJob,
  getMyJobs,
  getResponses,
  updateJob,
} from '@/api/jobs'
import { useMessagingStore } from '@/stores/messaging'
import {
  getLanguageOptions,
  languageLevelOptions,
  licenseOptions,
  normalizeLanguages,
  normalizeLicenses,
} from '@/utils/jobRequirements'
import { countryByKey, countryDropdownOptions, resolveCountryMeta } from '@/utils/countries'
import { analyzeCandidateMatch } from '@/utils/matchScore'
import { normalizeJob } from '@/utils/jobs'

const route = useRoute()
const router = useRouter()
const messaging = useMessagingStore()
const { language: currentLanguage } = useI18n()

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

const currentPlanId = 'standard'

const isEnglish = computed(() => currentLanguage.value === 'en')
const copy = computed(() => (
  isEnglish.value
    ? {
      sections: { jobs: 'Jobs', responses: 'Applications', messages: 'Messages', pricing: 'Plans' },
      stats: { jobs: 'Total jobs', published: 'Published', responses: 'Applications', conversations: 'Conversations' },
      fallbackSection: 'Jobs',
      saving: 'Saving...',
      saveChanges: 'Save changes',
      saveJob: 'Save vacancy',
      failLabel: 'Not a fit',
      activeJobs: 'Active vacancies',
      totalResponses: 'Total applications',
      strongMatch: 'Strong match',
      chatActive: 'Active chats',
      candidate: 'Candidate',
      noCandidateMessage: 'The candidate applied without an extra message.',
      dashboardLoadError: 'Failed to load the employer dashboard.',
      chooseCountryError: 'Choose the vacancy country.',
      jobUpdated: 'Vacancy updated.',
      jobSaved: 'Vacancy saved.',
      jobSaveError: 'Failed to save the vacancy.',
      deleteConfirm: 'Delete vacancy "{title}"?',
      jobDeleted: 'Vacancy deleted.',
      jobDeleteError: 'Failed to delete the vacancy.',
      chatConfirmed: 'Chat approved and opened in messages.',
      chatConfirmError: 'Failed to approve the chat.',
      statusApproved: 'Published',
      statusPending: 'In review',
      statusRejected: 'Rejected',
      statusDraft: 'Draft',
      shellEyebrow: 'Employer dashboard',
      shellDescription: 'Workspace for vacancies, applications, messages, and plans.',
      loadingDashboard: 'Loading dashboard...',
      editingEyebrow: 'Editing',
      newJobEyebrow: 'New vacancy',
      updateJob: 'Update vacancy',
      createJob: 'Create vacancy',
      title: 'Title',
      titlePlaceholder: 'Electrician',
      company: 'Company',
      salary: 'Salary',
      country: 'Country',
      countryAria: 'Vacancy country',
      location: 'Location',
      locationPlaceholder: 'Berlin, Germany',
      selectedCountry: 'Selected country',
      notSelected: 'Not selected',
      vacancyPhoto: 'Vacancy photo',
      vacancyPhotoHint: 'PNG, JPG, or WEBP',
      chooseFile: 'Choose file',
      noFileSelected: 'No file selected',
      vacancyPreview: 'Vacancy preview',
      hasHousing: 'Housing included',
      hasHousingHint: 'Show accommodation on the vacancy card',
      hasTransport: 'Transport included',
      hasTransportHint: 'Show shuttle or company transport on the vacancy card',
      description: 'Description',
      descriptionPlaceholder: 'Responsibilities, requirements, and working conditions',
      vacancyLanguages: 'Languages for the vacancy',
      requiredLanguage: 'Required language',
      requiredLanguageLevel: 'Required language level',
      addLanguage: 'Add language',
      licenses: 'Licences and certificates',
      licenseAria: 'Driving licence, certificate, or permit',
      add: 'Add',
      reset: 'Reset',
      publications: 'Publications',
      myJobs: 'My vacancies',
      noJobsYet: 'No vacancies yet.',
      housingTag: 'Housing included',
      transportTag: 'Transport included',
      open: 'Open',
      edit: 'Edit',
      deleting: 'Deleting...',
      delete: 'Delete',
      responsesEyebrow: 'Applications',
      candidatesByJobs: 'Candidates by vacancy',
      responsesSubtitle: 'Review candidates quickly, approve chats, and move straight into conversation.',
      noResponsesYet: 'No applications yet.',
      locationMissing: 'Location not specified',
      salaryNegotiable: 'Negotiable',
      responsesCount: '{count} applications',
      hideResponses: 'Hide applications',
      showResponses: 'View applications',
      candidateKicker: 'Candidate',
      chatWaiting: 'Awaiting approval',
      confirming: 'Approving...',
      confirmChat: 'Approve chat',
      openMessages: 'Open messages',
      currentPlan: 'Current plan',
      active: 'Active',
      cost: 'Price',
      limit: 'Limit',
      renewal: 'Renewal',
      in30Days: 'In 30 days',
      yourPlan: 'Your plan',
      available: 'Available',
      current: 'Current',
      renew: 'Renew',
      choosePlan: 'Choose plan',
    }
    : {
      sections: { jobs: 'Вакансии', responses: 'Отклики', messages: 'Сообщения', pricing: 'Тарифы' },
      stats: { jobs: 'Всего вакансий', published: 'Опубликовано', responses: 'Откликов', conversations: 'Диалогов' },
      fallbackSection: 'Вакансии',
      saving: 'Сохранение...',
      saveChanges: 'Сохранить изменения',
      saveJob: 'Сохранить вакансию',
      failLabel: 'Не соответствует',
      activeJobs: 'Активных вакансий',
      totalResponses: 'Всего откликов',
      strongMatch: 'Сильное совпадение',
      chatActive: 'Чат активен',
      candidate: 'Кандидат',
      noCandidateMessage: 'Кандидат отправил отклик без дополнительного сообщения.',
      dashboardLoadError: 'Не удалось загрузить кабинет работодателя.',
      chooseCountryError: 'Выберите страну вакансии.',
      jobUpdated: 'Вакансия обновлена.',
      jobSaved: 'Вакансия сохранена.',
      jobSaveError: 'Не удалось сохранить вакансию.',
      deleteConfirm: 'Удалить вакансию "{title}"?',
      jobDeleted: 'Вакансия удалена.',
      jobDeleteError: 'Не удалось удалить вакансию.',
      chatConfirmed: 'Чат подтверждён и открыт в сообщениях.',
      chatConfirmError: 'Не удалось подтвердить чат.',
      statusApproved: 'Опубликована',
      statusPending: 'На модерации',
      statusRejected: 'Отклонена',
      statusDraft: 'Черновик',
      shellEyebrow: 'Личный кабинет работодателя',
      shellDescription: 'Рабочее пространство для вакансий, откликов, сообщений и тарифа.',
      loadingDashboard: 'Загрузка кабинета...',
      editingEyebrow: 'Редактирование',
      newJobEyebrow: 'Новая вакансия',
      updateJob: 'Обновить вакансию',
      createJob: 'Создать вакансию',
      title: 'Название',
      titlePlaceholder: 'Электрик',
      company: 'Компания',
      salary: 'Зарплата',
      country: 'Страна',
      countryAria: 'Страна вакансии',
      location: 'Локация',
      locationPlaceholder: 'Берлин, Германия',
      selectedCountry: 'Выбранная страна',
      notSelected: 'Не выбрана',
      vacancyPhoto: 'Фото вакансии',
      vacancyPhotoHint: 'PNG, JPG или WEBP',
      chooseFile: 'Выбрать файл',
      noFileSelected: 'Файл не выбран',
      vacancyPreview: 'Превью вакансии',
      hasHousing: 'Есть жильё',
      hasHousingHint: 'Показывать проживание в карточке вакансии',
      hasTransport: 'Есть транспорт',
      hasTransportHint: 'Показывать наличие трансфера или служебного транспорта',
      description: 'Описание',
      descriptionPlaceholder: 'Обязанности, требования и условия работы',
      vacancyLanguages: 'Языки для вакансии',
      requiredLanguage: 'Требуемый язык',
      requiredLanguageLevel: 'Требуемый уровень языка',
      addLanguage: 'Добавить язык',
      licenses: 'Права, лицензии и сертификаты',
      licenseAria: 'Категория прав, лицензия или сертификат',
      add: 'Добавить',
      reset: 'Сбросить',
      publications: 'Публикации',
      myJobs: 'Мои вакансии',
      noJobsYet: 'Вакансий пока нет.',
      housingTag: 'Есть жильё',
      transportTag: 'Есть транспорт',
      open: 'Открыть',
      edit: 'Редактировать',
      deleting: 'Удаление...',
      delete: 'Удалить',
      responsesEyebrow: 'Отклики',
      candidatesByJobs: 'Кандидаты по вакансиям',
      responsesSubtitle: 'Быстро оценивайте кандидатов, подтверждайте чат и переходите к общению.',
      noResponsesYet: 'Откликов пока нет.',
      locationMissing: 'Локация не указана',
      salaryNegotiable: 'По договорённости',
      responsesCount: '{count} откликов',
      hideResponses: 'Скрыть отклики',
      showResponses: 'Смотреть отклики',
      candidateKicker: 'Кандидат',
      chatWaiting: 'Ждёт подтверждения',
      confirming: 'Подтверждаем...',
      confirmChat: 'Подтвердить чат',
      openMessages: 'Открыть сообщения',
      currentPlan: 'Текущий тариф',
      active: 'Активен',
      cost: 'Стоимость',
      limit: 'Лимит',
      renewal: 'Продление',
      in30Days: 'Через 30 дней',
      yourPlan: 'Ваш пакет',
      available: 'Доступно',
      current: 'Текущий',
      renew: 'Продлить',
      choosePlan: 'Выбрать тариф',
    }
))

const interpolate = (template, params = {}) => String(template).replace(/\{(\w+)\}/g, (_, key) => String(params[key] ?? ''))

const sections = [
  { id: 'jobs', label: 'Вакансии', icon: 'fas fa-briefcase', to: '/employer-dashboard?section=jobs' },
  { id: 'responses', label: 'Отклики', icon: 'fas fa-user-check', to: '/employer-dashboard?section=responses' },
  { id: 'messages', label: 'Сообщения', icon: 'fas fa-message', to: '/employer-dashboard?section=messages' },
  { id: 'pricing', label: 'Тарифы', icon: 'fas fa-credit-card', to: '/employer-dashboard?section=pricing' },
]

const localizedPlans = computed(() => plans.map((plan) => ({
  ...plan,
  vacancies: plan.id === 'basic'
    ? (isEnglish.value ? '1 job' : '1 вакансия')
    : plan.id === 'standard'
      ? (isEnglish.value ? '5 jobs' : '5 вакансий')
      : (isEnglish.value ? '20 jobs' : '20 вакансий'),
  description: plan.id === 'basic'
    ? (isEnglish.value ? 'For occasional hiring and one-off publications.' : 'Для точечного найма и редких публикаций.')
    : plan.id === 'standard'
      ? (isEnglish.value ? 'The best balance for an active employer.' : 'Лучший баланс для активного работодателя.')
      : (isEnglish.value ? 'For teams with a constant hiring pipeline.' : 'Для команд с постоянным потоком найма.'),
  features: plan.id === 'basic'
    ? (isEnglish.value ? ['30 days online', 'Basic vacancy card', 'Candidate applications'] : ['30 дней публикации', 'Базовая карточка вакансии', 'Отклики кандидатов'])
    : plan.id === 'standard'
      ? (isEnglish.value ? ['30 days online', 'Employer dashboard', 'Candidate comparison'] : ['30 дней публикации', 'Кабинет работодателя', 'Сравнение кандидатов'])
      : (isEnglish.value ? ['Priority listing', 'Advanced analytics', 'Priority support'] : ['Приоритетная выдача', 'Расширенная аналитика', 'Приоритетная поддержка']),
})))

const localizedSections = computed(() => sections.map((section) => ({
  ...section,
  label: copy.value.sections[section.id] || section.label,
  to: `${route.path}?section=${section.id}`,
})))

const localizedLanguageOptions = computed(() => getLanguageOptions())
const validSectionIds = sections.map((section) => section.id)
const normalizeSection = (section) => (validSectionIds.includes(section) ? section : 'jobs')

const blankForm = () => ({
  title: '',
  company: '',
  salary: '',
  country_key: '',
  location: '',
  description: '',
  languages: [],
  licenses: [],
  has_housing: false,
  has_transport: false,
  logo: null,
})

const activeSection = ref(normalizeSection(typeof route.query.section === 'string' ? route.query.section : 'jobs'))
const jobs = ref([])
const responses = ref([])
const isLoading = ref(false)
const isRefreshing = ref(false)
const isSaving = ref(false)
const deletingId = ref(null)
const approvingId = ref(null)
const editingId = ref(null)
const form = ref(blankForm())
const status = ref('')
const error = ref('')
const logoPreview = ref('')
const objectUrl = ref('')
const newLanguage = ref(localizedLanguageOptions.value[0]?.value || 'English')
const newLanguageLevel = ref(languageLevelOptions[2].value)
const newLicense = ref(licenseOptions[4].value)
const expandedResponseJobIds = ref([])
const brokenAvatars = ref(new Set())
const dashboardRefreshTimer = ref(null)

const conversations = computed(() => messaging.conversations)
const isEditing = computed(() => editingId.value !== null)
const approvedCount = computed(() => jobs.value.filter((job) => job.status === 'approved').length)
const canAddLanguage = computed(() => !form.value.languages.some((language) => (
  language.name === newLanguage.value && language.level === newLanguageLevel.value
)))
const currentPlan = computed(() => localizedPlans.value.find((plan) => plan.id === currentPlanId) || localizedPlans.value[1])
const selectedCountry = computed(() => countryByKey[form.value.country_key] || null)
const scoredResponses = computed(() => responses.value.map((item) => ({
  ...item,
  matchAnalysis: analyzeCandidateMatch(item, item),
})))

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
        { key: 'strong', label: 'Strong', count: group.counts.strong },
        { key: 'good', label: 'Good', count: group.counts.good },
        { key: 'partial', label: 'Partial', count: group.counts.partial },
        { key: 'weak', label: 'Weak', count: group.counts.weak },
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
    { key: 'strong', label: 'Strong', count: counters.strong },
    { key: 'good', label: 'Good', count: counters.good },
    { key: 'partial', label: 'Partial', count: counters.partial },
    { key: 'weak', label: 'Weak', count: counters.weak },
    { key: 'fail', label: copy.value.failLabel, count: counters.fail },
  ].filter((item) => item.count > 0)
})

const localizedShellStats = computed(() => ([
  { value: jobs.value.length, label: copy.value.stats.jobs },
  { value: approvedCount.value, label: copy.value.stats.published },
  { value: responses.value.length, label: copy.value.stats.responses },
  { value: conversations.value.length, label: copy.value.stats.conversations },
]))
const localizedActiveSectionLabel = computed(() => localizedSections.value.find((item) => item.id === activeSection.value)?.label || copy.value.fallbackSection)
const localizedSubmitLabel = computed(() => (isSaving.value ? copy.value.saving : (isEditing.value ? copy.value.saveChanges : copy.value.saveJob)))
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
  form.value = blankForm()
  logoPreview.value = ''
  revokeLogoPreview()
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

async function editJob(job) {
  const country = resolveCountryMeta(job)
  editingId.value = job.id
  form.value = {
    title: job.title,
    company: job.company,
    salary: job.salary,
    country_key: country.countryKey || '',
    location: job.location,
    description: job.description,
    languages: normalizeLanguages(job.languages ?? job.languages_json),
    licenses: normalizeLicenses(job.licenses ?? job.licenses_json),
    has_housing: Boolean(job.has_housing),
    has_transport: Boolean(job.has_transport),
    logo: null,
  }
  logoPreview.value = job.logo || ''
  status.value = ''
  error.value = ''
  await setSection('jobs')
}

async function submitJob() {
  status.value = ''
  error.value = ''
  isSaving.value = true

  try {
    const { languages, licenses, ...formPayload } = form.value
    if (!selectedCountry.value) {
      error.value = copy.value.chooseCountryError
      return
    }

    const payload = {
      ...formPayload,
      country_key: selectedCountry.value.key,
      country_label: selectedCountry.value.label,
      country_flag_code: selectedCountry.value.flagCode,
      languages_json: JSON.stringify(languages),
      licenses_json: JSON.stringify(licenses),
    }

    if (isEditing.value) {
      await updateJob(editingId.value, payload)
      status.value = copy.value.jobUpdated
    } else {
      await createJob(payload)
      status.value = copy.value.jobSaved
    }

    resetForm()
    await loadDashboard()
    await setSection('jobs')
  } catch {
    error.value = copy.value.jobSaveError
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
  await loadDashboard()
  startDashboardRealtime()
  messaging.startRealtime()
})

onBeforeUnmount(() => {
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
    >
      <p v-if="status" class="status success">{{ status }}</p>
      <p v-if="error" class="status danger">{{ error }}</p>
      <p v-if="isLoading" class="state">{{ copy.loadingDashboard }}</p>

      <template v-if="!isLoading">
        <section v-if="activeSection === 'jobs'" class="jobs-grid">
          <form class="panel form-panel" @submit.prevent="submitJob">
            <div class="panel-heading">
              <div>
                <p class="eyebrow compact">{{ isEditing ? copy.editingEyebrow : copy.newJobEyebrow }}</p>
                <h2>{{ isEditing ? copy.updateJob : copy.createJob }}</h2>
              </div>
            </div>

            <div class="field-grid">
              <label>
                {{ copy.title }}
                <input v-model="form.title" required :placeholder="copy.titlePlaceholder" />
              </label>
              <label>
                {{ copy.company }}
                <input v-model="form.company" required placeholder="Build Solutions GmbH" />
              </label>
            </div>

            <div class="field-grid">
              <label>
                {{ copy.salary }}
                <input v-model="form.salary" required placeholder="2 200 - 2 800 EUR" />
              </label>
              <label>
                {{ copy.country }}
                <BaseDropdown
                  v-model="form.country_key"
                  :aria-label="copy.countryAria"
                  full-width
                  :options="countryDropdownOptions"
                />
              </label>
            </div>

            <div class="field-grid">
              <label>
                {{ copy.location }}
                <input v-model="form.location" required :placeholder="copy.locationPlaceholder" />
              </label>
              <div class="field-hint">
                <span>{{ copy.selectedCountry }}</span>
                <strong>{{ selectedCountry?.label || copy.notSelected }}</strong>
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

            <label>
              {{ copy.description }}
              <textarea v-model="form.description" rows="6" required :placeholder="copy.descriptionPlaceholder"></textarea>
            </label>

            <div class="section">
              <label class="section-label">{{ copy.vacancyLanguages }}</label>

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

              <div class="field-grid">
                <BaseDropdown
                  v-model="newLanguage"
                  :aria-label="copy.requiredLanguage"
                  full-width
                  :options="localizedLanguageOptions"
                />

                <BaseDropdown
                  v-model="newLanguageLevel"
                  :aria-label="copy.requiredLanguageLevel"
                  full-width
                  :options="languageLevelOptions"
                />
              </div>

              <button
                type="button"
                class="btn-secondary btn-secondary--compact"
                :disabled="!canAddLanguage"
                @click="addLanguage"
              >
                {{ copy.addLanguage }}
              </button>
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
                  :options="licenseOptions"
                />
                <button type="button" class="btn-secondary btn-secondary--compact" @click="addLicense">{{ copy.add }}</button>
              </div>
            </div>

            <div class="form-actions">
              <button class="btn-primary" type="submit" :disabled="isSaving">{{ localizedSubmitLabel }}</button>
              <button v-if="isEditing" class="btn-secondary" type="button" @click="resetForm">{{ copy.reset }}</button>
            </div>
          </form>

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
            <div class="response-stats">
              <article v-for="item in localizedResponseStats" :key="item.label" class="response-stat-card">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </article>
            </div>

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
                <h2>{{ currentPlan.name }}</h2>
              </div>
              <span class="plan-badge">{{ copy.active }}</span>
            </div>

            <div class="current-plan-grid">
              <div class="current-plan-card">
                <span>{{ copy.cost }}</span>
                <strong>{{ currentPlan.price }}</strong>
              </div>
              <div class="current-plan-card">
                <span>{{ copy.limit }}</span>
                <strong>{{ currentPlan.vacancies }}</strong>
              </div>
              <div class="current-plan-card">
                <span>{{ copy.renewal }}</span>
                <strong>{{ copy.in30Days }}</strong>
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

<style scoped>
.jobs-grid,
.field-grid,
.attribute-grid,
.upload-grid,
.pricing-layout,
.pricing-grid {
  display: grid;
  gap: 1rem;
}

.jobs-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: start;
}

.pricing-layout {
  grid-template-columns: 1fr;
}

.pricing-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.panel,
.job-row,
.plan-card,
.response-row {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.25rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.panel,
.plan-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
}

.panel-heading,
.form-actions,
.plan-card__top,
.job-top,
.job-footer,
.response-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.eyebrow {
  margin: 0 0 0.45rem;
  color: var(--brand-strong);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.compact {
  font-size: 0.76rem;
}

h2,
h3,
p {
  margin: 0;
}

.dashboard-cta {
  min-width: 13.5rem;
}

.status,
.state {
  padding: 0.95rem 1rem;
  border-radius: 0.95rem;
}

.success,
.state {
  border: 0.0625rem solid var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
}

.danger {
  border: 0.0625rem solid rgba(220, 38, 38, 0.14);
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.form-panel {
  position: sticky;
  top: 5.5rem;
}

.section {
  display: grid;
  gap: 0.85rem;
}

.section-label {
  display: block;
  color: var(--text-primary);
  font-weight: 700;
}

.chips,
.summary-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 2.2rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 68%, white);
  color: var(--brand-strong);
  font-weight: 700;
}

.chip b {
  font-size: 0.78rem;
}

.chip button {
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font: inherit;
}

.inline-add {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.75rem;
  align-items: start;
}

.field-hint {
  display: grid;
  gap: 0.25rem;
  padding: 0.95rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--surface-secondary) 88%, white);
}

.field-hint span {
  color: var(--text-muted);
  font-size: 0.82rem;
}

.field-hint strong {
  color: var(--text-primary);
  font-size: 0.95rem;
}

.btn-secondary--compact {
  width: fit-content;
}

.jobs-panel {
  gap: 0.75rem;
}

label {
  display: grid;
  gap: 0.45rem;
  color: var(--text-primary);
  font-weight: 700;
}

input,
textarea {
  width: 100%;
  min-height: 3.15rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

textarea {
  min-height: 8.75rem;
  resize: vertical;
}

.upload-grid,
.attribute-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.upload-card,
.preview-card,
.attribute-card {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
}

.upload-card {
  position: relative;
  min-height: 11.5rem;
  padding: 1rem;
  display: grid;
  gap: 0.7rem;
  align-content: start;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 251, 248, 0.98));
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  text-align: center;
  border: 2px dashed rgb(31, 201, 127, 0.4);
}

.upload-card input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.upload-title,
.attribute-card strong {
  color: var(--text-primary);
}

.upload-copy {
  font-size: 0.82rem;
  line-height: 1.35;
}

.upload-copy,
.upload-filename,
.preview-placeholder,
.job-company,
.job-description,
.pricing-copy,
.plan-limit,
.response-main small,
.response-main p,
.attribute-card small,
.responses-subtitle,
.response-kicker,
.response-job,
.response-message,
.response-detail {
  color: var(--text-muted);
}

.upload-button,
.badge,
.text-button,
.plan-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  font-weight: 800;
}

.upload-button {
  width: fit-content;
  min-height: 2.8rem;
  padding: 0.72rem 1rem;
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--brand-soft) 70%, white);
  color: var(--brand-strong);
}

.preview-card {
  min-height: 11.5rem;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(232, 249, 238, 0.82), rgba(255, 255, 255, 0.98));
}

.preview-card img,
.company-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  display: grid;
  gap: 0.55rem;
  justify-items: center;
  text-align: center;
}

.preview-placeholder i,
.attribute-card > i,
.plan-features i {
  color: var(--brand-strong);
}

.attribute-card {
  display: grid;
  grid-template-columns: auto auto minmax(0, 1fr);
  align-items: center;
  gap: 0.75rem;
  min-height: 5rem;
  padding: 1rem;
  background: var(--surface-secondary);
  cursor: pointer;
}

.attribute-card input {
  width: 1rem;
  min-height: 1rem;
  margin: 0;
  padding: 0;
}

.attribute-card span {
  display: grid;
  gap: 0.18rem;
}

.attribute-card--active {
  border-color: var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 68%, white);
}

.job-row {
  display: grid;
  grid-template-columns: 4.75rem minmax(0, 1fr);
  gap: 0.9rem;
  align-items: start;
  padding: 1rem;
  margin-top: 0.75rem;
  background: color-mix(in srgb, var(--surface-secondary) 92%, transparent);
}


.company-logo {
  width: 4.75rem;
  height: 4.75rem;
  display: grid;
  place-items: center;
  border-radius: 1rem;
  color: #fff;
  font-size: 1.05rem;
  font-weight: 800;
  overflow: hidden;
}

.job-body,
.job-heading {
  display: grid;
}

.job-body {
  gap: 0.6rem;
}

.job-heading {
  gap: 0.16rem;
}

.job-tags {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.job-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 1.75rem;
  padding: 0.28rem 0.62rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
  color: var(--brand-strong);
  font-size: 0.76rem;
  font-weight: 700;
}


.job-description {
  line-height: 1.45;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}


.job-footer {
  padding-top: 0.65rem;
  border-top: 0.0625rem solid var(--border-subtle);
  align-items: center;
}

.job-salary,
.current-plan-card strong,
.plan-price {
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 800;
}

.job-buttons {
  display: flex;
  gap: 0.35rem;
  flex-wrap: nowrap;
}

.badge,
.plan-badge {
  min-height: 2rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
  font-size: 0.76rem;
}

.badge.pending {
  background: rgba(180, 83, 9, 0.1);
  color: #92400e;
}

.badge.approved {
  background: rgba(22, 163, 74, 0.1);
  color: #15803d;
}

.text-button {
  min-height: 2.35rem;
  padding: 0.5rem 0.8rem;
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
  border: none;
  font: inherit;
  font-size: 0.85rem;
  cursor: pointer;
  text-decoration: none;
}

.text-button.danger {
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.responses-panel {
  gap: 1.15rem;
}

.responses-heading {
  align-items: flex-start;
}

.responses-subtitle {
  margin-top: 0.45rem;
  line-height: 1.5;
}

.response-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.85rem;
}

.response-stat-card {
  padding: 1rem 1.1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 92%, transparent);
}

.response-stat-card span {
  display: block;
  color: var(--text-muted);
  font-size: 0.82rem;
  margin-bottom: 0.4rem;
}

.response-stat-card strong {
  color: var(--text-primary);
  font-size: 1.9rem;
  line-height: 1;
}

.response-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.response-summary__pill {
  display: inline-flex;
  align-items: center;
  min-height: 2rem;
  padding: 0.32rem 0.78rem;
  border-radius: 999rem;
  font-size: 0.8rem;
  font-weight: 800;
}

.response-summary__pill--strong {
  background: #e6f0ec;
  color: #19785a;
}

.response-summary__pill--good {
  background: #e8f0fe;
  color: #4a90e2;
}

.response-summary__pill--partial {
  background: #fef3e2;
  color: #d68a12;
}

.response-summary__pill--weak {
  background: #f3f4f6;
  color: #6b7280;
}

.response-summary__pill--fail {
  background: #fee2e2;
  color: #dc2626;
}

.responses-list {
  display: grid;
  gap: 0.85rem;
}

.response-vacancy-card {
  display: grid;
  gap: 0.9rem;
  padding: 1.15rem 1.2rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.2rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.response-vacancy-card__top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.response-vacancy-card__copy {
  display: grid;
  gap: 0.35rem;
}

.response-vacancy-card__copy h3 {
  color: var(--text-primary);
  font-size: 1.2rem;
  line-height: 1.25;
}

.response-vacancy-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.9rem;
  color: var(--text-muted);
  font-size: 0.88rem;
}

.response-vacancy-card__meta span {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.response-vacancy-card__toggle {
  min-height: 2.9rem;
  padding: 0.7rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background: #fff;
  color: var(--text-primary);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.response-summary--card {
  gap: 0.55rem;
}

.response-inline-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  align-items: center;
}

.response-candidate-pill,
.response-score-chip {
  display: inline-flex;
  align-items: center;
  min-height: 2rem;
  padding: 0.32rem 0.78rem;
  border-radius: 999rem;
  font-size: 0.8rem;
  font-weight: 800;
}

.response-candidate-pill--strong,
.response-score-chip--strong {
  background: #e6f0ec;
  color: #19785a;
}

.response-candidate-pill--good,
.response-score-chip--good {
  background: #e8f0fe;
  color: #4a90e2;
}

.response-candidate-pill--partial,
.response-score-chip--partial {
  background: #fef3e2;
  color: #d68a12;
}

.response-candidate-pill--weak,
.response-score-chip--weak {
  background: #f3f4f6;
  color: #6b7280;
}

.response-candidate-pill--fail,
.response-score-chip--fail {
  background: #fee2e2;
  color: #dc2626;
}

.response-candidate-list {
  display: grid;
  gap: 0.75rem;
  padding-top: 0.1rem;
}

.response-candidate-row {
  display: grid;
  grid-template-columns: 4.25rem minmax(0, 1fr) 12.5rem;
  gap: 1rem;
  align-items: start;
  padding-top: 0.85rem;
  border-top: 0.0625rem solid var(--border-subtle);
}

.response-candidate-row__body {
  display: grid;
  gap: 0.55rem;
}

.response-avatar {
  width: 4.25rem;
  height: 4.25rem;
  display: grid;
  place-items: center;
  flex: 0 0 4.25rem;
  border: 0.1875rem solid rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  background: #16a34a;
  color: #fff;
  font-family: Arial, sans-serif;
  font-size: 1.05rem;
  font-weight: 900;
  letter-spacing: 0.03em;
  line-height: 1;
  text-align: center;
  overflow: hidden;
  box-shadow: 0 0.75rem 1.6rem rgba(16, 185, 129, 0.18);
}

.response-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.response-content {
  display: grid;
  gap: 0.55rem;
  min-width: 0;
}

.response-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.response-title-block {
  display: grid;
  gap: 0.1rem;
  min-width: 0;
}

.response-kicker {
  font-size: 0.7rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.response-title-block h3 {
  color: var(--text-primary);
  font-size: 1.05rem;
  line-height: 1.25;
}

.response-job,
.response-details,
.response-detail {
  display: flex;
  align-items: center;
}

.response-job {
  gap: 0.45rem;
  min-width: 0;
  font-size: 0.9rem;
}

.response-job span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.response-job i,
.response-detail i {
  color: var(--brand-strong);
}

.response-message {
  max-width: 52rem;
  line-height: 1.5;
}

.response-details {
  gap: 0.55rem;
  flex-wrap: wrap;
}

.response-breakdown {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.7rem;
}

.response-breakdown-card {
  display: grid;
  gap: 0.45rem;
  padding: 0.8rem 0.9rem;
  border-radius: 0.95rem;
  border: 0.0625rem solid var(--border-subtle);
  background: color-mix(in srgb, var(--surface-secondary) 92%, white);
}

.response-breakdown-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.response-breakdown-card__head span {
  color: var(--text-primary);
  font-weight: 800;
  font-size: 0.88rem;
}

.response-breakdown-card__head strong {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  min-height: 2rem;
  padding: 0.2rem 0.55rem;
  border-radius: 999rem;
  font-size: 0.82rem;
}

.response-breakdown-card__detail {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.82rem;
  line-height: 1.45;
}

.response-breakdown-card--strong .response-breakdown-card__head strong {
  background: #e6f0ec;
  color: #19785a;
}

.response-breakdown-card--good .response-breakdown-card__head strong {
  background: #e8f0fe;
  color: #4a90e2;
}

.response-breakdown-card--partial .response-breakdown-card__head strong {
  background: #fef3e2;
  color: #d68a12;
}

.response-breakdown-card--weak .response-breakdown-card__head strong {
  background: #f3f4f6;
  color: #6b7280;
}

.response-breakdown-card--fail .response-breakdown-card__head strong {
  background: #fee2e2;
  color: #dc2626;
}

.response-detail {
  gap: 0.38rem;
  min-height: 1.85rem;
  padding: 0.28rem 0.6rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 999rem;
  background: rgba(255, 255, 255, 0.72);
  font-size: 0.78rem;
  font-weight: 700;
}

.response-actions {
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  width: 12.5rem;
  min-width: 12.5rem;
}

.response-status,
.response-action-button {
  width: 100%;
  min-height: 2.7rem;
  height: 2.7rem;
  padding: 0.65rem 0.9rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  border-radius: 0.9rem;
  font-size: 0.85rem;
  font-weight: 900;
  line-height: 1;
  white-space: nowrap;
}

.response-action-button {
  border: none;
  background: color-mix(in srgb, var(--brand-soft) 74%, white);
  color: var(--brand-strong);
  font: inherit;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background 0.2s ease,
    opacity 0.2s ease;
}

.response-action-button:hover:not(:disabled) {
  transform: translateY(-0.0625rem);
  background: color-mix(in srgb, var(--brand-soft) 86%, white);
}

.response-action-button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.response-status-mobile {
  display: none;
}

.message-shell {
  display: grid;
}

.current-plan-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.85rem;
}

.current-plan-card {
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 92%, transparent);
}

.current-plan-card span {
  display: block;
  color: var(--text-muted);
  margin-bottom: 0.35rem;
}

.pricing-action {
  width: fit-content;
}

.plan-card {
  gap: 1rem;
}

.plan-card--current {
  border-color: var(--border-strong);
}

.plan-features {
  display: grid;
  gap: 0.6rem;
  padding: 0;
  margin: 0;
  list-style: none;
  flex: 1;
}

.plan-features li {
  display: flex;
  gap: 0.55rem;
  align-items: flex-start;
  color: var(--text-primary);
}

.plan-card button,
.current-plan .pricing-action {
  margin-top: auto;
}

@media (max-width: 88rem) {
  .pricing-grid,
  .response-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 78rem) {
  .jobs-grid,
  .current-plan-grid {
    grid-template-columns: 1fr;
  }

  .form-panel {
    position: static;
  }
}

@media (max-width: 56rem) {
  .pricing-grid,
  .response-stats,
  .field-grid,
  .attribute-grid,
  .upload-grid,
  .inline-add,
  .panel-heading,
  .form-actions,
  .job-row,
  .job-top,
  .job-footer {
    grid-template-columns: 1fr;
    display: grid;
  }

  .response-vacancy-card__top,
  .response-candidate-row {
    grid-template-columns: 1fr;
    display: grid;
  }

  .response-breakdown {
    grid-template-columns: 1fr;
  }

  .response-actions {
    align-items: stretch;
    width: 100%;
    min-width: 0;
  }

  .response-status {
    display: none;
  }

  .response-status-mobile {
    display: inline-flex;
    width: fit-content;
    min-height: 2.35rem;
    height: 2.35rem;
  }

  .response-avatar {
    width: 3.8rem;
    height: 3.8rem;
    flex-basis: 3.8rem;
    border-radius: 50%;
  }

  .response-job span {
    white-space: normal;
  }

  .response-actions,
  .job-buttons {
    align-items: stretch;
  }

  .text-button,
  .btn-primary,
  .btn-secondary,
  .pricing-action,
  .response-action-button {
    width: 100%;
  }
}

@media (max-width: 34rem) {
  .response-stats {
    grid-template-columns: 1fr;
  }

  .response-avatar {
    width: 4rem;
    height: 4rem;
    flex-basis: 4rem;
  }

  .response-header {
    display: grid;
  }

  .response-status-mobile {
    width: fit-content;
  }
}
</style>
