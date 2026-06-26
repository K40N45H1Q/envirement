<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
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
  logo_url: '',
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

const isEditing = computed(() => editingId.value !== null)
const approvedCount = computed(() => jobs.value.filter((job) => job.status === 'approved').length)
const pendingCount = computed(() => jobs.value.filter((job) => job.status === 'pending').length)
const rejectedCount = computed(() => jobs.value.filter((job) => job.status === 'rejected').length)
const responsesHint = computed(() => responses.value.length)
const unreadConversations = computed(() => conversations.value.length)
const activeSectionLabel = computed(() => sections.find((item) => item.id === activeSection.value)?.label || 'Кабинет')
const latestResponses = computed(() => responses.value.slice(0, 4))
const latestConversations = computed(() => conversations.value.slice(0, 4))

const pricingPlans = [
  { name: 'Basic', price: '99 EUR', features: '1 вакансия · 30 дней публикации' },
  { name: 'Standard', price: '149 EUR', features: '3 вакансии · 30 дней публикации' },
  { name: 'Pro', price: '229 EUR', features: '5 вакансий · приоритет и аналитика' },
]

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
    error.value = 'Войдите в аккаунт работодателя, чтобы управлять вакансиями и перепиской.'
    jobs.value = []
    responses.value = []
    conversations.value = []
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  editingId.value = null
  form.value = blankForm()
}

const editJob = async (job) => {
  status.value = ''
  error.value = ''
  editingId.value = job.id
  form.value = {
    title: job.title,
    company: job.company,
    salary: job.salary,
    location: job.location,
    description: job.description,
    logo_url: job.logo || '',
  }
  await setSection('jobs')
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
    error.value = 'Не удалось сохранить вакансию. Проверьте поля и авторизацию.'
  } finally {
    isSaving.value = false
  }
}

