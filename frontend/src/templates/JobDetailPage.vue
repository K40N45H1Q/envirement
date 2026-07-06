<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { applyToJob, getJob } from '@/api/jobs'
import { useI18n } from '@/i18n'
import { getProfile } from '@/api/profile'
import { useAuth } from '@/stores/auth'
import { normalizeJob } from '@/utils/jobs'

const route = useRoute()
const { state } = useAuth()
const { language, t } = useI18n()

const job = ref(null)
const isLoading = ref(false)
const error = ref('')
const applyStatus = ref('')
const brokenLogo = ref(false)
const brokenBanner = ref(false)
const form = ref({
  name: '',
  surname: '',
  phone: '',
  email: '',
  nationality: '',
  message: '',
})

const user = computed(() => state.user)
const isEmployer = computed(() => {
  const accountType = String(user.value?.account_type || user.value?.accountType || '').toLowerCase()
  return accountType === 'employer'
})
const hasLogo = computed(() => !!job.value?.logo && !brokenLogo.value)
const hasBanner = computed(() => !!job.value?.banner_url && !brokenBanner.value)
const localizeLanguageName = (value = '') => {
  const normalized = String(value).trim().toLowerCase()

  if (normalized.includes('англ') || normalized === 'english') {
    return t('jobDetailPage.languageNames.english')
  }

  if (normalized.includes('нем') || normalized === 'german') {
    return t('jobDetailPage.languageNames.german')
  }

  if (normalized.includes('рус') || normalized === 'russian') {
    return t('jobDetailPage.languageNames.russian')
  }

  if (normalized.includes('лат') || normalized === 'latvian') {
    return t('jobDetailPage.languageNames.latvian')
  }

  return value
}

const requiredLanguages = computed(() => (
  Array.isArray(job.value?.languages)
    ? job.value.languages
      .filter((languageItem) => languageItem?.name && languageItem?.level)
      .map((languageItem) => ({
        ...languageItem,
        name: language.value === 'en' ? localizeLanguageName(languageItem.name) : languageItem.name,
      }))
    : []
))
const requiredLicenses = computed(() => (
  Array.isArray(job.value?.licenses)
    ? job.value.licenses.filter(Boolean)
    : []
))

const tagSet = computed(() => {
  if (!job.value) return []
  const haystack = `${job.value.title} ${job.value.description} ${job.value.location}`.toLowerCase()
  const tags = [t('jobDetailPage.officialEmployment')]

  if (/(монтаж|свар|electric|technician|repair|стро)/.test(haystack)) tags.push(t('jobDetailPage.technicalRole'))
  if (/(latvia|riga|герман|germany|netherlands|poland|belgium|france)/.test(haystack)) tags.push(t('jobDetailPage.workInEurope'))
  if (job.value.salary) tags.push(t('jobDetailPage.competitivePay'))

  return tags
})

const quickFacts = computed(() => {
  if (!job.value) return []

  return [
    {
      label: t('jobDetailPage.quickFacts.format'),
      value: t('jobDetailPage.quickFacts.directVacancy'),
      icon: 'fas fa-briefcase',
    },
    {
      label: t('jobDetailPage.quickFacts.location'),
      value: job.value.location,
      icon: 'fas fa-location-dot',
    },
    {
      label: t('jobDetailPage.quickFacts.salary'),
      value: job.value.salary,
      icon: 'fas fa-wallet',
    },
    {
      label: t('jobDetailPage.quickFacts.status'),
      value: t('jobDetailPage.quickFacts.applyNow'),
      icon: 'fas fa-circle-check',
    },
  ]
})

const loadJob = async () => {
  isLoading.value = true
  error.value = ''
  brokenLogo.value = false
  brokenBanner.value = false

  try {
    const data = await getJob(route.params.id)
    job.value = normalizeJob(data)
  } catch {
    job.value = null
    error.value = t('jobDetailPage.errors.notFound')
  } finally {
    isLoading.value = false
  }
}

const submitApplication = async () => {
  applyStatus.value = ''
  if (!user.value) {
    applyStatus.value = t('jobDetailPage.apply.loginRequired')
    return
  }

  try {
    const result = await applyToJob({
      ...form.value,
      username: user.value.email,
      email: form.value.email || user.value.email,
      job_id: Number(job.value.id),
    })
    applyStatus.value = result?.application_id
      ? t('jobDetailPage.apply.sentWithChat')
      : t('jobDetailPage.apply.sent')
  } catch (err) {
    applyStatus.value = err?.key === 'duplicate_application'
      ? t('jobDetailPage.apply.duplicate')
      : t('jobDetailPage.apply.failed')
  }
}

