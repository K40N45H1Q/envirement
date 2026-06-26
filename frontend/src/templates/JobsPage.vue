<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { getJobs } from '@/api/jobs'
import { normalizeJob } from '@/utils/jobs'

const jobs = ref([])
const isLoading = ref(false)
const error = ref('')
const searchTitle = ref('')
const searchLocation = ref('')
const selectedCategory = ref('all')
const selectedCountry = ref('all')
const selectedTab = ref('all')
const selectedSort = ref('newest')
const jobsListRef = ref(null)
const brokenLogos = ref({})

const categoryConfigs = [
  { id: 'all', label: 'Все категории', icon: 'fas fa-border-all' },
  { id: 'construction', label: 'Строительство', icon: 'fas fa-hard-hat' },
  { id: 'production', label: 'Производство', icon: 'fas fa-industry' },
  { id: 'logistics', label: 'Логистика', icon: 'fas fa-truck-fast' },
  { id: 'it', label: 'IT и технологии', icon: 'fas fa-laptop-code' },
  { id: 'health', label: 'Медицина', icon: 'fas fa-heart-pulse' },
  { id: 'hospitality', label: 'Гостиничный бизнес', icon: 'fas fa-bell-concierge' },
]

const inferCategory = (job) => {
  const haystack = `${job.title} ${job.description} ${job.company}`.toLowerCase()

  if (/(свар|монтаж|стро|electric|элект|technician|repair)/.test(haystack)) return 'construction'
  if (/(manufact|производ|factory|industrial)/.test(haystack)) return 'production'
  if (/(driver|логист|transport|ce|truck|warehouse)/.test(haystack)) return 'logistics'
  if (/(developer|software|data|it|tech|frontend|backend)/.test(haystack)) return 'it'
  if (/(medical|doctor|nurse|мед|clinic|care)/.test(haystack)) return 'health'
  if (/(hotel|hostel|chef|cook|restaurant|guest)/.test(haystack)) return 'hospitality'
  return 'construction'
}

const countryMeta = [
  { key: 'germany', label: 'Германия', flag: '🇩🇪' },
  { key: 'netherlands', label: 'Нидерланды', flag: '🇳🇱' },
  { key: 'poland', label: 'Польша', flag: '🇵🇱' },
  { key: 'belgium', label: 'Бельгия', flag: '🇧🇪' },
  { key: 'france', label: 'Франция', flag: '🇫🇷' },
  { key: 'latvia', label: 'Латвия', flag: '🇱🇻' },
  { key: 'estonia', label: 'Эстония', flag: '🇪🇪' },
]

const inferCountry = (location = '') => {
  const value = location.toLowerCase()
  if (value.includes('герман') || value.includes('germany') || value.includes('berlin')) return 'germany'
  if (value.includes('нидер') || value.includes('netherlands') || value.includes('rotterdam')) return 'netherlands'
  if (value.includes('польш') || value.includes('poland') || value.includes('warsaw')) return 'poland'
  if (value.includes('бельг') || value.includes('belgium') || value.includes('antwerp')) return 'belgium'
  if (value.includes('франц') || value.includes('france') || value.includes('paris')) return 'france'
  if (value.includes('латв') || value.includes('latvia') || value.includes('riga')) return 'latvia'
  if (value.includes('эстон') || value.includes('estonia') || value.includes('tallinn')) return 'estonia'
  return 'other'
}

const timeLabel = (createdAt) => {
  if (!createdAt) return 'Недавно'
  const date = new Date(createdAt)
  const now = new Date()
  const diff = Math.max(0, now.getTime() - date.getTime())
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days <= 0) return 'Сегодня'
  if (days === 1) return 'Вчера'
  if (days < 7) return `${days} дн. назад`
  return date.toLocaleDateString('ru-RU')
}

const enrichedJobs = computed(() => jobs.value.map((job, index) => {
  const category = inferCategory(job)
  const countryKey = inferCountry(job.location)
  const country = countryMeta.find((item) => item.key === countryKey)

  return {
    ...job,
    category,
    countryKey,
    countryLabel: country?.label || 'Европа',
    countryFlag: country?.flag || '🇪🇺',
    timeLabel: timeLabel(job.created_at),
    isHot: index < 2,
    isNew: index < 3,
    tags: [
      'Жильё',
      category === 'logistics' ? 'Транспорт' : 'Официальное трудоустройство',
      category === 'construction' ? 'Европейский проект' : 'Работа в ЕС',
    ],
  }
}))

