<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '@/i18n'
import { localizeJobTitle } from '@/utils/jobs'

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
const router = useRouter()
const { language, t } = useI18n()
const previewJob = ref(null)
const bannerModalJob = ref(null)
const rejectionJob = ref(null)
const rejectionReason = ref('')
const rejectionError = ref('')
const currentPage = ref(1)
const JOBS_PER_PAGE = 5
const displayJobTitle = (job) => localizeJobTitle(job, language.value)

const buildPaginationItems = (page, total) => {
  if (total <= 7) return Array.from({ length: total }, (_, index) => index + 1)
  if (page <= 4) return [1, 2, 3, 4, 5, 'ellipsis-right', total]
  if (page >= total - 3) return [1, 'ellipsis-left', total - 4, total - 3, total - 2, total - 1, total]
  return [1, 'ellipsis-left', page - 1, page, page + 1, 'ellipsis-right', total]
}

const totalPages = computed(() => Math.max(1, Math.ceil(props.jobs.length / JOBS_PER_PAGE)))
const paginatedJobs = computed(() => {
  const start = (currentPage.value - 1) * JOBS_PER_PAGE
  return props.jobs.slice(start, start + JOBS_PER_PAGE)
})
const paginationItems = computed(() => buildPaginationItems(currentPage.value, totalPages.value))
const pageStart = computed(() => (props.jobs.length ? ((currentPage.value - 1) * JOBS_PER_PAGE) + 1 : 0))
const pageEnd = computed(() => Math.min(currentPage.value * JOBS_PER_PAGE, props.jobs.length))

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
}

watch(() => props.jobs, () => {
  if (currentPage.value > totalPages.value) currentPage.value = totalPages.value
})

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

const openBannerModal = (job) => {
  if (!job?.banner_url) return
  bannerModalJob.value = job
}

const openJobPage = (job) => {
  if (props.moderation || !job?.id) return
  router.push(`/jobs/${job.id}`)
}

const openRejectionModal = (job) => {
  rejectionJob.value = job
  rejectionReason.value = ''
  rejectionError.value = ''
}

const closeRejectionModal = () => {
  rejectionJob.value = null
  rejectionReason.value = ''
  rejectionError.value = ''
}

