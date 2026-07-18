<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import PhoneInput from '@/components/PhoneInput.vue'
import { applyToJob, getJob, getJobMatch, getResponses } from '@/api/jobs'
import { getProfile } from '@/api/profile'
import { useI18n } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { localizeJobTitle, normalizeJob } from '@/utils/jobs'
import { presentMatchAnalysis } from '@/utils/matchPresentation'

const route = useRoute()
const router = useRouter()
const { state } = useAuth()
const { language, t } = useI18n()
const job = ref(null)
const loading = ref(false)
const submitting = ref(false)
const responses = ref([])
const matchResult = ref(null)
const error = ref('')
const applyStatus = ref('')
const brokenLogo = ref(false)
const brokenBanner = ref(false)
const applyModal = ref(null)
const bannerModal = ref(null)
const previousOverflow = ref('')
const form = ref({ name: '', surname: '', phone: '', email: '', nationality: '', message: '' })

const user = computed(() => state.user)
const isEmployer = computed(() => String(user.value?.account_type || user.value?.accountType || '').toLowerCase() === 'employer')
const isCandidate = computed(() => String(user.value?.account_type || user.value?.accountType || '').toLowerCase() === 'candidate')
const matchAnalysis = computed(() => matchResult.value ? presentMatchAnalysis(matchResult.value, language.value) : null)
const isJobOwner = computed(() => isEmployer.value && Number(user.value?.id || 0) === Number(job.value?.user_id || 0))
const hasActiveSubscription = computed(() => {
  if (!user.value?.subscription_plan || !user.value?.subscription_expires_at) return false
  const expiresAt = new Date(user.value.subscription_expires_at)
  return !Number.isNaN(expiresAt.getTime()) && expiresAt > new Date()
})
const canViewEmployerResponses = computed(() => isJobOwner.value && hasActiveSubscription.value)
const hasLogo = computed(() => !!job.value?.logo && !brokenLogo.value)
const hasBanner = computed(() => !!job.value?.banner_url && !brokenBanner.value)
const licenses = computed(() => job.value?.licenses?.map((item) => (
  typeof item === 'string' ? item : item?.label || item?.id || item?.value || ''
)).filter(Boolean) || [])
const jobResponses = computed(() => responses.value.filter((item) => Number(item.job_id) === Number(job.value?.id || 0)))
const approvedResponsesCount = computed(() => jobResponses.value.filter((item) => item.chat_approved).length)
const pendingResponsesCount = computed(() => Math.max(jobResponses.value.length - approvedResponsesCount.value, 0))
const localizedJobTitle = computed(() => localizeJobTitle(job.value || {}, language.value))

const localizeLanguage = (value = '') => {
  const name = String(value).trim().toLowerCase()
  if (name.includes('англ') || name === 'english') return t('jobDetailPage.languageNames.english')
  if (name.includes('нем') || name === 'german') return t('jobDetailPage.languageNames.german')
  if (name.includes('рус') || name === 'russian') return t('jobDetailPage.languageNames.russian')
  if (name.includes('лат') || name === 'latvian') return t('jobDetailPage.languageNames.latvian')
  return value
}

const languages = computed(() => (
  job.value?.languages?.filter(({ name, level }) => name && level)
    .map((item) => ({ ...item, name: language.value === 'ru' ? item.name : localizeLanguage(item.name) })) || []
))

const languageList = computed(() => languages.value.map(({ name, level }) => `${name} · ${level}`).join(', '))
const licenseList = computed(() => licenses.value.join(', '))

const openModal = (modal) => {
  previousOverflow.value = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  modal?.showModal()
}

const closeModal = (modal) => {
  modal?.close()
  document.body.style.overflow = previousOverflow.value
}

const openResponses = () => {
  router.push(`/dashboard?section=responses&job=${job.value?.id || ''}`)
}

const loadJob = async () => {
  loading.value = true
  error.value = ''
  brokenLogo.value = false
  brokenBanner.value = false

  try {
    job.value = normalizeJob(await getJob(route.params.id))
  } catch {
    job.value = null
    error.value = t('jobDetailPage.errors.notFound')
  } finally {
    loading.value = false
  }
}

