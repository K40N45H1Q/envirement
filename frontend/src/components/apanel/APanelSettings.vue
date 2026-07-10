<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  tokens: {
    type: Array,
    default: () => [],
  },
  betaAccessEnabled: {
    type: Boolean,
    default: false,
  },
  isSaving: {
    type: Boolean,
    default: false,
  },
  isSavingSettings: {
    type: Boolean,
    default: false,
  },
  createdToken: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['create-token', 'delete-token', 'update-beta-access'])

const note = ref('')

const betaAccessModel = computed({
  get: () => props.betaAccessEnabled,
  set: (value) => emit('update-beta-access', value),
})

const submit = () => {
  emit('create-token', {
    note: note.value,
  })
  note.value = ''
}

const copyToken = async (token) => {
  if (!token) return
  await navigator.clipboard?.writeText(token)
}

const formatDate = (value) => {
  if (!value) return '-'
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

const tokenStateLabel = (token) => {
  return token.used ? 'Активный' : 'Неактивный'
}
</script>

<template>
  <section class="apanel-settings">
    <section class="apanel-card apanel-token-card">
      <div class="apanel-card__head">
        <p class="apanel-eyebrow">Хранится в базе данных</p>
        <h2>Выданные токены</h2>
      </div>

      <div class="apanel-token-list">
        <div v-if="tokens.length" class="apanel-token-table-wrap">
          <table class="apanel-token-table">
            <thead>
              <tr>
                <th>Токен</th>
                <th>Заметка</th>
                <th>Статус</th>
                <th>Использован</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="token in tokens" :key="token.id">
                <td>
                  <div class="apanel-token-value">
                    <code>{{ token.token || '-' }}</code>
                  </div>
                </td>
                <td class="apanel-token-note">{{ token.note || '-' }}</td>
                <td>
                  <span
                    class="apanel-token-status"
                    :class="{
                      'apanel-token-status--active': token.used,
                    }"
                  >
                    {{ tokenStateLabel(token) }}
                  </span>
                </td>
                <td>{{ formatDate(token.usedAt || token.used_at) }}</td>
                <td>
                  <div class="apanel-token-actions">
                    <button
                      v-if="token.token"
                      type="button"
                      class="apanel-action-button apanel-copy-button"
                      aria-label="Копировать токен"
                      @click="copyToken(token.token)"
                    >
                      <i class="fas fa-copy"></i>
                    </button>
                    <button
                      type="button"
                      class="apanel-action-button btn-token-delete"
                      aria-label="Удалить токен"
                      @click="emit('delete-token', token)"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-else class="apanel-empty">Токенов пока нет.</p>
      </div>
    </section>

    <form class="apanel-card apanel-form" @submit.prevent="submit">
      <label class="toggle-field toggle-switch">
        <span>Бета-доступ</span>
        <span class="toggle-switch__control">
          <input v-model="betaAccessModel" type="checkbox" :disabled="isSavingSettings" />
          <span class="toggle-switch__track" aria-hidden="true">
            <span class="toggle-switch__thumb"></span>
          </span>
        </span>
      </label>

      <div>
        <p class="apanel-eyebrow">Бета-доступ</p>
        <h2>Создать токен</h2>
      </div>

      <label>
        Заметка
        <input v-model="note" placeholder="Например: тестовый доступ" />
      </label>

      <button class="btn-primary" type="submit" :disabled="isSaving">
        {{ isSaving ? 'Создаем...' : 'Создать токен' }}
      </button>

      <div v-if="createdToken" class="apanel-token-result">
        <span>Новый токен</span>
        <code>{{ createdToken }}</code>
      </div>
    </form>
  </section>
</template>

<style scoped>
.apanel-settings {
  display: grid;
  gap: 1rem;
  align-items: start;
}

.apanel-card {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(250, 253, 251, 0.98)),
    var(--surface-primary);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
}

.apanel-form,
.apanel-card__head {
  display: grid;
  gap: 1rem;
  padding: 1.25rem;
}

.apanel-form {
  grid-template-columns: minmax(12rem, 16rem) minmax(10rem, 16rem) minmax(16rem, 1fr) minmax(11rem, 14rem);
  align-items: end;
}

.apanel-form h2,
.apanel-card__head h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.2rem;
  line-height: 1.15;
}

