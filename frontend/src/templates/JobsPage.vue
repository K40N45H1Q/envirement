<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import AppLayout from '@/components/AppLayout.vue'
import BaseDropdown from '@/components/BaseDropdown.vue'
import JobLocationsMap from '@/components/JobLocationsMap.vue'
import { useJobsStore } from '@/stores/jobs'

const route = useRoute()
const router = useRouter()
const jobsListRef = ref(null)
const jobsStore = useJobsStore()

const {
  isLoading,
  error,
  filters,
  categoryCounts,
  featuredCountries,
  countries,
  filteredJobs,
  hotCount,
  bookmarkedCount,
  resultsLabel,
  employmentOptions,
} = storeToRefs(jobsStore)

const hasQueryChanged = (left, right) => JSON.stringify(left) !== JSON.stringify(right)

const syncRoute = async () => {
  const nextQuery = jobsStore.routeQuery
  const currentQuery = { ...route.query }

  if (hasQueryChanged(nextQuery, currentQuery)) {
    await router.replace({ path: '/jobs', query: nextQuery })
  }
}

const selectCategory = async (value) => {
  jobsStore.setFilter('selectedCategory', value)
  await syncRoute()
}

const selectCountry = async (value) => {
  jobsStore.setFilter('selectedCountry', value)
  await syncRoute()
}

const selectTab = async (value) => {
  jobsStore.setFilter('selectedTab', value)
  jobsStore.setFilter('onlyBookmarked', value === 'favorites')
  await syncRoute()
}

