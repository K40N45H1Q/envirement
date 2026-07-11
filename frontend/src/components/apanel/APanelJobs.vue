<script setup>
import { ref } from 'vue'

const props = defineProps({
  jobs: {
    type: Array,
    default: () => [],
  },
  moderation: {
    type: Boolean,
    default: false,
  },
  emptyText: {
    type: String,
    default: 'Нет вакансий',
  },
})

const emit = defineEmits(['approve', 'reject', 'delete'])
const previewJob = ref(null)
const bannerModalJob = ref(null)

const formatDate = (value) => {
  if (!value) return '-'
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

const statusLabel = (value) => {
  const labels = {
    pending: 'На модерации',
    approved: 'Одобрена',
    rejected: 'Отклонена',
    active: 'Активна',
    inactive: 'Неактивна',
  }
  return labels[value] || value || '-'
}

const jobInitials = (job) => {
  const source = job?.company || job?.title || '?'
  return source
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('')
}

const previewDescription = (job) => {
  const text = (job?.description || '').trim()
  return text || 'Описание вакансии не указано.'
}

const canModerateJob = (job) => props.moderation || job?.status === 'pending'

const openBannerModal = (job) => {
  if (!job?.banner_url) return
  bannerModalJob.value = job
}
</script>

<template>
  <section class="apanel-card">
    <div class="apanel-table-wrap">
      <table v-if="jobs.length" class="apanel-table">
        <thead>
          <tr>
            <th>Вакансия</th>
            <th>Компания</th>
            <th>Статус</th>
            <th>Локация</th>
            <th>Зарплата</th>
            <th>Создана</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id">
            <td>
              <div class="apanel-job-title">
                <span>{{ job.title }}</span>
                <small>{{ job.location || 'Локация не указана' }}</small>
              </div>
            </td>
            <td>{{ job.company || '-' }}</td>
            <td>
              <span class="apanel-pill" :class="`apanel-pill--${job.status || 'default'}`">
                {{ statusLabel(job.status) }}
              </span>
            </td>
            <td>{{ job.location || '-' }}</td>
            <td>{{ job.salary || '-' }}</td>
            <td>{{ formatDate(job.created_at) }}</td>
            <td class="apanel-actions">
              <button type="button" class="apanel-icon-button apanel-icon-button--preview" title="Предпросмотр" aria-label="Предпросмотр" @click="previewJob = job">
                <i class="fas fa-eye"></i>
              </button>
              <button v-if="canModerateJob(job)" type="button" class="apanel-icon-button apanel-icon-button--approve" title="Одобрить" aria-label="Одобрить" @click="emit('approve', job)">
                <i class="fas fa-check"></i>
              </button>
              <button v-if="canModerateJob(job)" type="button" class="apanel-icon-button apanel-icon-button--reject" title="Отклонить" aria-label="Отклонить" @click="emit('reject', job)">
                <i class="fas fa-xmark"></i>
              </button>
              <button type="button" class="apanel-icon-button apanel-icon-button--danger" title="Удалить" aria-label="Удалить" @click="emit('delete', job)">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else class="apanel-empty">{{ emptyText }}</p>
    </div>

    <div v-if="previewJob" class="apanel-preview">
      <div class="apanel-preview-toolbar">
        <strong>Предпросмотр страницы вакансии</strong>
        <button type="button" class="apanel-icon-button" title="Закрыть" aria-label="Закрыть" @click="previewJob = null">
          <i class="fas fa-xmark"></i>
        </button>
      </div>

      <main class="job-preview-page">
        <section class="job-preview-hero">
          <div class="job-preview-logo">
            <img v-if="previewJob.logo" :src="previewJob.logo" :alt="previewJob.company || previewJob.title" />
            <span v-else>{{ jobInitials(previewJob) }}</span>
          </div>

          <div>
            <p>Вакансия</p>
            <h1>{{ previewJob.title }}</h1>
            <p>{{ previewJob.company || 'Компания не указана' }} · {{ previewJob.location || 'Локация не указана' }}</p>
          </div>

          <aside>
            <strong>{{ previewJob.salary || 'По договорённости' }}</strong>
            <span>Актуальная ставка</span>
            <span class="job-preview-link">Все вакансии</span>
          </aside>
        </section>

        <section class="job-preview-grid">
          <article class="job-preview-panel">
            <h2>Описание вакансии</h2>
            <div class="job-preview-wrapper" :class="{ 'job-preview-wrapper--text-only': !previewJob.banner_url }">
              <button
                v-if="previewJob.banner_url"
                type="button"
                class="job-preview-banner-button"
                :aria-label="`Открыть баннер вакансии ${previewJob.title}`"
                @click="openBannerModal(previewJob)"
              >
                <img
                  class="job-preview-banner"
                  :src="previewJob.banner_url"
                  :alt="previewJob.title"
                />
              </button>
              <p>{{ previewDescription(previewJob) }}</p>
            </div>
          </article>

          <section class="job-preview-panel job-preview-facts">
            <dl>
              <div>
                <dt>Локация</dt>
                <dd>{{ previewJob.location || '-' }}</dd>
              </div>
              <div>
                <dt>Зарплата</dt>
                <dd>{{ previewJob.salary || '-' }}</dd>
              </div>
              <div>
                <dt>Статус</dt>
                <dd>{{ statusLabel(previewJob.status) }}</dd>
              </div>
            </dl>
          </section>
        </section>
      </main>
    </div>

    <div v-if="bannerModalJob" class="banner-modal" role="dialog" aria-modal="true" @click.self="bannerModalJob = null">
      <button type="button" class="banner-modal__close" aria-label="Закрыть" @click="bannerModalJob = null">
        <i class="fas fa-xmark"></i>
      </button>
      <img :src="bannerModalJob.banner_url" :alt="bannerModalJob.title" />
    </div>
  </section>
</template>

<style scoped>
.apanel-card {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(250, 253, 251, 0.98)),
    var(--surface-primary);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
}

