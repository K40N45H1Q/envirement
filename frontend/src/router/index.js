import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/templates/HomePage.vue'
import ProfilePage from '@/templates/ProfilePage.vue'
import JobsPage from '@/templates/JobsPage.vue'
import JobDetailPage from '@/templates/JobDetailPage.vue'
import JobDirectoryPage from '@/templates/JobDirectoryPage.vue'
import PricingPage from '@/templates/PricingPage.vue'
import ResumeBuilderPage from '@/templates/ResumeBuilderPage.vue'
import DashboardPage from '@/templates/DashboardPage.vue'
import ResponsesPage from '@/templates/ResponsesPage.vue'
import MessagesPage from '@/templates/MessagesPage.vue'
import AboutPage from '@/templates/AboutPage.vue'
import InfoPage from '@/templates/InfoPage.vue'
import SignInPage from '@/templates/SignInPage.vue'
import UnauthorizedPage from '@/templates/UnauthorizedPage.vue'
import AdminPanel from '@/components/apanel/AdminPanel.vue'
import BLogin from '@/components/BLogin.vue'
import { normalizeLanguage } from '@/i18n'
import { getAuthToken } from '@/api/client'
import { useAuth } from '@/stores/auth'
import { useBetaAccess } from '@/stores/betaAccess'
import { useUiStore } from '@/stores/ui'
import { getLocaleFromPath, hasLocalePrefix, localizeFullPath, stripLocaleFromPath, withLocale } from './locale'

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

  if (normalizedType === 'candidate') return '/dashboard'
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
  { path: 'createcv', component: ResumeBuilderPage, meta: { logicalPath: '/createcv' } },
  {
    path: 'resume-builder',
    redirect: (to) => ({
      path: '/createcv',
      query: to.query,
      hash: to.hash,
    }),
  },
  { path: 'beta-access', component: BLogin, meta: { logicalPath: '/beta-access' } },
  { path: 'signin', component: SignInPage, meta: { logicalPath: '/signin' } },
  { path: 'unauthorized', component: UnauthorizedPage, meta: { logicalPath: '/unauthorized' } },
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
  { path: 'messages', component: MessagesPage, meta: { logicalPath: '/messages', requiresAuth: true } },
  { path: 'blog', component: InfoPage, meta: { logicalPath: '/blog', page: 'blog' } },
  { path: 'about', component: AboutPage, meta: { logicalPath: '/about' } },
  { path: 'contacts', component: InfoPage, meta: { logicalPath: '/contacts', page: 'contacts' } },
  { path: 'faq', component: InfoPage, meta: { logicalPath: '/faq', page: 'faq' } },
  { path: 'terms', component: InfoPage, meta: { logicalPath: '/terms', page: 'terms' } },
]

const routes = [
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
  if (!to.hash) return

  window.requestAnimationFrame(() => {
    smoothScrollToElement(to.hash, 1100)
  })
})

router.beforeEach(async (to) => {
  const auth = useAuth()
  const betaAccess = useBetaAccess()
  const uiStore = useUiStore()
  const token = getAuthToken()
  const locale = hasLocalePrefix(to.path)
    ? getLocaleFromPath(to.path)
    : normalizeLanguage(uiStore.language)
  const logicalPath = stripLocaleFromPath(to.path)
  const routeLogicalPath = typeof to.meta.logicalPath === 'string' ? to.meta.logicalPath : logicalPath
  const isJobDetailRoute = to.matched.some((record) => record.meta?.logicalPath === '/jobs/:id')

  if (!hasLocalePrefix(to.path)) {
    return localizeFullPath(to.fullPath, locale)
  }

  if (uiStore.language !== locale) {
    uiStore.setLanguage(locale)
  }

  const skipsBetaGate = ['/beta-access', '/signin', '/admin'].includes(routeLogicalPath)

  if (!skipsBetaGate) {
    const hasBetaAccess = await betaAccess.initialize()

    if (!hasBetaAccess) {
      return localizeRouteLocation({
        path: '/beta-access',
        query: {
          redirect: to.fullPath,
        },
      }, locale)
    }
  } else if (routeLogicalPath === '/beta-access') {
    const hasBetaAccess = await betaAccess.initialize()

    if (hasBetaAccess) {
      const target = typeof to.query.redirect === 'string' ? to.query.redirect : withLocale('/', locale)
      if (target !== to.fullPath) {
        return target
      }
    }
  }

  if (isJobDetailRoute && !token) {
      return localizeRouteLocation({
        path: '/',
        query: {
          ...to.query,
          auth: 'login',
        redirect: to.fullPath,
      },
    }, locale)
  }

  if (to.meta.requiresAuth) {
    if (!token) {
      return localizeRouteLocation({
        path: '/signin',
        query: {
          auth: 'login',
          redirect: to.fullPath,
        },
      }, locale)
    }

    await auth.initialize()

    if (!auth.state.user) {
      if (auth.state.sessionExpired) {
        return localizeRouteLocation({
          path: '/unauthorized',
          query: {
            redirect: to.fullPath,
          },
        }, locale)
      }

      return localizeRouteLocation({
        path: '/signin',
        query: {
          auth: 'login',
          redirect: to.fullPath,
        },
      }, locale)
    }

    const normalizedType = normalizeAccountType(auth.state.user.account_type)

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

  if (routeLogicalPath === '/signin' && token) {
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