const submitRejection = () => {
  const reason = rejectionReason.value.trim()
  if (!reason) {
    rejectionError.value = t('aPanelJobs.rejectionReasonRequired')
    return
  }

  emit('reject', { job: rejectionJob.value, reason })
  closeRejectionModal()
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
          <tr
            v-for="job in paginatedJobs"
            :key="job.id"
            :class="{ 'apanel-job-row--clickable': !moderation }"
            :tabindex="moderation ? undefined : 0"
            :role="moderation ? undefined : 'link'"
            @click="openJobPage(job)"
            @keydown.enter="openJobPage(job)"
          >
            <td>
              <div class="apanel-job-title">
                <span>{{ displayJobTitle(job) }}</span>
                <small>{{ job.location || t('aPanelJobs.locationMissing') }}</small>
              </div>
            </td>
            <td>{{ job.company || '-' }}</td>
            <td>
              <span
                class="apanel-pill"
                :class="[
                  `apanel-pill--${job.status || 'default'}`,
                  { 'warning-radius': job.status === 'pending' },
                ]"
              >
                {{ statusLabel(job.status) }}
              </span>
            </td>
            <td>{{ job.location || '-' }}</td>
            <td>{{ job.salary || '-' }}</td>
            <td>{{ formatDate(job.created_at) }}</td>
            <td class="apanel-actions">
              <div class="apanel-actions__group">
                <button v-if="moderation" type="button" class="apanel-icon-button apanel-icon-button--preview" :title="t('aPanelJobs.preview')" :aria-label="t('aPanelJobs.preview')" @click.stop="previewJob = job">
                  <i class="fas fa-eye"></i>
                </button>
                <button v-if="moderation" type="button" class="apanel-icon-button apanel-icon-button--approve" :title="t('aPanelJobs.approve')" :aria-label="t('aPanelJobs.approve')" @click.stop="emit('approve', job)">
                  <i class="fas fa-check"></i>
                </button>
                <button v-if="moderation" type="button" class="apanel-icon-button apanel-icon-button--reject" :title="t('aPanelJobs.reject')" :aria-label="t('aPanelJobs.reject')" @click.stop="openRejectionModal(job)">
                  <i class="fas fa-xmark"></i>
                </button>
                <button v-if="!moderation" type="button" class="apanel-icon-button apanel-icon-button--danger" :title="t('aPanelJobs.delete')" :aria-label="t('aPanelJobs.delete')" @click.stop="emit('delete', job)">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else class="apanel-empty">{{ emptyText || t('aPanelJobs.emptyText') }}</p>
    </div>

    <nav v-if="jobs.length" class="jobs-pagination" :aria-label="t('jobsPage.pagination')">
      <div class="jobs-pagination__summary">
        {{ t('jobsPage.paginationSummary', { start: pageStart, end: pageEnd, total: jobs.length }) }}
      </div>

      <div class="jobs-pagination__controls">
        <button type="button" class="pagination-button pagination-button--ghost" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
          <i class="fas fa-arrow-left"></i>
          <span>{{ t('jobsPage.previousPage') }}</span>
        </button>

        <div class="pagination-numbers">
          <template v-for="item in paginationItems" :key="item">
            <span v-if="String(item).startsWith('ellipsis')" class="pagination-ellipsis">•••</span>
            <button v-else type="button" class="pagination-button pagination-button--number" :class="{ 'pagination-button--active': currentPage === item }" @click="goToPage(item)">
              {{ item }}
            </button>
          </template>
        </div>

        <button type="button" class="pagination-button" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
          <span>{{ t('jobsPage.nextPage') }}</span>
          <i class="fas fa-arrow-right"></i>
        </button>
      </div>
    </nav>

    <Teleport to="body">
      <div v-if="previewJob" class="apanel-preview" role="dialog" aria-modal="true" @click.self="previewJob = null">
        <div class="apanel-preview__dialog">
          <div class="apanel-preview-toolbar">
            <strong>{{ t('aPanelJobs.previewTitle') }}</strong>
            <button type="button" class="apanel-icon-button apanel-icon-button--close" :title="t('aPanelJobs.close')" :aria-label="t('aPanelJobs.close')" @click="previewJob = null">
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
            <p>{{ previewJob.company || t('aPanelJobs.companyMissing') }} &middot; {{ previewJob.location || t('aPanelJobs.locationMissing') }}</p>
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
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="rejectionJob" class="rejection-modal" role="dialog" aria-modal="true" @click.self="closeRejectionModal">
        <form class="rejection-modal__dialog" @submit.prevent="submitRejection">
          <h2>{{ t('aPanelJobs.rejectionTitle') }}</h2>
          <p>{{ t('aPanelJobs.rejectionDescription', { title: rejectionJob.title }) }}</p>

          <label for="job-rejection-reason">{{ t('aPanelJobs.rejectionReasonLabel') }}</label>
          <textarea
            id="job-rejection-reason"
            v-model="rejectionReason"
            maxlength="500"
            required
            autofocus
            :placeholder="t('aPanelJobs.rejectionReasonPlaceholder')"
            @input="rejectionError = ''"
          />
          <small v-if="rejectionError" class="rejection-modal__error">{{ rejectionError }}</small>

          <div class="rejection-modal__actions">
            <button type="button" class="rejection-modal__cancel" @click="closeRejectionModal">
              {{ t('aPanelJobs.cancel') }}
            </button>
            <button type="submit" class="rejection-modal__submit">
              {{ t('aPanelJobs.confirmReject') }}
            </button>
          </div>
        </form>
      </div>
    </Teleport>

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
  border-bottom: 0;
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

.apanel-table tbody tr {
  box-shadow: inset 0 -0.0625rem var(--border-subtle);
  transition: background-color 0.18s ease;
}

.apanel-table tbody tr:last-child {
  box-shadow: none;
}

.apanel-table tbody tr:hover {
  background: color-mix(in srgb, var(--brand-soft) 18%, white);
}

.apanel-job-row--clickable {
  cursor: pointer;
}

.apanel-job-row--clickable:focus-visible {
  outline: 0.1875rem solid color-mix(in srgb, var(--brand-base) 24%, transparent);
  outline-offset: -0.1875rem;
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
  min-width: 8.75rem;
  min-height: 2rem;
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
  width: 9.5rem;
  text-align: right !important;
  white-space: nowrap;
}

.apanel-actions__group {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: nowrap;
}

.apanel-table th:last-child {
  width: 9.5rem;
  text-align: right;
}