const loadJobs = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const data = await getJobs()
    jobs.value = Array.isArray(data) ? data.map(normalizeJob) : []
  } catch {
    jobs.value = []
    error.value = 'Не удалось загрузить вакансии из backend.'
  } finally {
    isLoading.value = false
  }
}

const categoryCounts = computed(() => categoryConfigs.map((category) => ({
  ...category,
  count: category.id === 'all'
    ? enrichedJobs.value.length
    : enrichedJobs.value.filter((job) => job.category === category.id).length,
})))

const countries = computed(() => {
  const counts = enrichedJobs.value.reduce((acc, job) => {
    acc[job.countryKey] = (acc[job.countryKey] || 0) + 1
    return acc
  }, {})

  return countryMeta
    .map((country) => ({
      ...country,
      count: counts[country.key] || 0,
    }))
    .filter((country) => country.count > 0)
    .sort((a, b) => b.count - a.count)
})

const filteredJobs = computed(() => {
  let result = [...enrichedJobs.value]
  const q = searchTitle.value.trim().toLowerCase()
  const loc = searchLocation.value.trim().toLowerCase()

  if (q) {
    result = result.filter((job) =>
      `${job.title} ${job.company} ${job.description}`.toLowerCase().includes(q))
  }

  if (loc) {
    result = result.filter((job) => job.location.toLowerCase().includes(loc))
  }

  if (selectedCategory.value !== 'all') {
    result = result.filter((job) => job.category === selectedCategory.value)
  }

  if (selectedCountry.value !== 'all') {
    result = result.filter((job) => job.countryKey === selectedCountry.value)
  }

  if (selectedTab.value === 'hot') {
    result = result.filter((job) => job.isHot)
  }

  if (selectedTab.value === 'new') {
    result = result.filter((job) => job.isNew)
  }

  if (selectedSort.value === 'salary') {
    result.sort((a, b) => b.salary.localeCompare(a.salary, 'ru'))
  } else {
    result.sort((a, b) => (b.id || 0) - (a.id || 0))
  }

  return result
})

const hotCount = computed(() => enrichedJobs.value.filter((job) => job.isHot).length)
const newCount = computed(() => enrichedJobs.value.filter((job) => job.isNew).length)
const featuredCountries = computed(() => countries.value.slice(0, 5))

const resultsLabel = computed(() => {
  if (isLoading.value) return 'Обновляем выдачу вакансий...'
  if (!filteredJobs.value.length) return 'По текущим фильтрам вакансии не найдены'

  const parts = [`Найдено ${filteredJobs.value.length} ваканс${filteredJobs.value.length === 1 ? 'ия' : filteredJobs.value.length < 5 ? 'ии' : 'ий'}`]

  if (selectedCategory.value !== 'all') {
    const category = categoryCounts.value.find((item) => item.id === selectedCategory.value)
    if (category) parts.push(category.label)
  }

  if (selectedCountry.value !== 'all') {
    const country = countries.value.find((item) => item.key === selectedCountry.value)
    if (country) parts.push(country.label)
  }

  return parts.join(' • ')
})

const hasLogo = (job) => !!job.logo && !brokenLogos.value[job.id]

const markBrokenLogo = (jobId) => {
  brokenLogos.value = {
    ...brokenLogos.value,
    [jobId]: true,
  }
}

const resetFilters = () => {
  searchTitle.value = ''
  searchLocation.value = ''
  selectedCategory.value = 'all'
  selectedCountry.value = 'all'
  selectedTab.value = 'all'
  selectedSort.value = 'newest'
}

