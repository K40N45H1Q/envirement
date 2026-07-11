<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { applyToJob, getJob } from '@/api/jobs'
import { getProfile } from '@/api/profile'
import { useI18n } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { normalizeJob } from '@/utils/jobs'

const route = useRoute()
const { state } = useAuth()
const { language, t } = useI18n()
const job = ref(null)
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const applyStatus = ref('')
const brokenLogo = ref(false)
const brokenBanner = ref(false)
const applyModal = ref(null)
const bannerModal = ref(null)
const resume = ref(null)
const previousOverflow = ref('')
const form = ref({ name: '', surname: '', phone: '', email: '', nationality: '', message: '' })

const user = computed(() => state.user)
const isEmployer = computed(() => String(user.value?.account_type || user.value?.accountType || '').toLowerCase() === 'employer')
const hasLogo = computed(() => !!job.value?.logo && !brokenLogo.value)
const hasBanner = computed(() => !!job.value?.banner_url && !brokenBanner.value)
const licenses = computed(() => job.value?.licenses?.filter(Boolean) || [])

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
      ...(resume.value && { resume: resume.value }),
    })

    applyStatus.value = t(result?.application_id ? 'jobDetailPage.apply.sentWithChat' : 'jobDetailPage.apply.sent')
  } catch (err) {
    applyStatus.value = t(err?.key === 'duplicate_application' ? 'jobDetailPage.apply.duplicate' : 'jobDetailPage.apply.failed')
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

  loadJob()
})

onBeforeUnmount(() => {
  document.body.style.overflow = previousOverflow.value
})

watch(() => route.params.id, loadJob)
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
            <h1>{{ job.title }}</h1>
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
                  :alt="job.title"
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

            <section v-if="!isEmployer" class="side-section apply">
              <div>
                <h2>{{ t('jobDetailPage.applyTitle') }}</h2>
                <p class="muted">{{ job.title }}</p>
              </div>
              <button
                class="primary"
                type="button"
                @click="applyStatus = ''; openModal(applyModal)"
              >
                {{ t('jobDetailPage.form.submit') }}
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
            <input v-model="form.phone" required type="tel">
          </label>
          <label>
            <span>{{ t('jobDetailExtra.email') }}</span>
            <input v-model="form.email" required type="email">
          </label>
          <label class="wide">
            <span>{{ t('jobDetailPage.form.message') }}</span>
            <textarea v-model="form.message" rows="5" />
          </label>
          <label class="wide upload">
            <input
              type="file"
              accept="application/pdf,.pdf"
              @change="resume = $event.target.files?.[0] || null"
            >
            <strong>{{ t('jobDetailExtra.uploadResume') }}</strong>
            <span>{{ resume?.name || t('jobDetailExtra.pdfFile') }}</span>
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

.upload {
  place-items: center;
  padding: 1.25rem;
  border: 2px dashed var(--brand-strong);
  border-radius: 0.9rem;
  background: var(--surface-secondary);
  text-align: center;
  cursor: pointer;
  transition: 0.2s;
}

.upload:hover {
  background: color-mix(in srgb, var(--brand-soft) 35%, var(--surface-secondary));
}

.upload input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

.upload strong {
  color: var(--brand-strong);
}

.upload span {
  color: var(--text-muted);
  font-weight: 400;
  overflow-wrap: anywhere;
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
