import { defineStore } from 'pinia'

export const useCvBuilderStore = defineStore('cvBuilder', {
  state: () => ({
    isOpen: false,
  }),

  actions: {
    open() {
      this.isOpen = true
    },

    close() {
      this.isOpen = false
    },
  },
})
