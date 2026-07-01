<script setup>
import { computed } from 'vue'
import { useI18n } from '@/i18n'
import { useMessagingStore } from '@/stores/messaging'

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '',
  },
  hint: {
    type: String,
    default: '',
  },
})

const { language } = useI18n()
const messaging = useMessagingStore()

const isEnglish = computed(() => language.value === 'en')
const copy = computed(() => (
  isEnglish.value
    ? {
      title: 'Messages',
      hint: 'All active conversations for approved applications and vacancies.',
      fallbackTitle: 'Messages',
      fallbackSubtitle: 'Approved conversations for applications',
      loading: 'Loading conversations...',
      emptyList: 'Conversations will appear after the employer approves a chat in the applications section.',
      deleting: 'Deleting...',
      deleteConversation: 'Delete conversation',
      deleteConfirm: 'Delete this conversation? The related application will be deleted too.',
      emptyThread: 'Choose a conversation on the left to start chatting.',
      inputPlaceholder: 'Write a message',
    }
    : {
      title: 'Сообщения',
      hint: 'Все активные диалоги по подтвержденным откликам и вакансиям.',
      fallbackTitle: 'Сообщения',
      fallbackSubtitle: 'Подтвержденные диалоги по откликам',
      loading: 'Загрузка диалогов...',
      emptyList: 'Диалоги появятся после подтверждения работодателем во вкладке откликов.',
      deleting: 'Удаление...',
      deleteConversation: 'Удалить диалог',
      deleteConfirm: 'Удалить этот диалог? Вместе с ним будет удален и связанный отклик.',
      emptyThread: 'Выберите диалог слева, чтобы начать общение.',
      inputPlaceholder: 'Напишите сообщение',
    }
))

const conversations = computed(() => messaging.conversations)
const activeApplicationId = computed(() => messaging.activeApplicationId)
const thread = computed(() => messaging.thread)
const draft = computed({
  get: () => messaging.draft,
  set: (value) => messaging.setDraft(value),
})
const status = computed(() => messaging.status)
const isLoading = computed(() => messaging.isLoading)
const isSending = computed(() => messaging.isSending)
const isDeleting = computed(() => messaging.isDeleting)
const activeConversation = computed(() => messaging.activeConversation)
const panelTitle = computed(() => props.title || copy.value.title)
const panelHint = computed(() => props.hint || copy.value.hint)
const dateLocale = computed(() => (isEnglish.value ? 'en-US' : 'ru-RU'))
const activeTitle = computed(() => activeConversation.value?.counterparty_name || copy.value.fallbackTitle)
const activeSubtitle = computed(() => {
  if (!activeConversation.value) return copy.value.fallbackSubtitle
  return `${activeConversation.value.job_title} · ${activeConversation.value.job_company}`
})

const emit = defineEmits(['open'])

const openConversation = async (applicationId) => {
  if (!applicationId) return
  emit('open', applicationId)
  await messaging.openConversation(applicationId)
}

const send = async () => {
  await messaging.sendCurrentMessage()
}

const deleteConversation = async () => {
  const confirmed = window.confirm(copy.value.deleteConfirm)
  if (!confirmed) return
  await messaging.deleteActiveConversation()
}
</script>

<template>
  <section class="messages" :class="{ 'messages--embedded': embedded }">
    <aside class="chat-list">
      <div class="chat-list__head">
        <div>
          <h2>{{ panelTitle }}</h2>
          <p class="chat-list__hint">{{ panelHint }}</p>
        </div>
        <span class="chat-count">{{ conversations.length }}</span>
      </div>

      <p v-if="status" class="status">{{ status }}</p>
      <p v-if="isLoading" class="status">{{ copy.loading }}</p>

      <button
        v-for="conversation in conversations"
        :key="conversation.application_id"
        type="button"
        class="chat-list__item"
        :class="{ active: activeApplicationId === conversation.application_id }"
        @click="openConversation(conversation.application_id)"
      >
        <div class="chat-list__item-head">
          <strong>{{ conversation.counterparty_name }}</strong>
          <span>{{ new Date(conversation.last_message_at).toLocaleDateString(dateLocale) }}</span>
        </div>
        <span class="chat-list__job">{{ conversation.job_title }}</span>
        <span class="chat-list__message">{{ conversation.last_message }}</span>
      </button>

      <p v-if="!isLoading && !conversations.length" class="status">
        {{ copy.emptyList }}
      </p>
    </aside>

    <article class="chat">
      <header class="chat-head">
        <div class="chat-head__copy">
          <strong>{{ activeTitle }}</strong>
          <span>{{ activeSubtitle }}</span>
        </div>

        <button
          v-if="activeApplicationId"
          type="button"
          class="delete-button"
          :disabled="isDeleting"
          @click="deleteConversation"
        >
          <i class="fas fa-trash-can"></i>
          <span>{{ isDeleting ? copy.deleting : copy.deleteConversation }}</span>
        </button>
      </header>

      <div class="thread">
        <div
          v-for="message in thread"
          :key="message.id"
          class="message-row"
          :class="{ 'message-row--own': message.is_own }"
        >
          <span class="message-author">{{ message.sender_name }}</span>
          <p class="bubble" :class="{ own: message.is_own }">{{ message.body }}</p>
        </div>

        <p v-if="!thread.length" class="empty-thread">
          {{ copy.emptyThread }}
        </p>
      </div>

      <form class="chat-form" @submit.prevent="send">
        <input
          v-model="draft"
          :disabled="!activeApplicationId || isSending"
          :placeholder="copy.inputPlaceholder"
        />
        <button type="submit" :disabled="!activeApplicationId || isSending">
          <i class="fas fa-paper-plane"></i>
        </button>
      </form>
    </article>
  </section>
