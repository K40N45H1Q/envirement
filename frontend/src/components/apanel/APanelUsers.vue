<script setup>
import { ref } from 'vue'
import BaseDropdown from '@/components/BaseDropdown.vue'

defineProps({
  users: {
    type: Array,
    default: () => [],
  },

  manageSubscriptions: {
    type: Boolean,
    default: false,
  },

  subscriptionMode: {
    type: String,
    default: 'assign',
  },

  emptyText: {
    type: String,
    default: 'Нет данных',
  },
})

const emit = defineEmits(['update-subscription'])

const subscriptionDrafts = ref({})

const planOptions = [
  { value: 'basic', label: 'Basic' },
  { value: 'standard', label: 'Standard' },
  { value: 'pro', label: 'Pro' },
]

const subscriptionDraft = (user) => {
  if (!subscriptionDrafts.value[user.id]) {
    subscriptionDrafts.value[user.id] = {
      plan: user.subscription_plan || 'standard',
    }
  }

  return subscriptionDrafts.value[user.id]
}

const daysLeft = (value) => {
  if (!value) return '-'

  const expiresAt = new Date(value)

  if (Number.isNaN(expiresAt.getTime())) {
    return '-'
  }

  const millisecondsInDay = 24 * 60 * 60 * 1000

  const days = Math.ceil(
    (expiresAt.getTime() - Date.now()) / millisecondsInDay,
  )

  return days > 0 ? `${days} дн.` : '0 дн.'
}

const roleLabel = (value) => {
  const labels = {
    admin: 'Админ',
    candidate: 'Кандидат',
    user: 'Кандидат',
    employer: 'Работодатель',
  }

  return labels[value] || value || '-'
}

const statusLabel = (value) => {
  const labels = {
    active: 'Активен',
    inactive: 'Неактивен',
    blocked: 'Заблокирован',
  }

  return labels[value] || value || 'Активен'
}

const mediaUrl = (user) => {
  return user.company_logo_url || user.avatar_url || ''
}

const mediaInitial = (user) => {
  const source =
    user.company_name ||
    user.full_name ||
    user.email ||
    '?'

  return source.trim().charAt(0).toUpperCase()
}

const planLabel = (value) => {
  return (
    planOptions.find((plan) => plan.value === value)?.label ||
    '-'
  )
}

const assignSubscription = (user) => {
  const draft = subscriptionDraft(user)

  emit('update-subscription', {
    user,
    plan: draft.plan,
  })
}

const revokeSubscription = (user) => {
  emit('update-subscription', {
    user,
    revoke: true,
  })
}
</script>