.apanel-table-wrap {
  width: 100%;
  overflow-x: auto;
}

.apanel-table {
  width: 100%;
  min-width: 52rem;
  border-collapse: separate;
  border-spacing: 0;
}

.apanel-table th,
.apanel-table td {
  padding: 0.85rem 0.8rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
  color: var(--text-primary);
  text-align: left;
  vertical-align: middle;
}

.apanel-table th {
  background: color-mix(in srgb, var(--brand-soft) 42%, white);
  color: color-mix(in srgb, var(--text-muted) 86%, var(--brand-strong));
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.apanel-table tbody tr:last-child td {
  border-bottom: 0;
}

.apanel-table tbody tr:hover {
  background: color-mix(in srgb, var(--brand-soft) 34%, transparent);
}

.apanel-job-title {
  display: grid;
  gap: 0.18rem;
}

.apanel-job-title span {
  font-weight: 850;
}

.apanel-job-title small {
  color: var(--text-muted);
}

.apanel-pill {
  display: inline-flex;
  min-height: 1.8rem;
  align-items: center;
  padding: 0.25rem 0.65rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 76%, white);
  color: var(--brand-strong);
  font-size: 0.78rem;
  font-weight: 800;
}

.apanel-pill--pending {
  background: #fff7ed;
  color: #c2410c;
}

.apanel-pill--approved,
.apanel-pill--active {
  background: color-mix(in srgb, var(--brand-soft) 78%, white);
  color: var(--brand-strong);
}

.apanel-pill--rejected,
.apanel-pill--inactive {
  background: #fff1f2;
  color: #be123c;
}

.apanel-actions {
  display: flex;
  gap: 0.45rem;
  white-space: nowrap;
}

.apanel-icon-button {
  width: 2.25rem;
  height: 2.25rem;
  display: inline-grid;
  place-items: center;
  border: 0.0625rem solid color-mix(in srgb, var(--border-subtle) 65%, var(--brand-base));
  border-radius: 0.72rem;
  background: linear-gradient(180deg, #ffffff, color-mix(in srgb, var(--brand-soft) 34%, white));
  color: var(--brand-strong);
  cursor: pointer;
  box-shadow: 0 0.45rem 1rem rgba(15, 23, 42, 0.06);
  transition:
    transform 0.16s ease,
    border-color 0.16s ease,
    color 0.16s ease,
    box-shadow 0.16s ease;
}

.apanel-icon-button i {
  font-size: 0.9rem;
  line-height: 1;
}

.apanel-icon-button:hover {
  transform: translateY(-0.08rem);
  border-color: color-mix(in srgb, var(--brand-base) 45%, var(--border-subtle));
  box-shadow: 0 0.7rem 1.25rem rgba(22, 155, 97, 0.12);
}

.apanel-icon-button--approve {
  border-color: color-mix(in srgb, var(--brand-base) 45%, var(--border-subtle));
  background: linear-gradient(135deg, var(--brand-base), var(--brand-strong));
  color: white;
  box-shadow: 0 0.6rem 1.1rem rgba(22, 155, 97, 0.18);
}

.apanel-icon-button--approve:hover {
  color: white;
}

.apanel-icon-button--reject {
  border-color: #fed7aa;
  background: #fff7ed;
  color: #c2410c;
}

.apanel-icon-button--danger {
  border-color: #fecdd3;
  background: #fff1f2;
  color: #be123c;
}

.apanel-icon-button--preview {
  border-color: color-mix(in srgb, var(--border-subtle) 55%, var(--brand-base));
  background: color-mix(in srgb, var(--brand-soft) 64%, white);
  color: var(--brand-strong);
}

.apanel-empty {
  margin: 0;
  padding: 3rem 1.5rem;
  color: var(--text-muted);
  text-align: center;
  font-weight: 800;
}

.apanel-preview {
  margin: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--surface-secondary) 80%, white);
  overflow: hidden;
}

