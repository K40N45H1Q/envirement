import { defineStore } from 'pinia'
import { getAuthToken } from '@/api/client'
import { getMe, logout as logoutRequest } from '@/api/auth'

export const useAuth = defineStore('auth', {
  state: () => ({
    state: {
      user: null,
      isLoading: false,
      isReady: false,
      sessionExpired: false,
    },
    bootstrapPromise: null,
  }),

  actions: {
    resetState() {
      this.state.user = null
      this.state.isLoading = false
    },

    finalizeReady() {
      this.state.isReady = true
    },

    async loadUser({ force = false } = {}) {
      const token = getAuthToken()

      if (!token) {
        this.resetState()
        this.state.sessionExpired = false
        this.finalizeReady()
        return null
      }

      if (!force && this.state.user) {
        this.finalizeReady()
        return this.state.user
      }

      if (!force && this.bootstrapPromise) {
        return this.bootstrapPromise
      }

      this.state.isLoading = true

      this.bootstrapPromise = (async () => {
        try {
          this.state.user = await getMe()
          this.state.sessionExpired = false
          return this.state.user
        } catch (error) {
          this.state.sessionExpired = error?.status === 401
          logoutRequest()
          this.state.user = null
          return null
        } finally {
          this.state.isLoading = false
          this.state.isReady = true
          this.bootstrapPromise = null
        }
      })()

      return this.bootstrapPromise
    },

    setUser(user) {
      this.state.user = user
      this.state.sessionExpired = false
      this.finalizeReady()
    },

    logout() {
      logoutRequest()
      this.resetState()
      this.state.sessionExpired = false
      this.finalizeReady()
    },

    async initialize() {
      if (this.state.isReady && this.state.user) return this.state.user
      if (this.state.isReady && !getAuthToken()) return null
      return this.loadUser()
    },
  },
})