<template>
  <section class="apanel-card">
    <div class="apanel-table-wrap">
      <table
        v-if="users.length"
        class="apanel-table"
        :class="{
          'apanel-table--basic': !manageSubscriptions,

          'apanel-table--assign':
            manageSubscriptions &&
            subscriptionMode === 'assign',

          'apanel-table--revoke':
            manageSubscriptions &&
            subscriptionMode === 'revoke',
        }"
      >
        <colgroup>
          <col class="apanel-col-profile" />
          <col class="apanel-col-email" />
          <col class="apanel-col-role" />
          <col class="apanel-col-status" />
          <col class="apanel-col-beta" />

          <col
            v-if="
              manageSubscriptions &&
              subscriptionMode === 'revoke'
            "
            class="apanel-col-plan"
          />

          <col
            v-if="
              manageSubscriptions &&
              subscriptionMode === 'revoke'
            "
            class="apanel-col-left"
          />

          <col class="apanel-col-phone" />

          <col
            v-if="manageSubscriptions"
            class="apanel-col-actions"
          />
        </colgroup>

        <thead>
          <tr>
            <th class="apanel-heading-profile">
              Профиль
            </th>

            <th class="apanel-heading-email">
              Почта
            </th>

            <th>Роль</th>

            <th>Статус</th>

            <th>Бета</th>

            <th
              v-if="
                manageSubscriptions &&
                subscriptionMode === 'revoke'
              "
            >
              Тариф
            </th>

            <th
              v-if="
                manageSubscriptions &&
                subscriptionMode === 'revoke'
              "
            >
              Осталось
            </th>

            <th>Телефон</th>

            <th
              v-if="manageSubscriptions"
              class="apanel-actions-heading"
            >
              Действия
            </th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="user in users"
            :key="user.id"
          >
            <td class="apanel-profile-cell">
              <div class="apanel-user-row">
                <div class="apanel-avatar">
                  <img
                    v-if="mediaUrl(user)"
                    :src="mediaUrl(user)"
                    :alt="
                      user.company_name ||
                      user.full_name ||
                      user.email
                    "
                  />

                  <span v-else>
                    {{ mediaInitial(user) }}
                  </span>
                </div>

                <div class="apanel-user">
                  <span
                    :title="
                      user.company_name ||
                      user.full_name ||
                      '-'
                    "
                  >
                    {{
                      user.company_name ||
                      user.full_name ||
                      '-'
                    }}
                  </span>

                  <small>
                    {{
                      user.account_type === 'employer'
                        ? 'Компания'
                        : 'Профиль'
                    }}
                  </small>
                </div>
              </div>
            </td>

            <td class="apanel-email-cell">
              <span
                class="apanel-email"
                :title="user.email || '-'"
              >
                {{ user.email || '-' }}
              </span>
            </td>

            <td>
              <span
                class="apanel-pill"
                :title="roleLabel(user.account_type)"
              >
                {{ roleLabel(user.account_type) }}
              </span>
            </td>

            <td>
              <span
                class="apanel-status-pill"
                :title="statusLabel(user.status)"
              >
                {{ statusLabel(user.status) }}
              </span>
            </td>

            <td>
              <span
                class="apanel-beta"
                :class="{
                  'apanel-beta--active':
                    user.has_beta_access,
                }"
              >
                {{ user.has_beta_access ? 'Есть' : 'Нет' }}
              </span>
            </td>

            <td
              v-if="
                manageSubscriptions &&
                subscriptionMode === 'revoke'
              "
            >
              <span
                class="apanel-plan"
                :class="{
                  'apanel-plan--active':
                    user.has_active_subscription,
                }"
                :title="
                  planLabel(user.subscription_plan)
                "
              >
                {{ planLabel(user.subscription_plan) }}
              </span>
            </td>

            <td
              v-if="
                manageSubscriptions &&
                subscriptionMode === 'revoke'
              "
            >
              <span class="apanel-cell-text">
                {{
                  daysLeft(
                    user.subscription_expires_at,
                  )
                }}
              </span>
            </td>

            <td>
              <span
                class="apanel-cell-text apanel-phone"
                :title="user.phone || '-'"
              >
                {{ user.phone || '-' }}
              </span>
            </td>

            <td
              v-if="manageSubscriptions"
              class="apanel-actions-cell"
            >
              <div class="apanel-actions">
                <template
                  v-if="subscriptionMode === 'assign'"
                >
                  <BaseDropdown
                    v-model="
                      subscriptionDraft(user).plan
                    "
                    class="apanel-plan-dropdown"
                    :options="planOptions"
                    size="sm"
                    align="right"
                    :show-selected-hint="false"
                    aria-label="Тариф"
                  />

                  <button
                    class="apanel-icon-button"
                    type="button"
                    title="Назначить"
                    aria-label="Назначить подписку"
                    @click="assignSubscription(user)"
                  >
                    <i
                      class="fas fa-check"
                      aria-hidden="true"
                    />
                  </button>
                </template>

                <button
                  v-else
                  class="
                    apanel-icon-button
                    apanel-icon-button--danger
                  "
                  type="button"
                  title="Отозвать"
                  aria-label="Отозвать подписку"
                  @click="revokeSubscription(user)"
                >
                  <i
                    class="fas fa-ban"
                    aria-hidden="true"
                  />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <p
        v-else
        class="apanel-empty"
      >
        {{ emptyText }}
      </p>
    </div>
  </section>
</template>

<style scoped>
.apanel-card {
  position: relative;
  width: 100%;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.98),
      rgba(250, 253, 251, 0.98)
    ),
    var(--surface-primary);
  box-shadow: var(--shadow-soft);
  overflow: visible;
}

.apanel-table-wrap {
  position: relative;
  width: 100%;
  max-width: 100%;
  overflow: visible;
}

.apanel-table {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  table-layout: fixed;
  border-collapse: separate;
  border-spacing: 0;
}

/* Без управления подписками */

.apanel-table--basic .apanel-col-profile {
  width: 18%;
}

.apanel-table--basic .apanel-col-email {
  width: 30%;
}

.apanel-table--basic .apanel-col-role {
  width: 16%;
}

.apanel-table--basic .apanel-col-status {
  width: 14%;
}

.apanel-table--basic .apanel-col-beta {
  width: 8%;
}

.apanel-table--basic .apanel-col-phone {
  width: 14%;
}

/* Назначение подписки */

.apanel-table--assign .apanel-col-profile {
  width: 15%;
}

.apanel-table--assign .apanel-col-email {
  width: 22%;
}

.apanel-table--assign .apanel-col-role {
  width: 12%;
}

.apanel-table--assign .apanel-col-status {
  width: 11%;
}