const runSearch = async () => {
  await syncRoute()
  jobsListRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const resetFilters = async () => {
  jobsStore.resetFilters()
  await syncRoute()
}

watch(
  () => route.query,
  (query) => {
    jobsStore.applyRouteQuery(query)
  },
)

onMounted(async () => {
  await jobsStore.initialize(route.query)
})

const categoryConfigs = computed(() => jobsStore.categoryConfigs)
const categoryDropdownOptions = computed(() => categoryCounts.value.map((category) => ({
  value: category.id,
  label: category.label,
  hint: `${category.count} вакансий`,
  iconClass: category.icon,
})))
const sortOptions = [
  { value: 'newest', label: 'Новые сначала' },
  { value: 'salary', label: 'По зарплате' },
]

const focusJob = (jobId) => {
  const target = document.getElementById(`job-card-${jobId}`)
  target?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

let routeSyncTimer = null

const scheduleRouteSync = () => {
  if (routeSyncTimer) {
    window.clearTimeout(routeSyncTimer)
  }

  routeSyncTimer = window.setTimeout(() => {
    syncRoute()
  }, 200)
}

watch(
  () => [
    filters.value.searchTitle,
    filters.value.searchLocation,
    filters.value.salaryFrom,
  ],
  () => {
    scheduleRouteSync()
  },
)

onBeforeUnmount(() => {
  if (routeSyncTimer) {
    window.clearTimeout(routeSyncTimer)
  }
})
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="hero surface-section">
        <div class="hero-copy">
          <p class="section-eyebrow">Вакансии</p>
          <h1>Найдите работу мечты по всей Европе</h1>
          <p>
            Подберите подходящую вакансию по стране, категории, зарплате и условиям работы,
            а закладки и фильтры сохранятся между переходами по сайту.
          </p>
        </div>

        <div class="hero-map">
          <JobLocationsMap
            :jobs="filteredJobs"
            :selected-country="filters.selectedCountry"
            height="15rem"
            @select-job="focusJob"
          />
        </div>
      </section>

      <section class="content-grid">
        <div class="main-column">
          <section class="search-shell surface-card">
            <form class="search-grid" @submit.prevent="runSearch">
              <label>
                <span>Я ищу</span>
                <div class="input-wrap">
                  <input v-model="filters.searchTitle" placeholder="Должность, ключевое слово" />
                  <i class="fas fa-magnifying-glass"></i>
                </div>
              </label>

              <label>
                <span>Где</span>
                <div class="input-wrap">
                  <input v-model="filters.searchLocation" placeholder="Страна, город или регион" />
                  <i class="fas fa-location-dot"></i>
                </div>
              </label>

              <label>
                <span>Категория</span>
                <BaseDropdown
                  v-model="filters.selectedCategory"
                  aria-label="Категория"
                  class="search-dropdown"
                  :options="categoryDropdownOptions"
                  full-width
                  :show-selected-hint="false"
                  @change="selectCategory($event.value)"
                />
              </label>

              <button type="submit" class="btn-primary search-button">
                Найти вакансии
              </button>
            </form>

            <div class="category-row">
              <button
                v-for="category in categoryConfigs"
                :key="category.id"
                type="button"
                class="category-pill"
                :class="{ 'category-pill--active': filters.selectedCategory === category.id }"
                @click="selectCategory(category.id)"
              >
                <i :class="category.icon"></i>
                <span>{{ category.label }}</span>
              </button>
            </div>
          </section>

          <section ref="jobsListRef" class="jobs-shell surface-card">
            <div class="results-banner">
              <div>
                <strong>{{ resultsLabel }}</strong>
                <p>Комбинируйте поиск, категории, зарплату и условия, чтобы быстро сузить выдачу.</p>
              </div>

              <button type="button" class="btn-secondary results-reset" @click="resetFilters">
                Сбросить фильтры
              </button>
            </div>

            <header class="jobs-toolbar">
              <div class="job-tabs">
                <button
                  type="button"
                  class="tab-button"
                  :class="{ 'tab-button--active': filters.selectedTab === 'all' }"
                  @click="selectTab('all')"
                >
                  Все вакансии
                  <span>{{ jobsStore.enrichedJobs.length }}</span>
                </button>
                <button
                  type="button"
                  class="tab-button"
                  :class="{ 'tab-button--active': filters.selectedTab === 'hot' }"
                  @click="selectTab('hot')"
                >
                  Горячие вакансии
                  <span>{{ hotCount }}</span>
                </button>
                <button
                  type="button"
                  class="tab-button"
                  :class="{ 'tab-button--active': filters.selectedTab === 'favorites' }"
                  @click="selectTab('favorites')"
                >
                  Избранные
                  <span>{{ bookmarkedCount }}</span>
                </button>
              </div>

              <div class="toolbar-actions">
                <label class="sort-label">
                  <span>Сортировка</span>
                  <BaseDropdown
                    v-model="filters.selectedSort"
                    aria-label="Сортировка"
                    align="right"
                    size="sm"
                    variant="ghost"
                    class="sort-dropdown"
                    :options="sortOptions"
                    @change="syncRoute"
                  />
                </label>
              </div>
            </header>

            <div v-if="error" class="notice">{{ error }}</div>
            <div v-else-if="isLoading" class="notice">Загрузка вакансий...</div>

            <div v-else class="jobs-list">
              <article :id="`job-card-${job.id}`" v-for="job in filteredJobs" :key="job.id" class="job-row">
                <div class="company-logo" :style="{ background: job.color }">
                  <img v-if="jobsStore.hasLogo(job)" :src="job.logo" :alt="job.company" @error="jobsStore.markBrokenLogo(job.id)" />
                  <span v-else>{{ job.initials }}</span>
                </div>

                <div class="job-summary">
                  <div class="job-title-line">
                    <h2>{{ job.title }}</h2>
                    <span class="job-time">{{ job.timeLabel }}</span>
                  </div>

                  <div class="job-company">{{ job.company }}</div>

                  <div class="job-location">
                    <span>{{ job.countryFlag }}</span>
                    <span>{{ job.countryLabel }}, {{ job.location }}</span>
                  </div>

                  <div class="job-tags">
                    <span v-for="tag in job.tags" :key="tag" class="job-tag">
                      {{ tag }}
                    </span>
                  </div>

                  <strong class="job-salary">от {{ job.salary }} / мес.</strong>
                </div>

                <div class="job-actions">
                  <button
                    type="button"
                    class="save-button"
                    :class="{ 'save-button--active': job.isBookmarked }"
                    :aria-label="job.isBookmarked ? 'Убрать из избранного' : 'Добавить в избранное'"
                    @click="jobsStore.toggleBookmark(job.id)"
                  >
                    <i :class="job.isBookmarked ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
                  </button>
                  <RouterLink :to="`/jobs/${job.id}`" class="btn-primary details-button">
                    Подробнее
                  </RouterLink>
                </div>
              </article>

              <div v-if="!filteredJobs.length" class="notice">
                Вакансии не найдены. Попробуйте изменить фильтры, зарплату или страну.
              </div>
            </div>
          </section>

          <section class="countries-strip surface-card">
            <header class="strip-head">
              <h3>Популярные страны</h3>
              <button type="button" class="link-button" @click="selectCountry('all')">Все страны</button>
            </header>

            <div class="country-cards">
              <button
                v-for="country in featuredCountries"
                :key="country.key"
                type="button"
                class="country-card"
                :class="{ 'country-card--active': filters.selectedCountry === country.key }"
                @click="selectCountry(country.key)"
              >
                <strong>{{ country.flag }} {{ country.label }}</strong>
                <span>{{ country.count }} вакансий</span>
              </button>
            </div>
          </section>
        </div>

        <aside class="sidebar-column">
          <section class="map-card surface-card">
            <header class="sidebar-head">
              <h3>Работа на карте</h3>
            </header>

            <JobLocationsMap
              :jobs="filteredJobs"
              :selected-country="filters.selectedCountry"
              height="18rem"
              @select-job="focusJob"
            />

            <div class="country-list">
              <button
                v-for="country in featuredCountries"
                :key="country.key"
                type="button"
                class="country-item"
                @click="selectCountry(country.key)"
              >
                <span>{{ country.flag }} {{ country.label }}</span>
                <strong>{{ country.count }}</strong>
              </button>
            </div>

            <button type="button" class="btn-secondary sidebar-button" @click="selectCountry('all')">
              Смотреть все страны
            </button>
          </section>

          <section class="filters-card surface-card">
            <header class="sidebar-head">
              <h3>Фильтры</h3>
              <button type="button" class="link-button" @click="resetFilters">
                Сбросить все
              </button>
            </header>

            <div class="filter-group">
              <h4>Страна</h4>
              <button
                v-for="country in countries"
                :key="country.key"
                type="button"
                class="filter-check"
                :class="{ 'filter-check--active': filters.selectedCountry === country.key }"
                @click="selectCountry(filters.selectedCountry === country.key ? 'all' : country.key)"
              >
                <span>{{ country.flag }} {{ country.label }}</span>
                <strong>{{ country.count }}</strong>
              </button>
            </div>

            <div class="filter-group">
              <h4>Зарплата от</h4>
              <div class="input-wrap">
                <input v-model="filters.salaryFrom" type="number" min="0" placeholder="Например, 2500" @change="syncRoute" />
                <i class="fas fa-wallet"></i>
              </div>
            </div>

            <div class="filter-group">
              <h4>Тип занятости</h4>
              <div class="stack-options">
                <button
                  v-for="option in employmentOptions"
                  :key="option.id"
                  type="button"
                  class="filter-chip"
                  :class="{ 'filter-chip--active': filters.selectedEmployment === option.id }"
                  @click="jobsStore.setFilter('selectedEmployment', option.id); syncRoute()"
                >
                  {{ option.label }}
                </button>
              </div>
            </div>

            <div class="filter-group">
              <h4>Условия</h4>
              <label class="toggle-row">
                <input v-model="filters.onlyWithHousing" type="checkbox" @change="syncRoute" />
                <span>Только с жильём</span>
              </label>
              <label class="toggle-row">
                <input v-model="filters.onlyWithTransport" type="checkbox" @change="syncRoute" />
                <span>Только с транспортом</span>
              </label>
              <label class="toggle-row">
                <input v-model="filters.onlyBookmarked" type="checkbox" @change="syncRoute" />
                <span>Только в закладках</span>
              </label>
            </div>
          </section>
        </aside>
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.page {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 1.6rem var(--shell-gutter) 4rem;
  display: grid;
  gap: 1.25rem;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(18rem, 24rem);
  gap: 1.5rem;
  padding: 1.75rem;
  overflow: hidden;
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.1rem);
  color: var(--text-primary);
  line-height: 1.08;
}

.hero-copy p:not(.section-eyebrow) {
  max-width: 40rem;
  margin-top: 0.85rem;
  color: var(--text-muted);
  line-height: 1.7;
}

.hero-map {
  min-height: 15rem;
  overflow: hidden;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.25rem;
  background: linear-gradient(180deg, rgba(232, 249, 238, 0.9), rgba(255, 255, 255, 0.96));
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 21rem;
  gap: 1.25rem;
  align-items: start;
}

.main-column,
.sidebar-column {
  display: grid;
  gap: 1.25rem;
}

.search-shell,
.jobs-shell,
.countries-strip,
.map-card,
.filters-card {
  padding: 1.25rem;
}

.map-card,
.filters-card {
  display: grid;
  gap: 1rem;
  align-content: start;
}

.sidebar-column {
  position: sticky;
  top: 5.75rem;
}

.search-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr) minmax(0, 1fr) auto;
  gap: 0.85rem;
  align-items: end;
}

