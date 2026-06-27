<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import DashboardShell from '@/components/dashboard/DashboardShell.vue'
import {
  createJob,
  deleteJob,
  getMessageConversations,
  getMyJobs,
  getResponses,
  updateJob,
} from '@/api/jobs'
import { normalizeJob } from '@/utils/jobs'

const route = useRoute()
const router = useRouter()

const blankForm = () => ({
  title: '',
  company: '',
  salary: '',
  location: '',
  description: '',
  has_housing: false,
  has_transport: false,
  logo_url: '',
  logo: null,
})

const sections = [
  { id: 'overview', label: 'Кабинет', icon: 'fas fa-table-columns', to: '/employer-dashboard' },
  { id: 'jobs', label: 'Вакансии', icon: 'fas fa-briefcase', to: '/employer-dashboard?section=jobs' },
  { id: 'responses', label: 'Отклики', icon: 'fas fa-user-check', to: '/employer-dashboard?section=responses' },
  { id: 'messages', label: 'Сообщения', icon: 'fas fa-message', to: '/employer-dashboard?section=messages' },
  { id: 'pricing', label: 'Тарифы', icon: 'fas fa-credit-card', to: '/employer-dashboard?section=pricing' },
]

const jobs = ref([])
const responses = ref([])
const conversations = ref([])
const isLoading = ref(false)
const isSaving = ref(false)
const deletingId = ref(null)
const editingId = ref(null)
const status = ref('')
const error = ref('')
const form = ref(blankForm())
const activeSection = ref(typeof route.query.section === 'string' ? route.query.section : 'overview')
const logoPreview = ref('')
const objectUrl = ref('')

const isEditing = computed(() => editingId.value !== null)
const approvedCount = computed(() => jobs.value.filter((job) => job.status === 'approved').length)
const pendingCount = computed(() => jobs.value.filter((job) => job.status === 'pending').length)
const rejectedCount = computed(() => jobs.value.filter((job) => job.status === 'rejected').length)
const responsesHint = computed(() => responses.value.length)
const unreadConversations = computed(() => conversations.value.length)
const activeSectionLabel = computed(() => sections.find((item) => item.id === activeSection.value)?.label || 'Кабинет')
const latestResponses = computed(() => responses.value.slice(0, 4))
const latestConversations = computed(() => conversations.value.slice(0, 4))
const shellStats = computed(() => ([
  { value: jobs.value.length, label: 'Всего вакансий' },
  { value: approvedCount.value, label: 'Опубликовано' },
  { value: responsesHint.value, label: 'Откликов' },
  { value: unreadConversations.value, label: 'Диалогов' },
]))

const responseConversion = computed(() => {
  if (!jobs.value.length) return '0%'
  return `${Math.round((responses.value.length / jobs.value.length) * 100)}%`
})

const moderationState = computed(() => {
  if (pendingCount.value) return 'На модерации'
  if (rejectedCount.value) return 'Нужна доработка'
  return 'Поток активен'
})

const moderationTone = computed(() => {
  if (pendingCount.value) return 'warm'
  if (rejectedCount.value) return 'danger'
  return 'success'
})

const quickActions = computed(() => ([
  {
    title: 'Создать публикацию',
    text: 'Добавьте новую вакансию и сразу проверьте карточку на живой витрине.',
    button: 'Новая вакансия',
    section: 'jobs',
  },
  {
    title: 'Разобрать отклики',
    text: 'Перейдите к списку кандидатов и откройте диалог без лишних переходов.',
    button: 'Открыть отклики',
    section: 'responses',
  },
  {
    title: 'Продолжить переписку',
    text: 'Следите за новыми сообщениями и быстро возвращайтесь к активным диалогам.',
    button: 'К сообщениям',
    section: 'messages',
  },
]))

const pricingPlans = [
  { name: 'Basic', price: '99 EUR', features: '1 вакансия · 30 дней публикации' },
  { name: 'Standard', price: '149 EUR', features: '3 вакансии · 30 дней публикации' },
  { name: 'Pro', price: '229 EUR', features: '5 вакансий · приоритет и аналитика' },
]

const revokeLogoPreview = () => {
  if (objectUrl.value) {
    URL.revokeObjectURL(objectUrl.value)
    objectUrl.value = ''
  }
}

