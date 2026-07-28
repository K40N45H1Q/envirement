import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/templates/HomePage.vue'
import ProfilePage from '@/templates/ProfilePage.vue'
import JobsPage from '@/templates/JobsPage.vue'
import JobDetailPage from '@/templates/JobDetailPage.vue'
import JobDirectoryPage from '@/templates/JobDirectoryPage.vue'
import PricingPage from '@/templates/PricingPage.vue'
import DashboardPage from '@/templates/DashboardPage.vue'
import ResponsesPage from '@/templates/ResponsesPage.vue'
import ResponseCvPage from '@/templates/ResponseCvPage.vue'
import MessagesPage from '@/templates/MessagesPage.vue'
import AboutPage from '@/templates/AboutPage.vue'
import InfoPage from '@/templates/InfoPage.vue'
import ContactsPage from '@/templates/ContactsPage.vue'
import SignInPage from '@/templates/SignInPage.vue'
import AdminPanel from '@/components/apanel/AdminPanel.vue'
import { normalizeLanguage } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { getLocaleFromPath, hasLocalePrefix, isPublicSeoPath, localizeFullPath, stripLocaleFromPath, withLocale } from './locale'

const SITE_ORIGIN = 'https://www.cvhold.com'

const SEO_COPY = {
  lv: {
    defaultTitle: 'CVHOLD - vakances un personala atlases platforma Eiropa',
    defaultDescription: 'CVHOLD palidz kandidatiem atrast vakances Eiropa un darba devejiem publicet vakances, parvaldit pieteikumus un atlasit piemerotus specialistus.',
    pages: {
      '/': ['Vakances Eiropa | CVHOLD', 'Atrodiet vakances pec valsts, kategorijas, algas un darba nosacijumiem platforma CVHOLD.'],
      '/jobs/categories': ['Darba kategorijas | CVHOLD', 'Parlukojiet vakances pec nozares un darba kategorijas.'],
      '/jobs/countries': ['Vakances pec valstim | CVHOLD', 'Atrodiet darba piedavajumus Latvija, Eiropa un citos virzienos.'],
      '/jobs/latvia-cities': ['Vakances Latvijas pilsetas | CVHOLD', 'Izvelieties Latvijas pilsetu un atrodiet aktualas vakances.'],
      '/employers': ['Darba devejiem | CVHOLD', 'Publicejiet vakances, sanemiet pieteikumus un atlasiet piemerotus kandidatus.'],
      '/pricing': ['Cenas | CVHOLD', 'Izvelieties CVHOLD planu vakancu publicesanai un pieteikumu parvaldiba.'],
      '/about': ['Par CVHOLD', 'Uzziniet vairak par CVHOLD darba meklesanas un personala atlases platformu.'],
      '/contacts': ['Kontakti | CVHOLD', 'Sazinieties ar CVHOLD komandu par platformu, vakancem vai sadarbibu.'],
      '/faq': ['BUJ | CVHOLD', 'Atbildes uz biezak uzdotajiem jautajumiem par CVHOLD.'],
      '/terms': ['Noteikumi | CVHOLD', 'CVHOLD lietosanas noteikumi un platformas nosacijumi.'],
      '/blog': ['Blogs | CVHOLD', 'CVHOLD jaunumi un noderiga informacija kandidatiem un darba devejiem.'],
    },
  },
  en: {
    defaultTitle: 'CVHOLD - jobs and workforce platform in Europe',
    defaultDescription: 'CVHOLD helps candidates find jobs across Europe and employers publish vacancies, manage applications, and shortlist suitable specialists.',
    pages: {
      '/': ['Jobs in Europe | CVHOLD', 'Browse jobs by country, category, salary, and working conditions on CVHOLD.'],
      '/jobs/categories': ['Job categories | CVHOLD', 'Browse vacancies by industry and job category.'],
      '/jobs/countries': ['Jobs by country | CVHOLD', 'Find job offers in Latvia, Europe, and other destinations.'],
      '/jobs/latvia-cities': ['Jobs in Latvian cities | CVHOLD', 'Choose a Latvian city and find current vacancies.'],
      '/employers': ['For employers | CVHOLD', 'Publish vacancies, receive applications, and shortlist suitable candidates.'],
      '/pricing': ['Pricing | CVHOLD', 'Choose a CVHOLD plan for publishing vacancies and managing applications.'],
      '/about': ['About CVHOLD', 'Learn more about the CVHOLD job search and recruitment platform.'],
      '/contacts': ['Contacts | CVHOLD', 'Contact the CVHOLD team about the platform, vacancies, or partnerships.'],
      '/faq': ['FAQ | CVHOLD', 'Answers to common questions about CVHOLD.'],
      '/terms': ['Terms | CVHOLD', 'CVHOLD terms of use and platform conditions.'],
      '/blog': ['Blog | CVHOLD', 'CVHOLD updates and useful information for candidates and employers.'],
    },
  },
  ru: {
    defaultTitle: 'CVHOLD - вакансии и платформа подбора персонала в Европе',
    defaultDescription: 'CVHOLD помогает кандидатам находить вакансии в Европе, а работодателям публиковать вакансии, управлять откликами и выбирать подходящих специалистов.',
    pages: {
      '/': ['Вакансии в Европе | CVHOLD', 'Ищите вакансии по стране, категории, зарплате и условиям работы на CVHOLD.'],
      '/jobs/categories': ['Категории вакансий | CVHOLD', 'Просматривайте вакансии по отраслям и рабочим категориям.'],
      '/jobs/countries': ['Вакансии по странам | CVHOLD', 'Находите предложения работы в Латвии, Европе и других направлениях.'],
      '/jobs/latvia-cities': ['Вакансии в городах Латвии | CVHOLD', 'Выберите город Латвии и найдите актуальные вакансии.'],
      '/employers': ['Работодателям | CVHOLD', 'Публикуйте вакансии, получайте отклики и выбирайте подходящих кандидатов.'],
      '/pricing': ['Цены | CVHOLD', 'Выберите тариф CVHOLD для публикации вакансий и управления откликами.'],
      '/about': ['О CVHOLD', 'Узнайте больше о платформе поиска работы и подбора персонала CVHOLD.'],
      '/contacts': ['Контакты | CVHOLD', 'Свяжитесь с командой CVHOLD по вопросам платформы, вакансий или сотрудничества.'],
      '/faq': ['FAQ | CVHOLD', 'Ответы на частые вопросы о CVHOLD.'],
      '/terms': ['Условия | CVHOLD', 'Условия использования CVHOLD и правила платформы.'],
      '/blog': ['Блог | CVHOLD', 'Новости CVHOLD и полезная информация для кандидатов и работодателей.'],
    },
  },
}

