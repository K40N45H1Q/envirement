<script setup>
import { computed, onMounted, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { createJob, deleteJob, getMyJobs, updateJob } from '@/api/jobs'
import { normalizeJob } from '@/utils/jobs'

const blankForm = () => ({
  title: '',
  company: '',
  salary: '',
  location: '',
  description: '',
  logo_url: '',
})

const jobs = ref([])
const isLoading = ref(false)
const isSaving = ref(false)
const deletingId = ref(null)
const editingId = ref(null)
const status = ref('')
const error = ref('')
const form = ref(blankForm())

const isEditing = computed(() => editingId.value !== null)
const approvedCount = computed(() => jobs.value.filter((job) => job.status === 'approved').length)
const pendingCount = computed(() => jobs.value.filter((job) => job.status === 'pending').length)
const rejectedCount = computed(() => jobs.value.filter((job) => job.status === 'rejected').length)
const responsesHint = computed(() => jobs.value.length ? Math.max(jobs.value.length * 3, 8) : 0)

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
  isLoading.value = true
  error.value = ''

  try {
    const data = await getMyJobs()
    jobs.value = Array.isArray(data) ? data.map(normalizeJob) : []
  } catch {
    error.value = 'Войдите в аккаунт работодателя, чтобы управлять вакансиями.'
    jobs.value = []
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  editingId.value = null
  form.value = blankForm()
}

const editJob = (job) => {
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
}

const submitJob = async () => {
  status.value = ''
  error.value = ''
  isSaving.value = true

  try {
    if (isEditing.value) {
      await updateJob(editingId.value, form.value)
      status.value = 'Вакансия обновлена и отправлена на повторную проверку.'
    } else {
      await createJob(form.value)
      status.value = 'Вакансия сохранена и отправлена на модерацию.'
    }

    resetForm()
    await loadMyJobs()
  } catch {
    error.value = 'Не удалось сохранить вакансию. Проверьте обязательные поля и авторизацию.'
  } finally {
    isSaving.value = false
  }
}

const removeJob = async (job) => {
  const ok = window.confirm(`Удалить вакансию "${job.title}"? Это действие нельзя отменить.`)
  if (!ok) return

  deletingId.value = job.id
  status.value = ''
  error.value = ''

  try {
    await deleteJob(job.id)
    status.value = 'Вакансия удалена.'
    if (editingId.value === job.id) resetForm()
    await loadMyJobs()
  } catch {
    error.value = 'Не удалось удалить вакансию. Возможно, она уже удалена или у вас нет доступа.'
  } finally {
    deletingId.value = null
  }
}

onMounted(loadMyJobs)
</script>

<template>
  <AppLayout>
    <main class="page">
      <aside class="sidebar">
        <RouterLink to="/employer-dashboard"><i class="fas fa-table-columns"></i> Кабинет</RouterLink>
        <RouterLink to="/responses"><i class="fas fa-user-check"></i> Отклики</RouterLink>
        <RouterLink to="/messages"><i class="fas fa-message"></i> Сообщения</RouterLink>
        <RouterLink to="/pricing"><i class="fas fa-credit-card"></i> Тарифы</RouterLink>
      </aside>

      <section class="content">
        <section class="head">
          <div>
            <p class="eyebrow">Личный кабинет работодателя</p>
            <h1>Вакансии и отклики</h1>
            <p>
              Создавайте вакансии, обновляйте условия, управляйте публикациями и следите
              за статусом модерации без лишних шагов.
            </p>
          </div>
          <div class="head-actions">
            <RouterLink to="/responses" class="btn-secondary">
              <i class="fas fa-chart-simple"></i>
              Смотреть отклики
            </RouterLink>
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
            <strong>{{ pendingCount }}</strong>
            <span>На модерации</span>
          </article>
          <article>
            <strong>{{ responsesHint }}</strong>
            <span>Кандидатов в работе</span>
          </article>
        </section>

        <section class="workspace">
          <form class="panel form-panel" @submit.prevent="submitJob">
            <div class="panel-title">
              <div>
                <p class="eyebrow compact">{{ isEditing ? 'Редактирование' : 'Новая вакансия' }}</p>
                <h2>{{ isEditing ? 'Обновить вакансию' : 'Создать вакансию' }}</h2>
              </div>
              <button
                v-if="isEditing"
                class="icon-button"
                type="button"
                aria-label="Отменить редактирование"
                @click="resetForm"
              >
                <i class="fas fa-xmark"></i>
              </button>
            </div>

            <p class="panel-note">
              Поля вакансии сохраняются в backend. Логотип необязателен: если оставить
              поле пустым, карточка покажет аккуратные инициалы компании.
            </p>

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

            <label>
              Логотип URL
              <input v-model="form.logo_url" placeholder="https://example.com/logo.png" />
            </label>

            <label>
              Описание
              <textarea
                v-model="form.description"
                required
                rows="7"
                placeholder="Обязанности, требования, условия работы и график"
              ></textarea>
            </label>

            <div class="form-actions">
              <button class="btn-primary" type="submit" :disabled="isSaving">
                {{ submitLabel }}
              </button>
              <button
                v-if="isEditing"
                class="btn-secondary"
                type="button"
                @click="resetForm"
              >
                Сбросить
              </button>
            </div>

            <p v-if="status" class="status success">{{ status }}</p>
            <p v-if="error" class="status danger">{{ error }}</p>
          </form>

          <div class="panel jobs-panel">
            <div class="panel-title">
              <div>
                <p class="eyebrow compact">Публикации</p>
                <h2>Мои вакансии</h2>
              </div>
              <button class="icon-button" type="button" aria-label="Обновить вакансии" @click="loadMyJobs">
                <i class="fas fa-rotate-right"></i>
              </button>
            </div>

            <div class="summary-row">
              <span class="summary-pill">Опубликовано: {{ approvedCount }}</span>
              <span class="summary-pill summary-pill--warm">На модерации: {{ pendingCount }}</span>
              <span v-if="rejectedCount" class="summary-pill summary-pill--danger">Отклонено: {{ rejectedCount }}</span>
            </div>

            <p v-if="isLoading" class="state">Загрузка вакансий...</p>

            <article v-for="job in jobs" v-else :key="job.id" class="job-row">
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

                <p class="job-description">
                  {{ job.description || 'Описание пока не заполнено.' }}
                </p>

                <div class="job-actions">
                  <strong>{{ job.salary }}</strong>
                  <div class="job-buttons">
                    <RouterLink
                      v-if="job.status === 'approved'"
                      :to="`/jobs/${job.id}`"
                      class="text-button"
                    >
                      Открыть
                    </RouterLink>
                    <button type="button" class="text-button" @click="editJob(job)">
                      Редактировать
                    </button>
                    <button
                      type="button"
                      class="text-button danger"
                      :disabled="deletingId === job.id"
                      @click="removeJob(job)"
                    >
                      {{ deletingId === job.id ? 'Удаление...' : 'Удалить' }}
                    </button>
                  </div>
                </div>
              </div>
            </article>

            <p v-if="!isLoading && !jobs.length" class="state">
              Вакансий пока нет. Создайте первую позицию, и она появится здесь сразу после сохранения.
            </p>
          </div>
        </section>
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
  grid-template-columns: 16rem minmax(0, 1fr);
  gap: 1.25rem;
}

