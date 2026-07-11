<script setup>
import { ref } from 'vue'
import { useI18n } from '@/i18n'

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
    default: '',
  },
})

const emit = defineEmits(['approve', 'reject', 'delete'])
const { language, t } = useI18n()
const previewJob = ref(null)
const bannerModalJob = ref(null)

const formatDate = (value) => {
  if (!value) return '-'
  const locale = language.value === 'lv' ? 'lv-LV' : language.value === 'en' ? 'en-GB' : 'ru-RU'
  return new Intl.DateTimeFormat(locale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

const statusLabel = (value) => t(`aPanelJobs.statuses.${value || 'inactive'}`)

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
  return text || t('aPanelJobs.descriptionFallback')
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
            <th>{{ t('aPanelJobs.vacancyColumn') }}</th>
            <th>{{ t('aPanelJobs.companyColumn') }}</th>
            <th>{{ t('aPanelJobs.statusColumn') }}</th>
            <th>{{ t('aPanelJobs.locationColumn') }}</th>
            <th>{{ t('aPanelJobs.salaryColumn') }}</th>
            <th>{{ t('aPanelJobs.createdColumn') }}</th>
            <th>{{ t('aPanelJobs.actionsColumn') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id">
            <td>
              <div class="apanel-job-title">
                <span>{{ job.title }}</span>
                <small>{{ job.location || t('aPanelJobs.locationMissing') }}</small>
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
              <button type="button" class="apanel-icon-button apanel-icon-button--preview" :title="t('aPanelJobs.preview')" :aria-label="t('aPanelJobs.preview')" @click="previewJob = job">
                <i class="fas fa-eye"></i>
              </button>
              <button v-if="canModerateJob(job)" type="button" class="apanel-icon-button apanel-icon-button--approve" :title="t('aPanelJobs.approve')" :aria-label="t('aPanelJobs.approve')" @click="emit('approve', job)">
                <i class="fas fa-check"></i>
              </button>
              <button v-if="canModerateJob(job)" type="button" class="apanel-icon-button apanel-icon-button--reject" :title="t('aPanelJobs.reject')" :aria-label="t('aPanelJobs.reject')" @click="emit('reject', job)">
                <i class="fas fa-xmark"></i>
              </button>
              <button type="button" class="apanel-icon-button apanel-icon-button--danger" :title="t('aPanelJobs.delete')" :aria-label="t('aPanelJobs.delete')" @click="emit('delete', job)">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else class="apanel-empty">{{ emptyText || t('aPanelJobs.emptyText') }}</p>
    </div>

    <div v-if="previewJob" class="apanel-preview">
      <div class="apanel-preview-toolbar">
        <strong>{{ t('aPanelJobs.previewTitle') }}</strong>
        <button type="button" class="apanel-icon-button" :title="t('aPanelJobs.close')" :aria-label="t('aPanelJobs.close')" @click="previewJob = null">
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
            <p>{{ t('aPanelJobs.vacancyLabel') }}</p>
            <h1>{{ previewJob.title }}</h1>
            <p>{{ previewJob.company || t('aPanelJobs.companyMissing') }} · {{ previewJob.location || t('aPanelJobs.locationMissing') }}</p>
          </div>

          <aside>
            <strong>{{ previewJob.salary || t('aPanelJobs.salaryFallback') }}</strong>
            <span>{{ t('aPanelJobs.currentRate') }}</span>
            <span class="job-preview-link">{{ t('aPanelJobs.allJobs') }}</span>
          </aside>
        </section>

        <section class="job-preview-grid">
          <article class="job-preview-panel">
            <h2>{{ t('aPanelJobs.descriptionTitle') }}</h2>
            <div class="job-preview-wrapper" :class="{ 'job-preview-wrapper--text-only': !previewJob.banner_url }">
              <button
                v-if="previewJob.banner_url"
                type="button"
                class="job-preview-banner-button"
                :aria-label="t('aPanelJobs.openBanner', { title: previewJob.title })"
                @click="openBannerModal(previewJob)"
              >
                <img class="job-preview-banner" :src="previewJob.banner_url" :alt="previewJob.title" />
              </button>
              <p>{{ previewDescription(previewJob) }}</p>
            </div>
          </article>

          <section class="job-preview-panel job-preview-facts">
            <dl>
              <div>
                <dt>{{ t('aPanelJobs.locationColumn') }}</dt>
                <dd>{{ previewJob.location || '-' }}</dd>
              </div>
              <div>
                <dt>{{ t('aPanelJobs.salaryColumn') }}</dt>
                <dd>{{ previewJob.salary || '-' }}</dd>
              </div>
              <div>
                <dt>{{ t('aPanelJobs.statusColumn') }}</dt>
                <dd>{{ statusLabel(previewJob.status) }}</dd>
              </div>
            </dl>
          </section>
        </section>
      </main>
    </div>

    <div v-if="bannerModalJob" class="banner-modal" role="dialog" aria-modal="true" @click.self="bannerModalJob = null">
      <button type="button" class="banner-modal__close" :aria-label="t('aPanelJobs.close')" @click="bannerModalJob = null">
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

.apanel-job-title {
  display: grid;
  gap: 0.2rem;
}

.apanel-job-title small {
  color: var(--text-muted);
}

.apanel-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.38rem 0.72rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.08);
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 800;
}

.apanel-pill--pending {
  background: #fff6db;
  color: #b45309;
}

.apanel-pill--approved,
.apanel-pill--active {
  background: color-mix(in srgb, var(--brand-soft) 70%, white);
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
}

.apanel-icon-button {
  width: 2.35rem;
  height: 2.35rem;
  border: 0;
  border-radius: 0.72rem;
  background: rgba(15, 23, 42, 0.06);
  color: var(--text-primary);
}

.apanel-icon-button--approve {
  color: var(--brand-strong);
}

.apanel-icon-button--reject,
.apanel-icon-button--danger {
  color: #be123c;
}

.apanel-empty {
  margin: 0;
  padding: 1rem 1.1rem;
  color: var(--text-muted);
}

.apanel-preview {
  border-top: 0.0625rem solid var(--border-subtle);
}

.apanel-preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.1rem;
}

.job-preview-page {
  display: grid;
  gap: 1rem;
  padding: 0 1.1rem 1.1rem;
}

.job-preview-hero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border-radius: 1rem;
  background: linear-gradient(135deg, rgba(25, 120, 90, 0.08), rgba(37, 99, 235, 0.06));
}

