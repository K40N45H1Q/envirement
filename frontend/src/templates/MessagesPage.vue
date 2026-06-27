<script setup>
import { computed, onBeforeUnmount, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useMessagingStore } from '@/stores/messaging'

const route = useRoute()
const router = useRouter()
const messaging = useMessagingStore()

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

const activeTitle = computed(() => activeConversation.value?.counterparty_name || 'Сообщения')
const activeSubtitle = computed(() => {
  if (!activeConversation.value) return 'Диалоги по вакансиям и откликам'
  return `${activeConversation.value.job_title} · ${activeConversation.value.job_company}`
})

const syncQuery = (applicationId) => {
  router.replace({
    path: '/messages',
    query: applicationId ? { application: String(applicationId) } : {},
  })
}

const openConversation = async (applicationId) => {
  if (!applicationId) return
  syncQuery(applicationId)
  await messaging.openConversation(applicationId)
}

const loadConversations = async () => {
  await messaging.loadConversations(route.query.application)

  if (messaging.activeApplicationId) {
    syncQuery(messaging.activeApplicationId)
  }
}

const send = async () => {
  await messaging.sendCurrentMessage()
}

const deleteConversation = async () => {
  const confirmed = window.confirm('Удалить этот диалог? Вместе с ним будет удалён и связанный отклик.')
  if (!confirmed) return

  const deleted = await messaging.deleteActiveConversation()
  if (deleted) {
    syncQuery(messaging.activeApplicationId)
  }
}

watch(() => route.query.application, async (value) => {
  const applicationId = Number(value)
  if (!applicationId || applicationId === messaging.activeApplicationId) return

  const exists = messaging.conversations.some((item) => item.application_id === applicationId)
  if (exists) {
    await openConversation(applicationId)
  }
})

onMounted(async () => {
  await loadConversations()
  messaging.startRealtime()
})

onBeforeUnmount(() => {
  messaging.stopRealtime()
})
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="messages">
        <aside class="chat-list">
          <div class="chat-list__head">
            <div>
              <h1>Сообщения</h1>
              <p class="chat-list__hint">Все активные диалоги по откликам и вакансиям</p>
            </div>
            <span class="chat-count">{{ conversations.length }}</span>
          </div>

          <p v-if="status" class="status">{{ status }}</p>
          <p v-if="isLoading" class="status">Загрузка диалогов...</p>

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
              <span>{{ new Date(conversation.last_message_at).toLocaleDateString('ru-RU') }}</span>
            </div>
            <span class="chat-list__job">{{ conversation.job_title }}</span>
            <span>{{ conversation.last_message }}</span>
          </button>

          <p v-if="!isLoading && !conversations.length" class="status">
            Пока нет диалогов. Они появятся после отклика кандидата или ответа работодателя.
          </p>
        </aside>

        <article class="chat">
          <header class="chat-head">
            <div>
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
              {{ isDeleting ? 'Удаляем...' : 'Удалить диалог' }}
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
              <p class="bubble" :class="{ own: message.is_own }">
                {{ message.body }}
              </p>
            </div>

            <p v-if="!thread.length" class="empty-thread">
              Выберите диалог слева, чтобы начать общение.
            </p>
          </div>

          <form class="chat-form" @submit.prevent="send">
            <input
              v-model="draft"
              :disabled="!activeApplicationId || isSending"
              placeholder="Напишите сообщение"
            />
            <button type="submit" :disabled="!activeApplicationId || isSending">
              <i class="fas fa-paper-plane"></i>
            </button>
          </form>
        </article>
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.page {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 2rem var(--shell-gutter) 4rem;
}

.messages {
  min-height: 36rem;
  display: grid;
  grid-template-columns: 24rem minmax(0, 1fr);
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.25rem;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(26, 177, 111, 0.1), transparent 30%),
    var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.chat-list {
  display: grid;
  align-content: start;
  gap: 0.75rem;
  padding: 1.25rem;
  border-right: 0.0625rem solid var(--border-subtle);
  background: color-mix(in srgb, var(--surface-secondary) 76%, transparent);
}

.chat-list__head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.chat-list__head h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(1.7rem, 2vw, 2.2rem);
}

.chat-list__hint {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  line-height: 1.5;
}

.chat-count {
  min-width: 2.4rem;
  min-height: 2.4rem;
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
.message-author {
  color: var(--text-muted);
}

.chat-list__job {
  font-size: 0.9rem;
}

.chat {
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-width: 0;
}

.chat-head,
.chat-form {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.2rem 1.25rem;
}

.chat-head {
  border-bottom: 0.0625rem solid var(--border-subtle);
  background: color-mix(in srgb, var(--surface-secondary) 82%, transparent);
}

.chat-head strong {
  display: block;
  color: var(--text-primary);
}

.delete-button {
  min-height: 2.9rem;
  padding: 0 1rem;
  border: 0.0625rem solid color-mix(in srgb, #d24646 28%, var(--border-subtle));
  border-radius: 0.875rem;
  background: #fff;
  color: #c03939;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.delete-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.thread {
  display: grid;
  align-content: start;
  gap: 0.85rem;
  padding: 1.25rem;
  overflow-y: auto;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 80%, transparent), color-mix(in srgb, var(--surface-secondary) 92%, transparent)),
    var(--surface-primary);
}

.message-row {
  display: grid;
  gap: 0.3rem;
}

.message-row--own {
  justify-items: end;
}

.message-author {
  font-size: 0.82rem;
}

.bubble {
  max-width: 32rem;
  margin: 0;
  padding: 0.95rem 1.05rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem 1rem 1rem 0.35rem;
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
  color: var(--text-primary);
  line-height: 1.55;
}

.own {
  border-color: color-mix(in srgb, var(--brand-base) 32%, transparent);
  border-radius: 1rem 1rem 0.35rem 1rem;
  background: color-mix(in srgb, var(--brand-soft) 70%, transparent);
}

.chat-form {
  border-top: 0.0625rem solid var(--border-subtle);
  background: color-mix(in srgb, var(--surface-secondary) 78%, transparent);
}

.chat-form input {
  flex: 1;
  min-height: 3rem;
  padding: 0.85rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  font: inherit;
}

.chat-form button {
  width: 3rem;
  height: 3rem;
  border: none;
  border-radius: 0.875rem;
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
  box-shadow: 0 0.875rem 1.8rem rgba(21, 149, 93, 0.18);
  cursor: pointer;
}

.chat-form button:disabled,
.chat-form input:disabled {
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

  .chat-head,
  .chat-form {
    padding: 1rem;
  }

  .chat-head {
    align-items: start;
    flex-direction: column;
  }

  .thread {
    padding: 1rem;
  }

  .bubble {
    max-width: 100%;
  }

  .delete-button {
    width: 100%;
  }
}
</style>