.search-grid label,
.filter-group {
  display: grid;
  gap: 0.45rem;
}

.search-grid label {
  color: var(--text-primary);
  font-weight: 700;
}

.input-wrap {
  position: relative;
}

.input-wrap input {
  width: 100%;
  min-height: 3.3rem;
  padding: 0.9rem 2.8rem 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

.input-wrap input:focus {
  outline: none;
  border-color: var(--brand-strong);
  box-shadow: 0 0 0 0.1875rem rgba(20, 184, 87, 0.12);
}

.input-wrap i {
  position: absolute;
  top: 50%;
  right: 1rem;
  transform: translateY(-50%);
  color: var(--brand-strong);
  pointer-events: none;
}

.search-dropdown,
.sort-dropdown {
  width: 100%;
}

.sort-dropdown {
  min-width: 12rem;
}

.search-button {
  min-width: 11.5rem;
}

.category-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}

.category-pill {
  min-height: 4.4rem;
  padding: 0.8rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  display: grid;
  place-items: center;
  gap: 0.35rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.category-pill i {
  color: var(--brand-strong);
}

.category-pill span {
  font-size: 0.82rem;
  line-height: 1.3;
}

.category-pill:hover,
.category-pill--active {
  border-color: color-mix(in srgb, var(--brand-base) 22%, var(--border-subtle));
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
  box-shadow: 0 0.65rem 1.35rem rgba(16, 24, 40, 0.06);
}

.results-banner,
.jobs-toolbar,
.sidebar-head,
.strip-head,
.country-item,
.filter-check,
.toggle-row,
.job-title-line,
.job-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.results-banner,
.sidebar-head,
.strip-head,
.country-item,
.filter-check,
.toggle-row,
.jobs-toolbar,
.job-title-line,
.job-actions {
  align-items: center;
  flex-shrink: 0;
}

.results-banner {
  margin-bottom: 1rem;
  padding: 1rem 1.05rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: linear-gradient(135deg, rgba(20, 184, 87, 0.09), rgba(255, 255, 255, 0.94)), var(--surface-secondary);
}

.results-banner p,
.country-card span,
.job-company,
.job-location,
.job-time,
.sort-label span {
  color: var(--text-muted);
}

.sidebar-head {
  padding-bottom: 0.9rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
}

.jobs-toolbar {
  padding-bottom: 1rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
}

.job-tabs,
.toolbar-actions,
.stack-options,
.job-tags {
  display: flex;
  gap: 0.75rem;
}

.job-tabs,
.job-tags,
.stack-options {
  flex-wrap: wrap;
}

.country-list,
.country-cards {
  display: grid;
  gap: 0.75rem;
}

.country-list {
  margin-top: 0.15rem;
}

.country-cards {
  grid-template-columns: repeat(auto-fit, minmax(9.5rem, 1fr));
}

.tab-button,
.link-button,
.filter-chip {
  border: none;
  background: transparent;
  font: inherit;
  cursor: pointer;
}

.tab-button {
  color: var(--text-muted);
  font-weight: 700;
  padding: 0 0 0.55rem;
  border-bottom: 0.125rem solid transparent;
}

.tab-button span,
.country-item strong,
.filter-check strong {
  color: var(--brand-strong);
}

.tab-button--active {
  color: var(--brand-strong);
  border-color: var(--brand-strong);
}

.sort-label {
  display: grid;
  gap: 0.35rem;
  justify-items: end;
}

.notice {
  padding: 1rem;
  border: 0.0625rem solid var(--border-strong);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--brand-soft) 68%, white);
  color: var(--brand-strong);
}

