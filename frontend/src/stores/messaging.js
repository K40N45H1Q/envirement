import { defineStore } from 'pinia'
import { getMessageConversations, getMessageThread, sendMessage } from '@/api/jobs'

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
    isSending: false,
    initialized: false,
  }),

  getters: {
    activeConversation(state) {
      return state.conversations.find((item) => item.application_id === state.activeApplicationId) || null
    },
  },

  actions: {
    reset() {
      this.conversations = []
      this.activeApplicationId = null
      this.thread = []
      this.draft = ''
      this.status = ''
      this.isLoading = false
      this.isSending = false
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

    async loadThread(applicationId) {
      if (!applicationId) {
        this.thread = []
        return
      }

      try {
        const data = await getMessageThread(applicationId)
        this.thread = Array.isArray(data?.messages) ? data.messages : []
      } catch {
        this.thread = []
        this.status = 'Не удалось открыть переписку по выбранному отклику.'
      }
    },

    async openConversation(applicationId) {
      this.activeApplicationId = applicationId || null
      this.status = ''
      await this.loadThread(this.activeApplicationId)
    },

    async loadConversations(requestedApplicationId = null) {
      this.isLoading = true
      this.status = ''

      try {
        const data = await getMessageConversations()
        this.conversations = sortConversations(Array.isArray(data) ? data : [])

        const requestedId = Number(requestedApplicationId)
        const initialConversation = this.conversations.find((item) => item.application_id === requestedId)
          || this.conversations[0]
          || null

        this.activeApplicationId = initialConversation?.application_id || null

        if (this.activeApplicationId) {
          await this.loadThread(this.activeApplicationId)
        } else {
          this.thread = []
        }

        this.initialized = true
      } catch {
        this.conversations = []
        this.thread = []
        this.status = 'Не удалось загрузить сообщения. Проверьте, что backend запущен и вы вошли в аккаунт.'
      } finally {
        this.isLoading = false
      }
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
      } catch {
        this.status = 'Не удалось отправить сообщение.'
        return null
      } finally {
        this.isSending = false
      }
    },
  },
})