const loadEmployerResponses = async () => {
  if (!canViewEmployerResponses.value) {
    responses.value = []
    return
  }

  try {
    const data = await getResponses()
    responses.value = Array.isArray(data) ? data : []
  } catch {
    responses.value = []
  }
}

const loadCandidateMatch = async () => {
  matchResult.value = null
  if (!isCandidate.value || !job.value?.id) return
  try {
    matchResult.value = await getJobMatch(job.value.id)
  } catch {
    matchResult.value = null
  }
}

const submitApplication = async () => {
  applyStatus.value = ''

  if (!user.value) {
    applyStatus.value = t('jobDetailPage.apply.loginRequired')
    return
  }

  if (submitting.value) return

  submitting.value = true

  try {
    const result = await applyToJob({
      ...form.value,
      username: user.value.email,
      email: form.value.email || user.value.email,
      job_id: Number(job.value.id),
    })

    applyStatus.value = t(result?.application_id ? 'jobDetailPage.apply.sentWithChat' : 'jobDetailPage.apply.sent')
    matchResult.value = result?.match_analysis || matchResult.value
  } catch (err) {
    applyStatus.value = t(
      err?.key === 'duplicate_application'
        ? 'jobDetailPage.apply.duplicate'
        : err?.key === 'forbidden'
          ? 'jobDetailPage.apply.candidateOnly'
          : err?.key === 'job_not_available'
            ? 'jobDetailPage.apply.jobUnavailable'
            : err?.key === 'outside_professional_area'
              ? 'jobDetailPage.apply.outsideProfessionalArea'
            : err?.key === 'missing_fields'
              ? 'jobDetailPage.apply.fillRequiredFields'
          : 'jobDetailPage.apply.failed',
    )
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  form.value.email = user.value?.email || ''

  if (user.value) {
    try {
      const profile = await getProfile()
      Object.assign(form.value, {
        name: profile.first_name || '',
        surname: profile.last_name || '',
        phone: profile.phone || '',
      })
    } catch {
      // Keep the form usable even if the profile prefill fails.
    }
  }

  await loadJob()
  await loadCandidateMatch()
  await loadEmployerResponses()
})

onBeforeUnmount(() => {
  document.body.style.overflow = previousOverflow.value
})

watch(() => route.params.id, async () => {
  await loadJob()
  await loadCandidateMatch()
  await loadEmployerResponses()
})
</script>