.jobs-list {
  display: grid;
}

.job-row {
  display: grid;
  grid-template-columns: 5rem minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
  padding: 1.15rem 0;
  border-bottom: 0.0625rem solid var(--border-subtle);
}

.job-row:last-child {
  border-bottom: none;
}

.company-logo {
  width: 4.6rem;
  height: 4.6rem;
  display: grid;
  place-items: center;
  border-radius: 1rem;
  color: #fff;
  font-size: 1.2rem;
  font-weight: 800;
  overflow: hidden;
}

.company-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.job-summary {
  display: grid;
  gap: 0.55rem;
}

.job-title-line h2,
.sidebar-head h3,
.strip-head h3,
.filter-group h4 {
  margin: 0;
  color: var(--text-primary);
}

.job-location {
  display: inline-flex;
  gap: 0.45rem;
  align-items: center;
}

.job-tag,
.filter-chip {
  display: inline-flex;
  align-items: center;
  min-height: 1.9rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999rem;
  font-size: 0.8rem;
  font-weight: 700;
}

.job-tag {
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
  color: var(--brand-strong);
}

.filter-chip {
  background: var(--surface-secondary);
  border: 0.0625rem solid var(--border-subtle);
  color: var(--text-primary);
}

.filter-chip--active {
  border-color: color-mix(in srgb, var(--brand-base) 28%, var(--border-subtle));
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
  color: var(--brand-strong);
}