.job-preview-logo {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.96);
  font-weight: 800;
  color: var(--brand-strong);
}

.job-preview-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.job-preview-hero p,
.job-preview-hero span {
  color: var(--text-muted);
}

.job-preview-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(16rem, 1fr);
  gap: 1rem;
}

.job-preview-panel {
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
}

.job-preview-wrapper {
  display: grid;
  gap: 1rem;
}

.job-preview-banner-button {
  border: 0;
  padding: 0;
  background: transparent;
}

.job-preview-banner {
  width: 100%;
  border-radius: 0.9rem;
  object-fit: cover;
}

.job-preview-facts dl {
  display: grid;
  gap: 0.8rem;
  margin: 0;
}

.job-preview-facts dt {
  color: var(--text-muted);
  font-size: 0.82rem;
}

.job-preview-facts dd {
  margin: 0.25rem 0 0;
  color: var(--text-primary);
  font-weight: 700;
}

.banner-modal {
  position: fixed;
  inset: 0;
  z-index: 30;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.74);
}

.banner-modal img {
  max-width: min(92vw, 70rem);
  max-height: 88vh;
  border-radius: 1rem;
}

.banner-modal__close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 2.8rem;
  height: 2.8rem;
  border: 0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}

@media (max-width: 64rem) {
  .job-preview-hero,
  .job-preview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