.sidebar,
.head,
.panel,
.stats article {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.sidebar {
  display: grid;
  align-content: start;
  gap: 0.45rem;
  padding: 1rem;
  position: sticky;
  top: 5.5rem;
}

.sidebar a {
  display: flex;
  gap: 0.65rem;
  align-items: center;
  min-height: 3rem;
  padding: 0.75rem 0.9rem;
  border-radius: 0.875rem;
  color: var(--text-primary);
  text-decoration: none;
  transition: background 0.2s ease, color 0.2s ease;
}

.sidebar a:hover,
.sidebar a:focus-visible {
  background: color-mix(in srgb, var(--brand-soft) 60%, transparent);
  color: var(--brand-strong);
}

.sidebar a.router-link-active {
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--brand-base) 22%, transparent),
    color-mix(in srgb, var(--brand-strong) 14%, transparent)
  );
  color: var(--text-primary);
  border: 0.0625rem solid var(--border-strong);
}

.content {
  display: grid;
  gap: 1.25rem;
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.6rem;
  background:
    radial-gradient(circle at top right, rgba(26, 177, 111, 0.14), transparent 28%),
    var(--surface-primary);
}

.head p:not(.eyebrow) {
  max-width: 48rem;
  margin: 0.7rem 0 0;
  color: var(--text-muted);
}

