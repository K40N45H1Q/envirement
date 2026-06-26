import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/templates/HomePage.vue'
import ProfilePage from '@/templates/ProfilePage.vue'
import JobsPage from '@/templates/JobsPage.vue'
import JobDetailPage from '@/templates/JobDetailPage.vue'
import EmployersPage from '@/templates/EmployersPage.vue'
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
import { canAccessRoute, defaultRouteForAccount } from '@/utils/auth'

const routes = [
  { path: '/', component: HomePage },
  { path: '/jobs', component: JobsPage },
  { path: '/jobs/:id', component: JobDetailPage },
  { path: '/employers', component: EmployersPage },
  { path: '/pricing', component: PricingPage },
  { path: '/resume-builder', component: ResumeBuilderPage },
  { path: '/signin', component: SignInPage },
  { path: '/profile', component: ProfilePage, meta: { requiresAuth: true, accountTypes: ['user', 'employer', 'admin'] } },
  { path: '/dashboard', component: CandidateDashboardPage, meta: { requiresAuth: true, accountTypes: ['user'] } },
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
})

router.beforeEach(async (to) => {
  const { state, loadUser } = useAuth()
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

    if (!state.user) {
      await loadUser()
    }

    if (!state.user) {
      return {
        path: '/signin',
        query: {
          auth: 'login',
          redirect: to.fullPath,
        },
      }
    }

    if (!canAccessRoute(state.user.account_type, to.meta.accountTypes || [])) {
      return defaultRouteForAccount(state.user.account_type)
    }
  }

  if (to.path === '/signin' && token) {
    if (!state.user) {
      await loadUser()
    }

    if (state.user) {
      return typeof to.query.redirect === 'string'
        ? to.query.redirect
        : defaultRouteForAccount(state.user.account_type)
    }
  }

  return true
})

export default router