const removeJob = async (job) => {
  const ok = window.confirm(`Удалить вакансию "${job.title}"?`)
  if (!ok) return

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
</script>

<template>
  <AppLayout>
    <main class="page">
      <aside class="sidebar">
        <button
          v-for="section in sections"
          :key="section.id"
          type="button"
          class="sidebar-link"
          :class="{ 'sidebar-link--active': activeSection === section.id }"
          @click="setSection(section.id)"
        >
          <i :class="section.icon"></i>
          <span>{{ section.label }}</span>
        </button>
      </aside>

      <section class="content">
        <section class="head">
          <div>
            <p class="eyebrow">Личный кабинет работодателя</p>
            <h1>{{ activeSectionLabel }}</h1>
            <p>
              Это единое рабочее пространство: sidebar переключает внутренние секции без ухода на другие страницы.
            </p>
          </div>
          <div class="head-actions">
            <button class="btn-secondary" type="button" @click="setSection('jobs')">
              <i class="fas fa-plus"></i>
              Новая вакансия
            </button>
          </div>
        </section>

        <section class="stats">
          <article>
            <strong>{{ jobs.length }}</strong>
            <span>Всего вакансий</span>
          </article>
          <article>
            <strong>{{ approvedCount }}</strong>
            <span>Опубликовано</span>
          </article>
          <article>
            <strong>{{ responsesHint }}</strong>
            <span>Откликов</span>
          </article>
          <article>
            <strong>{{ unreadConversations }}</strong>
            <span>Диалогов</span>
          </article>
        </section>

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
              <div class="panel-title">
                <div>
                  <p class="eyebrow compact">{{ isEditing ? 'Редактирование' : 'Новая вакансия' }}</p>
                  <h2>{{ isEditing ? 'Обновить вакансию' : 'Создать вакансию' }}</h2>
                </div>
                <button v-if="isEditing" class="icon-button" type="button" @click="resetForm">
                  <i class="fas fa-xmark"></i>
                </button>
              </div>

              <div class="field-grid">
                <label>Название<input v-model="form.title" required placeholder="Электрик" /></label>
                <label>Компания<input v-model="form.company" required placeholder="Build Solutions GmbH" /></label>
              </div>
              <div class="field-grid">
                <label>Зарплата<input v-model="form.salary" required placeholder="2 200 - 2 800 EUR" /></label>
                <label>Локация<input v-model="form.location" required placeholder="Берлин, Германия" /></label>
              </div>
              <label>Логотип URL<input v-model="form.logo_url" placeholder="https://example.com/logo.png" /></label>
              <label>
                Описание
                <textarea v-model="form.description" required rows="7" placeholder="Обязанности, требования, условия работы и график"></textarea>
              </label>

              <div class="form-actions">
                <button class="btn-primary" type="submit" :disabled="isSaving">{{ submitLabel }}</button>
                <button v-if="isEditing" class="btn-secondary" type="button" @click="resetForm">Сбросить</button>
              </div>
            </form>

            <div class="panel jobs-panel">
              <div class="panel-title">
                <div>
                  <p class="eyebrow compact">Публикации</p>
                  <h2>Мои вакансии</h2>
                </div>
                <button class="icon-button" type="button" @click="loadDashboard">
                  <i class="fas fa-rotate-right"></i>
                </button>
              </div>

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

                  <p class="job-description">{{ job.description || 'Описание пока не заполнено.' }}</p>

                  <div class="job-actions">
                    <strong>{{ job.salary }}</strong>
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
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.page { width: min(100%, var(--shell-max-width)); margin: 0 auto; padding: 2rem var(--shell-gutter) 4rem; display: grid; grid-template-columns: 16rem minmax(0, 1fr); gap: 1.25rem; }
.sidebar, .head, .panel, .stats article { border: 0.0625rem solid var(--border-subtle); border-radius: 1rem; background: var(--surface-primary); box-shadow: var(--shadow-soft); }
.sidebar { display: grid; align-content: start; gap: 0.45rem; padding: 1rem; position: sticky; top: 5.5rem; }
.sidebar-link { display: flex; gap: 0.65rem; align-items: center; min-height: 3rem; padding: 0.75rem 0.9rem; border: none; border-radius: 0.875rem; background: transparent; color: var(--text-primary); text-align: left; cursor: pointer; }
.sidebar-link:hover, .sidebar-link--active { background: linear-gradient(180deg, color-mix(in srgb, var(--brand-base) 22%, transparent), color-mix(in srgb, var(--brand-strong) 14%, transparent)); border: 0.0625rem solid var(--border-strong); }
.content, .workspace, .workspace--overview { display: grid; gap: 1.25rem; }
.head { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; padding: 1.6rem; background: radial-gradient(circle at top right, rgba(26, 177, 111, 0.14), transparent 28%), var(--surface-primary); }
.head p:not(.eyebrow), .muted, .job-description, .job-heading p { color: var(--text-muted); }
.eyebrow { margin: 0 0 0.45rem; color: var(--brand-strong); font-weight: 700; text-transform: uppercase; }
.compact { font-size: 0.76rem; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: clamp(2rem, 4vw, 3rem); color: var(--text-primary); }
.stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1.25rem; }
.stats article, .panel, .mini-card { padding: 1.25rem; }
.stats strong { display: block; color: var(--brand-strong); font-size: 2rem; }
.workspace { grid-template-columns: minmax(22rem, 30rem) minmax(0, 1fr); align-items: start; }
.panel { background: linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 92%, transparent), var(--surface-primary)), var(--surface-primary); }
.panel-title, .job-top, .job-actions, .response-row, .head-actions, .form-actions, .summary-row { display: flex; justify-content: space-between; gap: 1rem; }
.panel-title, .job-top, .job-actions, .response-row { align-items: flex-start; }
.summary-row, .overview-grid, .pricing-grid, .field-grid { display: grid; gap: 1rem; }
.overview-grid, .pricing-grid, .field-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.field-grid label, label { display: grid; gap: 0.45rem; color: var(--text-primary); font-weight: 700; }
input, textarea { width: 100%; min-height: 3.15rem; padding: 0.9rem 1rem; border: 0.0625rem solid var(--border-subtle); border-radius: 0.875rem; background: var(--surface-secondary); color: var(--text-primary); font: inherit; }
textarea { resize: vertical; min-height: 10rem; }
.btn-primary, .btn-secondary, .icon-button, .text-button { border: 0; font: inherit; cursor: pointer; }
.btn-primary, .btn-secondary { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; min-height: 3rem; padding: 0.75rem 1.1rem; border-radius: 0.875rem; text-decoration: none; }
.btn-primary { background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%); color: #fff; font-weight: 800; }
.btn-secondary { border: 0.125rem solid var(--border-strong); background: var(--surface-secondary); color: var(--brand-strong); font-weight: 800; }
.icon-button { width: 2.7rem; height: 2.7rem; display: grid; place-items: center; border: 0.0625rem solid var(--border-strong); border-radius: 0.75rem; background: color-mix(in srgb, var(--brand-soft) 70%, transparent); color: var(--brand-strong); }
.status, .state { padding: 0.95rem 1rem; border-radius: 0.875rem; }
.success, .state { border: 0.0625rem solid var(--border-strong); background: color-mix(in srgb, var(--brand-soft) 72%, transparent); color: var(--brand-strong); }
.danger { border: 0.0625rem solid rgba(220, 38, 38, 0.14); background: rgba(220, 38, 38, 0.08); color: #b91c1c; }
.summary-pill { display: inline-flex; align-items: center; min-height: 2.25rem; padding: 0.4rem 0.8rem; border-radius: 999rem; background: color-mix(in srgb, var(--brand-soft) 72%, transparent); color: var(--brand-strong); font-weight: 700; }
.summary-pill--warm { background: rgba(180, 83, 9, 0.1); color: #92400e; }
.summary-pill--danger { background: rgba(220, 38, 38, 0.1); color: #b91c1c; }
.job-row { display: grid; grid-template-columns: 4.5rem minmax(0, 1fr); gap: 1rem; padding: 1rem; border: 0.0625rem solid var(--border-subtle); border-radius: 1rem; background: color-mix(in srgb, var(--surface-secondary) 84%, transparent); }
.job-logo { width: 4.5rem; height: 4.5rem; display: grid; place-items: center; border-radius: 1rem; color: #fff; font-size: 1.35rem; font-weight: 800; overflow: hidden; }
.job-logo img { width: 100%; height: 100%; object-fit: cover; }
.job-body { min-width: 0; display: grid; gap: 0.8rem; }
.badge { padding: 0.45rem 0.8rem; border-radius: 999rem; font-size: 0.82rem; font-weight: 800; }
.badge.approved { background: rgba(25, 120, 90, 0.1); color: #19785a; }
.badge.pending { background: rgba(180, 83, 9, 0.1); color: #92400e; }
.badge.rejected { background: rgba(220, 38, 38, 0.1); color: #b91c1c; }
.job-buttons, .inline-item { display: flex; gap: 0.45rem; flex-wrap: wrap; }
.text-button, .inline-item { align-items: center; justify-content: center; min-height: 2.5rem; padding: 0.5rem 0.8rem; border-radius: 0.75rem; background: color-mix(in srgb, var(--brand-soft) 72%, transparent); color: var(--brand-strong); font-weight: 800; text-decoration: none; }
.text-button.danger { background: rgba(220, 38, 38, 0.08); color: #b91c1c; }
.mini-card { border: 0.0625rem solid var(--border-subtle); border-radius: 1rem; background: color-mix(in srgb, var(--surface-secondary) 90%, transparent); display: grid; gap: 0.75rem; }
.inline-item { justify-content: space-between; }
.inline-item span { color: var(--text-muted); font-weight: 600; }
.response-row { padding: 1rem; border: 0.0625rem solid var(--border-subtle); border-radius: 1rem; background: color-mix(in srgb, var(--surface-secondary) 88%, transparent); margin-top: 0.75rem; }
.plan-name { color: var(--brand-strong); font-size: 0.9rem; text-transform: uppercase; }
@media (max-width: 72rem) { .page, .workspace { grid-template-columns: 1fr; } .sidebar { position: static; grid-auto-flow: column; grid-auto-columns: minmax(10.5rem, 1fr); overflow-x: auto; } }
@media (max-width: 48rem) { .stats, .overview-grid, .pricing-grid, .field-grid { grid-template-columns: 1fr; } .head, .panel-title, .job-top, .job-actions, .response-row, .head-actions, .form-actions { display: grid; } .btn-primary, .btn-secondary { width: 100%; } .page { padding-top: 1.25rem; } }
</style>