.apanel-eyebrow {
  margin: 0 0 0.25rem;
  color: var(--brand-strong);
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

label {
  display: grid;
  gap: 0.45rem;
  color: var(--text-primary);
  font-weight: 700;
}

.toggle-field {
  align-content: start;
}

.toggle-switch {
  gap: 0.7rem;
}

.toggle-switch__control {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: 3.5rem;
  height: 2rem;
}

.toggle-switch__control input[type="checkbox"] {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  min-width: 100%;
  min-height: 100%;
  margin: 0;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
}

.toggle-switch__control input[type="checkbox"]:disabled {
  cursor: not-allowed;
}

.toggle-switch__track {
  position: relative;
  width: 100%;
  height: 100%;
  border: 0.0625rem solid color-mix(in srgb, var(--border-strong) 55%, white);
  border-radius: 999px;
  background: color-mix(in srgb, var(--border-subtle) 78%, white);
  box-shadow: inset 0 0.0625rem 0.2rem rgba(15, 23, 42, 0.08);
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.toggle-switch__thumb {
  position: absolute;
  top: 0.1875rem;
  left: 0.1875rem;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0.2rem 0.55rem rgba(15, 23, 42, 0.16);
  transition: transform 0.2s ease;
}

.toggle-switch__control input[type="checkbox"]:checked + .toggle-switch__track {
  border-color: color-mix(in srgb, var(--brand-strong) 70%, white);
  background: linear-gradient(135deg, var(--brand-base), var(--brand-strong));
  box-shadow: 0 0 0 0.1875rem rgba(20, 184, 87, 0.12);
}

.toggle-switch__control input[type="checkbox"]:checked + .toggle-switch__track .toggle-switch__thumb {
  transform: translateX(1.5rem);
}

.toggle-switch__control input[type="checkbox"]:focus-visible + .toggle-switch__track {
  outline: 0.1875rem solid rgba(20, 184, 87, 0.2);
  outline-offset: 0.125rem;
}

input {
  width: 100%;
  min-height: 2.8rem;
  padding: 0.75rem 0.85rem;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 18%, var(--border-subtle));
  border-radius: 0.7rem;
  background: #fff;
  color: var(--text-primary);
  font: inherit;
  transition: border-color 0.16s ease, box-shadow 0.16s ease;
}

input:focus {
  border-color: color-mix(in srgb, var(--brand-base) 72%, var(--border-subtle));
  box-shadow: 0 0 0 0.2rem color-mix(in srgb, var(--brand-soft) 78%, transparent);
  outline: none;
}

.btn-primary,
.btn-secondary {
  min-height: 2.6rem;
  padding: 0.65rem 0.95rem;
  border: 0.0625rem solid transparent;
  border-radius: 0.78rem;
  font: inherit;
  font-size: 0.86rem;
  font-weight: 850;
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.btn-primary {
  background: linear-gradient(135deg, var(--brand-base), var(--brand-strong));
  color: white;
  box-shadow: 0 0.7rem 1.25rem rgba(22, 155, 97, 0.18);
}

.btn-secondary {
  border-color: color-mix(in srgb, var(--border-subtle) 70%, var(--brand-base));
  background: var(--surface-secondary);
  color: var(--text-primary);
}

.btn-primary:hover:not(:disabled),
.btn-secondary:hover:not(:disabled) {
  transform: translateY(-0.08rem);
}

.btn-primary:disabled,
.btn-secondary:disabled {
  cursor: not-allowed;
  opacity: 0.68;
}

.apanel-token-result {
  display: grid;
  gap: 0.45rem;
  padding: 0.85rem;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 20%, transparent);
  border-radius: 0.8rem;
  background: color-mix(in srgb, var(--brand-soft) 70%, transparent);
}

.apanel-token-result span {
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 800;
}

.apanel-token-result code {
  overflow-wrap: anywhere;
  color: var(--text-primary);
}

.apanel-token-table-wrap {
  width: 100%;
  overflow-x: auto;
}

.apanel-token-table {
  width: 100%;
  min-width: 50rem;
  border-collapse: separate;
  border-spacing: 0;
}

.apanel-token-table th,
.apanel-token-table td {
  padding: 0.85rem 1rem;
  border-top: 0.0625rem solid var(--border-subtle);
  color: var(--text-primary);
  text-align: left;
  vertical-align: middle;
}

.apanel-token-table th {
  background: color-mix(in srgb, var(--brand-soft) 42%, white);
  color: color-mix(in srgb, var(--text-muted) 86%, var(--brand-strong));
  font-size: 0.74rem;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.apanel-token-table code {
  display: inline-block;
  padding: 0.28rem 0.45rem;
  border-radius: 0.5rem;
  background: color-mix(in srgb, var(--surface-secondary) 84%, var(--brand-soft));
  color: var(--text-primary);
  overflow-wrap: anywhere;
  user-select: text;
  vertical-align: middle;
  white-space: normal;
}

.apanel-token-value {
  min-width: 18rem;
}

.apanel-token-note {
  max-width: 12rem;
  color: var(--text-muted);
}

.apanel-token-actions {
  display: flex;
  gap: 0.45rem;
  align-items: center;
}

.apanel-action-button {
  width: 2.35rem;
  height: 2.35rem;
  display: inline-grid;
  place-items: center;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 24%, var(--border-subtle));
  border-radius: 0.72rem;
  background: color-mix(in srgb, var(--brand-soft) 58%, white);
  color: var(--brand-strong);
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}

.btn-token-delete {
  border-color: color-mix(in srgb, #be123c 24%, var(--border-subtle));
  background: #fff1f2;
  color: #be123c;
}

.apanel-action-button:hover {
  transform: translateY(-0.08rem);
  box-shadow: 0 0.5rem 1rem rgba(22, 155, 97, 0.14);
}

.btn-token-delete:hover {
  box-shadow: 0 0.5rem 1rem rgba(190, 18, 60, 0.12);
}

.apanel-token-status {
  display: inline-flex;
  min-height: 1.7rem;
  align-items: center;
  padding: 0.2rem 0.6rem;
  border-radius: 999rem;
  background: #f1f5f9;
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 900;
}

.apanel-token-status--active {
  background: color-mix(in srgb, var(--brand-soft) 78%, white);
  color: var(--brand-strong);
}

.apanel-empty {
  margin: 0;
  padding: 2rem 1.25rem;
  color: var(--text-muted);
  font-weight: 800;
}

@media (max-width: 64rem) {
  .apanel-form {
    grid-template-columns: 1fr;
  }
}
</style>
