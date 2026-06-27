import { defineStore } from 'pinia'

const LANGUAGE_STORAGE_KEY = 'cvhold-language'

const resolveInitialLanguage = () => {
  if (typeof window === 'undefined') {
    return 'ru'
  }

  return localStorage.getItem(LANGUAGE_STORAGE_KEY) || document.documentElement.lang || 'ru'
}

const applyLanguage = (language) => {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = language
  }

  if (typeof window !== 'undefined') {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, language)
  }
}

export const useUiStore = defineStore('ui', {
  state: () => ({
    language: resolveInitialLanguage(),
  }),

  actions: {
    initialize() {
      applyLanguage(this.language)
    },

    setLanguage(language) {
      this.language = language || 'ru'
      applyLanguage(this.language)
    },
  },
})