.apanel-icon-button {
  display: inline-grid;
  place-items: center;
  flex: 0 0 2.35rem;
  width: 2.35rem;
  height: 2.35rem;
  border: 0;
  border-radius: 0.72rem;
  background: linear-gradient(180deg, #64748b, #475569);
  color: #fff;
  box-shadow: 0 0.55rem 1rem rgba(71, 85, 105, 0.16);
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.apanel-icon-button:hover {
  box-shadow: none;
}

.apanel-icon-button:focus-visible {
  outline: 0.1875rem solid rgba(15, 23, 42, 0.16);
  outline-offset: 0.125rem;
}

.apanel-icon-button--preview {
  background: linear-gradient(180deg, rgba(29, 168, 107, 0.92), rgba(22, 155, 97, 0.92));
  box-shadow: 0 0.55rem 1rem rgba(29, 168, 107, 0.18);
}

.apanel-icon-button--approve {
  background: linear-gradient(180deg, #1ab16f, #15955d);
  box-shadow: 0 0.55rem 1rem rgba(21, 149, 93, 0.18);
}

.apanel-icon-button--reject {
  background: linear-gradient(180deg, #f59e0b, #d97706);
  box-shadow: 0 0.55rem 1rem rgba(217, 119, 6, 0.18);
}

.apanel-icon-button--danger {
  background: linear-gradient(180deg, #ef4444, #dc2626);
  box-shadow: 0 0.55rem 1rem rgba(220, 38, 38, 0.18);
}

.apanel-icon-button--close {
  background: linear-gradient(180deg, #ef4444, #dc2626);
  box-shadow: 0 0.55rem 1rem rgba(220, 38, 38, 0.18);
}

.apanel-empty {
  margin: 0;
  padding: 1rem;
  color: var(--text-muted);
  display: grid;
  place-items: center;
}

.jobs-pagination {
  display: grid;
  gap: 0.95rem;
  padding: 1rem;
  border-top: 0.0625rem solid var(--border-subtle);
}

.jobs-pagination__summary {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.jobs-pagination__controls,
.pagination-numbers {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.jobs-pagination__controls {
  justify-content: space-between;
}

.pagination-button {
  min-height: 2.85rem;
  padding: 0.72rem 1rem;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 18%, var(--border-subtle));
  border-radius: 999rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(241, 249, 245, 0.98));
  color: var(--text-primary);
  font: inherit;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  cursor: pointer;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-button--ghost {
  background: var(--surface-secondary);
}

.pagination-button--number {
  min-width: 2.85rem;
  padding-inline: 0.75rem;
}

.pagination-button--active {
  border-color: color-mix(in srgb, var(--brand-base) 60%, white);
  background: linear-gradient(135deg, color-mix(in srgb, var(--brand-base) 95%, white), color-mix(in srgb, var(--brand-strong) 90%, white));
  color: #fff;
}

.pagination-ellipsis {
  color: var(--text-muted);
  font-weight: 800;
  letter-spacing: 0.12em;
}

.apanel-preview {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.68);
  backdrop-filter: blur(0.35rem);
}

.rejection-modal {
  position: fixed;
  inset: 0;
  z-index: 3200;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(0.2rem);
}

.rejection-modal__dialog {
  width: min(27rem, 100%);
  display: grid;
  gap: 0.8rem;
  padding: 1.25rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: 0 1.5rem 4rem rgba(15, 23, 42, 0.24);
}

.rejection-modal__dialog h2,
.rejection-modal__dialog p {
  margin: 0;
}

.rejection-modal__dialog p {
  color: var(--text-muted);
  line-height: 1.45;
}

.rejection-modal__dialog label {
  font-size: 0.85rem;
  font-weight: 800;
}

.rejection-modal__dialog textarea {
  width: 100%;
  min-height: 7rem;
  resize: vertical;
  padding: 0.8rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.75rem;
  background: var(--surface-primary);
  color: var(--text-primary);
  font: inherit;
}

.rejection-modal__dialog textarea:focus {
  border-color: var(--brand-base);
  outline: 0.1875rem solid color-mix(in srgb, var(--brand-base) 18%, transparent);
}

.rejection-modal__error {
  color: #dc2626;
  font-weight: 700;
}

.rejection-modal__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
}

.rejection-modal__actions button {
  min-height: 2.75rem;
  border: 0;
  border-radius: 0.75rem;
  font: inherit;
  font-weight: 800;
  cursor: pointer;
}

.rejection-modal__cancel {
  background: var(--surface-muted);
  color: var(--text-primary);
}

.rejection-modal__submit {
  background: #dc2626;
  color: #fff;
}

.apanel-preview__dialog {
  width: min(76rem, 100%);
  max-height: calc(100vh - 3rem);
  overflow-y: auto;
  border: 0.0625rem solid rgba(255, 255, 255, 0.45);
  border-radius: 1.15rem;
  background: var(--surface-primary);
  box-shadow: 0 2rem 5rem rgba(15, 23, 42, 0.28);
}

.apanel-preview-toolbar {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.1rem;
  background: var(--surface-primary);
}

.job-preview-page {
  display: grid;
  gap: 1rem;
  padding: 1.1rem;
}

.job-preview-hero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border-radius: 1rem;
  background: linear-gradient(135deg, rgba(25, 120, 90, 0.08), rgba(29, 168, 107, 0.06));
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

.job-preview-hero h1,
.job-preview-hero p {
  margin: 0;
}

.job-preview-hero > div:nth-child(2) {
  display: grid;
  gap: 0.3rem;
}

.job-preview-hero aside {
  min-width: 11rem;
  display: grid;
  justify-items: center;
  gap: 0.3rem;
  padding: 0.8rem 0.9rem;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 18%, var(--border-subtle));
  border-radius: 0.85rem;
  background: rgba(255, 255, 255, 0.82);
  text-align: center;
}

.job-preview-hero aside strong {
  color: var(--text-primary);
  font-size: 1.05rem;
}

.job-preview-link {
  margin-top: 0.25rem;
  color: var(--brand-strong) !important;
  font-size: 0.82rem;
  font-weight: 800;
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

  .apanel-preview {
    padding: 0.75rem;
  }

  .apanel-preview__dialog {
    max-height: calc(100vh - 1.5rem);
  }
}
</style>
