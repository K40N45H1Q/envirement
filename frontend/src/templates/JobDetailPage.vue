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

const isEmployer = computed(() => (
  String(user.value?.account_type || user.value?.accountType || '').toLowerCase() === 'employer'
))

const hasLogo = computed(() => !!job.value?.logo && !brokenLogo.value)
const hasBanner = computed(() => !!job.value?.banner_url && !brokenBanner.value)

const localizeLanguageName = (value = '') => {
  const name = String(value).trim().toLowerCase()

  if (name.includes('англ') || name === 'english') return t('jobDetailPage.languageNames.english')
  if (name.includes('нем') || name === 'german') return t('jobDetailPage.languageNames.german')
  if (name.includes('рус') || name === 'russian') return t('jobDetailPage.languageNames.russian')
  if (name.includes('лат') || name === 'latvian') return t('jobDetailPage.languageNames.latvian')

  return value
}

const requiredLanguages = computed(() => (
  job.value?.languages
    ?.filter((item) => item?.name && item?.level)
    .map((item) => ({
      ...item,
      name: language.value === 'en' ? localizeLanguageName(item.name) : item.name,
    })) || []
))

const requiredLicenses = computed(() => job.value?.licenses?.filter(Boolean) || [])

const loadJob = async () => {
  isLoading.value = true
  error.value = ''
  brokenLogo.value = false
  brokenBanner.value = false

  try {
    job.value = normalizeJob(await getJob(route.params.id))
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
      form.value.email ||= user.value.email
    } catch {}
  }

  await loadJob()
})

watch(() => route.params.id, loadJob)
</script>

<template>
  <AppLayout>
    <main class="page">
      <p v-if="isLoading" class="notice">
        {{ t('jobDetailPage.loading') }}
      </p>

      <p v-else-if="error" class="notice error">
        {{ error }}
      </p>

      <template v-else-if="job">
        <section class="hero">
          <div class="logo" :style="{ background: job.color }">
            <img
              v-if="hasLogo"
              :src="job.logo"
              :alt="job.company"
              @error="brokenLogo = true"
            />
            <span v-else>{{ job.initials }}</span>
          </div>

          <div>
            <p>{{ t('jobDetailPage.eyebrow') }}</p>
            <h1>{{ job.title }}</h1>
            <p>{{ job.company }} · {{ job.location }}</p>
          </div>

          <aside>
            <strong>{{ job.salary }}</strong>
            <span>{{ t('jobDetailPage.currentRate') }}</span>
            <RouterLink to="/jobs">
              {{ t('jobDetailPage.allJobs') }}
            </RouterLink>
          </aside>
        </section>

        <section class="grid">
          <article class="panel">
            <h2>{{ t('jobDetailPage.descriptionTitle') }}</h2>
            
            <div class="wrapper">
              <img
                v-if="hasBanner"
                class="banner"
                :src="job.banner_url"
                :alt="job.title"
                @error="brokenBanner = true"
              />
              <p>{{ job.description || t('jobDetailPage.descriptionFallback') }}</p>
            </div>
            

            <section v-if="requiredLanguages.length">
              <h3>{{ t('jobDetailPage.languagesTitle') }}</h3>
              <ul>
                <li
                  v-for="item in requiredLanguages"
                  :key="`${item.name}-${item.level}`"
                >
                  {{ item.name }} · {{ item.level }}
                </li>
              </ul>
            </section>

            <section v-if="requiredLicenses.length">
              <h3>{{ t('jobDetailPage.licensesTitle') }}</h3>
              <ul>
                <li v-for="license in requiredLicenses" :key="license">
                  {{ license }}
                </li>
              </ul>
            </section>
          </article>
          <section class="panel grid-panel">
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
            </dl>
          </section>

          <aside>

            <form v-if="!isEmployer" class="panel form" @submit.prevent="submitApplication">
              <h2>{{ t('jobDetailPage.applyTitle') }}</h2>

              <input v-model="form.name" required :placeholder="t('jobDetailPage.form.name')" />
              <input v-model="form.surname" required :placeholder="t('jobDetailPage.form.surname')" />
              <input v-model="form.phone" required :placeholder="t('jobDetailPage.form.phone')" />
              <input v-model="form.email" required type="email" placeholder="Email" />
              <input v-model="form.nationality" :placeholder="t('jobDetailPage.form.nationality')" />
              <textarea v-model="form.message" rows="5" :placeholder="t('jobDetailPage.form.message')" />

              <button type="submit">
                {{ t('jobDetailPage.form.submit') }}
              </button>
              
              <p v-if="applyStatus" class="notice">
                {{ applyStatus }}
              </p>
            </form>
          </aside>
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
  padding: 2rem;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 1.25rem;
}

.hero > div:nth-child(2),
.hero aside,
.grid > aside,
.panel,
.form {
  display: grid;
  gap: 1rem;
}

.hero p,
.hero span,
.panel > p,
dt {
  color: var(--text-muted);
}

.hero aside {
  justify-items: end;
  text-align: right;
}

.hero strong {
  color: var(--brand-strong);
  font-size: 2rem;
}

.logo {
  width: 5rem;
  height: 5rem;
  display: grid;
  place-items: center;
  border-radius: 1rem;
  color: #fff;
  font-weight: 800;
  overflow: hidden;
}

.logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.grid {
  display: flex;
  flex-direction: column;
  grid-template-columns: minmax(0, 1fr) 22rem;
  gap: 1rem;
  align-items: start;
}

.panel {
  padding: 1.5rem;
  width: 100%;
}


dl {
  margin: 0;
  display: grid;
  gap: 1rem;
}

dd {
  margin: 0;
  color: var(--text-primary);
  font-weight: 700;
}

ul {
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: .5rem;
  list-style: none;
}

li {
  padding: .35rem .75rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 68%, white);
  color: var(--brand-strong);
  font-weight: 700;
}

input,
textarea {
  width: 100%;
  min-height: 3rem;
  padding: .85rem 1rem;
  border: 1px solid var(--border-subtle);
  border-radius: .875rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

textarea {
  min-height: 8rem;
  resize: vertical;
}

button {
  min-height: 3rem;
  border: 0;
  border-radius: .875rem;
  background: var(--brand-strong);
  color: #fff;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

a {
  color: var(--brand-strong);
  font-weight: 700;
  text-decoration: none;
}

.notice {
  padding: 1rem;
  color: var(--brand-strong);
}

.error {
  border-color: rgba(220, 38, 38, .14);
  background: rgba(220, 38, 38, .08);
  color: #b91c1c;
}

@media (max-width: 60rem) {
  .hero,
  .grid {
    grid-template-columns: 1fr;
  }

  .hero {
    padding: 1rem;
  }

  .hero aside {
    justify-items: start;
    text-align: left;
  }

  .panel {
    padding: 1rem;
  }
}

.wrapper {
  display: flex;
  align-items: stretch;
  gap: 15px;
  max-width: 100%;
}

.banner {
  width: 50%;
  max-height: 500px;
  object-fit: contain;
  border: 1px solid black;
  border-radius: 15px;
}

.wrapper p {
  width: 50%;
  max-width: 50%;
  max-height: 500px;
  margin: 0;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  line-height: 1.6;
  font-size: 20px;
  border: 1px solid black;
  box-sizing: border-box;
}



.grid > aside {
  width: 100%;
}

dl {
  width: 100%;
  grid-template-columns: repeat(3, 1fr);
}

dl > div {
  padding: 1rem;
  border: 1px solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
}

@media (max-width: 60rem) {
  dl {
    grid-template-columns: 1fr;
  }
}
</style>