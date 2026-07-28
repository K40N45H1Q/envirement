import { defineStore } from 'pinia'
import { getMe, logout as logoutRequest } from '@/api/auth'

const normalizeAccountType = (accountType) => {
  if (accountType === 'user') return 'candidate'
  return accountType || ''
}

let logoutRequestPromise = null

export const useAuth = defineStore('auth', {
  state: () => ({
    state: {
      user: null,
      isLoading: false,
      isReady: false,
      isGuest: false,
    },
    bootstrapPromise: null,
  }),

  getters: {
    user: (store) => store.state.user,

    accountType: (store) => {
      return normalizeAccountType(store.state.user?.account_type)
    },

    isCandidate: (store) => {
      return normalizeAccountType(store.state.user?.account_type) === 'candidate'
    },

    isEmployer: (store) => {
      return normalizeAccountType(store.state.user?.account_type) === 'employer'
    },

    isAdmin: (store) => {
      return normalizeAccountType(store.state.user?.account_type) === 'admin'
    },
  },

  actions: {
    resetState() {
      this.state.user = null
      this.state.isLoading = false
      this.state.isGuest = true
    },

    finalizeReady() {
      this.state.isReady = true
    },

    async loadUser({ force = false } = {}) {
      if (!force && this.state.user) {
        this.finalizeReady()
        return this.state.user
      }

      if (!force && this.state.isGuest) {
        this.finalizeReady()
        return null
      }

      if (!force && this.bootstrapPromise) {
        return this.bootstrapPromise
      }

      this.state.isLoading = true

      this.bootstrapPromise = (async () => {
        try {
          this.state.user = await getMe()
          return this.state.user
        } catch (error) {
          const isUnauthorized = error?.status === 401

          if (isUnauthorized) {
            this.state.isGuest = true
            if (!logoutRequestPromise) {
              logoutRequestPromise = logoutRequest().finally(() => {
                logoutRequestPromise = null
              })
            }
            this.state.user = null
          }

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
      this.state.isGuest = false
      this.finalizeReady()
    },

    logout() {
      if (!logoutRequestPromise) {
        logoutRequestPromise = logoutRequest().finally(() => {
          logoutRequestPromise = null
        })
      }
      this.resetState()
      this.finalizeReady()
    },

    async initialize() {
      if (this.state.isReady && this.state.user) return this.state.user
      return this.loadUser()
    },
  },
})