.job-salary {
  color: var(--text-primary);
}

.save-button {
  width: 2.9rem;
  height: 2.9rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.9rem;
  background: var(--surface-secondary);
  color: var(--text-muted);
  cursor: pointer;
}

.save-button--active {
  border-color: color-mix(in srgb, var(--brand-base) 28%, var(--border-subtle));
  color: var(--brand-strong);
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
}

.details-button {
  min-width: 8.5rem;
  height: 2.9rem;
  padding-block: 0;
  justify-content: center;
}

.country-card,
.country-item,
.filter-check {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
}

.country-card {
  appearance: none;
  padding: 0.9rem 1rem;
  display: grid;
  gap: 0.25rem;
  min-height: 5rem;
  align-content: center;
  text-align: left;
  font: inherit;
  color: var(--text-primary);
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.country-card:hover,
.country-card--active {
  border-color: color-mix(in srgb, var(--brand-base) 22%, var(--border-subtle));
  background: color-mix(in srgb, var(--brand-soft) 58%, white);
  box-shadow: 0 0.625rem 1.25rem rgba(16, 24, 40, 0.06);
}

.country-card--active strong {
  color: var(--brand-strong);
}

.country-item,
.filter-check {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 0.95rem;
  border: 0.0625rem solid var(--border-subtle);
  text-align: left;
  font: inherit;
  color: var(--text-primary);
  appearance: none;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.country-item:hover,
.filter-check:hover,
.filter-check--active {
  border-color: color-mix(in srgb, var(--brand-base) 22%, var(--border-subtle));
  background: color-mix(in srgb, var(--brand-soft) 58%, white);
  box-shadow: 0 0.625rem 1.25rem rgba(16, 24, 40, 0.06);
}

.sidebar-button {
  width: 100%;
  justify-content: center;
  margin-top: 0.25rem;
}

.filter-group {
  display: grid;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 0.0625rem solid var(--border-subtle);
}

.filter-group:first-of-type {
  padding-top: 0;
  border-top: none;
}

.toggle-row {
  justify-content: start;
  gap: 0.65rem;
  color: var(--text-primary);
}

@media (max-width: 72rem) {
  .hero,
  .content-grid {
    grid-template-columns: 1fr;
  }

  .sidebar-column {
    position: static;
  }
}

@media (max-width: 56rem) {
  .search-grid {
    grid-template-columns: 1fr;
  }

  .category-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .jobs-toolbar,
  .results-banner,
  .job-row,
  .job-title-line,
  .job-actions {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: stretch;
  }

  .sort-label {
    justify-items: stretch;
  }

  .sort-dropdown {
    min-width: 0;
  }

  .job-row {
    display: grid;
  }

  .details-button,
  .save-button {
    width: 100%;
  }
}
</style>