const setSection = async (sectionId) => {
  activeSection.value = sectionId
  await router.replace({
    path: '/employer-dashboard',
    query: sectionId === 'overview' ? {} : { section: sectionId },
  })
}

const statusLabel = (value) => ({
  approved: 'Опубликована',
  pending: 'На модерации',
  rejected: 'Отклонена',
}[value] || value || 'Черновик')

const submitLabel = computed(() => {
  if (isSaving.value) return 'Сохранение...'
  return isEditing.value ? 'Сохранить изменения' : 'Сохранить вакансию'
})

const loadMyJobs = async () => {
  const data = await getMyJobs()
  jobs.value = Array.isArray(data) ? data.map(normalizeJob) : []
}

const loadResponsesList = async () => {
  const data = await getResponses()
  responses.value = Array.isArray(data) ? data : []
}

const loadConversations = async () => {
  const data = await getMessageConversations()
  conversations.value = Array.isArray(data) ? data : []
}

const loadDashboard = async () => {
  isLoading.value = true
  error.value = ''

  try {
    await Promise.all([loadMyJobs(), loadResponsesList(), loadConversations()])
  } catch {
    error.value = 'Не удалось загрузить кабинет работодателя.'
    jobs.value = []
    responses.value = []
    conversations.value = []
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  editingId.value = null
  revokeLogoPreview()
  logoPreview.value = ''
  form.value = blankForm()
}

const editJob = async (job) => {
  status.value = ''
  error.value = ''
  editingId.value = job.id
  revokeLogoPreview()
  logoPreview.value = job.logo || ''
  form.value = {
    title: job.title,
    company: job.company,
    salary: job.salary,
    location: job.location,
    description: job.description,
    has_housing: Boolean(job.has_housing),
    has_transport: Boolean(job.has_transport),
    logo_url: job.logo || '',
    logo: null,
  }
  await setSection('jobs')
}

const onLogoChange = (event) => {
  const file = event.target.files?.[0] || null
  form.value.logo = file
  revokeLogoPreview()

  if (file) {
    objectUrl.value = URL.createObjectURL(file)
    logoPreview.value = objectUrl.value
  } else {
    logoPreview.value = form.value.logo_url || ''
  }
}

const submitJob = async () => {
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
    error.value = 'Не удалось сохранить вакансию. Проверьте поля и попробуйте ещё раз.'
  } finally {
    isSaving.value = false
  }
}

const removeJob = async (job) => {
  if (!window.confirm(`Удалить вакансию "${job.title}"?`)) return

  deletingId.value = job.id
  status.value = ''
  error.value = ''

  try {
    await deleteJob(job.id)
    status.value = 'Вакансия удалена.'
    if (editingId.value === job.id) resetForm()
    await loadDashboard()
  } catch {
    error.value = 'Не удалось удалить вакансию.'
  } finally {
    deletingId.value = null
  }
}

watch(
  () => route.query.section,
  (section) => {
    activeSection.value = typeof section === 'string' ? section : 'overview'
  },
)

watch(
  () => form.value.logo_url,
  (value) => {
    if (!form.value.logo) {
      logoPreview.value = value || ''
    }
  },
)

onMounted(loadDashboard)
onBeforeUnmount(revokeLogoPreview)
</script>