<template>
  <AppLayout>
    <main class="page">
      <p v-if="loading" class="notice">{{ t('jobDetailPage.loading') }}</p>
      <p v-else-if="error" class="notice error">{{ error }}</p>

      <template v-else-if="job">
        <section class="hero">
          <div class="logo" :style="{ background: job.color }">
            <img
              v-if="hasLogo"
              :src="job.logo"
              :alt="job.company"
              @error="brokenLogo = true"
            >
            <span v-else>{{ job.initials }}</span>
          </div>
          <div>
            <p class="brand">{{ t('jobDetailPage.eyebrow') }}</p>
            <h1>{{ localizedJobTitle }}</h1>
            <p class="muted">{{ job.company }}</p>
          </div>
        </section>

        <section class="content">
          <article class="panel description-panel">
            <h2>{{ t('jobDetailPage.descriptionTitle') }}</h2>
            <div class="description" :class="{ single: !hasBanner }">
              <button
                v-if="hasBanner"
                class="banner"
                type="button"
                @click="openModal(bannerModal)"
              >
                <img
                  :src="job.banner_url"
                  :alt="localizedJobTitle"
                  @error="brokenBanner = true"
                >
              </button>
              <div class="description-box">
                <div class="description-scroll">
                  <p>{{ job.description || t('jobDetailPage.descriptionFallback') }}</p>
                </div>
              </div>
            </div>
          </article>

          <aside class="panel sidebar">
            <RouterLink class="side-footer" to="/jobs">
              ← {{ t('jobDetailPage.allJobs') }}
            </RouterLink>

            <section class="side-section details">
              <dl>
                <div>
                  <dt>{{ t('jobDetailPage.quickFacts.location') }}</dt>
                  <dd>{{ job.location }}</dd>
                </div>
                <div>
                  <dt>{{ t('jobDetailPage.quickFacts.salary') }}</dt>
                  <dd>{{ job.salary }}</dd>
                </div>
                <div>
                  <dt>{{ t('jobDetailPage.quickFacts.status') }}</dt>
                  <dd>{{ t('jobDetailPage.publicVacancy') }}</dd>
                </div>
                <div v-if="languages.length">
                  <dt>{{ t('jobDetailPage.languagesTitle') }}</dt>
                  <dd>{{ languageList }}</dd>
                </div>
                <div v-if="licenses.length">
                  <dt>{{ t('jobDetailPage.licensesTitle') }}</dt>
                  <dd>{{ licenseList }}</dd>
                </div>
              </dl>
            </section>

            <section v-if="canViewEmployerResponses" class="side-section employer-responses">
              <div class="employer-responses__head">
                <div>
                  <p class="brand">{{ t('jobDetailPage.employerResponses.eyebrow') }}</p>
                </div>

                <button class="primary ghost" type="button" @click="openResponses">
                  {{ t('jobDetailPage.employerResponses.viewButton') }}
                </button>
              </div>

              <div class="employer-responses__stats">
                <article class="response-stat-card">
                  <span>{{ t('jobDetailPage.employerResponses.total') }}</span>
                  <strong>{{ jobResponses.length }}</strong>
                </article>
                <article class="response-stat-card">
                  <span>{{ t('jobDetailPage.employerResponses.pending') }}</span>
                  <strong>{{ pendingResponsesCount }}</strong>
                </article>
                <article class="response-stat-card">
                  <span>{{ t('jobDetailPage.employerResponses.approved') }}</span>
                  <strong>{{ approvedResponsesCount }}</strong>
                </article>
              </div>
            </section>

            <section v-if="isCandidate && matchAnalysis" class="side-section candidate-match">
              <div class="candidate-match__header">
                <div>
                  <strong>{{ matchAnalysis.meta.label }}</strong>
                  <span>{{ matchAnalysis.profile }}</span>
                </div>
                <b :style="{ color: matchAnalysis.meta.textColor }">{{ matchAnalysis.excluded ? '0/100' : `${matchAnalysis.score}/100` }}</b>
              </div>
              <div class="candidate-match__parts">
                <span v-for="part in matchAnalysis.breakdown" :key="part.key">
                  {{ part.label }} <b>{{ part.score }}</b>
                </span>
              </div>
              <p v-for="flag in matchAnalysis.failedGates" :key="flag" class="candidate-match__flag">{{ flag }}</p>
            </section>

            <section v-if="!isEmployer" class="side-section apply">
              <div>
                <h2>{{ t('jobDetailPage.applyTitle') }}</h2>
                <p class="muted">{{ localizedJobTitle }}</p>
              </div>
              <button
                class="primary"
                type="button"
                :disabled="matchAnalysis?.excluded"
                @click="applyStatus = ''; openModal(applyModal)"
              >
                {{ matchAnalysis?.excluded ? matchAnalysis.meta.label : t('jobDetailPage.form.submit') }}
              </button>
            </section>
          </aside>
        </section>
      </template>
    </main>

    <dialog ref="applyModal" class="modal" @cancel.prevent>
      <form class="modal-card" @submit.prevent="submitApplication">
        <header>
          <div>
            <h2>{{ t('jobDetailPage.applyTitle') }}</h2>
            <p class="muted">{{ job?.title }}</p>
          </div>
          <button
            class="close"
            type="button"
            :aria-label="t('jobDetailExtra.close')"
            @click="closeModal(applyModal)"
          >
            ×
          </button>
        </header>
        <div class="form-grid">
          <label>
            <span>{{ t('jobDetailPage.form.name') }}</span>
            <input v-model="form.name" required>
          </label>
          <label>
            <span>{{ t('jobDetailPage.form.surname') }}</span>
            <input v-model="form.surname" required>
          </label>
          <label>
            <span>{{ t('jobDetailPage.form.phone') }}</span>
            <PhoneInput
              v-model="form.phone"
              required
              :placeholder="t('jobDetailPage.form.phone')"
              :aria-label="t('jobDetailPage.form.phone')"
            />
          </label>
          <label>
            <span>{{ t('jobDetailExtra.email') }}</span>
            <input v-model="form.email" required type="email">
          </label>
          <label class="wide">
            <span>{{ t('jobDetailPage.form.message') }}</span>
            <textarea v-model="form.message" rows="5" />
          </label>
        </div>
        <p v-if="applyStatus" class="status">{{ applyStatus }}</p>
        <footer>
          <button class="primary" :disabled="submitting">
            {{ t('jobDetailPage.form.submit') }}{{ submitting ? t('jobDetailExtra.submittingSuffix') : '' }}
          </button>
        </footer>
      </form>
    </dialog>

    <dialog ref="bannerModal" class="media-modal" @cancel.prevent>
      <button
        class="close"
        type="button"
        :aria-label="t('jobDetailExtra.close')"
        @click="closeModal(bannerModal)"
      >
        ×
      </button>
      <img :src="job?.banner_url" :alt="job?.title">
    </dialog>
  </AppLayout>
