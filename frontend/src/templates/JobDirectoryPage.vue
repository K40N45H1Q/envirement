<script setup>
import { computed, onMounted } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import AppFlag from '@/components/AppFlag.vue'
import AppLayout from '@/components/AppLayout.vue'
import { translate, useI18n } from '@/i18n'
import { useJobsStore } from '@/stores/jobs'
import { countryByKey, getCityOptions, normalizeText } from '@/utils/countries'

const route = useRoute()
const router = useRouter()
const jobsStore = useJobsStore()
const { t, language } = useI18n()
const { enrichedJobs } = storeToRefs(jobsStore)

const pageKey = computed(() => route.meta.directory || 'categories')

const copy = computed(() => translate(`jobDirectoryPage.${pageKey.value}`, {}, language.value))
const formatCount = (value) => translate(`jobDirectoryPage.${pageKey.value}.count`, { value }, language.value)

const items = computed(() => {
  if (pageKey.value === 'countries') {
    return jobsStore.countries.map((country) => ({
      key: country.key,
      title: country.label,
      count: country.count,
      flagCode: country.flagCode,
      to: { path: '/jobs', query: { country: country.key } },
    }))
  }

  if (pageKey.value === 'latvia-cities') {
    const latvia = countryByKey.latvia
    const localizedCities = getCityOptions('latvia')
    const labelByValue = Object.fromEntries(localizedCities.map((item) => [item.value, item.label]))
    const cityCounts = enrichedJobs.value.reduce((acc, job) => {
      if (job.countryKey !== 'latvia') return acc

      const normalizedLocation = normalizeText(job.location)
      const matchedCity = latvia.cities.find((city) => city.aliases.some((alias) => normalizeText(alias) === normalizedLocation))
      if (!matchedCity) return acc

      acc[matchedCity.value] = (acc[matchedCity.value] || 0) + 1
      return acc
    }, {})

    return latvia.cities.map((city) => ({
      key: city.value,
      title: labelByValue[city.value] || city.value,
      count: cityCounts[city.value] || 0,
      to: { path: '/jobs', query: { country: 'latvia', loc: city.value } },
    }))
  }

  return jobsStore.categoryConfigs
    .filter((category) => category.id !== 'all')
    .map((category) => {
      const count = enrichedJobs.value.filter((job) => job.category === category.id).length
      return {
        key: category.id,
        title: category.label,
        count,
        to: { path: '/jobs', query: { category: category.id } },
      }
    })
})

const gridClass = computed(() => {
  if (pageKey.value === 'latvia-cities') return 'directory-grid directory-grid--cities'
  if (pageKey.value === 'countries') return 'directory-grid directory-grid--countries'
  return 'directory-grid'
})

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
    return
  }

  router.push('/jobs')
}

onMounted(async () => {
  if (!jobsStore.initialized || !jobsStore.jobs.length) {
    await jobsStore.initialize({})
  }
})
</script>

<template>
  <AppLayout>
    <main class="directory-page">
      <section class="directory-topbar">
        <nav class="breadcrumbs">
          <RouterLink to="/jobs">{{ copy.breadcrumbRoot }}</RouterLink>
          <i class="fas fa-angle-right"></i>
          <span>{{ copy.breadcrumbCurrent }}</span>
        </nav>

        <button type="button" class="back-link" @click="goBack">
          <i class="fas fa-angle-left"></i>
          <span>{{ copy.back }}</span>
        </button>
      </section>

      <section class="directory-hero">
        <p class="directory-eyebrow">{{ copy.eyebrow }}</p>
        <h1>{{ copy.title }}</h1>
        <p>{{ copy.description }}</p>
      </section>

      <section :class="gridClass">
        <RouterLink
          v-for="item in items"
          :key="item.key"
          :to="item.to"
          class="directory-card"
        >
          <strong class="directory-card__title">
            <AppFlag v-if="item.flagCode" :code="item.flagCode" :alt="item.title" />
            <span>{{ item.title }}</span>
          </strong>
          <span>{{ formatCount(item.count) }}</span>
        </RouterLink>
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.directory-page {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 0 0 4rem;
}

.directory-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 1.15rem var(--shell-gutter);
  border-bottom: 0.0625rem solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.92);
}

.breadcrumbs {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.breadcrumbs a {
  color: inherit;
  text-decoration: none;
}

.breadcrumbs a:hover,
.back-link:hover {
  color: var(--brand-strong);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font: inherit;
  cursor: pointer;
}

.directory-hero {
  display: grid;
  gap: 1rem;
  padding: 3.6rem var(--shell-gutter);
  background:
    radial-gradient(circle at top right, rgba(52, 211, 153, 0.12), transparent 28%),
    linear-gradient(90deg, rgba(221, 246, 255, 0.92), rgba(191, 229, 255, 0.94));
}

.directory-eyebrow {
  margin: 0;
  color: var(--brand-strong);
  font-size: 0.82rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(2rem, 4vw, 3rem);
}

.directory-hero p:last-child {
  max-width: 72rem;
  margin: 0;
  color: color-mix(in srgb, var(--text-primary) 82%, white);
  font-size: 1.04rem;
  line-height: 1.7;
}

.directory-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem 2.2rem;
  padding: 2.2rem var(--shell-gutter) 0;
}

.directory-grid--cities {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.directory-grid--countries {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.directory-card {
  display: grid;
  gap: 0.7rem;
  align-content: start;
  min-height: 7rem;
  padding: 0.35rem 0 1.05rem;
  border-bottom: 0.0625rem solid color-mix(in srgb, var(--brand-base) 22%, var(--border-subtle));
  color: var(--text-primary);
  text-decoration: none;
  transition: color 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
}

.directory-card strong {
  font-size: 1.1rem;
  line-height: 1.4;
}

.directory-card__title {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
}

.directory-card span {
  color: var(--text-muted);
  font-size: 0.98rem;
}

.directory-card:hover,
.directory-card:focus-visible {
  color: var(--brand-strong);
  transform: translateY(-0.0625rem);
  border-color: color-mix(in srgb, var(--brand-base) 42%, var(--border-subtle));
}

@media (max-width: 72rem) {
  .directory-grid,
  .directory-grid--cities,
  .directory-grid--countries {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 48rem) {
  .directory-topbar {
    display: grid;
    justify-content: stretch;
  }

  .directory-grid,
  .directory-grid--cities,
  .directory-grid--countries {
    grid-template-columns: 1fr;
  }

  .directory-hero {
    padding-block: 2.4rem;
  }
}
</style>
