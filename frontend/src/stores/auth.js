import { reactive, readonly } from 'vue'
import { getAuthToken } from '@/api/client'
import { getMe, logout as logoutRequest } from '@/api/auth'

const state = reactive({
  user: null,
  isLoading: false,
  isReady: false,
})

export const useAuth = () => {
  const loadUser = async () => {
    const token = getAuthToken()

    if (!token) {
      state.user = null
      state.isReady = true
      return null
    }

    state.isLoading = true

    try {
      state.user = await getMe()
      return state.user
    } catch {
      logoutRequest()
      state.user = null
      return null
    } finally {
      state.isLoading = false
      state.isReady = true
    }
  }

  const setUser = (user) => {
    state.user = user
    state.isReady = true
  }

  const logout = () => {
    logoutRequest()
    state.user = null
    state.isReady = true
  }

  return {
    state: readonly(state),
    loadUser,
    setUser,
    logout,
  }
}