const runSearch = () => {
  jobsListRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(loadJobs)
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="hero surface-section">
        <div class="hero-copy">
          <p class="section-eyebrow">Вакансии</p>
          <h1>Найдите работу мечты по всей Европе</h1>
          <p>
            Реальные вакансии из backend, быстрый поиск по роли и локации, плюс
            понятные фильтры и свежая выдача.
          </p>
        </div>

        <div class="hero-map" aria-hidden="true">
          <div class="map-glow map-glow--one"></div>
          <div class="map-glow map-glow--two"></div>
          <div class="map-grid"></div>
        </div>
      </section>

      <section class="content-grid">
        <div class="main-column">
          <section class="search-shell surface-card">
            <div class="search-grid">
              <label>
                <span>Я ищу</span>
                <div class="input-wrap">
                  <input v-model="searchTitle" placeholder="Должность, ключевое слово" />
                  <i class="fas fa-magnifying-glass"></i>
                </div>
              </label>

              <label>
                <span>Где</span>
                <div class="input-wrap">
                  <input v-model="searchLocation" placeholder="Страна, город или регион" />
                  <i class="fas fa-location-dot"></i>
                </div>
              </label>

              <label>
                <span>Категория</span>
                <div class="input-wrap">
                  <select v-model="selectedCategory">
                    <option v-for="category in categoryCounts" :key="category.id" :value="category.id">
                      {{ category.label }}
                    </option>
                  </select>
                  <i class="fas fa-angle-down"></i>
                </div>
              </label>

              <button type="button" class="btn-primary search-button" @click="runSearch">
                Найти вакансии
              </button>
            </div>

            <div class="category-row">
              <button
                v-for="category in categoryCounts"
                :key="category.id"
                type="button"
                class="category-pill"
                :class="{ 'category-pill--active': selectedCategory === category.id }"
                @click="selectedCategory = category.id"
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
                <p>Лента формируется напрямую из backend и обновляется с учётом выбранных фильтров.</p>
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
                  :class="{ 'tab-button--active': selectedTab === 'all' }"
                  @click="selectedTab = 'all'"
                >
                  Все вакансии
                  <span>{{ enrichedJobs.length }}</span>
                </button>
                <button
                  type="button"
                  class="tab-button"
                  :class="{ 'tab-button--active': selectedTab === 'hot' }"
                  @click="selectedTab = 'hot'"
                >
                  Горячие вакансии
                  <span>{{ hotCount }}</span>
                </button>
                <button
                  type="button"
                  class="tab-button"
                  :class="{ 'tab-button--active': selectedTab === 'new' }"
                  @click="selectedTab = 'new'"
                >
                  Новые вакансии
                  <span>{{ newCount }}</span>
                </button>
              </div>

              <div class="toolbar-actions">
                <label class="sort-label">
                  <span>Сортировка:</span>
                  <select v-model="selectedSort">
                    <option value="newest">Новые сначала</option>
                    <option value="salary">По зарплате</option>
                  </select>
                </label>
              </div>
            </header>

            <div v-if="error" class="notice">{{ error }}</div>
            <div v-else-if="isLoading" class="notice">Загрузка вакансий...</div>

            <div v-else class="jobs-list">
              <article v-for="job in filteredJobs" :key="job.id" class="job-row">
                <div class="company-logo" :style="{ background: job.color }">
                  <img v-if="hasLogo(job)" :src="job.logo" :alt="job.company" @error="markBrokenLogo(job.id)" />
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
                  <button type="button" class="save-button" aria-label="Сохранить">
                    <i class="far fa-bookmark"></i>
                  </button>
                  <RouterLink :to="`/jobs/${job.id}`" class="btn-primary details-button">
                    Подробнее
                  </RouterLink>
                </div>
              </article>

              <div v-if="!filteredJobs.length" class="notice">
                Вакансии не найдены. Попробуйте изменить фильтры или запрос.
              </div>
            </div>
          </section>

          <section class="countries-strip surface-card">
            <header class="strip-head">
              <h3>Популярные страны</h3>
              <button type="button" class="link-button">Все страны</button>
            </header>

            <div class="country-cards">
              <article v-for="country in featuredCountries" :key="country.key" class="country-card">
                <strong>{{ country.flag }} {{ country.label }}</strong>
                <span>{{ country.count }} вакансий</span>
              </article>
            </div>
          </section>
        </div>

        <aside class="sidebar-column">
          <section class="map-card surface-card">
            <header class="sidebar-head">
              <h3>Работа на карте</h3>
            </header>

            <div class="mini-map" aria-hidden="true">
              <div class="map-glow map-glow--three"></div>
              <div class="map-glow map-glow--four"></div>
              <div class="map-grid"></div>
            </div>

            <div class="country-list">
              <button
                v-for="country in featuredCountries"
                :key="country.key"
                type="button"
                class="country-item"
                @click="selectedCountry = country.key"
              >
                <span>{{ country.flag }} {{ country.label }}</span>
                <strong>{{ country.count }}</strong>
              </button>
            </div>

            <button type="button" class="btn-secondary sidebar-button" @click="selectedCountry = 'all'">
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
                :class="{ 'filter-check--active': selectedCountry === country.key }"
                @click="selectedCountry = selectedCountry === country.key ? 'all' : country.key"
              >
                <span>{{ country.flag }} {{ country.label }}</span>
                <strong>{{ country.count }}</strong>
              </button>
            </div>

            <div class="filter-group filter-group--collapsed">
              <h4>Зарплата</h4>
            </div>
            <div class="filter-group filter-group--collapsed">
              <h4>Тип занятости</h4>
            </div>
            <div class="filter-group filter-group--collapsed">
              <h4>Жильё</h4>
            </div>
            <div class="filter-group filter-group--collapsed">
              <h4>Транспорт</h4>
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
  padding: 1.5rem var(--shell-gutter) 4rem;
  display: grid;
  gap: 1.25rem;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(18rem, 24rem);
  gap: 1.5rem;
  padding: 1.75rem;
  overflow: hidden;
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.1rem);
  color: var(--text-primary);
}

