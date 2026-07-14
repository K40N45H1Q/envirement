<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useI18n } from '@/i18n'
import AppFlag from '@/components/AppFlag.vue'
import AppLayout from '@/components/AppLayout.vue'
import BaseDropdown from '@/components/BaseDropdown.vue'
import HeroBannerCarousel from '@/components/HeroBannerCarousel.vue'
import JobLocationsMap from '@/components/JobLocationsMap.vue'
import { useAuth } from '@/stores/auth'
import { useJobsStore } from '@/stores/jobs'

const route = useRoute()
const router = useRouter()
const jobsListRef = ref(null)
const auth = useAuth()
const jobsStore = useJobsStore()
const { t } = useI18n()
const draftSearchTitle = ref('')
const draftSearchLocation = ref('')
const draftSelectedCategory = ref('all')
const currentPage = ref(1)
const JOBS_PER_PAGE = 4

const {
  isLoading,
  error,
  filters,
  categoryCounts,
  countries,
  filteredJobs,
  bookmarkedCount,
  resultsLabel,
  employmentOptions,
} = storeToRefs(jobsStore)

const hasQueryChanged = (left, right) => JSON.stringify(left) !== JSON.stringify(right)
const isAuthenticated = computed(() => !!auth.user)
const parsePage = (value) => {
  const parsed = Number.parseInt(String(value || '1'), 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1
}

const buildPaginationItems = (page, total) => {
  if (total <= 7) return Array.from({ length: total }, (_, index) => index + 1)
  if (page <= 4) return [1, 2, 3, 4, 5, 'ellipsis-right', total]
  if (page >= total - 3) return [1, 'ellipsis-left', total - 4, total - 3, total - 2, total - 1, total]
  return [1, 'ellipsis-left', page - 1, page, page + 1, 'ellipsis-right', total]
}

const resetGuestFavoriteFilters = () => {
  if (isAuthenticated.value) return false
  if (filters.value.selectedTab !== 'favorites' && !filters.value.onlyBookmarked) return false

  jobsStore.setFilter('selectedTab', 'all')
  jobsStore.setFilter('onlyBookmarked', false)
  return true
}

const openLogin = async () => {
  await router.push({
    path: route.path,
    query: {
      ...route.query,
      auth: 'login',
      redirect: route.fullPath,
    },
    hash: route.hash,
  })
}

const syncSearchDrafts = () => {
  draftSearchTitle.value = filters.value.searchTitle
  draftSearchLocation.value = filters.value.searchLocation
  draftSelectedCategory.value = filters.value.selectedCategory
}

const syncRoute = async (page = currentPage.value) => {
  const nextQuery = { ...jobsStore.routeQuery }
  currentPage.value = page
  if (page > 1) nextQuery.page = String(page)
  const currentQuery = { ...route.query }

  if (hasQueryChanged(nextQuery, currentQuery)) {
    await router.replace({ path: route.path, query: nextQuery, hash: route.hash })
  }
}

const selectCountry = async (value) => {
  jobsStore.setFilter('selectedCountry', value)
  await syncRoute(1)
}

const selectTab = async (value) => {
  if (value === 'favorites' && !isAuthenticated.value) {
    await openLogin()
    return
  }

  jobsStore.setFilter('selectedTab', value)
  jobsStore.setFilter('onlyBookmarked', value === 'favorites')
  await syncRoute(1)
}

const toggleBookmark = async (jobId) => {
  if (!isAuthenticated.value) {
    await openLogin()
    return
  }

  jobsStore.toggleBookmark(jobId)
}

const isJobBookmarked = (job) => isAuthenticated.value && job.isBookmarked

const runSearch = async () => {
  jobsStore.setFilter('searchTitle', draftSearchTitle.value.trim())
  jobsStore.setFilter('searchLocation', draftSearchLocation.value.trim())
  jobsStore.setFilter('selectedCategory', draftSelectedCategory.value)
  await syncRoute(1)
  jobsListRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const resetFilters = async () => {
  jobsStore.resetFilters()
  syncSearchDrafts()
  await syncRoute(1)
}

const handleSortChange = async () => {
  await syncRoute(1)
}

watch(
  () => route.query,
  async (query) => {
    jobsStore.applyRouteQuery(query)
    currentPage.value = parsePage(query.page)
    syncSearchDrafts()
    if (resetGuestFavoriteFilters()) await syncRoute(1)
  },
)

watch(isAuthenticated, async (value) => {
  if (!value && resetGuestFavoriteFilters()) await syncRoute(1)
})

onMounted(async () => {
  await jobsStore.initialize(route.query)
  currentPage.value = parsePage(route.query.page)
  syncSearchDrafts()
  if (resetGuestFavoriteFilters()) await syncRoute(1)
})

const categoryConfigs = computed(() => jobsStore.categoryConfigs)
const jobsHeroCategories = computed(() => (
  categoryConfigs.value
    .filter((category) => category.id !== 'all')
    .slice(0, 6)
    .map((category) => ({
      id: category.id,
      label: category.label,
      icon: category.icon,
    }))
))
const categoryDropdownOptions = computed(() => categoryCounts.value.map((category) => ({
  value: category.id,
  label: category.label,
  hint: t('jobsPage.jobsCount', { count: category.count }),
  iconClass: category.icon,
})))
const sortOptions = computed(() => [
  { value: 'newest', label: t('jobsPage.newestFirst') },
  { value: 'salary', label: t('jobsPage.bySalary') },
])

const formatSalaryLabel = (salary) => t('jobsPage.salaryFromValue', { salary })
const totalPages = computed(() => Math.max(1, Math.ceil(filteredJobs.value.length / JOBS_PER_PAGE)))
const paginatedJobs = computed(() => {
  const start = (currentPage.value - 1) * JOBS_PER_PAGE
  return filteredJobs.value.slice(start, start + JOBS_PER_PAGE)
})
const paginationItems = computed(() => buildPaginationItems(currentPage.value, totalPages.value))
const pageStart = computed(() => (filteredJobs.value.length ? ((currentPage.value - 1) * JOBS_PER_PAGE) + 1 : 0))
const pageEnd = computed(() => Math.min(currentPage.value * JOBS_PER_PAGE, filteredJobs.value.length))

const focusJob = (jobId) => {
  const target = document.getElementById(`job-card-${jobId}`)
  target?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

const goToPage = async (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  await syncRoute(page)
  jobsListRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

watch(filteredJobs, async () => {
  if (currentPage.value > totalPages.value) {
    await syncRoute(totalPages.value)
  }
})
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="hero surface-section">
        <div class="hero-copy">
          <p class="section-eyebrow">{{ t('jobsPage.heroEyebrow') }}</p>
          <h1>{{ t('jobsPage.heroTitle') }}</h1>
          <p>{{ t('jobsPage.heroDescription') }}</p>
        </div>

        <HeroBannerCarousel />
      </section>

      <section class="content-grid">
        <div class="main-column">
          <section class="search-shell surface-card">
            <form class="search-grid" @submit.prevent="runSearch">
              <label>
                <span>{{ t('search.lookingFor') }}</span>
                <div class="input-wrap">
                  <input v-model="draftSearchTitle" :placeholder="t('search.lookingPlaceholder')" />
                  <i class="fas fa-magnifying-glass"></i>
                </div>
              </label>

              <label>
                <span>{{ t('search.where') }}</span>
                <div class="input-wrap">
                  <input v-model="draftSearchLocation" :placeholder="t('search.wherePlaceholder')" />
                  <i class="fas fa-location-dot"></i>
                </div>
              </label>

              <label>
                <span>{{ t('search.category') }}</span>
                <BaseDropdown
                  v-model="draftSelectedCategory"
                  :aria-label="t('search.category')"
                  class="search-dropdown"
                  :options="categoryDropdownOptions"
                  full-width
                  :show-selected-hint="false"
                />
              </label>

              <button type="submit" class="btn-primary search-button">
                {{ t('search.submit') }}
              </button>
            </form>

            <div class="category-row">
              <button
                v-for="category in jobsHeroCategories"
                :key="category.id"
                type="button"
                class="category-pill"
                :class="{ 'category-pill--active': draftSelectedCategory === category.id }"
                @click="draftSelectedCategory = category.id"
              >
                <i :class="category.icon"></i>
                <span>{{ category.label }}</span>
              </button>
            </div>
          </section>

          <section id="jobs-results" ref="jobsListRef" class="jobs-shell surface-card">
            <div class="results-banner">
              <div>
                <strong>{{ resultsLabel }}</strong>
                <p>{{ t('jobsPage.resultsHint') }}</p>
              </div>

              <button type="button" class="btn-secondary results-reset" @click="resetFilters">
                {{ t('jobsPage.resetFilters') }}
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
                  {{ t('jobsPage.allJobs') }}
                  <span>{{ jobsStore.enrichedJobs.length }}</span>
                </button>

                <button
                  v-if="isAuthenticated"
                  type="button"
                  class="tab-button"
                  :class="{ 'tab-button--active': filters.selectedTab === 'favorites' }"
                  @click="selectTab('favorites')"
                >
                  {{ t('jobsPage.favorites') }}
                  <span>{{ bookmarkedCount }}</span>
                </button>
              </div>

              <div class="toolbar-actions">
                <label class="sort-label">
                  <span>{{ t('jobsPage.sorting') }}</span>
                  <BaseDropdown
                    v-model="filters.selectedSort"
                    :aria-label="t('jobsPage.sorting')"
                    align="right"
                    size="sm"
                    variant="ghost"
                    class="sort-dropdown"
                    :options="sortOptions"
                    @change="handleSortChange"
                  />
                </label>
              </div>
            </header>

            <div v-if="filteredJobs.length" class="jobs-list">
              <article :id="`job-card-${job.id}`" v-for="job in paginatedJobs" :key="job.id" class="job-row">
                <RouterLink
                  :to="`/jobs/${job.id}`"
                  class="job-card-link"
                  :aria-label="`${job.title} — ${job.company}`"
                />

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
                    <AppFlag :code="job.countryFlagCode" :alt="job.countryLabel" />
                    <span>{{ job.displayLocation }}</span>
                  </div>

                  <div class="job-tags">
                    <span v-for="tag in job.tags" :key="tag" class="job-tag">
                      {{ tag }}
                    </span>
                  </div>
                  <strong class="job-salary">{{ formatSalaryLabel(job.salary) }}</strong>

                </div>

                <div class="job-actions">
                  <button
                    v-if="isAuthenticated"
                    type="button"
                    class="save-button"
                    :class="{
                      'save-button--active': isJobBookmarked(job),
                      'save-button--guest': !isAuthenticated,
                    }"
                    :aria-pressed="isJobBookmarked(job)"
                    :aria-label="isJobBookmarked(job) ? t('jobsPage.removeBookmark') : t('jobsPage.addBookmark')"
                    @click.stop="toggleBookmark(job.id)"
                  >
                    <svg class="bookmark-icon" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M7.25 3.5h9.5c.97 0 1.75.78 1.75 1.75v15.1L12 16.3l-6.5 4.05V5.25c0-.97.78-1.75 1.75-1.75Z" />
                    </svg>
                  </button>
                  <RouterLink :to="`/jobs/${job.id}`" class="btn-primary details-button" @click.stop>
                    {{ t('jobsPage.details') }}
                  </RouterLink>
                </div>
              </article>

              <div v-if="!filteredJobs.length" class="notice">
                {{ t('jobsPage.noJobsFound') }}
              </div>
            </div>

            <nav v-if="filteredJobs.length" class="jobs-pagination" :aria-label="t('jobsPage.pagination')">
              <div class="jobs-pagination__summary">
                {{ t('jobsPage.paginationSummary', { start: pageStart, end: pageEnd, total: filteredJobs.length }) }}
              </div>

              <div class="jobs-pagination__controls">
                <button
                  type="button"
                  class="pagination-button pagination-button--ghost pagination-button--prev"
                  :disabled="currentPage === 1"
                  @click="goToPage(currentPage - 1)"
                >
                  <i class="fas fa-arrow-left"></i>
                  <span>{{ t('jobsPage.previousPage') }}</span>
                </button>

                <div class="pagination-numbers">
                  <template v-for="item in paginationItems" :key="item">
                    <span v-if="String(item).startsWith('ellipsis')" class="pagination-ellipsis">•••</span>
                    <button
                      v-else
                      type="button"
                      class="pagination-button pagination-button--number"
                      :class="{ 'pagination-button--active': currentPage === item }"
                      @click="goToPage(item)"
                    >
                      {{ item }}
                    </button>
                  </template>
                </div>

                <button
                  type="button"
                  class="pagination-button pagination-button--next"
                  :disabled="currentPage === totalPages"
                  @click="goToPage(currentPage + 1)"
                >
                  <span>{{ t('jobsPage.nextPage') }}</span>
                  <i class="fas fa-arrow-right"></i>
                </button>
              </div>
            </nav>
          </section>

        </div>

        <aside class="sidebar-column">
          <section class="map-card surface-card">
            <header class="sidebar-head">
              <h3>{{ t('jobsPage.jobsOnMap') }}</h3>
            </header>

            <JobLocationsMap
              class="map"
              :jobs="filteredJobs"
              :selected-country="filters.selectedCountry"
              height="18rem"
              @select-job="focusJob"
            />
          </section>

          <section id="jobs-filters" class="filters-card surface-card">
            <header class="sidebar-head">
              <h3>{{ t('jobsPage.filters') }}</h3>
              <button type="button" class="link-button" @click="resetFilters">
                {{ t('jobsPage.resetAll') }}
              </button>
            </header>

            <div class="filter-group">
              <h4>{{ t('jobsPage.country') }}</h4>
              <button
                v-for="country in countries"
                :key="country.key"
                type="button"
                class="filter-check"
                :class="{ 'filter-check--active': filters.selectedCountry === country.key }"
                @click="selectCountry(filters.selectedCountry === country.key ? 'all' : country.key)"
              >
                <span><AppFlag :code="country.flagCode" :alt="country.label" /> {{ country.label }}</span>
                <strong>{{ country.count }}</strong>
              </button>
            </div>

            <div class="filter-group">
              <h4>{{ t('jobsPage.salaryFrom') }}</h4>
              <div class="input-wrap">
                <input v-model="filters.salaryFrom" type="number" min="0" :placeholder="t('jobsPage.salaryPlaceholder')" @change="syncRoute(1)" />
                <i class="fas fa-wallet"></i>
              </div>
            </div>

            <div class="filter-group">
              <h4>{{ t('jobsPage.employmentType') }}</h4>
              <div class="stack-options">
                <button
                  v-for="option in employmentOptions"
                  :key="option.id"
                  type="button"
                  class="filter-chip"
                  :class="{ 'filter-chip--active': filters.selectedEmployment === option.id }"
                  @click="jobsStore.setFilter('selectedEmployment', option.id); syncRoute(1)"
                >
                  {{ option.label }}
                </button>
              </div>
            </div>

            <div class="filter-group">
              <h4>{{ t('jobsPage.conditions') }}</h4>
              <label class="toggle-row">
                <input v-model="filters.onlyWithHousing" type="checkbox" @change="syncRoute(1)" />
                <span>{{ t('jobsPage.onlyHousing') }}</span>
              </label>
              <label class="toggle-row">
                <input v-model="filters.onlyWithTransport" type="checkbox" @change="syncRoute(1)" />
                <span>{{ t('jobsPage.onlyTransport') }}</span>
              </label>
              <label class="toggle-row">
                <input v-model="filters.onlyBookmarked" type="checkbox" @change="syncRoute(1)" />
                <span>{{ t('jobsPage.onlyBookmarks') }}</span>
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
  background: var(--glow-bg-left);
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
  display: flex;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 21rem;
  gap: 1.25rem;
  align-items: stretch;
}

.main-column,
.sidebar-column {
  display: grid;
  gap: 1.25rem;
  align-content: start;
}

.main-column {
  grid-template-rows: auto 1fr;
}

.sidebar-column {
  grid-template-rows: auto 1fr;
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

.filters-card {
  height: 100%;
}

.jobs-shell {
  height: 100%;
  display: grid;
  align-content: start;
}

.map-card {
  gap: 0.75rem;
}

.map {
  border: 4px solid rgb(31, 201, 127, 0.4);
  background: transparent;
}

.sidebar-column {
  position: sticky;
  top: 5.75rem;
  align-self: start;
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

.input-wrap :is(i, svg.svg-inline--fa) {
  position: absolute;
  top: 50%;
  right: 1rem;
  transform: translateY(-50%);
  color: var(--brand-strong);
  pointer-events: none;
  width: 1rem;
  height: 1rem;
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
  grid-template-columns: repeat(6, minmax(0, 1fr));
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

.category-pill :is(i, svg.svg-inline--fa) {
  width: 1.4rem;
  height: 1.4rem;
  display: grid;
  place-items: center;
  font-size: 1.15rem;
  line-height: 1;
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
  margin-top: 0;
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
  gap: 0.85rem;
  padding-top: 1rem;
}

.jobs-pagination {
  display: grid;
  gap: 0.95rem;
  margin-top: 1.2rem;
  padding-top: 1.15rem;
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
  box-shadow: 0 0.55rem 1.35rem rgba(16, 24, 40, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease, color 0.2s ease;
}

.pagination-button:hover:not(:disabled),
.pagination-button:focus-visible:not(:disabled) {
  border-color: color-mix(in srgb, var(--brand-base) 44%, var(--border-subtle));
  color: var(--brand-strong);
  transform: translateY(-0.0625rem);
  box-shadow: 0 0.8rem 1.6rem rgba(16, 24, 40, 0.1);
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.pagination-button--ghost {
  background: var(--surface-secondary);
}

  .pagination-button--number {
    min-width: 2.85rem;
    padding-inline: 0.75rem;
  }

  .pagination-button--prev,
  .pagination-button--next {
    min-width: 9.5rem;
  }

.pagination-button--active {
  border-color: color-mix(in srgb, var(--brand-base) 60%, white);
  background: linear-gradient(135deg, color-mix(in srgb, var(--brand-base) 95%, white), color-mix(in srgb, var(--brand-strong) 90%, white));
  color: #fff;
  box-shadow: 0 0.9rem 1.7rem rgba(20, 184, 87, 0.22);
}

.pagination-ellipsis {
  color: var(--text-muted);
  font-weight: 800;
  letter-spacing: 0.12em;
  padding-inline: 0.15rem;
}

.job-row {
  position: relative;
  display: grid;
  grid-template-columns: 5rem minmax(0, 1fr) auto;
  gap: 1.1rem;
  align-items: center;
  padding: 1.15rem;
  overflow: hidden;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.15rem;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), color-mix(in srgb, var(--brand-soft) 18%, white));
  box-shadow: 0 0.45rem 1.2rem rgba(15, 23, 42, 0.045);
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.job-row:hover,
.job-row:focus-within {
  border-color: color-mix(in srgb, var(--brand-base) 34%, var(--border-subtle));
  background:
    linear-gradient(135deg, #fff, color-mix(in srgb, var(--brand-soft) 35%, white));
  box-shadow: 0 0.9rem 1.8rem rgba(15, 23, 42, 0.09);
}

.job-card-link {
  position: absolute;
  inset: 0;
  z-index: 1;
  border-radius: inherit;
}

.job-card-link:focus-visible {
  outline: 0.1875rem solid color-mix(in srgb, var(--brand-base) 70%, white);
  outline-offset: -0.25rem;
}

.company-logo,
.job-summary {
  pointer-events: none;
}

.company-logo {
  position: relative;
  z-index: 2;
  width: 4.75rem;
  height: 4.75rem;
  display: grid;
  place-items: center;
  border: 0.1875rem solid rgba(255, 255, 255, 0.9);
  border-radius: 1.1rem;
  color: #fff;
  font-size: 1.2rem;
  font-weight: 800;
  overflow: hidden;
  box-shadow: 0 0.55rem 1.1rem rgba(15, 23, 42, 0.12);
}

.company-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.job-summary {
  display: grid;
  gap: 0.48rem;
}

.job-title-line h2 {
  padding-right: 5.5rem;
  font-size: 1.14rem;
  line-height: 1.28;
}

.job-company {
  font-weight: 750;
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
  width: fit-content;
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
  width: fit-content;
  padding: 0.42rem 0.7rem;
  border-radius: 0.7rem;
  background: color-mix(in srgb, var(--brand-soft) 65%, white);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.job-time {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 3;
  padding: 0.28rem 0.55rem;
  border-radius: 999rem;
  background: var(--surface-secondary);
  font-size: 0.76rem;
  font-weight: 700;
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
  transition: color 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.save-button:hover {
  border-color: color-mix(in srgb, var(--brand-base) 28%, var(--border-subtle));
  color: var(--brand-strong);
}

.save-button--guest:hover,
.save-button--guest:active,
.save-button--guest:focus-visible {
  border-color: var(--border-subtle);
  background: var(--surface-secondary);
  color: var(--text-muted);
  box-shadow: none;
}

.bookmark-icon {
  width: 1.2rem;
  height: 1.2rem;
  fill: transparent;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linejoin: round;
  transition: fill 0.2s ease, stroke 0.2s ease, color 0.2s ease;
}

.save-button--active {
  border-color: color-mix(in srgb, var(--brand-base) 28%, var(--border-subtle));
  color: var(--brand-strong);
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
}

.save-button--active .bookmark-icon {
  fill: currentColor;
  stroke: currentColor;
  color: var(--brand-strong);
}

.details-button {
  min-width: 8.5rem;
  height: 2.9rem;
  padding-block: 0;
  justify-content: center;
}

.job-actions {
  position: relative;
  z-index: 3;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
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
  margin-top: 0;
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

.toggle-row input[type='checkbox'] {
  cursor: pointer;
  accent-color: var(--brand-base);
  width: 1.11rem;
  height: 1.11rem;
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
  .results-banner {
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
    grid-template-columns: 3.75rem minmax(0, 1fr);
    column-gap: 0.85rem;
    row-gap: 0.45rem;
    align-items: start;
    padding: 1rem;
  }

  .company-logo {
    grid-column: 1;
    grid-row: 1 / span 3;
    width: 3.75rem;
    height: 3.75rem;
    border-radius: 0.9rem;
    font-size: 1rem;
  }

  .job-summary {
    display: contents;
  }

  .job-title-line {
    grid-column: 2;
    grid-row: 1;
    min-width: 0;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: start;
    gap: 0.55rem;
  }

  .job-title-line h2 {
    min-width: 0;
    padding-right: 0;
    font-size: 1.05rem;
    overflow-wrap: anywhere;
  }

  .job-time {
    position: static;
    align-self: start;
    white-space: nowrap;
    padding: 0.2rem 0.45rem;
    font-size: 0.7rem;
  }

  .job-company {
    grid-column: 2;
    grid-row: 2;
    min-width: 0;
    overflow-wrap: anywhere;
    font-size: 0.9rem;
  }

  .job-location {
    grid-column: 2;
    grid-row: 3;
    min-width: 0;
    font-size: 0.84rem;
  }

  .job-tags {
    grid-column: 1 / -1;
    grid-row: 4;
    gap: 0.4rem;
    margin-top: 0.55rem;
  }

  .job-tag {
    min-height: 1.75rem;
    padding: 0.28rem 0.55rem;
    font-size: 0.72rem;
  }

  .job-salary {
    grid-column: 1 / -1;
    grid-row: 5;
    margin-top: 0.15rem;
    font-size: 0.92rem;
  }

  .job-actions {
    grid-column: 1 / -1;
    grid-row: 6;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: stretch;
    margin-top: 0.45rem;
    padding-top: 0.85rem;
    border-top: 0.0625rem solid var(--border-subtle);
  }

  .details-button {
    flex: 1;
    min-width: 0;
  }

  .save-button {
    width: 2.9rem;
  }

  .jobs-pagination {
    gap: 0.75rem;
  }

  .jobs-pagination__summary {
    text-align: center;
    font-size: 0.84rem;
  }

  .jobs-pagination__controls {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    gap: 0.5rem;
    align-items: center;
  }

  .pagination-numbers {
    grid-column: 2;
    justify-content: center;
    flex-wrap: nowrap;
    overflow: hidden;
    gap: 0.45rem;
  }

  .pagination-button {
    min-height: 2.6rem;
    font-size: 0.84rem;
  }

  .pagination-button--prev,
  .pagination-button--next {
    width: 2.6rem;
    min-width: 2.6rem;
    height: 2.6rem;
    padding: 0;
    border-radius: 999rem;
    justify-content: center;
    gap: 0;
    box-shadow: 0 0.45rem 1rem rgba(16, 24, 40, 0.08);
  }

  .pagination-button--number {
    min-width: 2.25rem;
    width: 2.25rem;
    height: 2.25rem;
    min-height: 2.25rem;
    padding-inline: 0;
  }

  .pagination-button--prev span,
  .pagination-button--next span {
    display: none;
  }

  .pagination-ellipsis {
    font-size: 0.8rem;
    padding-inline: 0;
  }
}

@media (max-width: 25rem) {
  .jobs-pagination__controls {
    grid-template-columns: auto minmax(0, 1fr) auto;
  }
}
</style>
