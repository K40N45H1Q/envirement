<script setup>
import { ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'

const chats = [
  { name: 'Build Solutions GmbH', text: 'Добрый день! Ваш отклик получен.' },
  { name: 'Nord Metal', text: 'Можем обсудить дату выхода?' },
  { name: 'Euro Logistics', text: 'Спасибо за резюме.' },
]

const active = ref(chats[0])
const draft = ref('')
const sent = ref([])

const send = () => {
  if (!draft.value.trim()) return
  sent.value.push(draft.value.trim())
  draft.value = ''
}
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="messages">
        <aside class="chat-list">
          <h1>Сообщения</h1>
          <button
            v-for="chat in chats"
            :key="chat.name"
            type="button"
            :class="{ active: active.name === chat.name }"
            @click="active = chat"
          >
            <strong>{{ chat.name }}</strong>
            <span>{{ chat.text }}</span>
          </button>
        </aside>

        <article class="chat">
          <header>
            <strong>{{ active.name }}</strong>
            <span>online</span>
          </header>
          <div class="thread">
            <p class="bubble">{{ active.text }}</p>
            <p v-for="message in sent" :key="message" class="bubble own">{{ message }}</p>
          </div>
          <form @submit.prevent="send">
            <input v-model="draft" placeholder="Напишите сообщение" />
            <button type="submit"><i class="fas fa-paper-plane"></i></button>
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
header span {
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