</template>

<style scoped>
.page {
  width: min(100%, var(--shell-max-width));
  margin: auto;
  padding: 1.5rem var(--shell-gutter) 4rem;
  display: grid;
  gap: 1rem;
}

.page :is(h1, h2, h3, p) {
  margin: 0;
}

.hero,
.panel,
.notice {
  border: 1px solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.hero {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 2rem;
}

.hero h1 {
  font-size: clamp(1.8rem, 4vw, 3rem);
  line-height: 1.08;
}

.logo {
  width: 5rem;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 1rem;
  color: #fff;
  font-weight: 900;
}

.logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #fff;
}

.brand,
a {
  color: var(--brand-strong);
  font-weight: 700;
}

.muted,
dt {
  color: var(--text-muted);
}

a {
  text-decoration: none;
}

.content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(18rem, 22rem);
  gap: 1rem;
  align-items: stretch;
}

.panel {
  min-width: 0;
}

.description-panel {
  padding: 1.5rem;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 1rem;
}

.description {
  display: grid;
  grid-template-columns: minmax(15rem, 0.85fr) minmax(0, 1.15fr);
  gap: 1rem;
  min-height: 0;
}

.banner {
  min-width: 0;
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
  cursor: zoom-in;
}

.banner img {
  width: 100%;
  max-height: 32rem;
  display: block;
  object-fit: contain;
}

.description-box {
  position: relative;
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
}

.description-scroll {
  position: absolute;
  inset: 0;
  overflow: auto;
  padding: 1.1rem;
  scrollbar-gutter: stable;
}

.description-scroll p {
  line-height: 1.65;
  white-space: pre-wrap;
}

.single {
  grid-template-columns: 1fr;
}

.single .description-box {
  min-height: 12rem;
}

.single .description-scroll {
  position: static;
  max-height: 32rem;
}

