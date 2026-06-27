import { defineStore } from 'pinia'
import {
  deleteMessageConversation,
  getMessageConversations,
  getMessageThread,
  sendMessage,
} from '@/api/jobs'

const sortConversations = (conversations) => {
  return [...conversations].sort((a, b) => {
    const left = a?.last_message_at ? new Date(a.last_message_at).getTime() : 0
    const right = b?.last_message_at ? new Date(b.last_message_at).getTime() : 0
    return right - left
  })
}

export const useMessagingStore = defineStore('messaging', {
  state: () => ({
    conversations: [],
    activeApplicationId: null,
    thread: [],
    draft: '',
    status: '',
    isLoading: false,
    isRefreshing: false,
    isSending: false,
    isDeleting: false,
    initialized: false,
    pollingTimer: null,
  }),

  getters: {
    activeConversation(state) {
      return state.conversations.find((item) => item.application_id === state.activeApplicationId) || null
    },
  },

  actions: {
    reset() {
      this.stopRealtime()
      this.conversations = []
      this.activeApplicationId = null
      this.thread = []
      this.draft = ''
      this.status = ''
      this.isLoading = false
      this.isRefreshing = false
      this.isSending = false
      this.isDeleting = false
      this.initialized = false
    },

    setDraft(value) {
      this.draft = value
    },

    syncConversationMessage(message) {
      this.conversations = sortConversations(this.conversations.map((conversation) => (
        conversation.application_id === this.activeApplicationId
          ? {
              ...conversation,
              last_message: message.body,
              last_message_at: message.created_at,
            }
          : conversation
      )))
    },

    async loadThread(applicationId, { silent = false } = {}) {
      if (!applicationId) {
        this.thread = []
        return
      }

      try {
        const data = await getMessageThread(applicationId)
        this.thread = Array.isArray(data?.messages) ? data.messages : []
      } catch (error) {
        this.thread = []

        if (!silent) {
          this.status = error?.key === 'chat_not_approved'
            ? 'Чат станет доступен после подтверждения работодателем.'
            : 'Не удалось открыть переписку по выбранному отклику.'
        }
      }
    },

    async openConversation(applicationId) {
      this.activeApplicationId = Number(applicationId) || null
      this.status = ''
      await this.loadThread(this.activeApplicationId)
    },

    async loadConversations(requestedApplicationId = null, { silent = false } = {}) {
      if (!silent) {
        this.isLoading = true
        this.status = ''
      }

      try {
        const data = await getMessageConversations()
        const nextConversations = sortConversations(Array.isArray(data) ? data : [])

        const requestedId = Number(requestedApplicationId)
        const preferredId = requestedId || this.activeApplicationId

        const selectedConversation = nextConversations.find((item) => item.application_id === preferredId)
          || nextConversations[0]
          || null

        this.conversations = nextConversations
        this.activeApplicationId = selectedConversation?.application_id || null

        if (this.activeApplicationId) {
          await this.loadThread(this.activeApplicationId, { silent })
        } else {
          this.thread = []
        }

        this.initialized = true
      } catch {
        if (!silent) {
          this.conversations = []
          this.thread = []
          this.status = 'Не удалось загрузить сообщения. Проверьте подключение и вход в аккаунт.'
        }
      } finally {
        if (!silent) {
          this.isLoading = false
        }
      }
    },

    async refreshConversations() {
      if (this.isRefreshing || this.isLoading || this.isSending || this.isDeleting) return

      this.isRefreshing = true

      try {
        await this.loadConversations(this.activeApplicationId, { silent: true })
      } finally {
        this.isRefreshing = false
      }
    },

    startRealtime() {
      if (this.pollingTimer) return

      this.refreshConversations()

      this.pollingTimer = window.setInterval(() => {
        this.refreshConversations()
      }, 2500)
    },

    stopRealtime() {
      if (!this.pollingTimer) return

      window.clearInterval(this.pollingTimer)
      this.pollingTimer = null
    },

    async sendCurrentMessage() {
      const body = this.draft.trim()

      if (!body) return null

      if (!this.activeApplicationId) {
        this.status = 'Сначала выберите диалог.'
        return null
      }

      this.isSending = true
      this.status = ''

      try {
        const message = await sendMessage(this.activeApplicationId, body)
        this.thread = [...this.thread, message]
        this.syncConversationMessage(message)
        this.draft = ''
        return message
      } catch (error) {
        this.status = error?.key === 'chat_not_approved'
          ? 'Работодатель ещё не подтвердил чат по этому отклику.'
          : 'Не удалось отправить сообщение.'
        return null
      } finally {
        this.isSending = false
        await this.refreshConversations()
      }
    },

    async deleteActiveConversation() {
      if (!this.activeApplicationId) return false

      this.isDeleting = true
      this.status = ''

      try {
        const deletedId = this.activeApplicationId
        await deleteMessageConversation(deletedId)

        this.conversations = this.conversations.filter((item) => item.application_id !== deletedId)
        this.thread = []
        this.draft = ''
        this.activeApplicationId = this.conversations[0]?.application_id || null

        if (this.activeApplicationId) {
          await this.loadThread(this.activeApplicationId)
        }

        await this.refreshConversations()

        return true
      } catch {
        this.status = 'Не удалось удалить диалог.'
        return false
      } finally {
        this.isDeleting = false
      }
    },
  },
})