onMounted(async () => {
  if (user.value?.email) form.value.email = user.value.email

  if (user.value) {
    try {
      const profile = await getProfile()
      form.value.name = profile.first_name || ''
      form.value.surname = profile.last_name || ''
      form.value.phone = profile.phone || ''
      form.value.email = form.value.email || user.value.email
    } catch {}
  }

  await loadJob()
})

watch(() => route.params.id, loadJob)
</script>

<template>
  <AppLayout>
    <main class="page">
      <div v-if="isLoading" class="notice">{{ t('jobDetailPage.loading') }}</div>
      <div v-else-if="error" class="notice notice--error">{{ error }}</div>

      <template v-else-if="job">
        <section class="hero surface-section">
          <div class="hero-brand">
            <div class="logo" :style="{ background: job.color }">
              <img
                v-if="hasLogo"
                :src="job.logo"
                :alt="job.company"
                @error="brokenLogo = true"
              />
              <span v-else>{{ job.initials }}</span>
            </div>

            <div class="hero-copy">
              <p class="section-eyebrow">{{ t('jobDetailPage.eyebrow') }}</p>
              <h1>{{ job.title }}</h1>
              <div class="hero-meta">
                <span><i class="fas fa-building"></i>{{ job.company }}</span>
                <span><i class="fas fa-location-dot"></i>{{ job.location }}</span>
              </div>
              <div class="hero-tags">
                <span v-for="tag in tagSet" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>
          </div>

          <div class="hero-side">
            <strong>{{ job.salary }}</strong>
            <span>{{ t('jobDetailPage.currentRate') }}</span>
            <RouterLink to="/jobs" class="btn-secondary back-link">
              <i class="fas fa-arrow-left"></i>
              {{ t('jobDetailPage.allJobs') }}
            </RouterLink>
          </div>
        </section>

        <section class="facts-grid">
          <article v-for="fact in quickFacts" :key="fact.label" class="fact-card">
            <div class="fact-icon">
              <i :class="fact.icon"></i>
            </div>
            <div>
              <span>{{ fact.label }}</span>
              <strong>{{ fact.value }}</strong>
            </div>
          </article>
        </section>

        <section class="content-grid">
          <div class="main-column">
            <section class="panel">
              <div class="panel-head">
                <div>
                  <h2>{{ t('jobDetailPage.descriptionTitle') }}</h2>
                </div>
                <p class="section-eyebrow compact">{{ t('jobDetailPage.descriptionEyebrow') }}</p>
              </div>

              <div v-if="hasBanner" class="description-banner">
                <img
                  :src="job.banner_url"
                  :alt="job.title"
                  @error="brokenBanner = true"
                />
              </div>

              <p class="lead">
                {{ job.description || t('jobDetailPage.descriptionFallback') }}
              </p>

              <div v-if="requiredLanguages.length || requiredLicenses.length" class="requirements-summary">
                <article v-if="requiredLanguages.length" class="summary-card">
                  <h3>{{ t('jobDetailPage.languagesTitle') }}</h3>
                  <div class="summary-chips">
                    <span v-for="language in requiredLanguages" :key="`${language.name}-${language.level}`" class="summary-chip">
                      {{ language.name }} · {{ language.level }}
                    </span>
                  </div>
                </article>

                <article v-if="requiredLicenses.length" class="summary-card">
                  <h3>{{ t('jobDetailPage.licensesTitle') }}</h3>
                  <div class="summary-chips">
                    <span v-for="license in requiredLicenses" :key="license" class="summary-chip">
                      {{ license }}
                    </span>
                  </div>
                </article>
              </div>
            </section>

              <div class="company-grid">
                <div>
                  <span class="company-label">{{ t('jobDetailPage.quickFacts.location') }}</span>
                  <strong>{{ job.location }}</strong>
                </div>
                <div>
                  <span class="company-label">{{ t('jobDetailPage.quickFacts.salary') }}</span>
                  <strong>{{ job.salary }}</strong>
                </div>
                <div>
                  <span class="company-label">{{ t('jobDetailPage.quickFacts.status') }}</span>
                  <strong>{{ t('jobDetailPage.publicVacancy') }}</strong>
                </div>
              </div>

          </div>

          <form v-if="!isEmployer" class="panel apply-form" @submit.prevent="submitApplication">
            <div class="panel-head">
              <div>
                <h2>{{ t('jobDetailPage.applyTitle') }}</h2>
              </div>
            </div>
            
            <input v-model="form.name" required :placeholder="t('jobDetailPage.form.name')" />
            <input v-model="form.surname" required :placeholder="t('jobDetailPage.form.surname')" />
            <input v-model="form.phone" required :placeholder="t('jobDetailPage.form.phone')" />
            <input v-model="form.email" required type="email" placeholder="Email" />
            <input v-model="form.nationality" :placeholder="t('jobDetailPage.form.nationality')" />
            <textarea v-model="form.message" rows="5" :placeholder="t('jobDetailPage.form.message')"></textarea>

            <button type="submit" class="btn-primary">{{ t('jobDetailPage.form.submit') }}</button>
            <p v-if="applyStatus" class="status">{{ applyStatus }}</p>
          </form>
        </section>
      </template>
    </main>
  </AppLayout>