<template>
  <AppLayout>
    <DashboardShell
      :sections="sections"
      :active-section="activeSection"
      eyebrow="Личный кабинет работодателя"
      :title="activeSectionLabel"
      description="Единое рабочее пространство для вакансий, откликов, сообщений и управления публикациями."
      :stats="shellStats"
      @select-section="setSection"
    >
      <template #actions>
        <button class="btn-secondary dashboard-cta" type="button" @click="setSection('jobs')">
          <i class="fas fa-plus"></i>
          Новая вакансия
        </button>
      </template>

      <p v-if="status" class="status success">{{ status }}</p>
      <p v-if="error" class="status danger">{{ error }}</p>
      <p v-if="isLoading" class="state">Загрузка кабинета...</p>

      <template v-if="!isLoading">
        <section v-if="activeSection === 'overview'" class="workspace workspace--overview">
          <div class="panel overview-main">
            <div class="panel-heading">
              <div>
                <p class="eyebrow compact">Сводка</p>
                <h2>Что происходит сейчас</h2>
              </div>
              <span class="overview-state" :class="`overview-state--${moderationTone}`">{{ moderationState }}</span>
            </div>

            <div class="health-grid">
              <article class="health-card health-card--success">
                <span class="health-card__label">Опубликовано</span>
                <strong>{{ approvedCount }}</strong>
                <p>Активные вакансии уже доступны кандидатам.</p>
              </article>
              <article class="health-card health-card--warm">
                <span class="health-card__label">На модерации</span>
                <strong>{{ pendingCount }}</strong>
                <p>Проверяются карточки, которые ещё не вышли в выдачу.</p>
              </article>
              <article v-if="rejectedCount" class="health-card health-card--danger">
                <span class="health-card__label">Нужна доработка</span>
                <strong>{{ rejectedCount }}</strong>
                <p>У этих публикаций стоит проверить описание и медиа.</p>
              </article>
              <article class="health-card">
                <span class="health-card__label">Конверсия в отклик</span>
                <strong>{{ responseConversion }}</strong>
                <p>Соотношение откликов к числу ваших вакансий.</p>
              </article>
            </div>

            <div class="activity-grid">
              <article class="mini-card">
                <div class="mini-card__head">
                  <h3>Последние отклики</h3>
                  <button class="mini-link" type="button" @click="setSection('responses')">Все отклики</button>
                </div>
                <p v-if="!latestResponses.length" class="muted">Пока откликов нет.</p>
                <RouterLink
                  v-for="item in latestResponses"
                  :key="item.id"
                  :to="`/messages?application=${item.id}`"
                  class="inline-item"
                >
                  <span class="inline-item__copy">
                    <strong>{{ item.name }} {{ item.surname }}</strong>
                    <small>{{ item.job_title }}</small>
                  </span>
                  <i class="fas fa-arrow-right"></i>
                </RouterLink>
              </article>

              <article class="mini-card">
                <div class="mini-card__head">
                  <h3>Последние диалоги</h3>
                  <button class="mini-link" type="button" @click="setSection('messages')">Все сообщения</button>
                </div>
                <p v-if="!latestConversations.length" class="muted">Сообщений пока нет.</p>
                <RouterLink
                  v-for="conversation in latestConversations"
                  :key="conversation.application_id"
                  :to="`/messages?application=${conversation.application_id}`"
                  class="inline-item"
                >
                  <span class="inline-item__copy">
                    <strong>{{ conversation.counterparty_name }}</strong>
                    <small>{{ conversation.job_title }}</small>
                  </span>
                  <i class="fas fa-arrow-right"></i>
                </RouterLink>
              </article>
            </div>
          </div>

          <div class="overview-side">
            <article class="panel quick-panel">
              <div class="panel-heading panel-heading--stack">
                <div>
                  <p class="eyebrow compact">Быстрые действия</p>
                  <h2>Рабочий ритм</h2>
                </div>
                <p class="muted">Все основные задачи под рукой без переходов по разным кабинетам.</p>
              </div>

              <div class="quick-grid">
                <button
                  v-for="action in quickActions"
                  :key="action.title"
                  class="quick-action"
                  type="button"
                  @click="setSection(action.section)"
                >
                  <span class="quick-action__title">{{ action.title }}</span>
                  <span class="quick-action__text">{{ action.text }}</span>
                  <span class="quick-action__button">{{ action.button }}</span>
                </button>
              </div>
            </article>

            <article class="panel compact-panel">
              <div class="panel-heading panel-heading--stack">
                <div>
                  <p class="eyebrow compact">Публикации</p>
                  <h2>Текущий пакет</h2>
                </div>
                <span class="summary-pill">Standard · 5 слотов</span>
              </div>

              <div class="plan-lines">
                <div class="plan-line">
                  <span>Использовано</span>
                  <strong>{{ jobs.length }} / 5</strong>
                </div>
                <div class="plan-line">
                  <span>Отклики</span>
                  <strong>{{ responsesHint }}</strong>
                </div>
                <div class="plan-line">
                  <span>Активные диалоги</span>
                  <strong>{{ unreadConversations }}</strong>
                </div>
              </div>

              <button class="btn-primary" type="button" @click="setSection('pricing')">Открыть тарифы</button>
            </article>
          </div>
        </section>

        <section v-if="activeSection === 'jobs'" class="workspace workspace--jobs">
          <form class="panel form-panel" @submit.prevent="submitJob">
            <div class="panel-heading">
              <div>
                <p class="eyebrow compact">{{ isEditing ? 'Редактирование' : 'Новая вакансия' }}</p>
                <h2>{{ isEditing ? 'Обновить вакансию' : 'Создать вакансию' }}</h2>
              </div>
              <button v-if="isEditing" class="icon-button" type="button" @click="resetForm">
                <i class="fas fa-xmark"></i>
              </button>
            </div>

            <div class="form-content">
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
                  <span class="upload-card__label">Фото вакансии</span>
                  <span class="upload-card__hint">PNG, JPG или WEBP для карточки вакансии</span>
                  <input type="file" accept="image/*" @change="onLogoChange" />
                  <span class="upload-card__button">Выбрать файл</span>
                </label>

                <div class="preview-card">
                  <span class="upload-card__label">Превью</span>
                  <div class="logo-preview">
                    <img v-if="logoPreview || form.logo_url" :src="logoPreview || form.logo_url" alt="Превью фото вакансии" />
                    <div v-else class="logo-preview__empty">
                      <i class="fas fa-image"></i>
                      <span>Изображение появится здесь</span>
                    </div>
                  </div>
                </div>
              </div>

              <label>
                Резервная ссылка на изображение
                <input v-model="form.logo_url" placeholder="https://example.com/logo.png" />
              </label>

              <div class="attribute-grid">
                <label class="attribute-card" :class="{ 'attribute-card--active': form.has_housing }">
                  <input v-model="form.has_housing" type="checkbox" />
                  <i class="fas fa-house"></i>
                  <span>
                    <strong>Есть жильё</strong>
                    <small>Показывать фильтр проживания в карточке вакансии</small>
                  </span>
                </label>

                <label class="attribute-card" :class="{ 'attribute-card--active': form.has_transport }">
                  <input v-model="form.has_transport" type="checkbox" />
                  <i class="fas fa-van-shuttle"></i>
                  <span>
                    <strong>Есть транспорт</strong>
                    <small>Указывать наличие трансфера или служебного транспорта</small>
                  </span>
                </label>
              </div>

              <label>
                Описание
                <textarea
                  v-model="form.description"
                  required
                  rows="7"
                  placeholder="Обязанности, требования, условия работы и график"
                ></textarea>
              </label>
            </div>

            <div class="form-actions">
              <button class="btn-primary" type="submit" :disabled="isSaving">{{ submitLabel }}</button>
              <button v-if="isEditing" class="btn-secondary" type="button" @click="resetForm">Сбросить</button>
            </div>
          </form>

          <div class="panel jobs-panel">
            <div class="panel-heading">
              <div>
                <p class="eyebrow compact">Публикации</p>
                <h2>Мои вакансии</h2>
              </div>
              <button class="icon-button" type="button" @click="loadDashboard">
                <i class="fas fa-rotate-right"></i>
              </button>
            </div>

            <div v-if="jobs.length" class="jobs-list">
              <article v-for="job in jobs" :key="job.id" class="job-row">
                <div class="job-logo" :style="{ background: job.color }">
                  <img v-if="job.logo" :src="job.logo" :alt="job.company" />
                  <span v-else>{{ job.initials }}</span>
                </div>

                <div class="job-body">
                  <div class="job-top">
                    <div class="job-heading">
                      <h3>{{ job.title }}</h3>
                      <p>{{ job.company }} · {{ job.location }}</p>
                    </div>
                    <span class="badge" :class="job.status">{{ statusLabel(job.status) }}</span>
                  </div>

                  <div class="job-meta">
                    <span class="meta-chip" :class="{ 'meta-chip--muted': !job.has_housing }">
                      <i class="fas fa-house"></i>
                      {{ job.has_housing ? 'Есть жильё' : 'Без жилья' }}
                    </span>
                    <span class="meta-chip" :class="{ 'meta-chip--muted': !job.has_transport }">
                      <i class="fas fa-van-shuttle"></i>
                      {{ job.has_transport ? 'Есть транспорт' : 'Без транспорта' }}
                    </span>
                  </div>

                  <p class="job-description">{{ job.description || 'Описание пока не заполнено.' }}</p>

                  <div class="job-actions">
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
            </div>

            <p v-else class="state">Вакансий пока нет.</p>
          </div>
        </section>

        <section v-if="activeSection === 'responses'" class="panel">
          <div class="panel-heading">
            <div>
              <p class="eyebrow compact">Кандидаты</p>
              <h2>Все отклики</h2>
            </div>
          </div>

          <div class="list-grid">
            <article v-for="item in responses" :key="item.id" class="response-row">
              <div>
                <strong>{{ item.name }} {{ item.surname }}</strong>
                <p>{{ item.job_title }} · {{ item.job_company }}</p>
              </div>
              <RouterLink :to="`/messages?application=${item.id}`" class="text-button">Открыть диалог</RouterLink>
            </article>
          </div>

          <p v-if="!responses.length" class="state">Откликов пока нет.</p>
        </section>

        <section v-if="activeSection === 'messages'" class="panel">
          <div class="panel-heading">
            <div>
              <p class="eyebrow compact">Переписка</p>
              <h2>Диалоги с кандидатами</h2>
            </div>
          </div>

          <div class="list-grid">
            <article v-for="conversation in conversations" :key="conversation.application_id" class="response-row">
              <div>
                <strong>{{ conversation.counterparty_name }}</strong>
                <p>{{ conversation.job_title }} · {{ conversation.last_message }}</p>
              </div>
              <RouterLink :to="`/messages?application=${conversation.application_id}`" class="text-button">Открыть</RouterLink>
            </article>
          </div>

          <p v-if="!conversations.length" class="state">Диалогов пока нет.</p>
        </section>

        <section v-if="activeSection === 'pricing'" class="panel">
          <div class="panel-heading">
            <div>
              <p class="eyebrow compact">Тарифы</p>
              <h2>Пакеты для публикации</h2>
            </div>
          </div>

          <div class="pricing-grid">
            <article v-for="plan in pricingPlans" :key="plan.name" class="mini-card plan-card">
              <strong class="plan-name">{{ plan.name }}</strong>
              <h3>{{ plan.price }}</h3>
              <p class="muted">{{ plan.features }}</p>
            </article>
          </div>
        </section>
      </template>
    </DashboardShell>
  </AppLayout>
