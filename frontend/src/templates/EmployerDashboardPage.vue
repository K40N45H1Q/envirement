<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
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
import { normalizeJob } from '@/utils/jobs'

const route = useRoute()
const router = useRouter()
const messaging = useMessagingStore()

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

const sections = [
  { id: 'jobs', label: 'Вакансии', icon: 'fas fa-briefcase', to: '/employer-dashboard?section=jobs' },
  { id: 'responses', label: 'Отклики', icon: 'fas fa-user-check', to: '/employer-dashboard?section=responses' },
  { id: 'messages', label: 'Сообщения', icon: 'fas fa-message', to: '/employer-dashboard?section=messages' },
  { id: 'pricing', label: 'Тарифы', icon: 'fas fa-credit-card', to: '/employer-dashboard?section=pricing' },
]

const validSectionIds = sections.map((section) => section.id)
const normalizeSection = (section) => (validSectionIds.includes(section) ? section : 'jobs')

const blankForm = () => ({
  title: '',
  company: '',
  salary: '',
  location: '',
  description: '',
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
const brokenAvatars = ref(new Set())
const dashboardRefreshTimer = ref(null)

const conversations = computed(() => messaging.conversations)
const isEditing = computed(() => editingId.value !== null)
const approvedCount = computed(() => jobs.value.filter((job) => job.status === 'approved').length)
const shellStats = computed(() => ([
  { value: jobs.value.length, label: 'Всего вакансий' },
  { value: approvedCount.value, label: 'Опубликовано' },
  { value: responses.value.length, label: 'Откликов' },
  { value: conversations.value.length, label: 'Диалогов' },
]))
const activeSectionLabel = computed(() => sections.find((item) => item.id === activeSection.value)?.label || 'Вакансии')
const showHeaderAction = computed(() => activeSection.value === 'jobs')
const submitLabel = computed(() => {
  if (isSaving.value) return 'Сохранение...'
  return isEditing.value ? 'Сохранить изменения' : 'Сохранить вакансию'
})
const currentPlan = computed(() => plans.find((plan) => plan.id === currentPlanId) || plans[1])

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
  return [item.name, item.surname].filter(Boolean).join(' ') || 'Кандидат'
}

function responseInitials(item) {
  const firstNameInitial = getFirstLetter(item.name)
  const lastNameInitial = getFirstLetter(item.surname)

  if (firstNameInitial && lastNameInitial && firstNameInitial !== lastNameInitial) {
    return `${firstNameInitial}${lastNameInitial}`
  }

  return getFirstTwoLetters(item.name) || getFirstTwoLetters(item.surname) || 'CV'
}

function responseJobMeta(item) {
  return [item.job_title, item.job_company].filter(Boolean).join(' · ') || 'Вакансия не указана'
}

function responseMessage(item) {
  return item.message || 'Кандидат отправил отклик без дополнительного сообщения.'
}

async function setSection(sectionId) {
  activeSection.value = normalizeSection(sectionId)
  await router.replace({
    path: '/employer-dashboard',
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
      error.value = 'Не удалось загрузить кабинет работодателя.'
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
  editingId.value = job.id
  form.value = {
    title: job.title,
    company: job.company,
    salary: job.salary,
    location: job.location,
    description: job.description,
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
    if (isEditing.value) {
      await updateJob(editingId.value, form.value)
      status.value = 'Вакансия обновлена.'
    } else {
      await createJob(form.value)
      status.value = 'Вакансия сохранена.'
    }

    resetForm()
    await loadDashboard()
    await setSection('jobs')
  } catch {
    error.value = 'Не удалось сохранить вакансию.'
  } finally {
    isSaving.value = false
  }
}

async function removeJob(job) {
  if (!window.confirm(`Удалить вакансию "${job.title}"?`)) return

  deletingId.value = job.id
  status.value = ''
  error.value = ''

  try {
    await deleteJob(job.id)
    if (editingId.value === job.id) resetForm()
    status.value = 'Вакансия удалена.'
    await loadDashboard()
  } catch {
    error.value = 'Не удалось удалить вакансию.'
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
    status.value = 'Чат подтверждён и открыт в сообщениях.'
  } catch {
    error.value = 'Не удалось подтвердить чат.'
  } finally {
    approvingId.value = null
  }
}

function openDashboardConversation(applicationId) {
  router.replace({
    path: '/employer-dashboard',
    query: { section: 'messages', application: String(applicationId) },
  })
}

function statusLabel(value) {
  return {
    approved: 'Опубликована',
    pending: 'На модерации',
    rejected: 'Отклонена',
  }[value] || 'Черновик'
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
      :sections="sections"
      :active-section="activeSection"
      eyebrow="Личный кабинет работодателя"
      :title="activeSectionLabel"
      description="Рабочее пространство для вакансий, откликов, сообщений и тарифа."
      :stats="shellStats"
      @select-section="setSection"
    >
      <template #actions>
        <button v-if="showHeaderAction" class="btn-secondary dashboard-cta" type="button" @click="setSection('jobs')">
          <i class="fas fa-plus"></i>
          Новая вакансия
        </button>
      </template>

      <p v-if="status" class="status success">{{ status }}</p>
      <p v-if="error" class="status danger">{{ error }}</p>
      <p v-if="isLoading" class="state">Загрузка кабинета...</p>

      <template v-if="!isLoading">
        <section v-if="activeSection === 'jobs'" class="jobs-grid">
          <form class="panel form-panel" @submit.prevent="submitJob">
            <div class="panel-heading">
              <div>
                <p class="eyebrow compact">{{ isEditing ? 'Редактирование' : 'Новая вакансия' }}</p>
                <h2>{{ isEditing ? 'Обновить вакансию' : 'Создать вакансию' }}</h2>
              </div>
            </div>

            <div class="field-grid">
              <label>
                Название
                <input v-model="form.title" required placeholder="Электрик" />
              </label>
              <label>
                Компания
                <input v-model="form.company" required placeholder="Build Solutions GmbH" />
              </label>
            </div>

            <div class="field-grid">
              <label>
                Зарплата
                <input v-model="form.salary" required placeholder="2 200 - 2 800 EUR" />
              </label>
              <label>
                Локация
                <input v-model="form.location" required placeholder="Берлин, Германия" />
              </label>
            </div>

            <div class="upload-grid">
              <label class="upload-card">
                <span class="upload-title">Фото вакансии</span>
                <span class="upload-copy">PNG, JPG или WEBP для карточки вакансии</span>
                <span class="upload-button">Выбрать файл</span>
                <span class="upload-filename">{{ form.logo?.name || 'Файл не выбран' }}</span>
                <input type="file" accept="image/*" @change="onLogoChange" />
              </label>

              <div class="preview-card">
                <img v-if="logoPreview" :src="logoPreview" alt="Превью вакансии" />
                <div v-else class="preview-placeholder">
                  <i class="fas fa-image"></i>
                  <span>Превью вакансии</span>
                </div>
              </div>
            </div>

            <div class="attribute-grid">
              <label class="attribute-card" :class="{ 'attribute-card--active': form.has_housing }">
                <input v-model="form.has_housing" type="checkbox" />
                <i class="fas fa-house"></i>
                <span>
                  <strong>Есть жильё</strong>
                  <small>Показывать проживание в карточке вакансии</small>
                </span>
              </label>

              <label class="attribute-card" :class="{ 'attribute-card--active': form.has_transport }">
                <input v-model="form.has_transport" type="checkbox" />
                <i class="fas fa-bus"></i>
                <span>
                  <strong>Есть транспорт</strong>
                  <small>Показывать наличие трансфера или служебного транспорта</small>
                </span>
              </label>
            </div>

            <label>
              Описание
              <textarea v-model="form.description" rows="6" required placeholder="Обязанности, требования и условия работы"></textarea>
            </label>

            <div class="form-actions">
              <button class="btn-primary" type="submit" :disabled="isSaving">{{ submitLabel }}</button>
              <button v-if="isEditing" class="btn-secondary" type="button" @click="resetForm">Сбросить</button>
            </div>
          </form>

          <section class="panel jobs-panel">
            <div class="panel-heading">
              <div>
                <p class="eyebrow compact">Публикации</p>
                <h2>Мои вакансии</h2>
              </div>
            </div>

            <p v-if="!jobs.length" class="state">Вакансий пока нет.</p>

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
                  <span v-if="job.has_housing" class="job-tag"><i class="fas fa-house"></i> Есть жильё</span>
                  <span v-if="job.has_transport" class="job-tag"><i class="fas fa-bus"></i> Есть транспорт</span>
                </div>

                <p class="job-description">{{ job.description }}</p>

                <div class="job-footer">
                  <strong class="job-salary">{{ job.salary }}</strong>
                  <div class="job-buttons">
                    <RouterLink v-if="job.status === 'approved'" :to="`/jobs/${job.id}`" class="text-button">Открыть</RouterLink>
                    <button type="button" class="text-button" @click="editJob(job)">Редактировать</button>
                    <button type="button" class="text-button danger" :disabled="deletingId === job.id" @click="removeJob(job)">
                      {{ deletingId === job.id ? 'Удаление...' : 'Удалить' }}
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
              <p class="eyebrow compact">Отклики</p>
              <h2>Кандидаты по вакансиям</h2>
              <p class="responses-subtitle">Быстро оценивайте кандидатов, подтверждайте чат и переходите к общению.</p>
            </div>
          </div>

          <p v-if="!responses.length" class="state">Откликов пока нет.</p>

          <div v-else class="responses-list">
            <article
              v-for="item in responses"
              :key="item.id"
              class="response-row"
              :class="{ 'response-row--approved': item.chat_approved }"
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

              <div class="response-content">
                <div class="response-header">
                  <div class="response-title-block">
                    <p class="response-kicker">Кандидат</p>
                    <h3>{{ responseFullName(item) }}</h3>
                  </div>

                  <span class="badge response-status-mobile" :class="item.chat_approved ? 'approved' : 'pending'">
                    {{ item.chat_approved ? 'Чат активен' : 'Ждёт подтверждения' }}
                  </span>
                </div>

                <div class="response-job">
                  <i class="fas fa-briefcase"></i>
                  <span>{{ responseJobMeta(item) }}</span>
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
              </div>

              <div class="response-actions">
                <span class="badge response-status" :class="item.chat_approved ? 'approved' : 'pending'">
                  {{ item.chat_approved ? 'Чат активен' : 'Ждёт подтверждения' }}
                </span>

                <button
                  v-if="!item.chat_approved"
                  type="button"
                  class="response-action-button"
                  :disabled="approvingId === item.id"
                  @click="approveChat(item)"
                >
                  <i class="fas fa-message"></i>
                  {{ approvingId === item.id ? 'Подтверждаем...' : 'Подтвердить чат' }}
                </button>

                <button
                  v-else
                  type="button"
                  class="response-action-button"
                  @click="openDashboardConversation(item.id)"
                >
                  <i class="fas fa-arrow-up-right-from-square"></i>
                  Открыть сообщения
                </button>
              </div>
            </article>
          </div>
        </section>

        <section v-if="activeSection === 'messages'" class="message-shell">
          <MessagesPanel embedded @open="openDashboardConversation" />
        </section>

        <section v-if="activeSection === 'pricing'" class="pricing-layout">
          <article class="panel current-plan">
            <div class="panel-heading">
              <div>
                <p class="eyebrow compact">Текущий тариф</p>
                <h2>{{ currentPlan.name }}</h2>
              </div>
              <span class="plan-badge">Активен</span>
            </div>

            <div class="current-plan-grid">
              <div class="current-plan-card">
                <span>Стоимость</span>
                <strong>{{ currentPlan.price }}</strong>
              </div>
              <div class="current-plan-card">
                <span>Лимит</span>
                <strong>{{ currentPlan.vacancies }}</strong>
              </div>
              <div class="current-plan-card">
                <span>Продление</span>
                <strong>Через 30 дней</strong>
              </div>
            </div>
          </article>

          <section class="pricing-grid">
            <article
              v-for="plan in plans"
              :key="plan.id"
              class="plan-card"
              :class="{ 'plan-card--current': plan.id === currentPlanId }"
            >
              <div class="plan-card__top">
                <div>
                  <p class="eyebrow compact">{{ plan.id === currentPlanId ? 'Ваш пакет' : 'Доступно' }}</p>
                  <h3>{{ plan.name }}</h3>
                </div>
                <span v-if="plan.id === currentPlanId" class="plan-badge">Текущий</span>
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
                {{ plan.id === currentPlanId ? 'Продлить' : 'Выбрать тариф' }}
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
  margin-top: auto;
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

.responses-list {
  display: grid;
  gap: 0.85rem;
}

.response-row {
  position: relative;
  display: grid;
  cursor: pointer;
  grid-template-columns: 4.25rem minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(240, 253, 244, 0.82), rgba(255, 255, 255, 0.98) 44%),
    var(--surface-primary);
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.response-row::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 0.25rem;
  background: var(--brand-strong);
  opacity: 0.85;
}

.response-row:hover {
  transform: translateY(-0.125rem);
  border-color: var(--border-strong);
  box-shadow: 0 1.25rem 2.6rem rgba(15, 23, 42, 0.08);
}

.response-row--approved::before {
  background: #16a34a;
}

.response-avatar {
  width: 4.25rem;
  height: 4.25rem;
  display: grid;
  place-items: center;
  flex: 0 0 4.25rem;
  border: 0.1875rem solid rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  background: #0f766e;
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
  .pricing-grid {
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
  .field-grid,
  .attribute-grid,
  .upload-grid,
  .panel-heading,
  .form-actions,
  .job-row,
  .job-top,
  .job-footer {
    grid-template-columns: 1fr;
    display: grid;
  }

  .response-row {
    grid-template-columns: 3.8rem minmax(0, 1fr);
    align-items: start;
  }

  .response-actions {
    grid-column: 1 / -1;
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

  .response-header {
    align-items: flex-start;
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
  .response-row {
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