.sidebar {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.side-section {
  padding: 1.25rem;
}

.sidebar > * + * {
  border-top: 1px solid var(--border-subtle);
}

.apply {
  display: grid;
  gap: 1rem;
  margin-top: auto;
}

.candidate-match {
  display: grid;
  gap: 0.85rem;
  background: color-mix(in srgb, var(--brand-base) 7%, #fff);
}

.candidate-match__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.candidate-match__header > div {
  display: grid;
  gap: 0.2rem;
}

.candidate-match__header span {
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.candidate-match__header > b {
  font-size: 1.45rem;
}

.candidate-match__parts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.45rem;
}

.candidate-match__parts span {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.5rem 0.6rem;
  border: 1px solid color-mix(in srgb, var(--brand-base) 18%, #dde5df);
  border-radius: 0.65rem;
  background: #fff;
  font-size: 0.76rem;
}

.candidate-match__flag {
  margin: 0;
  color: #c62828;
  font-size: 0.78rem;
  font-weight: 700;
}

.employer-responses {
  display: grid;
  gap: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 55%, var(--surface-primary));
}

.employer-responses__head {
  display: grid;
  gap: 0.85rem;
}

.employer-responses__stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.response-stat-card {
  display: grid;
  grid-template-rows: minmax(2.1rem, auto) auto;
  align-content: space-between;
  gap: 0.25rem;
  min-height: 5.75rem;
  padding: 0.8rem 0.7rem;
  border: 1px solid var(--border-subtle);
  border-radius: 0.9rem;
  background: var(--surface-primary);
}

.response-stat-card span {
  color: var(--text-muted);
  font-size: 0.72rem;
  line-height: 1.15;
  text-wrap: balance;
}

.response-stat-card strong {
  color: var(--text-primary);
  font-size: 1.05rem;
  line-height: 1;
  letter-spacing: -0.02em;
}

.details {
  flex: 1;
  background: color-mix(in srgb, var(--surface-secondary) 55%, var(--surface-primary));
}

.details dl {
  margin: 0;
  display: grid;
  gap: 0.85rem;
}

.details dl > div {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.details dd {
  max-width: 65%;
  margin: 0;
  text-align: right;
  font-weight: 800;
  overflow-wrap: anywhere;
}

.side-footer {
  padding: 1rem 1.25rem;
  background: var(--surface-secondary);
}

.primary {
  min-height: 3rem;
  padding: 0.75rem 1rem;
  border: 0;
  border-radius: 0.875rem;
  background: var(--brand-strong);
  color: #fff;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.primary:disabled {
  opacity: 0.6;
}

.ghost {
  width: 100%;
}

.notice {
  padding: 1rem;
  color: var(--brand-strong);
}

.error {
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.modal,
.media-modal {
  position: fixed;
  inset: 0;
  width: fit-content;
  height: fit-content;
  margin: auto;
  padding: 0;
  border: 0;
  background: transparent;
  overflow: visible;
}

.modal::backdrop,
.media-modal::backdrop {
  background: rgba(15, 23, 42, 0.78);
}

.modal-card {
  width: min(92vw, 46rem);
  max-height: 90dvh;
  overflow: auto;
  border: 1px solid var(--border-subtle);
  border-radius: 1.2rem;
  background: var(--surface-primary);
  color: var(--text-primary);
}

.modal-card header,
.modal-card footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
}

.modal-card header {
  border-bottom: 1px solid var(--border-subtle);
}

.modal-card footer {
  justify-content: flex-end;
  border-top: 1px solid var(--border-subtle);
}

.close {
  width: 2.7rem;
  height: 2.7rem;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font-size: 1.5rem;
  cursor: pointer;
}

.form-grid {
  padding: 1.25rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.form-grid label {
  display: grid;
  gap: 0.4rem;
  font-weight: 700;
}

.wide {
  grid-column: 1 / -1;
}

.form-grid :is(input, textarea) {
  width: 100%;
  min-width: 0;
  padding: 0.8rem 0.9rem;
  border: 1px solid var(--border-subtle);
  border-radius: 0.8rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

.form-grid textarea {
  resize: vertical;
}

.status {
  margin: 0 1.25rem 1rem;
  padding: 0.8rem;
  border-radius: 0.8rem;
  background: var(--brand-soft);
  color: var(--brand-strong);
  font-weight: 700;
}

.media-modal {
  max-width: none;
  max-height: none;
}

.media-modal img {
  max-width: 92vw;
  max-height: 92dvh;
  display: block;
  border-radius: 1rem;
  background: #fff;
}

.media-modal .close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: rgba(15, 23, 42, 0.7);
  color: #fff;
}

@media (max-width: 60rem) {
  .content {
    grid-template-columns: 1fr;
  }

  .description {
    grid-template-columns: 1fr;
  }

  .description-scroll {
    position: static;
    max-height: 24rem;
  }

  .banner img {
    margin: auto;
  }

  .sidebar {
    min-height: auto;
  }

  .employer-responses__stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 40rem) {
  .page {
    padding: 1rem var(--shell-gutter) 2rem;
  }

  .hero {
    align-items: flex-start;
    padding: 1rem;
  }

  .panel,
  .description-panel {
    padding: 1rem;
  }

  .sidebar {
    padding: 0;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .wide {
    grid-column: auto;
  }

  .modal-card {
    width: 94vw;
    max-height: 90dvh;
  }
}
</style>
