import { defineStore } from 'pinia'
import { getJobs } from '@/api/jobs'
import { translate } from '@/i18n'
import { useUiStore } from '@/stores/ui'
import { formatJobLocation, getJobLocationSearchValues, normalizeText, resolveCountryMeta } from '@/utils/countries'
import { inferJobCategory, localizeCategoryConfigs } from '@/utils/jobCategories'
import { normalizeJob } from '@/utils/jobs'

const BOOKMARKS_STORAGE_KEY = 'cvhold-job-bookmarks'

const countryMeta = [
  { key: 'germany', labelKey: 'jobsStore.germany', flagCode: 'de' },
  { key: 'finland', labelKey: 'jobsStore.finland', flagCode: 'fi' },
  { key: 'czechia', labelKey: 'jobsStore.czechia', flagCode: 'cz' },
  { key: 'netherlands', labelKey: 'jobsStore.netherlands', flagCode: 'nl' },
  { key: 'poland', labelKey: 'jobsStore.poland', flagCode: 'pl' },
  { key: 'belgium', labelKey: 'jobsStore.belgium', flagCode: 'be' },
  { key: 'france', labelKey: 'jobsStore.france', flagCode: 'fr' },
  { key: 'latvia', labelKey: 'jobsStore.latvia', flagCode: 'lv' },
  { key: 'estonia', labelKey: 'jobsStore.estonia', flagCode: 'ee' },
]

const employmentOptions = [
  { id: 'all', labelKey: 'jobsStore.anyType' },
  { id: 'full-time', labelKey: 'jobsStore.fullTime' },
  { id: 'shift', labelKey: 'jobsStore.shift' },
  { id: 'contract', labelKey: 'jobsStore.contract' },
]

const getLanguage = () => {
  try {
    return useUiStore().language
  } catch {
    return 'ru'
  }
}

const t = (key, params = {}) => translate(key, params, getLanguage())

const getLocalizedCategories = () => localizeCategoryConfigs((key) => t(key))

const localizeCountryMeta = () => countryMeta.map((country) => ({
  ...country,
  label: t(country.labelKey),
}))

const localizeEmploymentOptions = () => employmentOptions.map((option) => ({
  ...option,
  label: t(option.labelKey),
}))

const buildSearchTokens = (value = '') => normalizeText(value).split(/\s+/).filter(Boolean)

const includesAllTokens = (value = '', tokens = []) => {
  if (!tokens.length) return true
  const haystack = normalizeText(value)
  return tokens.every((token) => haystack.includes(token))
}

const isLatviaKey = (value = '') => normalizeText(value).replace(/\s+/g, '') === 'latvia'

const keywordHaystack = (job) => [
  job.title,
].filter(Boolean).join(' ')

const locationHaystack = (job) => getJobLocationSearchValues(job).join(' ')

const readBookmarks = () => {
  try {
    const raw = localStorage.getItem(BOOKMARKS_STORAGE_KEY)
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed.map((value) => String(value)) : []
  } catch {
    return []
  }
}

const persistBookmarks = (bookmarks) => {
  localStorage.setItem(BOOKMARKS_STORAGE_KEY, JSON.stringify(bookmarks))
}

const legacyInferCountry = (location = '') => {
  const value = location.toLowerCase()
  if (value.includes('герман') || value.includes('germany') || value.includes('berlin')) return 'germany'
  if (value.includes('финля') || value.includes('finland') || value.includes('tampere')) return 'finland'
  if (value.includes('чех') || value.includes('czech') || value.includes('prague') || value.includes('praha')) return 'czechia'
  if (value.includes('нидер') || value.includes('netherlands') || value.includes('rotterdam')) return 'netherlands'
  if (value.includes('польш') || value.includes('poland') || value.includes('warsaw')) return 'poland'
  if (value.includes('бельг') || value.includes('belgium') || value.includes('antwerp')) return 'belgium'
  if (value.includes('франц') || value.includes('france') || value.includes('paris')) return 'france'
  if (value.includes('латв') || value.includes('latvia') || value.includes('riga')) return 'latvia'
  if (value.includes('эстон') || value.includes('estonia') || value.includes('tallinn')) return 'estonia'
  return 'other'
}

