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
    <form class="apanel-card apanel-form" @submit.prevent="submit">
      <div class="apanel-form__intro">
        <span class="apanel-form__icon" aria-hidden="true">
          <i class="fas fa-key"></i>
        </span>
        <div>
          <p class="apanel-eyebrow">{{ t('aPanelSettings.betaAccess') }}</p>
          <h2>{{ t('aPanelSettings.createToken') }}</h2>
        </div>
      </div>

      <div class="apanel-form__controls">
        <label class="toggle-field toggle-switch">
          <span class="toggle-field__copy">
            <strong>{{ t('aPanelSettings.betaAccess') }}</strong>
            <small>{{ betaAccessEnabled ? t('aPanelSettings.active') : t('aPanelSettings.inactive') }}</small>
          </span>
          <span class="toggle-switch__control">
            <input v-model="betaAccessModel" type="checkbox" :disabled="isSavingSettings" />
            <span class="toggle-switch__track" aria-hidden="true">
              <span class="toggle-switch__thumb"></span>
            </span>
          </span>
        </label>

        <label class="note-field">
          <span class="visually-hidden">{{ t('aPanelSettings.note') }}</span>
          <input v-model="note" :placeholder="t('aPanelSettings.notePlaceholder')" />
        </label>

        <button class="btn-primary apanel-create-button" type="submit" :disabled="isSaving">
          <i class="fas fa-plus" aria-hidden="true"></i>
          {{ isSaving ? t('aPanelSettings.creating') : t('aPanelSettings.createToken') }}
        </button>
      </div>
    </form>

    <section class="apanel-card apanel-token-card">
      <div class="apanel-card__head">
        <div>
          <p class="apanel-eyebrow">{{ t('aPanelSettings.storedEyebrow') }}</p>
          <h2>{{ t('aPanelSettings.issuedTokens') }}</h2>
        </div>
        <span class="apanel-token-count">{{ tokens.length }}</span>
      </div>

      <div class="apanel-token-table-wrap">
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
                      <span>{{ t('aPanelSettings.copyToken') }}</span>
                    </button>
                    <button
                      type="button"
                      class="apanel-action-button btn-token-delete"
                      :aria-label="t('aPanelSettings.deleteToken')"
                      @click="emit('delete-token', token)"
                    >
                      <i class="fas fa-trash"></i>
                      <span>{{ t('aPanelSettings.deleteToken') }}</span>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="!tokens.length" class="apanel-token-empty-row">
                <td colspan="5">
                  <div class="apanel-empty">
                    <span class="apanel-empty__icon" aria-hidden="true"><i class="fas fa-key"></i></span>
                    <strong>{{ t('aPanelSettings.emptyTokens') }}</strong>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
      </div>
    </section>
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
  padding: 1.25rem;
}

.apanel-form {
  display: grid;
  grid-template-columns: minmax(11rem, 0.26fr) minmax(0, 1fr);
  gap: 1.25rem;
  align-items: stretch;
}

.apanel-form__controls {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  align-items: center;
}

.apanel-form__intro,
.apanel-card__head {
  display: flex;
  align-items: center;
}

.apanel-form__intro {
  gap: 0.85rem;
  min-height: 3.25rem;
}

.apanel-form__icon,
.apanel-empty__icon {
  display: grid;
  place-items: center;
  color: var(--brand-strong);
  background: color-mix(in srgb, var(--brand-soft) 66%, white);
}

.apanel-form__icon {
  width: 2.8rem;
  height: 2.8rem;
  flex: 0 0 auto;
  border-radius: 0.85rem;
}

.apanel-card__head {
  justify-content: space-between;
  gap: 1rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
}

.apanel-token-count {
  display: grid;
  min-width: 2.25rem;
  height: 2.25rem;
  place-items: center;
  border-radius: 0.7rem;
  background: color-mix(in srgb, var(--brand-soft) 66%, white);
  color: var(--brand-strong);
  font-weight: 900;
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
  box-sizing: border-box;
  height: 3.7rem;
  padding: 0.55rem 0.8rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.85rem;
  background: color-mix(in srgb, var(--brand-soft) 24%, white);
}

.toggle-switch {
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  column-gap: 1rem;
}

.toggle-field__copy {
  display: grid;
  gap: 0.15rem;
}

.toggle-field__copy small {
  color: var(--text-muted);
  font-weight: 600;
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
  cursor: pointer;
}

.toggle-switch__track {
  width: 3.4rem;
  height: 1.95rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.15);
  padding: 0.2rem;
  transition: background 0.2s ease;
  cursor: pointer;
}

.toggle-switch__control input:focus-visible + .toggle-switch__track {
  outline: 0.1875rem solid rgba(20, 184, 87, 0.18);
  outline-offset: 0.125rem;
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

.note-field input {
  width: 100%;
  height: 3.7rem;
  padding: 0.8rem 0.95rem;
  border: 0.0625rem solid rgba(15, 23, 42, 0.12);
  border-radius: 0.8rem;
  background: rgba(255, 255, 255, 0.92);
  color: var(--text-primary);
  font: inherit;
}

.note-field input:hover {
  border-color: color-mix(in srgb, var(--brand-base) 35%, var(--border-subtle));
}

.note-field input:focus {
  outline: none;
  border-color: var(--brand-strong);
  box-shadow: 0 0 0 0.1875rem rgba(20, 184, 87, 0.12);
}

.apanel-create-button {
  width: 100%;
  height: 3.7rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  padding-inline: 1.35rem;
  white-space: nowrap;
  cursor: pointer;
  transition: transform 0.2s ease, filter 0.2s ease, box-shadow 0.2s ease;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

.apanel-create-button:hover:not(:disabled) {
  transform: translateY(-0.0625rem);
  filter: brightness(1.04);
  box-shadow: 0 0.8rem 1.5rem rgba(21, 149, 93, 0.2);
}

.apanel-create-button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
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
  padding: 0.95rem 1.25rem;
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
  min-width: 2.4rem;
  height: 2.4rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0 0.75rem;
  border: 0;
  border-radius: 0.72rem;
  color: #fff;
  cursor: pointer;
  transition: transform 0.2s ease, filter 0.2s ease, box-shadow 0.2s ease;
}

.apanel-action-button span {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}

.apanel-action-button:hover {
  transform: translateY(-0.0625rem);
  filter: brightness(1.05);
}

.apanel-action-button:focus-visible {
  outline: 0.1875rem solid rgba(15, 23, 42, 0.16);
  outline-offset: 0.125rem;
}

.apanel-copy-button {
  background: linear-gradient(180deg, #22a6f2, #1684c7);
  box-shadow: 0 0.55rem 1rem rgba(22, 132, 199, 0.18);
}

.btn-token-delete {
  background: linear-gradient(180deg, #ef4444, #dc2626);
  box-shadow: 0 0.55rem 1rem rgba(220, 38, 38, 0.18);
}

.apanel-empty {
  min-height: 10rem;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 0.65rem;
  color: var(--text-muted);
  text-align: center;
}

.apanel-empty__icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  font-size: 1.05rem;
}

.apanel-token-empty-row td {
  border-bottom: 0;
}

@media (max-width: 90rem) {
  .apanel-form {
    grid-template-columns: 1fr;
  }

  .apanel-form__controls {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 52rem) {
  .apanel-form__controls {
    grid-template-columns: 1fr;
  }
}
</style>