.apanel-preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 1rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
  background: white;
}

.job-preview-page {
  display: grid;
  gap: 1rem;
  padding: 1rem;
}

.job-preview-page :is(h1, h2, p) {
  margin: 0;
}

.job-preview-hero,
.job-preview-panel {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.job-preview-hero {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 1.25rem;
  overflow: hidden;
  padding: 2rem;
}

.job-preview-hero::before {
  position: absolute;
  inset: 0 0 auto;
  height: 0.22rem;
  background: linear-gradient(90deg, var(--brand-base), color-mix(in srgb, var(--brand-base) 20%, white));
  content: "";
}

.job-preview-hero > div:nth-child(2),
.job-preview-hero aside,
.job-preview-panel {
  display: grid;
  gap: 1rem;
}

.job-preview-hero p,
.job-preview-hero span,
.job-preview-facts dt {
  color: var(--text-muted);
}

.job-preview-hero h1 {
  font-size: clamp(1.65rem, 2.6vw, 2.6rem);
  line-height: 1.08;
}

.job-preview-hero aside {
  justify-items: end;
  text-align: right;
}

.job-preview-hero strong {
  color: var(--brand-strong);
  font-size: clamp(1.45rem, 2vw, 2rem);
}

.job-preview-link {
  color: var(--brand-strong);
  font-weight: 700;
}

.job-preview-logo {
  width: 5rem;
  height: 5rem;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 1rem;
  background: var(--brand-strong);
  color: #fff;
  font-weight: 900;
}

.job-preview-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: white;
}

.job-preview-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.job-preview-panel {
  width: 100%;
  padding: 1.5rem;
}

.job-preview-wrapper {
  display: grid;
  grid-template-columns: minmax(18rem, 0.85fr) minmax(0, 1fr);
  gap: 1rem;
  align-items: stretch;
}

.job-preview-wrapper--text-only {
  grid-template-columns: 1fr;
}

.job-preview-banner-button {
  min-height: 0;
  padding: 0;
  border: 0;
  border-radius: 1rem;
  background: var(--surface-secondary);
  cursor: zoom-in;
  overflow: hidden;
}

.job-preview-banner {
  width: 100%;
  height: 100%;
  max-height: 31rem;
  display: block;
  object-fit: contain;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 80%, white);
}

.job-preview-wrapper p {
  min-height: 16rem;
  max-height: 31rem;
  margin: 0;
  padding: 1.25rem;
  overflow-y: auto;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
  line-height: 1.65;
  white-space: pre-wrap;
}

.job-preview-facts dl {
  width: 100%;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.job-preview-facts dl > div {
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
}

.job-preview-facts dd {
  margin: 0;
  color: var(--text-primary);
  font-weight: 800;
}

.banner-modal {
  position: fixed;
  z-index: 1000;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 2rem;
  background: rgba(15, 23, 42, 0.82);
}

.banner-modal img {
  max-width: min(96vw, 90rem);
  max-height: 90vh;
  border-radius: 1rem;
  background: white;
  object-fit: contain;
  box-shadow: 0 1.5rem 4rem rgba(0, 0, 0, 0.35);
}

.banner-modal__close {
  position: fixed;
  top: 1.2rem;
  right: 1.2rem;
  width: 2.8rem;
  height: 2.8rem;
  display: grid;
  place-items: center;
  border: 0.0625rem solid rgba(255, 255, 255, 0.24);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.14);
  color: white;
  cursor: pointer;
}

@media (max-width: 60rem) {
  .job-preview-hero,
  .job-preview-wrapper,
  .job-preview-facts dl {
    grid-template-columns: 1fr;
  }

  .job-preview-hero {
    padding: 1rem;
  }

  .job-preview-hero aside {
    justify-items: start;
    text-align: left;
  }

  .job-preview-panel {
    padding: 1rem;
  }
}
</style>