const parseSalaryAmount = (salary = '') => {
  const values = String(salary)
    .replace(/[^\d,-]/g, ' ')
    .match(/\d[\d\s]*/g)

  if (!values?.length) return 0
  return Math.max(...values.map((value) => Number(value.replace(/\s+/g, '')) || 0))
}

const inferHousing = (job) => job.has_housing ?? /(жиль|housing|accommodation|relocation|прожив)/i.test(`${job.title} ${job.description}`)
const inferTransport = (job) => job.has_transport ?? /(transport|shuttle|car|vehicle|авто|транспорт|доставка)/i.test(`${job.title} ${job.description}`)
const inferEmployment = (job) => {
  if (job.employment_type || job.employmentType) {
    return String(job.employment_type || job.employmentType)
  }

  const haystack = `${job.title} ${job.description}`.toLowerCase()
  if (/(вахт|shift)/.test(haystack)) return 'shift'
  if (/(contract|project|проект|контракт)/.test(haystack)) return 'contract'
  return 'full-time'
}

const timeLabel = (createdAt) => {
  if (!createdAt) return t('jobsStore.recent')
  const date = new Date(createdAt)
  const now = new Date()
  const diff = Math.max(0, now.getTime() - date.getTime())
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days <= 0) return t('jobsStore.today')
  if (days === 1) return t('jobsStore.yesterday')
  if (days < 7) return t('jobsStore.daysAgo', { count: days })
  return date.toLocaleDateString(getLanguage() === 'en' ? 'en-GB' : 'ru-RU')
}

const defaultFilters = () => ({
  searchTitle: '',
  searchLocation: '',
  selectedCategory: 'all',
  selectedCountry: 'all',
  onlyAbroad: false,
  selectedTab: 'all',
  selectedSort: 'newest',
  selectedEmployment: 'all',
  salaryFrom: '',
  onlyWithHousing: false,
  onlyWithTransport: false,
  onlyBookmarked: false,
})