</template>

<style scoped>
.workspace,
.panel,
.mini-card,
.btn-secondary,
.job-row,
.health-card,
.quick-action,
.response-row {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.25rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.workspace,
.overview-side,
.health-grid,
.activity-grid,
.pricing-grid,
.field-grid,
.form-content,
.quick-grid,
.list-grid,
.plan-lines,
.upload-grid,
.attribute-grid {
  display: grid;
  gap: 1rem;
}

.workspace--overview {
  grid-template-columns: minmax(0, 1.45fr) minmax(20rem, 0.85fr);
  align-items: start;
}

.workspace--jobs {
  grid-template-columns: minmax(21rem, 0.86fr) minmax(26rem, 1.14fr);
  align-items: start;
}

.panel,
.mini-card,
.health-card,
.quick-action,
.response-row {
  padding: 1.5rem;
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background:
    radial-gradient(circle at top right, rgba(26, 177, 111, 0.08), transparent 28%),
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 96%, transparent), var(--surface-primary));
}

.overview-main,
.jobs-panel {
  min-height: 100%;
}

.overview-side {
  align-content: start;
}

.panel-heading,
.job-top,
.job-actions,
.form-actions,
.response-row,
.mini-card__head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.panel-heading--stack {
  display: grid;
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

h2 {
  font-size: clamp(1.35rem, 2.2vw, 1.8rem);
  line-height: 1.15;
  color: var(--text-primary);
}

h3 {
  font-size: 1.02rem;
  color: var(--text-primary);
}

.muted,
.job-description,
.job-heading p,
.quick-action__text,
.upload-card__hint,
.plan-line span,
.inline-item small {
  color: var(--text-muted);
}

.dashboard-cta {
  min-width: 13.5rem;
}

.overview-state {
  display: inline-flex;
  align-items: center;
  min-height: 2.5rem;
  padding: 0.45rem 0.95rem;
  border-radius: 999rem;
  font-weight: 800;
  white-space: nowrap;
}

.overview-state--success {
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
}

.overview-state--warm {
  background: rgba(180, 83, 9, 0.12);
  color: #92400e;
}

.overview-state--danger {
  background: rgba(220, 38, 38, 0.1);
  color: #b91c1c;
}

.health-grid {
  grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr));
}