.apanel-table--assign .apanel-col-beta {
  width: 7%;
}

.apanel-table--assign .apanel-col-phone {
  width: 13%;
}

.apanel-table--assign .apanel-col-actions {
  width: 20%;
}

/* Отзыв подписки */

.apanel-table--revoke .apanel-col-profile {
  width: 12%;
}

.apanel-table--revoke .apanel-col-email {
  width: 20%;
}

.apanel-table--revoke .apanel-col-role {
  width: 10%;
}

.apanel-table--revoke .apanel-col-status {
  width: 9%;
}

.apanel-table--revoke .apanel-col-beta {
  width: 6%;
}

.apanel-table--revoke .apanel-col-plan {
  width: 9%;
}

.apanel-table--revoke .apanel-col-left {
  width: 8%;
}

.apanel-table--revoke .apanel-col-phone {
  width: 14%;
}

.apanel-table--revoke .apanel-col-actions {
  width: 12%;
}

.apanel-table th,
.apanel-table td {
  box-sizing: border-box;
  min-width: 0;
  padding: 0.7rem 0.55rem;
  border-bottom: 0.0625rem solid
    var(--border-subtle);
  text-align: center;
  vertical-align: middle;
  overflow: visible;
}

.apanel-table th {
  background:
    color-mix(
      in srgb,
      var(--brand-soft) 42%,
      white
    );
  color:
    color-mix(
      in srgb,
      var(--text-muted) 86%,
      var(--brand-strong)
    );
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.045em;
  line-height: 1.2;
  text-transform: uppercase;
  white-space: nowrap;
}

.apanel-table thead th:first-child {
  border-top-left-radius: 0.95rem;
}

.apanel-table thead th:last-child {
  border-top-right-radius: 0.95rem;
}

.apanel-table td {
  height: 3.75rem;
  color: var(--text-primary);
  font-size: 0.82rem;
}

.apanel-heading-profile,
.apanel-heading-email,
.apanel-profile-cell,
.apanel-email-cell {
  text-align: left !important;
}

.apanel-table tbody tr {
  position: relative;
  transition: background 0.16s ease;
}

.apanel-table tbody tr:hover {
  background:
    color-mix(
      in srgb,
      var(--brand-soft) 34%,
      transparent
    );
}

.apanel-table tbody tr:focus-within {
  z-index: 100;
}

.apanel-table tbody tr:last-child td {
  border-bottom: 0;
}

.apanel-user-row {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  min-width: 0;
  gap: 0.5rem;
}

.apanel-avatar {
  box-sizing: border-box;
  display: grid;
  place-items: center;
  width: 2.35rem;
  min-width: 2.35rem;
  height: 2.35rem;
  flex: 0 0 2.35rem;
  overflow: hidden;
  border: 0.0625rem solid
    var(--border-subtle);
  border-radius: 0.72rem;
  background:
    color-mix(
      in srgb,
      var(--brand-soft) 70%,
      white
    );
  color: var(--brand-strong);
  font-weight: 900;
}

.apanel-avatar img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.apanel-user {
  display: grid;
  min-width: 0;
  max-width: 100%;
  gap: 0.14rem;
}