export const useJobsStore = defineStore('jobs', {
  state: () => ({
    jobs: [],
    isLoading: false,
    error: '',
    brokenLogos: {},
    bookmarks: readBookmarks(),
    filters: defaultFilters(),
    initialized: false,
  }),

  getters: {
    categoryConfigs: () => getLocalizedCategories(),
    employmentOptions: () => localizeEmploymentOptions(),

    enrichedJobs(state) {
      const countries = localizeCountryMeta()
      const countriesByKey = Object.fromEntries(countries.map((country) => [country.key, country]))
      const categoriesById = Object.fromEntries(getLocalizedCategories().map((category) => [category.id, category.label]))

      return state.jobs.map((job, index) => {
        const category = inferJobCategory(job)
        const resolvedCountry = resolveCountryMeta(job)
        const countryKey = resolvedCountry.countryKey || legacyInferCountry(job.location)
        const country = countriesByKey[countryKey]
        const salaryAmount = parseSalaryAmount(job.salary)

        return {
          ...job,
          category,
          countryKey,
          countryLabel: country?.label || resolvedCountry.countryLabel || t('jobsStore.europe'),
          countryFlagCode: country?.flagCode || resolvedCountry.countryFlagCode || 'eu',
          displayLocation: formatJobLocation({
            ...job,
            country_key: countryKey,
            country_label: country?.label || resolvedCountry.countryLabel || '',
          }),
          timeLabel: timeLabel(job.created_at),
          isHot: index < 2,
          isNew: index < 3,
          salaryAmount,
          hasHousing: inferHousing(job),
          hasTransport: inferTransport(job),
          employmentType: inferEmployment(job),
          isBookmarked: state.bookmarks.includes(String(job.id)),
          categoryLabel: categoriesById[category] || '',
          tags: [
            inferHousing(job) ? t('jobsStore.housing') : t('jobsStore.noHousing'),
            inferTransport(job) ? t('jobsStore.transport') : t('jobsStore.selfCommute'),
            category === 'construction-real-estate' ? t('jobsStore.euProject') : t('jobsStore.euWork'),
          ],
        }
      })
    },

    categoryCounts() {
      return this.categoryConfigs.map((category) => ({
        ...category,
        count: category.id === 'all'
          ? this.enrichedJobs.length
          : this.enrichedJobs.filter((job) => job.category === category.id).length,
      }))
    },

    countries() {
      const localizedCountries = localizeCountryMeta()
      const counts = this.enrichedJobs.reduce((acc, job) => {
        if (this.filters.onlyAbroad && isLatviaKey(job.countryKey)) return acc
        acc[job.countryKey] = (acc[job.countryKey] || 0) + 1
        return acc
      }, {})

      return localizedCountries
        .map((country) => ({
          ...country,
          count: counts[country.key] || 0,
        }))
        .filter((country) => country.count > 0)
        .sort((a, b) => b.count - a.count)
    },

    featuredCountries() {
      return this.countries.slice(0, 5)
    },

    filteredJobs() {
      let result = [...this.enrichedJobs]
      const qTokens = buildSearchTokens(this.filters.searchTitle)
      const locTokens = buildSearchTokens(this.filters.searchLocation)
      const salaryFrom = Number(this.filters.salaryFrom) || 0

      if (qTokens.length) {
        result = result.filter((job) => includesAllTokens(keywordHaystack(job), qTokens))
      }

      if (locTokens.length) {
        result = result.filter((job) => includesAllTokens(locationHaystack(job), locTokens))
      }

      if (this.filters.selectedCategory !== 'all') {
        result = result.filter((job) => job.category === this.filters.selectedCategory)
      }

      if (this.filters.selectedCountry !== 'all') {
        result = result.filter((job) => job.countryKey === this.filters.selectedCountry)
      }

      if (this.filters.onlyAbroad) {
        result = result.filter((job) => !isLatviaKey(job.countryKey))
      }

      if (this.filters.selectedEmployment !== 'all') {
        result = result.filter((job) => job.employmentType === this.filters.selectedEmployment)
      }

      if (salaryFrom > 0) {
        result = result.filter((job) => job.salaryAmount >= salaryFrom)
      }

      if (this.filters.onlyWithHousing) {
        result = result.filter((job) => job.hasHousing)
      }

      if (this.filters.onlyWithTransport) {
        result = result.filter((job) => job.hasTransport)
      }

      if (this.filters.onlyBookmarked) {
        result = result.filter((job) => job.isBookmarked)
      }

      if (this.filters.selectedTab === 'hot') {
        result = result.filter((job) => job.isHot)
      }

      if (this.filters.selectedTab === 'favorites') {
        result = result.filter((job) => job.isBookmarked)
      }

      if (this.filters.selectedSort === 'salary') {
        result.sort((a, b) => b.salaryAmount - a.salaryAmount)
      } else {
        result.sort((a, b) => (b.id || 0) - (a.id || 0))
      }

      return result
    },

    hotCount() {
      return this.enrichedJobs.filter((job) => job.isHot).length
    },

    bookmarkedCount() {
      return this.enrichedJobs.filter((job) => job.isBookmarked).length
    },

    resultsLabel() {
      if (this.isLoading) return t('jobsStore.updating')
      if (!this.filteredJobs.length) return t('jobsStore.noMatches')

      const parts = [t('jobsStore.foundJobs', { count: this.filteredJobs.length })]

      if (this.filters.selectedCategory !== 'all') {
        const category = this.categoryCounts.find((item) => item.id === this.filters.selectedCategory)
        if (category) parts.push(category.label)
      }

      if (this.filters.selectedCountry !== 'all') {
        const country = this.countries.find((item) => item.key === this.filters.selectedCountry)
        if (country) parts.push(country.label)
      }

      if (this.filters.onlyAbroad) {
        parts.push(t('navbar.jobsMenuAbroad'))
      }

      if (this.filters.onlyBookmarked) {
        parts.push(t('jobsStore.bookmarks'))
      }

      return parts.join(' • ')
    },

    routeQuery(state) {
      const query = {}
      const filters = state.filters

      if (filters.searchTitle) query.q = filters.searchTitle
      if (filters.searchLocation) query.loc = filters.searchLocation
      if (filters.selectedCategory !== 'all') query.category = filters.selectedCategory
      if (filters.selectedCountry !== 'all') query.country = filters.selectedCountry
      if (filters.onlyAbroad) query.abroad = '1'
      if (filters.selectedTab !== 'all') query.tab = filters.selectedTab
      if (filters.selectedSort !== 'newest') query.sort = filters.selectedSort
      if (filters.selectedEmployment !== 'all') query.employment = filters.selectedEmployment
      if (filters.salaryFrom) query.salary_from = filters.salaryFrom
      if (filters.onlyWithHousing) query.housing = '1'
      if (filters.onlyWithTransport) query.transport = '1'
      if (filters.onlyBookmarked) query.bookmarked = '1'

      return query
    },
  },

  actions: {
    async loadJobs() {
      this.isLoading = true
      this.error = ''

      try {
        const data = await getJobs()
        this.jobs = Array.isArray(data) ? data.map(normalizeJob) : []
      } catch {
        this.jobs = []
        this.error = t('jobsStore.loadError')
      } finally {
        this.isLoading = false
      }
    },

    async initialize(query = {}) {
      this.applyRouteQuery(query)
      await this.loadJobs()
      this.initialized = true
    },

    applyRouteQuery(query = {}) {
      this.filters.searchTitle = typeof query.q === 'string' ? query.q : ''
      this.filters.searchLocation = typeof query.loc === 'string' ? query.loc : ''
      this.filters.selectedCategory = typeof query.category === 'string' ? query.category : 'all'
      this.filters.selectedCountry = typeof query.country === 'string' ? query.country : 'all'
      this.filters.onlyAbroad = query.abroad === '1'
      if (this.filters.onlyAbroad && isLatviaKey(this.filters.selectedCountry)) {
        this.filters.selectedCountry = 'all'
      }
      this.filters.selectedTab = typeof query.tab === 'string' ? query.tab : 'all'
      this.filters.selectedSort = typeof query.sort === 'string' ? query.sort : 'newest'
      this.filters.selectedEmployment = typeof query.employment === 'string' ? query.employment : 'all'
      this.filters.salaryFrom = typeof query.salary_from === 'string' ? query.salary_from : ''
      this.filters.onlyWithHousing = query.housing === '1'
      this.filters.onlyWithTransport = query.transport === '1'
      this.filters.onlyBookmarked = query.bookmarked === '1'
    },

    resetFilters() {
      this.filters = defaultFilters()
    },

    setFilter(key, value) {
      this.filters[key] = value
    },

    toggleBookmark(jobId) {
      const normalizedJobId = String(jobId)

      if (this.bookmarks.includes(normalizedJobId)) {
        this.bookmarks = this.bookmarks.filter((id) => id !== normalizedJobId)
      } else {
        this.bookmarks = [...this.bookmarks, normalizedJobId]
      }

      if (this.filters.selectedTab === 'favorites') {
        this.filters.onlyBookmarked = true
      }

      persistBookmarks(this.bookmarks)
    },

    markBrokenLogo(jobId) {
      this.brokenLogos = {
        ...this.brokenLogos,
        [jobId]: true,
      }
    },

    hasLogo(job) {
      return !!job.logo && !this.brokenLogos[job.id]
    },
  },
})