.head-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
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

h1,
h2,
h3 {
  margin: 0;
  color: var(--text-primary);
}

h1 {
  font-size: clamp(2rem, 4vw, 3rem);
}

h2 {
  font-size: 1.45rem;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1.25rem;
}

.stats article {
  padding: 1.25rem;
}

.stats strong {
  display: block;
  color: var(--brand-strong);
  font-size: 2rem;
}

.stats span,
.job-top p,
.job-description {
  color: var(--text-muted);
}

.workspace {
  display: grid;
  grid-template-columns: minmax(22rem, 30rem) minmax(0, 1fr);
  gap: 1.25rem;
  align-items: start;
}

.panel {
  display: grid;
  gap: 1rem;
  padding: 1.5rem;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 92%, transparent), var(--surface-primary)),
    var(--surface-primary);
}

.panel-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.panel-note {
  margin: 0;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: color-mix(in srgb, var(--surface-secondary) 80%, transparent);
  color: var(--text-muted);
  line-height: 1.6;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
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
  min-width: 0;
  min-height: 3.15rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

textarea {
  resize: vertical;
  min-height: 10rem;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: var(--border-strong);
  box-shadow: 0 0 0 0.1875rem rgba(29, 168, 107, 0.12);
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
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
  box-shadow: 0 0.875rem 1.8rem rgba(21, 149, 93, 0.18);
}

.btn-secondary {
  border: 0.125rem solid var(--border-strong);
  background: var(--surface-secondary);
  color: var(--brand-strong);
  font-weight: 800;
}

.btn-primary:disabled,
.text-button:disabled {
  cursor: wait;
  opacity: 0.65;
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
  margin: 0;
  padding: 0.95rem 1rem;
  border-radius: 0.875rem;
  border: 0.0625rem solid transparent;
}

.success,
.state {
  border-color: var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
}

.danger {
  border-color: rgba(220, 38, 38, 0.14);
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.summary-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
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
  gap: 0.8rem;
}

.job-top,
.job-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.job-heading p,
.job-description {
  margin: 0.25rem 0 0;
}

.job-description {
  line-height: 1.6;
}

.badge {
  flex: 0 0 auto;
  padding: 0.45rem 0.8rem;
  border-radius: 999rem;
  background: rgba(30, 35, 38, 0.08);
  color: rgba(30, 35, 38, 0.7);
  font-size: 0.82rem;
  font-weight: 800;
}

.badge.approved {
  background: rgba(25, 120, 90, 0.1);
  color: #19785a;
}

.badge.pending {
  background: rgba(180, 83, 9, 0.1);
  color: #92400e;
}

.badge.rejected {
  background: rgba(220, 38, 38, 0.1);
  color: #b91c1c;
}

.job-actions {
  align-items: center;
}

.job-actions strong {
  color: var(--brand-strong);
  font-size: 1.1rem;
}

.job-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.45rem;
}

.text-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.5rem;
  padding: 0.5rem 0.8rem;
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
  font-weight: 800;
  text-decoration: none;
}

.text-button.danger {
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

@media (max-width: 72rem) {
  .page,
  .workspace {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    grid-auto-flow: column;
    grid-auto-columns: minmax(10.5rem, 1fr);
    overflow-x: auto;
    padding-bottom: 0.9rem;
    scrollbar-width: thin;
  }
}

@media (max-width: 48rem) {
  .head,
  .field-grid,
  .stats {
    grid-template-columns: 1fr;
    display: grid;
  }

  .head-actions,
  .form-actions,
  .job-actions,
  .job-top {
    display: grid;
  }

  .sidebar {
    grid-auto-columns: minmax(12rem, 1fr);
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }

  .job-buttons {
    justify-content: flex-start;
  }

  .page {
    padding-top: 1.25rem;
  }

  .head,
  .panel,
  .stats article {
    padding: 1.15rem;
  }
}
</style>