.hero-copy p:not(.section-eyebrow) {
  max-width: 40rem;
  margin-top: 0.75rem;
  color: var(--text-muted);
  line-height: 1.65;
}

.hero-map,
.mini-map {
  position: relative;
  overflow: hidden;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.25rem;
  background:
    radial-gradient(circle at 25% 35%, rgba(29, 168, 107, 0.16), transparent 24%),
    radial-gradient(circle at 70% 55%, rgba(29, 168, 107, 0.14), transparent 18%),
    linear-gradient(180deg, rgba(232, 249, 238, 0.9), rgba(255, 255, 255, 0.96));
}

.hero-map {
  min-height: 13rem;
}

.mini-map {
  min-height: 15rem;
}

.map-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(29, 168, 107, 0.06) 0.0625rem, transparent 0.0625rem),
    linear-gradient(90deg, rgba(29, 168, 107, 0.06) 0.0625rem, transparent 0.0625rem);
  background-size: 1rem 1rem;
  mask-image: radial-gradient(circle at center, black 45%, transparent 95%);
}

.map-glow {
  position: absolute;
  width: 5.5rem;
  height: 5.5rem;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(20, 184, 87, 0.42) 0%, rgba(20, 184, 87, 0.06) 58%, transparent 75%);
  filter: blur(0.125rem);
}

.map-glow--one {
  top: 18%;
  right: 24%;
}

.map-glow--two {
  bottom: 12%;
  left: 28%;
}

.map-glow--three {
  top: 24%;
  left: 34%;
}

.map-glow--four {
  bottom: 18%;
  right: 18%;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 20rem;
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

.sidebar-column {
  position: sticky;
  top: 5.5rem;
}

.search-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 0.95fr) auto;
  gap: 0.85rem;
}

.search-grid label {
  display: grid;
  gap: 0.45rem;
  color: var(--text-primary);
  font-weight: 700;
}

.input-wrap {
  position: relative;
}

.input-wrap input,
.input-wrap select {
  width: 100%;
  min-height: 3.3rem;
  padding: 0.9rem 2.8rem 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
  appearance: none;
}

.input-wrap i {
  position: absolute;
  top: 50%;
  right: 1rem;
  transform: translateY(-50%);
  color: var(--brand-strong);
  pointer-events: none;
}

.search-button {
  align-self: end;
  min-width: 11rem;
}

.category-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}

.category-pill {
  min-height: 4.3rem;
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
  transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease;
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
  border-color: var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
}

.jobs-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
}

.results-banner {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.95rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background:
    linear-gradient(135deg, rgba(20, 184, 87, 0.09), rgba(255, 255, 255, 0.94)),
    var(--surface-secondary);
}