const upsertHeadElement = (selector, createElement, attributes = {}) => {
  if (typeof document === 'undefined') return

  let element = document.head.querySelector(selector)
  if (!element) {
    element = createElement()
    document.head.appendChild(element)
  }

  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, value)
  })
}

const updateSeoHead = (to) => {
  if (typeof document === 'undefined') return

  const locale = getLocaleFromPath(to.path)
  const logicalPath = stripLocaleFromPath(to.path)
  const seoLocale = SEO_COPY[locale] || SEO_COPY.lv
  const [title, description] = seoLocale.pages[logicalPath] || [seoLocale.defaultTitle, seoLocale.defaultDescription]
  const isIndexable = isPublicSeoPath(logicalPath)
  const canonicalLogicalPath = logicalPath === '/jobs' ? '/' : logicalPath
  const canonicalUrl = canonicalLogicalPath === '/' && !hasLocalePrefix(to.path)
    ? `${SITE_ORIGIN}/`
    : `${SITE_ORIGIN}${withLocale(canonicalLogicalPath, locale)}`

  document.documentElement.lang = locale
  document.title = title

  upsertHeadElement('meta[name="description"]', () => document.createElement('meta'), {
    name: 'description',
    content: description,
  })
  upsertHeadElement('meta[name="robots"]', () => document.createElement('meta'), {
    name: 'robots',
    content: isIndexable ? 'index, follow' : 'noindex, nofollow',
  })
  upsertHeadElement('link[rel="canonical"]', () => {
    const link = document.createElement('link')
    link.rel = 'canonical'
    return link
  }, {
    rel: 'canonical',
    href: canonicalUrl,
  })
  upsertHeadElement('meta[property="og:title"]', () => document.createElement('meta'), {
    property: 'og:title',
    content: title,
  })
  upsertHeadElement('meta[property="og:description"]', () => document.createElement('meta'), {
    property: 'og:description',
    content: description,
  })
  upsertHeadElement('meta[property="og:url"]', () => document.createElement('meta'), {
    property: 'og:url',
    content: canonicalUrl,
  })
}