.health-card {
  display: grid;
  gap: 0.5rem;
  padding: 1.25rem;
  background: color-mix(in srgb, var(--surface-secondary) 86%, transparent);
}

.health-card strong {
  font-size: 2rem;
  line-height: 1;
  color: var(--text-primary);
}

.health-card__label {
  color: var(--brand-strong);
  font-size: 0.8rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.health-card--success {
  background: linear-gradient(180deg, rgba(16, 185, 129, 0.08), rgba(255, 255, 255, 0.98));
}

.health-card--warm {
  background: linear-gradient(180deg, rgba(245, 158, 11, 0.09), rgba(255, 255, 255, 0.98));
}

.health-card--danger {
  background: linear-gradient(180deg, rgba(239, 68, 68, 0.08), rgba(255, 255, 255, 0.98));
}

.activity-grid,
.pricing-grid,
.field-grid,
.upload-grid,
.attribute-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.mini-card {
  display: grid;
  gap: 0.85rem;
  background: color-mix(in srgb, var(--surface-secondary) 90%, transparent);
}

.mini-card__head {
  align-items: center;
}

.mini-link {
  border: none;
  background: transparent;
  color: var(--brand-strong);
  font: inherit;
  font-weight: 800;
  cursor: pointer;
}

.inline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 1rem;
  text-decoration: none;
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.8);
  border: 0.0625rem solid var(--border-subtle);
}

