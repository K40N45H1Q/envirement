import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/templates/HomePage.vue'
import ProfilePage from '@/templates/ProfilePage.vue'
import JobsPage from '@/templates/JobsPage.vue'
import JobDetailPage from '@/templates/JobDetailPage.vue'
import PricingPage from '@/templates/PricingPage.vue'
import ResumeBuilderPage from '@/templates/ResumeBuilderPage.vue'
import CandidateDashboardPage from '@/templates/CandidateDashboardPage.vue'
import EmployerDashboardPage from '@/templates/EmployerDashboardPage.vue'
import ResponsesPage from '@/templates/ResponsesPage.vue'
import MessagesPage from '@/templates/MessagesPage.vue'
import InfoPage from '@/templates/InfoPage.vue'
import SignInPage from '@/templates/SignInPage.vue'
import { getAuthToken } from '@/api/client'
import { useAuth } from '@/stores/auth'

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

  if (normalizedType === 'candidate') {
    return '/dashboard'
  }

  if (normalizedType === 'employer') {
    return '/employer-dashboard'
  }

  if (normalizedType === 'admin') {
    return '/employer-dashboard'
  }

  return '/'
}

const shouldRedirect = (to, target) => {
  if (!target) return false

  const targetPath = typeof target === 'string'
    ? target.split('?')[0]
    : target.path

  return targetPath && targetPath !== to.path
}

const routes = [
  { path: '/', component: HomePage },
  { path: '/jobs', component: JobsPage },
  { path: '/jobs/:id', component: JobDetailPage },
  { path: '/pricing', component: PricingPage },
  { path: '/resume-builder', component: ResumeBuilderPage, meta: { requiresAuth: true, accountTypes: ['candidate'] } },
  { path: '/signin', component: SignInPage },
  { path: '/profile', component: ProfilePage, meta: { requiresAuth: true, accountTypes: ['candidate', 'employer', 'admin'] } },
  { path: '/dashboard', component: CandidateDashboardPage, meta: { requiresAuth: true, accountTypes: ['candidate'] } },
  { path: '/employer-dashboard', component: EmployerDashboardPage, meta: { requiresAuth: true, accountTypes: ['employer', 'admin'] } },
  { path: '/responses', component: ResponsesPage, meta: { requiresAuth: true, accountTypes: ['employer', 'admin'] } },
  { path: '/messages', component: MessagesPage, meta: { requiresAuth: true } },
  { path: '/blog', component: InfoPage, meta: { page: 'blog' } },
  { path: '/about', component: InfoPage, meta: { page: 'about' } },
  { path: '/contacts', component: InfoPage, meta: { page: 'contacts' } },
  { path: '/faq', component: InfoPage, meta: { page: 'faq' } },
  { path: '/terms', component: InfoPage, meta: { page: 'terms' } },
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
  const { state, initialize } = useAuth()
  const token = getAuthToken()

  if (to.meta.requiresAuth) {
    if (!token) {
      return {
        path: '/signin',
        query: {
          auth: 'login',
          redirect: to.fullPath,
        },
      }
    }

    await initialize()

    if (!state.user) {
      return {
        path: '/signin',
        query: {
          auth: 'login',
          redirect: to.fullPath,
        },
      }
    }

    const normalizedType = normalizeAccountType(state.user.account_type)

    if (to.path === '/profile' && ['employer', 'admin'].includes(normalizedType)) {
      const target = '/employer-dashboard?section=profile'

      if (to.fullPath !== target) {
        return target
      }

      return true
    }

    if (to.path === '/messages' && normalizedType === 'candidate') {
      return {
        path: '/dashboard',
        query: {
          section: 'messages',
          ...(typeof to.query.application === 'string' ? { application: to.query.application } : {}),
        },
      }
    }

    if (!canAccessRoute(normalizedType, to.meta.accountTypes || [])) {
      const target = defaultRouteForAccount(normalizedType)

      if (shouldRedirect(to, target)) {
        return target
      }

      return true
    }
  }

  if (to.path === '/signin' && token) {
    await initialize()

    if (state.user) {
      const target = typeof to.query.redirect === 'string'
        ? to.query.redirect
        : defaultRouteForAccount(state.user.account_type)

      if (shouldRedirect(to, target)) {
        return target
      }
    }
  }

  return true
})

export default router
