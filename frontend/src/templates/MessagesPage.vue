<script setup>
import { computed, onMounted, watch } from 'vue'
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

watch(() => route.query.application, async (value) => {
  const applicationId = Number(value)
  if (!applicationId || applicationId === messaging.activeApplicationId) return

  const exists = messaging.conversations.some((item) => item.application_id === applicationId)
  if (exists) {
    await openConversation(applicationId)
  }
})

onMounted(loadConversations)
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="messages">
        <aside class="chat-list">
          <h1>Сообщения</h1>
          <p v-if="status" class="status">{{ status }}</p>
          <p v-if="isLoading" class="status">Загрузка диалогов...</p>

          <button
            v-for="conversation in conversations"
            :key="conversation.application_id"
            type="button"
            :class="{ active: activeApplicationId === conversation.application_id }"
            @click="openConversation(conversation.application_id)"
          >
            <strong>{{ conversation.counterparty_name }}</strong>
            <span>{{ conversation.last_message }}</span>
          </button>

          <p v-if="!isLoading && !conversations.length" class="status">
            Пока нет диалогов. Они появятся после публикации вакансии и отклика.
          </p>
        </aside>

        <article class="chat">
          <header>
            <strong>{{ activeTitle }}</strong>
            <span>{{ activeSubtitle }}</span>
          </header>

          <div class="thread">
            <p
              v-for="message in thread"
              :key="message.id"
              class="bubble"
              :class="{ own: message.is_own }"
            >
              {{ message.body }}
            </p>

            <p v-if="!thread.length" class="empty-thread">
              Выберите диалог слева, чтобы начать общение.
            </p>
          </div>

          <form @submit.prevent="send">
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
  min-height: 34rem;
  display: grid;
  grid-template-columns: 22rem minmax(0, 1fr);
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
  gap: 0.6rem;
  padding: 1.25rem;
  border-right: 0.0625rem solid var(--border-subtle);
  background: color-mix(in srgb, var(--surface-secondary) 76%, transparent);
}

.chat-list h1 {
  margin: 0 0 0.4rem;
  color: var(--text-primary);
  font-size: clamp(1.7rem, 2vw, 2.2rem);
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

.chat-list button {
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

.chat-list button:hover,
.chat-list button:focus-visible {
  border-color: var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 52%, transparent);
}

.chat-list button.active {
  border-color: var(--border-strong);
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--brand-soft) 75%, transparent), color-mix(in srgb, var(--surface-secondary) 88%, transparent)),
    var(--surface-secondary);
  box-shadow: inset 0 0 0 0.0625rem rgba(22, 155, 97, 0.06);
}

.chat-list span,
header span,
.empty-thread {
  color: var(--text-muted);
}

.chat {
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-width: 0;
}

header,
form {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.2rem 1.25rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
}

form {
  border-top: 0.0625rem solid var(--border-subtle);
  border-bottom: none;
  background: color-mix(in srgb, var(--surface-secondary) 78%, transparent);
}

header {
  background: color-mix(in srgb, var(--surface-secondary) 82%, transparent);
}

header strong {
  color: var(--text-primary);
}

.thread {
  display: grid;
  align-content: start;
  gap: 0.85rem;
  padding: 1.25rem;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 80%, transparent), color-mix(in srgb, var(--surface-secondary) 92%, transparent)),
    var(--surface-primary);
}

.bubble {
  max-width: 28rem;
  padding: 0.95rem 1.05rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem 1rem 1rem 0.35rem;
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
  color: var(--text-primary);
  line-height: 1.55;
}

.own {
  margin-left: auto;
  border-color: color-mix(in srgb, var(--brand-base) 32%, transparent);
  border-radius: 1rem 1rem 0.35rem 1rem;
  background: color-mix(in srgb, var(--brand-soft) 70%, transparent);
}

input {
  flex: 1;
  min-height: 3rem;
  padding: 0.85rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  font: inherit;
}

form button {
  width: 3rem;
  height: 3rem;
  border: none;
  border-radius: 0.875rem;
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
  box-shadow: 0 0.875rem 1.8rem rgba(21, 149, 93, 0.18);
}

form button:disabled,
input:disabled {
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

  header,
  form {
    padding: 1rem;
  }

  .thread {
    padding: 1rem;
  }

  .bubble {
    max-width: 100%;
  }
}
</style>