.apanel-user span,
.apanel-user small {
  display: block;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  text-align: left;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.apanel-user span {
  font-size: 0.82rem;
  font-weight: 800;
}

.apanel-user small {
  color: var(--text-muted);
  font-size: 0.7rem;
}

/* Почта полностью помещается в колонку */

.apanel-email {
  display: block;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  color: var(--text-muted);
  font-size: clamp(0.69rem, 0.78vw, 0.82rem);
  line-height: 1.25;
  text-align: left;
  overflow-wrap: anywhere;
  word-break: break-word;
  white-space: normal;
}

.apanel-cell-text {
  display: block;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  line-height: 1.25;
  text-align: center;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.apanel-phone {
  font-variant-numeric: tabular-nums;
}

.apanel-pill,
.apanel-status-pill,
.apanel-beta,
.apanel-plan {
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  min-height: 1.65rem;
  padding: 0.18rem 0.42rem;
  overflow: hidden;
  border-radius: 999rem;
  font-size: clamp(0.6rem, 0.67vw, 0.68rem);
  font-weight: 900;
  line-height: 1.1;
  text-overflow: ellipsis;
  vertical-align: middle;
  white-space: nowrap;
}

.apanel-pill,
.apanel-beta--active,
.apanel-plan--active {
  background:
    color-mix(
      in srgb,
      var(--brand-soft) 78%,
      white
    );
  color: var(--brand-strong);
}

.apanel-status-pill {
  background:
    color-mix(
      in srgb,
      var(--surface-secondary) 84%,
      var(--brand-soft)
    );
  color: var(--text-primary);
}

.apanel-beta,
.apanel-plan {
  background:
    color-mix(
      in srgb,
      #f1f5f9 78%,
      white
    );
  color: var(--text-muted);
}

/* Колонка действий */

.apanel-actions-heading,
.apanel-actions-cell {
  text-align: center !important;
}

.apanel-actions-cell {
  position: relative;
  z-index: 10;
  overflow: visible !important;
}

.apanel-actions-cell:focus-within {
  z-index: 1000;
}

.apanel-actions {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-width: 0;
  margin: 0 auto;
  gap: 0.4rem;
  overflow: visible;
}

.apanel-icon-button {
  box-sizing: border-box;
  display: inline-grid;
  place-items: center;
  width: 2.15rem;
  min-width: 2.15rem;
  max-width: 2.15rem;
  height: 2.15rem;
  min-height: 2.15rem;
  max-height: 2.15rem;
  flex: 0 0 2.15rem;
  margin: 0;
  padding: 0;
  border: 0.0625rem solid
    color-mix(
      in srgb,
      var(--brand-base) 42%,
      var(--border-subtle)
    );
  border-radius: 0.65rem;
  background:
    color-mix(
      in srgb,
      var(--brand-soft) 62%,
      white
    );
  color: var(--brand-strong);
  cursor: pointer;
  font-size: 0.95rem;
  line-height: 1;
}

.apanel-icon-button:hover {
  filter: brightness(0.98);
}

.apanel-icon-button:focus-visible {
  outline: 0.125rem solid
    color-mix(
      in srgb,
      var(--brand-base) 55%,
      transparent
    );
  outline-offset: 0.125rem;
}

.apanel-icon-button i {
  pointer-events: none;
}

.apanel-icon-button--danger {
  border-color:
    color-mix(
      in srgb,
      #dc2626 42%,
      var(--border-subtle)
    );
  background:
    color-mix(
      in srgb,
      #fee2e2 74%,
      white
    );
  color: #be123c;
}

/* Дропдаун */

.apanel-plan-dropdown {
  position: relative;
  z-index: 50;
  width: min(100%, 7.5rem);
  min-width: 0;
  overflow: visible;
}

.apanel-plan-dropdown:focus-within {
  z-index: 2000;
}

.apanel-plan-dropdown :deep(.dropdown__trigger) {
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  height: 2.15rem;
  min-height: 2.15rem;
  padding: 0.32rem 0.55rem;
  overflow: hidden;
  border-radius: 0.65rem;
}

.apanel-plan-dropdown :deep(.dropdown__label) {
  display: block;
  min-width: 0;
  overflow: hidden;
  font-size: 0.72rem;
  font-weight: 850;
  text-align: center;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.apanel-plan-dropdown :deep(.dropdown__menu) {
  z-index: 9999;
  min-width: 10rem;
  max-height: 16rem;
}

.apanel-empty {
  margin: 0;
  padding: 3rem 1.5rem;
  background:
    radial-gradient(
      circle at top,
      color-mix(
        in srgb,
        var(--brand-soft) 50%,
        transparent
      ),
      transparent 44%
    ),
    transparent;
  color: var(--text-muted);
  text-align: center;
  font-weight: 800;
}

@media (max-width: 75rem) {
  .apanel-table th,
  .apanel-table td {
    padding-inline: 0.4rem;
  }

  .apanel-table th {
    font-size: 0.62rem;
    letter-spacing: 0.025em;
  }

  .apanel-table td {
    font-size: 0.76rem;
  }

  .apanel-avatar {
    width: 2.05rem;
    min-width: 2.05rem;
    height: 2.05rem;
    flex-basis: 2.05rem;
  }

  .apanel-user-row {
    gap: 0.35rem;
  }

  .apanel-user span {
    font-size: 0.76rem;
  }

  .apanel-user small {
    font-size: 0.64rem;
  }

  .apanel-email {
    font-size: 0.69rem;
  }

  .apanel-pill,
  .apanel-status-pill,
  .apanel-beta,
  .apanel-plan {
    padding-inline: 0.32rem;
    font-size: 0.6rem;
  }
}

/*
 * На узком экране таблица сохраняет читаемые размеры.
 * Горизонтальная прокрутка включается только при нехватке места.
 */
@media (max-width: 62rem) {
  .apanel-card {
    overflow: hidden;
  }

  .apanel-table-wrap {
    overflow-x: auto;
    overflow-y: visible;
  }

  .apanel-table {
    min-width: 62rem;
  }
}
</style>