</template>

<style scoped>
.messages {
  min-height: 40rem;
  display: grid;
  grid-template-columns: 23rem minmax(0, 1fr);
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.35rem;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(26, 177, 111, 0.1), transparent 30%),
    var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.messages--embedded {
  min-height: 38rem;
}

.chat-list {
  display: grid;
  align-content: start;
  gap: 0.85rem;
  padding: 1.3rem;
  border-right: 0.0625rem solid var(--border-subtle);
  background: color-mix(in srgb, var(--surface-secondary) 76%, transparent);
}

.chat-list__head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.chat-list__head h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(1.4rem, 2vw, 1.9rem);
}

.chat-list__hint {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  line-height: 1.5;
}

.chat-count {
  min-width: 2.5rem;
  min-height: 2.5rem;
  display: grid;
  place-items: center;
  padding: 0.3rem 0.7rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, white);
  color: var(--brand-strong);
  font-weight: 700;
}

.status {
  margin: 0;
  padding: 0.75rem 0.85rem;
  border: 0.0625rem solid var(--border-strong);
  border-radius: 0.85rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
  line-height: 1.5;
}

.chat-list__item {
  display: grid;
  gap: 0.35rem;
  padding: 1rem;
  border: 0.0625rem solid transparent;
  border-radius: 1rem;
  background: transparent;
  text-align: left;
  cursor: pointer;
  color: var(--text-primary);
  transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.chat-list__item:hover,
.chat-list__item:focus-visible {
  border-color: var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 52%, transparent);
}

.chat-list__item.active {
  border-color: var(--border-strong);
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--brand-soft) 75%, transparent), color-mix(in srgb, var(--surface-secondary) 88%, transparent)),
    var(--surface-secondary);
  box-shadow: inset 0 0 0 0.0625rem rgba(22, 155, 97, 0.06);
}

.chat-list__item-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
}

.chat-list__item-head span,
.chat-list__job,
.chat-head span,
.empty-thread,
.message-author,
.chat-list__message {
  color: var(--text-muted);
}

.chat-list__job {
  font-size: 0.92rem;
}

.chat-list__message {
  line-height: 1.55;
}

.chat {
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-width: 0;
}

.chat-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.2rem 1.25rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
  background: color-mix(in srgb, var(--surface-secondary) 82%, transparent);
}

.chat-head__copy {
  display: grid;
  gap: 0.2rem;
}

.chat-head strong {
  display: block;
  color: var(--text-primary);
  font-size: 1.15rem;
}

.delete-button {
  min-height: 2.9rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  padding: 0.78rem 1rem;
  border: 0.0625rem solid rgba(220, 38, 38, 0.14);
  border-radius: 0.9rem;
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
  font: inherit;
  font-weight: 800;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease,
    opacity 0.2s ease;
}

.delete-button:hover:not(:disabled) {
  transform: translateY(-0.0625rem);
  background: rgba(220, 38, 38, 0.12);
  border-color: rgba(220, 38, 38, 0.2);
}

.delete-button i {
  font-size: 0.9rem;
}

.thread {
  display: grid;
  align-content: start;
  gap: 1rem;
  padding: 1.35rem;
  overflow-y: auto;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 80%, transparent), color-mix(in srgb, var(--surface-secondary) 92%, transparent)),
    var(--surface-primary);
}

.message-row {
  display: grid;
  gap: 0.35rem;
}

.message-row--own {
  justify-items: end;
}

.message-author {
  font-size: 0.82rem;
}

.bubble {
  max-width: 36rem;
  margin: 0;
  padding: 1rem 1.1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem 1rem 1rem 0.35rem;
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
  color: var(--text-primary);
  line-height: 1.6;
}

.own {
  border-color: color-mix(in srgb, var(--brand-base) 32%, transparent);
  border-radius: 1rem 1rem 0.35rem 1rem;
  background: color-mix(in srgb, var(--brand-soft) 70%, transparent);
}

.chat-form {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 1rem 1.25rem 1.25rem;
  border-top: 0.0625rem solid var(--border-subtle);
  background: color-mix(in srgb, var(--surface-secondary) 78%, transparent);
}

.chat-form input {
  flex: 1;
  min-height: 3.15rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  font: inherit;
}

.chat-form button {
  width: 3.25rem;
  height: 3.25rem;
  border: none;
  border-radius: 1rem;
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
  box-shadow: 0 0.875rem 1.8rem rgba(21, 149, 93, 0.18);
  cursor: pointer;
}

.chat-form button:disabled,
.chat-form input:disabled,
.delete-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 56rem) {
  .messages {
    grid-template-columns: 1fr;
  }

  .chat-list {
    border-right: none;
    border-bottom: 0.0625rem solid var(--border-subtle);
  }

  .chat-head {
    align-items: start;
    flex-direction: column;
  }

  .chat-form,
  .thread {
    padding: 1rem;
  }

  .delete-button,
  .chat-form button {
    width: 100%;
  }

  .chat-form {
    flex-direction: column;
  }

  .bubble {
    max-width: 100%;
  }
}
</style>
