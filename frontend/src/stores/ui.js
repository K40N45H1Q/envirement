import { defineStore } from 'pinia'
import { normalizeLanguage } from '@/i18n'

const LANGUAGE_STORAGE_KEY = 'cvhold-language'

const resolveInitialLanguage = () => {
  if (typeof window === 'undefined') {
    return 'ru'
  }

  return normalizeLanguage(localStorage.getItem(LANGUAGE_STORAGE_KEY) || document.documentElement.lang || 'ru')
}

const applyLanguage = (language) => {
  const normalizedLanguage = normalizeLanguage(language)

  if (typeof document !== 'undefined') {
    document.documentElement.lang = normalizedLanguage
  }

  if (typeof window !== 'undefined') {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, normalizedLanguage)
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
      this.language = normalizeLanguage(language || 'ru')
      applyLanguage(this.language)
    },
  },
})