const smoothScrollToElement = (selector, duration = 1100) => {
  if (typeof window === 'undefined' || typeof document === 'undefined') return

  const target = document.querySelector(selector)
  if (!target) return

  const navbar = document.querySelector('.navbar')
  const offset = navbar ? navbar.offsetHeight + 20 : 96
  const startY = window.scrollY
  const targetY = target.getBoundingClientRect().top + window.scrollY - offset
  const distance = targetY - startY
  const startTime = performance.now()

  const easeInOutCubic = (progress) => {
    return progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 3) / 2
  }

  const step = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easedProgress = easeInOutCubic(progress)

    window.scrollTo({
      top: startY + distance * easedProgress,
      behavior: 'auto',
    })

    if (progress < 1) {
      window.requestAnimationFrame(step)
    }
  }

  window.requestAnimationFrame(step)
}

const normalizeAccountType = (accountType) => {
  if (accountType === 'user') return 'candidate'
  return accountType || ''
}

const canAccessRoute = (accountType, allowedTypes = []) => {
  if (!allowedTypes.length) return true

  const normalizedType = normalizeAccountType(accountType)
  const normalizedAllowedTypes = allowedTypes.map(normalizeAccountType)

  return normalizedAllowedTypes.includes(normalizedType)
}

const defaultRouteForAccount = (accountType) => {
  const normalizedType = normalizeAccountType(accountType)

  if (normalizedType === 'candidate') return '/dashboard?section=profile'
  if (normalizedType === 'employer') return '/dashboard?section=jobs'
  if (normalizedType === 'admin') return '/admin'

  return '/'
}

const localizeRouteLocation = (target, locale = 'lv') => {
  if (typeof target === 'string') {
    return localizeFullPath(target, locale)
  }

  return {
    ...target,
    path: withLocale(target.path || '/', locale),
  }
}

const shouldRedirect = (logicalPath, target) => {
  if (!target) return false

  const targetPath = typeof target === 'string'
    ? stripLocaleFromPath(target.split('?')[0])
    : stripLocaleFromPath(target.path)

  return targetPath && targetPath !== logicalPath
}

const localizedChildren = [
  { path: '', component: JobsPage, meta: { logicalPath: '/' } },
  { path: 'jobs', component: JobsPage, meta: { logicalPath: '/jobs' } },
  { path: 'jobs/categories', component: JobDirectoryPage, meta: { logicalPath: '/jobs/categories', directory: 'categories' } },
  { path: 'jobs/countries', component: JobDirectoryPage, meta: { logicalPath: '/jobs/countries', directory: 'countries' } },
  { path: 'jobs/latvia-cities', component: JobDirectoryPage, meta: { logicalPath: '/jobs/latvia-cities', directory: 'latvia-cities' } },
  { path: 'jobs/:id', component: JobDetailPage, meta: { logicalPath: '/jobs/:id' } },
  { path: 'employers', component: HomePage, meta: { logicalPath: '/employers' } },
  { path: 'pricing', component: PricingPage, meta: { logicalPath: '/pricing' } },
  { path: 'signin', component: SignInPage, meta: { logicalPath: '/signin' } },
  { path: 'profile', component: ProfilePage, meta: { logicalPath: '/profile', requiresAuth: true, accountTypes: ['candidate', 'admin'] } },
  { path: 'dashboard', component: DashboardPage, meta: { logicalPath: '/dashboard', requiresAuth: true, accountTypes: ['candidate', 'employer', 'admin'] } },
  { path: 'admin', component: AdminPanel, meta: { logicalPath: '/admin', requiresAuth: true, accountTypes: ['admin'] } },
  {
    path: 'employer-dashboard',
    redirect: (to) => ({
      path: '/dashboard',
      query: to.query,
    }),
  },
  { path: 'responses', component: ResponsesPage, meta: { logicalPath: '/responses', requiresAuth: true, accountTypes: ['employer', 'admin'] } },
  { path: 'responses/:id/cv', component: ResponseCvPage, meta: { logicalPath: '/responses/:id/cv', requiresAuth: true, accountTypes: ['employer', 'admin'] } },
  { path: 'messages', component: MessagesPage, meta: { logicalPath: '/messages', requiresAuth: true } },
  { path: 'blog', component: InfoPage, meta: { logicalPath: '/blog', page: 'blog' } },
  { path: 'about', component: AboutPage, meta: { logicalPath: '/about' } },
  { path: 'contacts', component: ContactsPage, meta: { logicalPath: '/contacts' } },
  { path: 'faq', component: InfoPage, meta: { logicalPath: '/faq', page: 'faq' } },
  { path: 'terms', component: InfoPage, meta: { logicalPath: '/terms', page: 'terms' } },
]