</template>

<style scoped>
.page {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 1.5rem var(--shell-gutter) 4rem;
  display: grid;
  gap: 1.25rem;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 15rem;
  gap: 1.5rem;
  padding: 2rem;
}

.hero-brand {
  display: grid;
  grid-template-columns: 5.5rem minmax(0, 1fr);
  gap: 1.1rem;
  align-items: start;
}

.logo {
  width: 5rem;
  height: 5rem;
  display: grid;
  place-items: center;
  border-radius: 1rem;
  color: #fff;
  font-size: 1.25rem;
  font-weight: 800;
  overflow: hidden;
}

.logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-copy h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(2rem, 4vw, 3rem);
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  margin-top: 0.55rem;
  color: var(--text-muted);
}

.hero-meta span {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.tag {
  display: inline-flex;
  align-items: center;
  min-height: 2rem;
  padding: 0.2rem 0.7rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 64%, white);
  color: var(--brand-strong);
  font-size: 0.82rem;
  font-weight: 700;
}

.hero-side {
  display: grid;
  align-content: start;
  justify-items: end;
  gap: 0.55rem;
  text-align: right;
}

.hero-side strong {
  color: var(--brand-strong);
  font-size: 2rem;
}

.hero-side span {
  color: var(--text-muted);
}

.back-link {
  margin-top: 0.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.facts-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.fact-card {
  display: flex;
  gap: 0.9rem;
  align-items: center;
  padding: 1rem 1.1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(232, 249, 238, 0.58)),
    var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.fact-icon {
  width: 2.7rem;
  height: 2.7rem;
  display: grid;
  place-items: center;
  border-radius: 0.85rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, white);
  color: var(--brand-strong);
}

.fact-card span {
  display: block;
  color: var(--text-muted);
  font-size: 0.84rem;
}

.fact-card strong {
  display: block;
  margin-top: 0.2rem;
  color: var(--text-primary);
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 24rem;
  gap: 1rem;
}

.main-column {
  display: grid;
  gap: 1.25rem;
  height: 100%;
}

.panel {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.compact {
  font-size: 0.76rem;
}

.lead {
  margin: 1rem 0 0;
  color: var(--text-muted);
  line-height: 1.75;
  font-size: 1.02rem;
}

.description-banner {
  margin-top: 1rem;
  border-radius: 1rem;
  overflow: hidden;
  border: 0.0625rem solid var(--border-subtle);
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
  box-shadow: var(--shadow-soft);
}

.description-banner img {
  width: 100%;
  display: block;
  height: auto;
  object-fit: contain;
}

.requirements-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1.25rem;
}

.summary-card {
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
}

.summary-card h3 {
  margin: 0 0 0.75rem;
}

.summary-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.summary-chip {
  display: inline-flex;
  align-items: center;
  min-height: 2rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 68%, white);
  color: var(--brand-strong);
  font-weight: 700;
}

.company-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
}

.company-grid div {
  padding: 1rem;
  max-height: max-content;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
}

.company-label {
  display: block;
  margin-bottom: 0.4rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.company-grid strong {
  color: var(--text-primary);
}

.apply-form {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

.apply-form input,
.apply-form textarea {
  width: 100%;
  min-height: 3.15rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

.apply-form textarea {
  min-height: 8rem;
  resize: vertical;
}

.notice,
.status {
  padding: 1rem;
  border-radius: 1rem;
  border: 0.0625rem solid var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 68%, white);
  color: var(--brand-strong);
}

.notice--error {
  border-color: rgba(220, 38, 38, 0.14);
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.message-link {
  width: 100%;
}

@media (max-width: 72rem) {
  .facts-grid,
  .content-grid,
  .requirements-summary,
  .company-grid {
    grid-template-columns: 1fr;
  }

  .apply-form {
    position: static;
  }
}

@media (max-width: 60rem) {
  .hero {
    grid-template-columns: 1fr;
    padding: 1.25rem;
  }

  .hero-side {
    justify-items: start;
    text-align: left;
    padding-top: 1rem;
    border-top: 0.0625rem solid var(--border-subtle);
  }

  .hero-side strong {
    font-size: 1.85rem;
  }
}

@media (max-width: 48rem) {
  .page {
    padding-top: 1.15rem;
  }

  .hero,
  .panel {
    padding: 1rem;
  }

  .hero-brand {
    grid-template-columns: 1fr;
  }

  .hero-meta,
  .hero-tags {
    gap: 0.65rem;
  }
}
</style>