.inline-item__copy {
  display: grid;
  gap: 0.2rem;
}

.quick-panel,
.compact-panel {
  gap: 1.1rem;
}

.quick-action {
  display: grid;
  gap: 0.55rem;
  text-align: left;
  cursor: pointer;
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
}

.quick-action__title,
.quick-action__button {
  font-weight: 800;
}

.quick-action__title {
  color: var(--text-primary);
}

.quick-action__button {
  color: var(--brand-strong);
}

.summary-pill {
  display: inline-flex;
  align-items: center;
  min-height: 2.25rem;
  padding: 0.4rem 0.8rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
  font-weight: 700;
}

.plan-lines {
  gap: 0.85rem;
}

.plan-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
}

.plan-line strong {
  color: var(--text-primary);
}

.form-panel {
  position: sticky;
  top: 5.5rem;
}

.field-grid label,
label {
  display: grid;
  gap: 0.45rem;
  color: var(--text-primary);
  font-weight: 700;
}

input,
textarea {
  width: 100%;
  min-height: 3.2rem;
  padding: 0.92rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: var(--brand-base);
  box-shadow: 0 0 0 0.1875rem rgba(16, 185, 129, 0.12);
}

textarea {
  resize: vertical;
  min-height: 10rem;
}

.upload-card,
.preview-card,
.attribute-card {
  min-height: 100%;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
}

.upload-card,
.preview-card {
  display: grid;
  gap: 0.55rem;
  padding: 1rem;
}

.upload-card {
  position: relative;
  overflow: hidden;
}

.upload-card input[type='file'] {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.upload-card__label {
  color: var(--text-primary);
  font-size: 0.88rem;
  font-weight: 800;
}

.upload-card__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.85rem;
  width: fit-content;
  padding: 0.65rem 1rem;
  border-radius: 0.85rem;
  background: color-mix(in srgb, var(--brand-soft) 78%, transparent);
  color: var(--brand-strong);
  font-weight: 800;
}

.preview-card {
  align-content: start;
}

.logo-preview {
  width: 100%;
  min-height: 13rem;
  border-radius: 1rem;
  overflow: hidden;
  border: 0.0625rem solid var(--border-subtle);
  background: linear-gradient(180deg, rgba(243, 246, 244, 0.85), rgba(233, 244, 238, 0.96));
}

.logo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-preview__empty {
  min-height: 13rem;
  display: grid;
  place-items: center;
  gap: 0.55rem;
  color: var(--text-muted);
  text-align: center;
}