const routes = [
  { path: '/', component: JobsPage, meta: { logicalPath: '/' } },
  {
    path: '/:locale(ru|en|lv)',
    children: localizedChildren,
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: (to) => {
      if (hasLocalePrefix(to.path || '')) {
        return withLocale('/', getLocaleFromPath(to.path || '/'))
      }

      const uiStore = useUiStore()
      const locale = normalizeLanguage(uiStore.language)
      return localizeFullPath(to.fullPath || '/', locale)
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }

    if (to.hash) {
      return false
    }

    // Если пользователь остался на той же странице,
    // например /ru/jobs, но изменились query-параметры фильтров,
    // не скроллим страницу вверх.
    if (to.path === from.path) {
      return false
    }

    return { top: 0 }
  },
})

router.afterEach((to) => {
  updateSeoHead(to)

  if (!to.hash) return

  window.requestAnimationFrame(() => {
    smoothScrollToElement(to.hash, 1100)
  })
})

router.beforeEach(async (to) => {
  const auth = useAuth()
  const uiStore = useUiStore()
  const locale = hasLocalePrefix(to.path)
    ? getLocaleFromPath(to.path)
    : normalizeLanguage(uiStore.language)
  const logicalPath = stripLocaleFromPath(to.path)
  const routeLogicalPath = typeof to.meta.logicalPath === 'string' ? to.meta.logicalPath : logicalPath
  const isJobDetailRoute = to.matched.some((record) => record.meta?.logicalPath === '/jobs/:id')

  if (!hasLocalePrefix(to.path) && to.path !== '/') {
    return localizeFullPath(to.fullPath, locale)
  }

  if (uiStore.language !== locale) {
    uiStore.setLanguage(locale)
  }

  if (isJobDetailRoute) {
    const authenticatedUser = await auth.initialize()

    if (!authenticatedUser) {
      return localizeRouteLocation({
        path: '/',
        query: {
          auth: 'login',
          redirect: to.fullPath,
        },
      }, locale)
    }
  }

  if (to.meta.requiresAuth) {
    await auth.initialize()

    if (!auth.state.user) {
      return localizeRouteLocation({
        path: '/signin',
        query: {
          auth: 'login',
          redirect: to.fullPath,
        },
      }, locale)
    }

    const normalizedType = normalizeAccountType(auth.state.user.account_type)

    if (routeLogicalPath === '/dashboard' && normalizedType === 'candidate' && !to.query.section) {
      return localizeRouteLocation({
        path: '/dashboard',
        query: {
          ...to.query,
          section: 'profile',
        },
      }, locale)
    }

    if (routeLogicalPath === '/profile') {
      const target = normalizedType === 'candidate'
        ? localizeFullPath('/dashboard?section=profile', locale)
        : normalizedType === 'admin'
          ? localizeFullPath('/dashboard?section=users', locale)
          : localizeFullPath('/dashboard?section=jobs', locale)

      if (to.fullPath !== target) {
        return target
      }

      return true
    }

    if (routeLogicalPath === '/messages') {
      if (normalizedType === 'candidate') {
        return localizeRouteLocation({
          path: '/dashboard',
          query: {
            section: 'messages',
            ...(typeof to.query.application === 'string' ? { application: to.query.application } : {}),
          },
        }, locale)
      }

      if (['employer', 'admin'].includes(normalizedType)) {
        return localizeRouteLocation({
          path: '/dashboard',
          query: {
            section: 'messages',
            ...(typeof to.query.application === 'string' ? { application: to.query.application } : {}),
          },
        }, locale)
      }
    }

    if (routeLogicalPath === '/responses' && ['employer', 'admin'].includes(normalizedType)) {
      return localizeRouteLocation({
        path: '/dashboard',
        query: { section: 'responses' },
      }, locale)
    }

    if (!canAccessRoute(normalizedType, to.meta.accountTypes || [])) {
      const target = defaultRouteForAccount(normalizedType)

      if (shouldRedirect(logicalPath, target)) {
        return localizeRouteLocation(target, locale)
      }

      return true
    }
  }

  if (routeLogicalPath === '/signin') {
    await auth.initialize()

    if (auth.state.user) {
      const target = typeof to.query.redirect === 'string'
        ? to.query.redirect
        : withLocale(defaultRouteForAccount(auth.state.user.account_type), locale)

      if (shouldRedirect(logicalPath, target)) {
        return typeof target === 'string' ? target : localizeRouteLocation(target, locale)
      }
    }
  }

  return true
})

export default router
