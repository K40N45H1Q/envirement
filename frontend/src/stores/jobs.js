import { defineStore } from 'pinia'
import { getJobs } from '@/api/jobs'
import { normalizeJob } from '@/utils/jobs'

const BOOKMARKS_STORAGE_KEY = 'cvhold-job-bookmarks'

const categoryConfigs = [
  { id: 'all', label: 'Все категории', icon: 'fas fa-border-all' },
  { id: 'construction', label: 'Строительство', icon: 'fas fa-hard-hat' },
  { id: 'production', label: 'Производство', icon: 'fas fa-industry' },
  { id: 'logistics', label: 'Логистика', icon: 'fas fa-truck-fast' },
  { id: 'it', label: 'IT и технологии', icon: 'fas fa-laptop-code' },
  { id: 'health', label: 'Медицина', icon: 'fas fa-heart-pulse' },
  { id: 'hospitality', label: 'Гостиничный бизнес', icon: 'fas fa-bell-concierge' },
]

const countryMeta = [
  { key: 'germany', label: 'Германия', flag: 'DE' },
  { key: 'netherlands', label: 'Нидерланды', flag: 'NL' },
  { key: 'poland', label: 'Польша', flag: 'PL' },
  { key: 'belgium', label: 'Бельгия', flag: 'BE' },
  { key: 'france', label: 'Франция', flag: 'FR' },
  { key: 'latvia', label: 'Латвия', flag: 'LV' },
  { key: 'estonia', label: 'Эстония', flag: 'EE' },
]

const employmentOptions = [
  { id: 'all', label: 'Любой тип' },
  { id: 'full-time', label: 'Полная занятость' },
  { id: 'shift', label: 'Сменный график' },
  { id: 'contract', label: 'Проект / контракт' },
]

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

const inferCategory = (job) => {
  const haystack = `${job.title} ${job.description} ${job.company}`.toLowerCase()

  if (/(свар|weld|welder|welding|монтаж|стро|construction|electric|элект|technician|repair|metal)/.test(haystack)) return 'construction'
  if (/(manufactur|производ|factory|industrial|assembly|operator)/.test(haystack)) return 'production'
  if (/(driver|логист|transport|truck|warehouse|fleet|\bce\b|courier|delivery)/.test(haystack)) return 'logistics'
  if (/(\bdeveloper\b|\bsoftware\b|\bdata\b|\btech\b|\bfrontend\b|\bbackend\b|\bfullstack\b|\bdevops\b|\bqa\b|\bit support\b)/.test(haystack)) return 'it'
  if (/(medical|doctor|nurse|мед|clinic|caregiver|healthcare)/.test(haystack)) return 'health'
  if (/(hotel|hostel|chef|cook|restaurant|guest|hospitality|waiter)/.test(haystack)) return 'hospitality'
  return 'construction'
}

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
  const haystack = `${job.title} ${job.description}`.toLowerCase()
  if (/(вахт|shift)/.test(haystack)) return 'shift'
  if (/(contract|project|проект|контракт)/.test(haystack)) return 'contract'
  return 'full-time'
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

const defaultFilters = () => ({
  searchTitle: '',
  searchLocation: '',
  selectedCategory: 'all',
  selectedCountry: 'all',
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
    categoryConfigs: () => categoryConfigs,
    employmentOptions: () => employmentOptions,

    enrichedJobs(state) {
      return state.jobs.map((job, index) => {
        const category = inferCategory(job)
        const countryKey = inferCountry(job.location)
        const country = countryMeta.find((item) => item.key === countryKey)
        const salaryAmount = parseSalaryAmount(job.salary)

        return {
          ...job,
          category,
          countryKey,
          countryLabel: country?.label || 'Европа',
          countryFlag: country?.flag || 'EU',
          timeLabel: timeLabel(job.created_at),
          isHot: index < 2,
          isNew: index < 3,
          salaryAmount,
          hasHousing: inferHousing(job),
          hasTransport: inferTransport(job),
          employmentType: inferEmployment(job),
          isBookmarked: state.bookmarks.includes(String(job.id)),
          tags: [
            inferHousing(job) ? 'Жильё' : 'Без жилья',
            inferTransport(job) ? 'Транспорт' : 'Самостоятельный доезд',
            category === 'construction' ? 'Европейский проект' : 'Работа в ЕС',
          ],
        }
      })
    },

    categoryCounts() {
      return categoryConfigs.map((category) => ({
        ...category,
        count: category.id === 'all'
          ? this.enrichedJobs.length
          : this.enrichedJobs.filter((job) => job.category === category.id).length,
      }))
    },

    countries() {
      const counts = this.enrichedJobs.reduce((acc, job) => {
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
    },

    featuredCountries() {
      return this.countries.slice(0, 5)
    },

    filteredJobs() {
      let result = [...this.enrichedJobs]
      const q = this.filters.searchTitle.trim().toLowerCase()
      const loc = this.filters.searchLocation.trim().toLowerCase()
      const salaryFrom = Number(this.filters.salaryFrom) || 0

      if (q) {
        result = result.filter((job) => `${job.title} ${job.company} ${job.description}`.toLowerCase().includes(q))
      }

      if (loc) {
        result = result.filter((job) => job.location.toLowerCase().includes(loc))
      }

      if (this.filters.selectedCategory !== 'all') {
        result = result.filter((job) => job.category === this.filters.selectedCategory)
      }

      if (this.filters.selectedCountry !== 'all') {
        result = result.filter((job) => job.countryKey === this.filters.selectedCountry)
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
      if (this.isLoading) return 'Обновляем выдачу вакансий...'
      if (!this.filteredJobs.length) return 'По текущим фильтрам вакансии не найдены'

      const parts = [`Найдено ${this.filteredJobs.length} вакансий`]

      if (this.filters.selectedCategory !== 'all') {
        const category = this.categoryCounts.find((item) => item.id === this.filters.selectedCategory)
        if (category) parts.push(category.label)
      }

      if (this.filters.selectedCountry !== 'all') {
        const country = this.countries.find((item) => item.key === this.filters.selectedCountry)
        if (country) parts.push(country.label)
      }

      if (this.filters.onlyBookmarked) {
        parts.push('закладки')
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
        this.error = 'Не удалось загрузить вакансии. Попробуйте обновить страницу.'
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

