<script setup>
import { computed, ref } from 'vue'
import { useI18n } from '@/i18n'

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
const { language, t } = useI18n()
const note = ref('')

const betaAccessModel = computed({
  get: () => props.betaAccessEnabled,
  set: (value) => emit('update-beta-access', value),
})

const submit = () => {
  emit('create-token', { note: note.value })
  note.value = ''
}

const copyToken = async (token) => {
  if (!token) return
  await navigator.clipboard?.writeText(token)
}

const formatDate = (value) => {
  if (!value) return '-'
  const locale = language.value === 'lv' ? 'lv-LV' : language.value === 'en' ? 'en-GB' : 'ru-RU'
  return new Intl.DateTimeFormat(locale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

const tokenStateLabel = (token) => (token.used ? t('aPanelSettings.active') : t('aPanelSettings.inactive'))
</script>

<template>
  <section class="apanel-settings">
    <section class="apanel-card apanel-token-card">
      <div class="apanel-card__head">
        <p class="apanel-eyebrow">{{ t('aPanelSettings.storedEyebrow') }}</p>
        <h2>{{ t('aPanelSettings.issuedTokens') }}</h2>
      </div>

      <div class="apanel-token-list">
        <div v-if="tokens.length" class="apanel-token-table-wrap">
          <table class="apanel-token-table">
            <thead>
              <tr>
                <th>{{ t('aPanelSettings.tokenColumn') }}</th>
                <th>{{ t('aPanelSettings.noteColumn') }}</th>
                <th>{{ t('aPanelSettings.statusColumn') }}</th>
                <th>{{ t('aPanelSettings.usedColumn') }}</th>
                <th>{{ t('aPanelSettings.actionsColumn') }}</th>
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
                    :class="{ 'apanel-token-status--active': token.used }"
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
                      :aria-label="t('aPanelSettings.copyToken')"
                      @click="copyToken(token.token)"
                    >
                      <i class="fas fa-copy"></i>
                    </button>
                    <button
                      type="button"
                      class="apanel-action-button btn-token-delete"
                      :aria-label="t('aPanelSettings.deleteToken')"
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

        <p v-else class="apanel-empty">{{ t('aPanelSettings.emptyTokens') }}</p>
      </div>
    </section>

    <form class="apanel-card apanel-form" @submit.prevent="submit">
      <label class="toggle-field toggle-switch">
        <span>{{ t('aPanelSettings.betaAccess') }}</span>
        <span class="toggle-switch__control">
          <input v-model="betaAccessModel" type="checkbox" :disabled="isSavingSettings" />
          <span class="toggle-switch__track" aria-hidden="true">
            <span class="toggle-switch__thumb"></span>
          </span>
        </span>
      </label>

      <div>
        <p class="apanel-eyebrow">{{ t('aPanelSettings.betaAccess') }}</p>
        <h2>{{ t('aPanelSettings.createToken') }}</h2>
      </div>

      <label>
        {{ t('aPanelSettings.note') }}
        <input v-model="note" :placeholder="t('aPanelSettings.notePlaceholder')" />
      </label>

      <button class="btn-primary" type="submit" :disabled="isSaving">
        {{ isSaving ? t('aPanelSettings.creating') : t('aPanelSettings.createToken') }}
      </button>

      <div v-if="createdToken" class="apanel-token-result">
        <span>{{ t('aPanelSettings.newToken') }}</span>
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
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  column-gap: 1rem;
}

.toggle-switch__control {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.toggle-switch__control input {
  position: absolute;
  inset: 0;
  opacity: 0;
}

.toggle-switch__track {
  width: 3.4rem;
  height: 1.95rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.15);
  padding: 0.2rem;
  transition: background 0.2s ease;
}

.toggle-switch__thumb {
  display: block;
  width: 1.55rem;
  height: 1.55rem;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0.45rem 1rem rgba(15, 23, 42, 0.18);
  transition: transform 0.2s ease;
}

.toggle-switch__control input:checked + .toggle-switch__track {
  background: color-mix(in srgb, var(--brand-strong) 70%, white);
}

.toggle-switch__control input:checked + .toggle-switch__track .toggle-switch__thumb {
  transform: translateX(1.45rem);
}

input {
  width: 100%;
  min-height: 2.9rem;
  padding: 0.8rem 0.95rem;
  border: 0.0625rem solid rgba(15, 23, 42, 0.12);
  border-radius: 0.8rem;
  background: rgba(255, 255, 255, 0.92);
  color: var(--text-primary);
  font: inherit;
}

.apanel-token-list {
  padding: 0 1.25rem 1.25rem;
}

.apanel-token-table-wrap {
  overflow-x: auto;
}

.apanel-token-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  min-width: 46rem;
}

.apanel-token-table th,
.apanel-token-table td {
  padding: 0.85rem 0.8rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
  text-align: left;
  color: var(--text-primary);
}

.apanel-token-table th {
  background: color-mix(in srgb, var(--brand-soft) 42%, white);
  color: color-mix(in srgb, var(--text-muted) 86%, var(--brand-strong));
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.apanel-token-value code,
.apanel-token-result code {
  display: inline-block;
  padding: 0.35rem 0.5rem;
  border-radius: 0.55rem;
  background: rgba(15, 23, 42, 0.06);
  color: var(--text-primary);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.82rem;
}

.apanel-token-note {
  max-width: 20rem;
  word-break: break-word;
}

.apanel-token-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 7rem;
  padding: 0.4rem 0.7rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.08);
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 800;
}

.apanel-token-status--active {
  background: color-mix(in srgb, var(--brand-soft) 72%, white);
  color: var(--brand-strong);
}

.apanel-token-actions {
  display: flex;
  gap: 0.45rem;
}

.apanel-action-button {
  width: 2.4rem;
  height: 2.4rem;
  border: 0;
  border-radius: 0.72rem;
  background: rgba(15, 23, 42, 0.06);
  color: var(--text-primary);
}

.btn-token-delete {
  color: #be123c;
}

.apanel-token-result {
  display: grid;
  gap: 0.45rem;
  padding: 0.95rem 1rem;
  border: 0.0625rem dashed color-mix(in srgb, var(--brand-strong) 30%, white);
  border-radius: 0.85rem;
  background: color-mix(in srgb, var(--brand-soft) 40%, white);
}

.apanel-empty {
  margin: 0;
  color: var(--text-muted);
}

@media (max-width: 72rem) {
  .apanel-form {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 52rem) {
  .apanel-form {
    grid-template-columns: 1fr;
  }
}
</style>
