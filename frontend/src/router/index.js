import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/templates/HomePage.vue'
import ProfilePage from '@/templates/ProfilePage.vue'
import JobsPage from '@/templates/JobsPage.vue'
import JobDetailPage from '@/templates/JobDetailPage.vue'
import PricingPage from '@/templates/PricingPage.vue'
import ResumeBuilderPage from '@/templates/ResumeBuilderPage.vue'
import DashboardPage from '@/templates/DashboardPage.vue'
import ResponsesPage from '@/templates/ResponsesPage.vue'
import MessagesPage from '@/templates/MessagesPage.vue'
import InfoPage from '@/templates/InfoPage.vue'
import SignInPage from '@/templates/SignInPage.vue'
import UnauthorizedPage from '@/templates/UnauthorizedPage.vue'
import { normalizeLanguage } from '@/i18n'
import { getAuthToken } from '@/api/client'
import { useAuth } from '@/stores/auth'
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
  if (normalizedType === 'admin') return '/dashboard?section=jobs'

  return '/'
}

const localizeRouteLocation = (target, locale = 'ru') => {
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
  { path: '', component: HomePage, meta: { logicalPath: '/' } },
  { path: 'jobs', component: JobsPage, meta: { logicalPath: '/jobs' } },
  { path: 'jobs/:id', component: JobDetailPage, meta: { logicalPath: '/jobs/:id' } },
  { path: 'pricing', component: PricingPage, meta: { logicalPath: '/pricing' } },
  { path: 'resume-builder', component: ResumeBuilderPage, meta: { logicalPath: '/resume-builder' } },
  { path: 'signin', component: SignInPage, meta: { logicalPath: '/signin' } },
  { path: 'unauthorized', component: UnauthorizedPage, meta: { logicalPath: '/unauthorized' } },
  { path: 'profile', component: ProfilePage, meta: { logicalPath: '/profile', requiresAuth: true, accountTypes: ['candidate', 'employer', 'admin'] } },
  { path: 'dashboard', component: DashboardPage, meta: { logicalPath: '/dashboard', requiresAuth: true, accountTypes: ['candidate', 'employer', 'admin'] } },
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
  { path: 'about', component: InfoPage, meta: { logicalPath: '/about', page: 'about' } },
  { path: 'contacts', component: InfoPage, meta: { logicalPath: '/contacts', page: 'contacts' } },
  { path: 'faq', component: InfoPage, meta: { logicalPath: '/faq', page: 'faq' } },
  { path: 'terms', component: InfoPage, meta: { logicalPath: '/terms', page: 'terms' } },
]

const routes = [
  {
    path: '/:locale(ru|en)',
    children: localizedChildren,
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: (to) => {
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

  if (isJobDetailRoute && !token) {
    return localizeRouteLocation({
      path: '/jobs',
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
      const target = localizeFullPath('/dashboard?section=profile', locale)

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