.results-banner strong {
  color: var(--text-primary);
  font-size: 1rem;
}

.results-banner p {
  margin: 0.3rem 0 0;
  color: var(--text-muted);
  line-height: 1.5;
}

.results-reset {
  white-space: nowrap;
}

.job-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.tab-button {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font: inherit;
  font-weight: 700;
  padding: 0 0 0.55rem;
  cursor: pointer;
  border-bottom: 0.125rem solid transparent;
}

.tab-button span {
  margin-left: 0.45rem;
  color: var(--brand-strong);
}

.tab-button--active {
  color: var(--brand-strong);
  border-color: var(--brand-strong);
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sort-label {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--text-muted);
}

.sort-label select {
  border: none;
  background: transparent;
  color: var(--brand-strong);
  font: inherit;
  font-weight: 700;
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
  transition: transform 0.2s ease, background 0.2s ease;
}

.job-row:hover {
  transform: translateY(-0.0625rem);
  background: linear-gradient(90deg, rgba(20, 184, 87, 0.035), transparent 50%);
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

.job-company {
  color: var(--text-muted);
  font-weight: 600;
}

.job-title-line {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.job-title-line h2 {
  margin: 0;
  font-size: 1.35rem;
  color: var(--text-primary);
}

.job-time {
  color: var(--text-muted);
  white-space: nowrap;
}

.job-location {
  display: inline-flex;
  gap: 0.45rem;
  align-items: center;
  color: var(--text-muted);
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.job-tag {
  display: inline-flex;
  align-items: center;
  min-height: 1.85rem;
  padding: 0.2rem 0.65rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
  color: var(--brand-strong);
  font-size: 0.8rem;
  font-weight: 700;
}

.job-salary {
  color: var(--text-muted);
  font-size: 0.98rem;
}

.job-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.save-button {
  width: 2.8rem;
  height: 2.8rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.9rem;
  background: var(--surface-secondary);
  color: var(--text-muted);
  cursor: pointer;
}

.details-button {
  min-width: 8rem;
}

.sidebar-head,
.strip-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.sidebar-head h3,
.strip-head h3 {
  margin: 0;
  color: var(--text-primary);
}

.country-list,
.filter-group,
.country-cards {
  display: grid;
  gap: 0.7rem;
}

.country-list {
  margin-top: 1rem;
}

.country-item,
.filter-check {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.1rem 0;
  border: none;
  background: transparent;
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;
}

.country-item strong,
.filter-check strong {
  color: var(--brand-strong);
}

.sidebar-button {
  width: 100%;
  margin-top: 1rem;
}

.link-button {
  border: none;
  background: transparent;
  color: var(--brand-strong);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.filter-group {
  padding-top: 1rem;
  border-top: 0.0625rem solid var(--border-subtle);
}

.filter-group h4 {
  margin: 0 0 0.2rem;
  color: var(--text-primary);
}

.filter-check--active {
  color: var(--brand-strong);
}

.filter-group--collapsed {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-group--collapsed::after {
  content: '+';
  color: var(--text-muted);
}

.country-cards {
  grid-template-columns: repeat(5, minmax(0, 1fr));
  margin-top: 1rem;
}

.country-card {
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
}

.country-card strong,
.country-card span {
  display: block;
}

.country-card span {
  margin-top: 0.35rem;
  color: var(--text-muted);
}

@media (max-width: 76rem) {
  .content-grid,
  .hero {
    grid-template-columns: 1fr;
  }

  .sidebar-column {
    position: static;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .category-row {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .country-cards {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 58rem) {
  .search-grid,
  .job-row,
  .sidebar-column,
  .country-cards {
    grid-template-columns: 1fr;
  }

  .results-banner,
  .jobs-toolbar,
  .job-title-line,
  .job-actions {
    align-items: start;
    flex-direction: column;
  }

  .category-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .company-logo {
    width: 4rem;
    height: 4rem;
  }

  .details-button,
  .search-button,
  .results-reset {
    width: 100%;
  }
}

@media (max-width: 40rem) {
  .page {
    padding-top: 1.1rem;
  }

  .hero,
  .search-shell,
  .jobs-shell,
  .countries-strip,
  .map-card,
  .filters-card {
    padding: 1rem;
  }

  .category-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
