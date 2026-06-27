<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
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
  { id: 'overview', label: 'Кабинет', icon: 'fas fa-table-columns' },
  { id: 'jobs', label: 'Вакансии', icon: 'fas fa-briefcase' },
  { id: 'responses', label: 'Отклики', icon: 'fas fa-user-check' },
  { id: 'messages', label: 'Сообщения', icon: 'fas fa-message' },
  { id: 'pricing', label: 'Тарифы', icon: 'fas fa-credit-card' },
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
        <button class="btn-secondary" type="button" @click="setSection('jobs')">
          <i class="fas fa-plus"></i>
          Новая вакансия
        </button>
      </template>

      <p v-if="status" class="status success">{{ status }}</p>
      <p v-if="error" class="status danger">{{ error }}</p>
      <p v-if="isLoading" class="state">Загрузка кабинета...</p>

      <template v-if="!isLoading">
        <section v-if="activeSection === 'overview'" class="workspace workspace--overview">
          <div class="panel">
            <div class="panel-title">
              <div>
                <p class="eyebrow compact">Сводка</p>
                <h2>Что происходит сейчас</h2>
              </div>
            </div>

            <div class="summary-row">
              <span class="summary-pill">Опубликовано: {{ approvedCount }}</span>
              <span class="summary-pill summary-pill--warm">На модерации: {{ pendingCount }}</span>
              <span v-if="rejectedCount" class="summary-pill summary-pill--danger">Отклонено: {{ rejectedCount }}</span>
            </div>

            <div class="overview-grid">
              <article class="mini-card">
                <h3>Последние отклики</h3>
                <p v-if="!latestResponses.length" class="muted">Пока откликов нет.</p>
                <RouterLink
                  v-for="item in latestResponses"
                  :key="item.id"
                  :to="`/messages?application=${item.id}`"
                  class="inline-item"
                >
                  <strong>{{ item.name }} {{ item.surname }}</strong>
                  <span>{{ item.job_title }}</span>
                </RouterLink>
              </article>

              <article class="mini-card">
                <h3>Последние диалоги</h3>
                <p v-if="!latestConversations.length" class="muted">Сообщений пока нет.</p>
                <RouterLink
                  v-for="conversation in latestConversations"
                  :key="conversation.application_id"
                  :to="`/messages?application=${conversation.application_id}`"
                  class="inline-item"
                >
                  <strong>{{ conversation.counterparty_name }}</strong>
                  <span>{{ conversation.job_title }}</span>
                </RouterLink>
              </article>
            </div>
          </div>
        </section>

        <section v-if="activeSection === 'jobs'" class="workspace">
          <form class="panel form-panel" @submit.prevent="submitJob">
            <div class="panel-header">
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
                <label>Название<input v-model="form.title" required placeholder="Электрик" /></label>
                <label>Компания<input v-model="form.company" required placeholder="Build Solutions GmbH" /></label>
              </div>
              <div class="field-grid">
                <label>Зарплата<input v-model="form.salary" required placeholder="2 200 - 2 800 EUR" /></label>
                <label>Локация<input v-model="form.location" required placeholder="Берлин, Германия" /></label>
              </div>
              <div class="field-grid">
                <label class="upload-field">
                  Фото вакансии
                  <input type="file" accept="image/*" @change="onLogoChange" />
                </label>
                <label>Или ссылка на изображение<input v-model="form.logo_url" placeholder="https://example.com/logo.png" /></label>
              </div>
              <div class="field-grid">
                <label class="checkbox-field">
                  <input v-model="form.has_housing" type="checkbox" />
                  <span>Есть жильё</span>
                </label>
                <label class="checkbox-field">
                  <input v-model="form.has_transport" type="checkbox" />
                  <span>Есть транспорт</span>
                </label>
              </div>
              <div v-if="logoPreview || form.logo_url" class="logo-preview">
                <img :src="logoPreview || form.logo_url" alt="Превью фото вакансии" />
              </div>
              <label>
                Описание
                <textarea v-model="form.description" required rows="7" placeholder="Обязанности, требования, условия работы и график"></textarea>
              </label>
            </div>

            <div class="form-actions">
              <button class="btn-primary" type="submit" :disabled="isSaving">{{ submitLabel }}</button>
              <button v-if="isEditing" class="btn-secondary" type="button" @click="resetForm">Сбросить</button>
            </div>
          </form>

          <div class="panel jobs-panel">
            <div class="panel-header">
              <div>
                <p class="eyebrow compact">Публикации</p>
                <h2>Мои вакансии</h2>
              </div>
              <button class="icon-button" type="button" @click="loadDashboard">
                <i class="fas fa-rotate-right"></i>
              </button>
            </div>

            <div class="jobs-list">
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
                    <span class="summary-pill" :class="{ 'summary-pill--muted': !job.has_housing }">
                      {{ job.has_housing ? 'С жильём' : 'Без жилья' }}
                    </span>
                    <span class="summary-pill" :class="{ 'summary-pill--muted': !job.has_transport }">
                      {{ job.has_transport ? 'С транспортом' : 'Без транспорта' }}
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

            <p v-if="!jobs.length" class="state">Вакансий пока нет.</p>
          </div>
        </section>

        <section v-if="activeSection === 'responses'" class="panel">
          <div class="panel-title">
            <div>
              <p class="eyebrow compact">Кандидаты</p>
              <h2>Все отклики</h2>
            </div>
          </div>

          <article v-for="item in responses" :key="item.id" class="response-row">
            <div>
              <strong>{{ item.name }} {{ item.surname }}</strong>
              <p>{{ item.job_title }} · {{ item.job_company }}</p>
            </div>
            <RouterLink :to="`/messages?application=${item.id}`" class="text-button">Открыть диалог</RouterLink>
          </article>

          <p v-if="!responses.length" class="state">Откликов пока нет.</p>
        </section>

        <section v-if="activeSection === 'messages'" class="panel">
          <div class="panel-title">
            <div>
              <p class="eyebrow compact">Переписка</p>
              <h2>Диалоги с кандидатами</h2>
            </div>
          </div>

          <article v-for="conversation in conversations" :key="conversation.application_id" class="response-row">
            <div>
              <strong>{{ conversation.counterparty_name }}</strong>
              <p>{{ conversation.job_title }} · {{ conversation.last_message }}</p>
            </div>
            <RouterLink :to="`/messages?application=${conversation.application_id}`" class="text-button">Открыть</RouterLink>
          </article>

          <p v-if="!conversations.length" class="state">Диалогов пока нет.</p>
        </section>

        <section v-if="activeSection === 'pricing'" class="panel">
          <div class="panel-title">
            <div>
              <p class="eyebrow compact">Тарифы</p>
              <h2>Пакеты для публикации</h2>
            </div>
          </div>

          <div class="pricing-grid">
            <article v-for="plan in pricingPlans" :key="plan.name" class="mini-card">
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
.btn-secondary {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.workspace,
.workspace--overview {
  display: grid;
  gap: 1.5rem;
}

.workspace {
  grid-template-columns: 1fr 1fr;
  align-items: stretch;
}

.panel,
.mini-card {
  padding: 1.5rem;
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background: linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 92%, transparent), var(--surface-primary)), var(--surface-primary);
}

