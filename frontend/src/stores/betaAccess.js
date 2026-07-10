import { defineStore } from 'pinia'
import { getBetaStatus, loginToBeta, logoutFromBeta } from '@/api/beta'

const BETA_SESSION_KEY = 'cvhold-beta-session'
const BETA_STATUS_POLL_INTERVAL_MS = 1000

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
    isCheckingStatus: false,
    isReady: false,
    monitorId: null,
  }),

  actions: {
    reset() {
      this.isAuthorized = false
      this.isLoading = false
      this.isCheckingStatus = false
      this.isReady = false
      this.stopMonitoring()
      clearBrowserBetaSession()
    },

    applyStatus(data) {
      this.isEnabled = data?.enabled !== false
      const hasSessionMarker = hasBrowserBetaSession()

      this.isAuthorized = (
        this.isEnabled === false
        || (data?.authorized === true && hasSessionMarker)
      )

      if (!this.isAuthorized) {
        clearBrowserBetaSession()
      }
    },

    async refreshStatus() {
      this.isCheckingStatus = true

      try {
        const data = await getBetaStatus()
        this.applyStatus(data)
        this.isReady = true
        return this.isAuthorized
      } catch (error) {
        if (error?.status === 404 || error?.status === 0) {
          redirectToBlockedPage()
          return false
        }

        this.isEnabled = true
        this.isAuthorized = false
        this.isReady = true
        clearBrowserBetaSession()
        return false
      } finally {
        this.isCheckingStatus = false
      }
    },

    async initialize({ force = false } = {}) {
      this.isLoading = true

      try {
        return await this.refreshStatus()
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

    startMonitoring() {
      if (typeof window === 'undefined' || this.monitorId) return

      this.monitorId = window.setInterval(() => {
        this.refreshStatus()
      }, BETA_STATUS_POLL_INTERVAL_MS)
    },

    stopMonitoring() {
      if (typeof window === 'undefined' || !this.monitorId) return

      window.clearInterval(this.monitorId)
      this.monitorId = null
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
