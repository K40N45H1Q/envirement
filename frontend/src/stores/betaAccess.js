import { defineStore } from 'pinia'
import { getBetaStatus, loginToBeta, logoutFromBeta } from '@/api/beta'

const BETA_SESSION_KEY = 'cvhold-beta-session'

const hasBrowserBetaSession = () => {
  if (typeof window === 'undefined') return false
  return window.sessionStorage.getItem(BETA_SESSION_KEY) === '1'
}

const markBrowserBetaSession = () => {
  if (typeof window === 'undefined') return
  window.sessionStorage.setItem(BETA_SESSION_KEY, '1')
}

const clearBrowserBetaSession = () => {
  if (typeof window === 'undefined') return
  window.sessionStorage.removeItem(BETA_SESSION_KEY)
}

const redirectToBlockedPage = () => {
  if (typeof window === 'undefined') return
  window.location.replace(window.location.href)
}

export const useBetaAccess = defineStore('beta-access', {
  state: () => ({
    isEnabled: true,
    isAuthorized: false,
    isLoading: false,
    isReady: false,
  }),

  actions: {
    reset() {
      this.isAuthorized = false
      this.isLoading = false
      this.isReady = false
      clearBrowserBetaSession()
    },

    async initialize({ force = false } = {}) {
      if (this.isReady && !force) {
        return this.isAuthorized
      }

      this.isLoading = true

      try {
        const data = await getBetaStatus()
        this.isEnabled = data?.enabled !== false
        const hasSessionMarker = hasBrowserBetaSession()

        this.isAuthorized = (
          this.isEnabled === false
          || (data?.authorized === true && hasSessionMarker)
        )

        if (!this.isAuthorized) {
          clearBrowserBetaSession()
        }
        return this.isAuthorized
      } catch (error) {
        if (error?.status === 404 || error?.status === 0) {
          redirectToBlockedPage()
          return false
        }

        this.isEnabled = true
        this.isAuthorized = false
        clearBrowserBetaSession()
        return false
      } finally {
        this.isLoading = false
        this.isReady = true
      }
    },

    async login(credentials) {
      this.isLoading = true

      try {
        const data = await loginToBeta(credentials)
        this.isEnabled = true
        this.isAuthorized = data?.authorized === true
        if (this.isAuthorized) {
          markBrowserBetaSession()
        } else {
          clearBrowserBetaSession()
        }
        this.isReady = true
        return this.isAuthorized
      } catch (error) {
        const remainingAttempts = error?.payload?.detail?.remaining_attempts
        const isBlocked = error?.payload?.detail?.blocked === true

        if (
          error?.status === 500
          || error?.status === 404
          || error?.status === 0
          || isBlocked
          || (typeof remainingAttempts === 'number' && remainingAttempts <= 0)
        ) {
          redirectToBlockedPage()
        }
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      try {
        await logoutFromBeta()
      } catch {}

      this.isAuthorized = false
      this.isReady = true
      clearBrowserBetaSession()
    },
  },
})