.attribute-card {
  display: grid;
  grid-template-columns: auto auto minmax(0, 1fr);
  align-items: center;
  gap: 0.85rem;
  padding: 1rem;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.attribute-card input {
  width: 1rem;
  min-height: 1rem;
  margin: 0;
  padding: 0;
}

.attribute-card i {
  color: var(--brand-strong);
}

.attribute-card span {
  display: grid;
  gap: 0.2rem;
}

.attribute-card strong {
  color: var(--text-primary);
  font-size: 0.95rem;
}

.attribute-card small {
  color: var(--text-muted);
  font-size: 0.82rem;
}

.attribute-card--active {
  border-color: var(--border-strong);
  background: linear-gradient(180deg, rgba(16, 185, 129, 0.08), rgba(255, 255, 255, 0.98));
  transform: translateY(-0.0625rem);
}

.btn-primary,
.btn-secondary,
.icon-button,
.text-button {
  border: none;
  font: inherit;
  cursor: pointer;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 3rem;
  padding: 0.8rem 1.15rem;
  border-radius: 0.95rem;
  text-decoration: none;
  font-weight: 800;
}

.btn-primary {
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
}

.btn-secondary {
  background: var(--surface-secondary);
  color: var(--brand-strong);
}

.icon-button {
  width: 2.9rem;
  height: 2.9rem;
  display: grid;
  place-items: center;
  border-radius: 0.85rem;
  border: 0.0625rem solid var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
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

.jobs-list {
  display: grid;
  gap: 1rem;
}

.job-row {
  display: grid;
  grid-template-columns: 5.25rem minmax(0, 1fr);
  gap: 1rem;
  padding: 1.1rem;
  background: color-mix(in srgb, var(--surface-secondary) 90%, transparent);
}

.job-logo {
  width: 5.25rem;
  height: 5.25rem;
  display: grid;
  place-items: center;
  border-radius: 1rem;
  color: #fff;
  font-size: 1.5rem;
  font-weight: 800;
  overflow: hidden;
}

.job-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.job-body {
  min-width: 0;
  display: grid;
  gap: 0.85rem;
}

.job-heading h3 {
  margin: 0 0 0.25rem;
  font-size: 1.2rem;
}

.job-actions {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: end;
  gap: 1rem;
}

.job-buttons {
  display: flex;
  gap: 0.55rem;
  flex-wrap: nowrap;
  justify-content: end;
  align-items: center;
}

.job-meta {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 2.15rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
  font-size: 0.82rem;
  font-weight: 700;
}

.meta-chip--muted {
  opacity: 0.72;
}

.job-salary {
  color: var(--text-primary);
  font-size: 1.05rem;
  font-weight: 900;
}

.text-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.65rem;
  padding: 0.58rem 0.82rem;
  border-radius: 0.8rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
  font-size: 0.94rem;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
}

.text-button.danger {
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.2rem;
  padding: 0.35rem 0.8rem;
  border-radius: 999rem;
  font-size: 0.78rem;
  font-weight: 800;
  white-space: nowrap;
}

.badge.approved {
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
}

.badge.pending {
  background: rgba(180, 83, 9, 0.1);
  color: #92400e;
}

.badge.rejected {
  background: rgba(220, 38, 38, 0.1);
  color: #b91c1c;
}

.list-grid {
  gap: 0.85rem;
}

.response-row {
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
}

.plan-card h3 {
  font-size: 1.65rem;
}

.plan-name {
  color: var(--brand-strong);
  font-size: 0.8rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

@media (max-width: 78rem) {
  .workspace--overview,
  .workspace--jobs {
    grid-template-columns: 1fr;
  }

  .form-panel {
    position: static;
  }
}

@media (max-width: 48rem) {
  .activity-grid,
  .pricing-grid,
  .field-grid,
  .upload-grid,
  .attribute-grid,
  .panel-heading,
  .job-top,
  .job-actions,
  .form-actions,
  .response-row,
  .mini-card__head {
    grid-template-columns: 1fr;
    display: grid;
  }

  .overview-state {
    width: fit-content;
  }

  .health-grid {
    grid-template-columns: 1fr;
  }

  .attribute-card {
    grid-template-columns: auto auto 1fr;
  }

  .job-row {
    grid-template-columns: 1fr;
  }

  .job-logo {
    width: 4.5rem;
    height: 4.5rem;
  }

  .btn-primary,
  .btn-secondary,
  .text-button {
    width: 100%;
  }

  .job-buttons {
    flex-direction: column;
    flex-wrap: nowrap;
  }
}
</style>