.form-content,
.summary-row,
.overview-grid,
.pricing-grid,
.field-grid {
  display: grid;
  gap: 1rem;
}

.overview-grid,
.pricing-grid,
.field-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.panel-header,
.panel-title,
.job-top,
.job-actions,
.response-row,
.form-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.eyebrow {
  margin: 0 0 0.45rem;
  color: var(--brand-strong);
  font-weight: 700;
  text-transform: uppercase;
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
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
}

.muted,
.job-description,
.job-heading p {
  color: var(--text-muted);
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
  min-height: 3.15rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

textarea {
  resize: vertical;
  min-height: 10rem;
}

.btn-primary,
.btn-secondary,
.icon-button,
.text-button {
  border: 0;
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
  padding: 0.75rem 1.1rem;
  border-radius: 0.875rem;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
  font-weight: 800;
}

.btn-secondary {
  background: var(--surface-secondary);
  color: var(--brand-strong);
  font-weight: 800;
}

.icon-button {
  width: 2.7rem;
  height: 2.7rem;
  display: grid;
  place-items: center;
  border: 0.0625rem solid var(--border-strong);
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 70%, transparent);
  color: var(--brand-strong);
}

.status,
.state {
  padding: 0.95rem 1rem;
  border-radius: 0.875rem;
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

.summary-pill--warm {
  background: rgba(180, 83, 9, 0.1);
  color: #92400e;
}

.summary-pill--danger {
  background: rgba(220, 38, 38, 0.1);
  color: #b91c1c;
}

.summary-pill--muted {
  opacity: 0.75;
}

.upload-field input[type='file'] {
  padding: 0.75rem;
}

.checkbox-field {
  display: flex !important;
  align-items: center;
  gap: 0.75rem;
  min-height: 3.15rem;
  padding: 0 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: var(--surface-secondary);
}

.checkbox-field input {
  width: 1rem;
  min-height: 1rem;
  padding: 0;
}

.logo-preview {
  width: 100%;
  max-width: 10rem;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  background: var(--surface-secondary);
}

.logo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.jobs-panel {
  min-height: 0;
}

.jobs-list {
  display: grid;
  gap: 1rem;
}

.job-row {
  display: grid;
  grid-template-columns: 4.5rem minmax(0, 1fr);
  gap: 1rem;
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 84%, transparent);
}

.job-logo {
  width: 4.5rem;
  height: 4.5rem;
  display: grid;
  place-items: center;
  border-radius: 1rem;
  color: #fff;
  font-size: 1.35rem;
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
  gap: 0.75rem;
}

.job-heading h3 {
  margin: 0 0 0.25rem;
  font-size: 1.05rem;
}

.job-meta,
.job-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.job-salary {
  font-weight: 800;
  color: var(--brand-strong);
}

.text-button,
.inline-item {
  align-items: center;
  justify-content: center;
  min-height: 2.5rem;
  padding: 0.5rem 0.85rem;
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
  font-weight: 700;
  text-decoration: none;
  border: none;
  white-space: nowrap;
}

.text-button.danger {
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.inline-item {
  display: flex;
  justify-content: space-between;
}

.inline-item span {
  color: var(--text-muted);
}

.mini-card,
.response-row {
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
}

.response-row {
  padding: 1rem;
}

.plan-name {
  color: var(--brand-strong);
  font-size: 0.9rem;
  text-transform: uppercase;
}

@media (max-width: 72rem) {
  .workspace {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 48rem) {
  .overview-grid,
  .pricing-grid,
  .field-grid,
  .panel-header,
  .panel-title,
  .job-top,
  .job-actions,
  .response-row,
  .form-actions {
    grid-template-columns: 1fr;
    display: grid;
  }

  .btn-primary,
  .btn-secondary,
  .text-button {
    width: 100%;
  }

  .job-buttons {
    flex-direction: column;
  }
}
</style>
