<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from '@/i18n'
import BaseDropdown from '@/components/BaseDropdown.vue'

const props = defineProps({
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
    default: '',
  },
})

const emit = defineEmits(['update-subscription'])
const { t } = useI18n()
const subscriptionDrafts = ref({})
const brokenMedia = ref(new Set())
const currentPage = ref(1)
const ITEMS_PER_PAGE = 5

const buildPaginationItems = (page, total) => {
  if (total <= 7) return Array.from({ length: total }, (_, index) => index + 1)
  if (page <= 4) return [1, 2, 3, 4, 5, 'ellipsis-right', total]
  if (page >= total - 3) return [1, 'ellipsis-left', total - 4, total - 3, total - 2, total - 1, total]
  return [1, 'ellipsis-left', page - 1, page, page + 1, 'ellipsis-right', total]
}

const totalPages = computed(() => Math.max(1, Math.ceil(props.users.length / ITEMS_PER_PAGE)))
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * ITEMS_PER_PAGE
  return props.users.slice(start, start + ITEMS_PER_PAGE)
})
const pageStart = computed(() => (props.users.length ? ((currentPage.value - 1) * ITEMS_PER_PAGE) + 1 : 0))
const pageEnd = computed(() => Math.min(currentPage.value * ITEMS_PER_PAGE, props.users.length))
const paginationItems = computed(() => buildPaginationItems(currentPage.value, totalPages.value))

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
}

watch(() => props.users, () => {
  if (currentPage.value > totalPages.value) currentPage.value = totalPages.value
})

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
  if (Number.isNaN(expiresAt.getTime())) return '-'
  const days = Math.ceil((expiresAt.getTime() - Date.now()) / (24 * 60 * 60 * 1000))
  return days > 0 ? t('aPanelUsers.daysLeft', { count: days }) : t('aPanelUsers.zeroDays')
}

const roleLabel = (value) => t(`aPanelUsers.roles.${value || 'candidate'}`)
const statusLabel = (value) => t(`aPanelUsers.statuses.${value || 'active'}`)
const subscriptionLabel = (user, activeValue) => (
  user.has_active_subscription ? activeValue : t('aPanelUsers.expired')
)

const mediaUrl = (user) => user.company_logo_url || user.avatar_url || ''
const mediaKey = (user) => `${user.id || ''}:${mediaUrl(user)}`
const hasMedia = (user) => Boolean(mediaUrl(user)) && !brokenMedia.value.has(mediaKey(user))
const markMediaBroken = (user) => {
  const next = new Set(brokenMedia.value)
  next.add(mediaKey(user))
  brokenMedia.value = next
}

const mediaInitial = (user) => {
  const source = user.company_name || user.full_name || user.email || '?'
  return source.trim().charAt(0).toUpperCase()
}

const planLabel = (value) => planOptions.find((plan) => plan.value === value)?.label || '-'

const assignSubscription = (user) => {
  emit('update-subscription', { user, plan: subscriptionDraft(user).plan })
}

const revokeSubscription = (user) => {
  emit('update-subscription', { user, revoke: true })
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
          'apanel-table--assign': manageSubscriptions && subscriptionMode === 'assign',
          'apanel-table--revoke': manageSubscriptions && subscriptionMode !== 'assign',
        }"
      >
        <colgroup>
          <col class="apanel-col-profile" />
          <col class="apanel-col-email" />
          <col class="apanel-col-role" />
          <col class="apanel-col-status" />
          <col v-if="manageSubscriptions && subscriptionMode !== 'assign'" class="apanel-col-plan" />
          <col v-if="manageSubscriptions && subscriptionMode !== 'assign'" class="apanel-col-left" />
          <col class="apanel-col-phone" />
          <col v-if="manageSubscriptions" class="apanel-col-actions" />
        </colgroup>

        <thead>
          <tr>
            <th class="apanel-heading-profile">{{ t('aPanelUsers.profileColumn') }}</th>
            <th class="apanel-heading-email">{{ t('aPanelUsers.emailColumn') }}</th>
            <th>{{ t('aPanelUsers.roleColumn') }}</th>
            <th>{{ t('aPanelUsers.statusColumn') }}</th>
            <th v-if="manageSubscriptions && subscriptionMode !== 'assign'">{{ t('aPanelUsers.planColumn') }}</th>
            <th v-if="manageSubscriptions && subscriptionMode !== 'assign'">{{ t('aPanelUsers.leftColumn') }}</th>
            <th>{{ t('aPanelUsers.phoneColumn') }}</th>
            <th v-if="manageSubscriptions" class="apanel-actions-heading">{{ t('aPanelUsers.actionsColumn') }}</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="user in paginatedUsers" :key="user.id">
            <td class="apanel-profile-cell" :data-label="t('aPanelUsers.profileColumn')">
              <div class="apanel-user-row">
                <div class="apanel-avatar">
                  <img
                    v-if="hasMedia(user)"
                    :src="mediaUrl(user)"
                    :alt="user.company_name || user.full_name || user.email"
                    @error="markMediaBroken(user)"
                  />
                  <span v-else>{{ mediaInitial(user) }}</span>
                </div>

                <div class="apanel-user">
                  <span :title="user.company_name || user.full_name || '-'">
                    {{ user.company_name || user.full_name || '-' }}
                  </span>
                  <small>
                    {{ user.account_type === 'employer' ? t('aPanelUsers.companyLabel') : t('aPanelUsers.profileLabel') }}
                  </small>
                </div>
              </div>
            </td>

            <td class="apanel-email-cell" :data-label="t('aPanelUsers.emailColumn')">
              <span class="apanel-email" :title="user.email || '-'">{{ user.email || '-' }}</span>
            </td>

            <td :data-label="t('aPanelUsers.roleColumn')">
              <span class="apanel-pill" :title="roleLabel(user.account_type)">
                {{ roleLabel(user.account_type) }}
              </span>
            </td>

            <td :data-label="t('aPanelUsers.statusColumn')">
              <span
                class="apanel-status-pill"
                :class="[
                  `apanel-status-pill--${user.status || 'active'}`,
                  user.status === 'active' || !user.status ? 'active-radius' : 'inactive-radius',
                ]"
                :title="statusLabel(user.status)"
              >
                {{ statusLabel(user.status) }}
              </span>
            </td>

            <td v-if="manageSubscriptions && subscriptionMode !== 'assign'" :data-label="t('aPanelUsers.planColumn')">
              <span
                class="apanel-plan"
                :class="{
                  'apanel-plan--active active-radius': user.has_active_subscription,
                  'apanel-subscription--expired inactive-radius': !user.has_active_subscription,
                }"
                :title="subscriptionLabel(user, planLabel(user.subscription_plan))"
              >
                {{ subscriptionLabel(user, planLabel(user.subscription_plan)) }}
              </span>
            </td>

            <td v-if="manageSubscriptions && subscriptionMode !== 'assign'" :data-label="t('aPanelUsers.leftColumn')">
              <span
                class="apanel-cell-text"
                :class="{ 'apanel-days-zero': !user.has_active_subscription }"
              >
                {{ user.has_active_subscription ? daysLeft(user.subscription_expires_at) : t('aPanelUsers.zeroDays') }}
              </span>
            </td>

            <td :data-label="t('aPanelUsers.phoneColumn')">
              <span class="apanel-cell-text apanel-phone" :title="user.phone || '-'">{{ user.phone || '-' }}</span>
            </td>

            <td v-if="manageSubscriptions" class="apanel-actions-cell" :data-label="t('aPanelUsers.actionsColumn')">
              <div class="apanel-actions">
                <template v-if="subscriptionMode === 'assign' || (subscriptionMode === 'manage' && !user.has_active_subscription)">
                  <BaseDropdown
                    v-model="subscriptionDraft(user).plan"
                    class="apanel-plan-dropdown"
                    :options="planOptions"
                    size="sm"
                    align="right"
                    overlay
                    menu-class="apanel-plan-menu"
                    :show-selected-hint="false"
                    :aria-label="t('aPanelUsers.subscriptionAria')"
                  />

                  <button
                    class="apanel-icon-button"
                    type="button"
                    :title="t('aPanelUsers.assignTitle')"
                    :aria-label="t('aPanelUsers.assignAria')"
                    @click="assignSubscription(user)"
                  >
                    <i class="fas fa-check" aria-hidden="true" />
                  </button>
                </template>

                <button
                  v-else
                  class="apanel-icon-button apanel-icon-button--danger"
                  type="button"
                  :title="t('aPanelUsers.revokeTitle')"
                  :aria-label="t('aPanelUsers.revokeAria')"
                  @click="revokeSubscription(user)"
                >
                  <i class="fas fa-undo" aria-hidden="true" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else class="apanel-empty">{{ emptyText || t('aPanelUsers.emptyText') }}</p>
    </div>

    <nav v-if="users.length" class="jobs-pagination" :aria-label="t('jobsPage.pagination')">
      <div class="jobs-pagination__summary">
        {{ t('jobsPage.paginationSummary', { start: pageStart, end: pageEnd, total: users.length }) }}
      </div>
      <div class="jobs-pagination__controls">
        <button type="button" class="pagination-button pagination-button--ghost" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
          <i class="fas fa-arrow-left"></i>
          <span>{{ t('jobsPage.previousPage') }}</span>
        </button>
        <div class="pagination-numbers">
          <template v-for="item in paginationItems" :key="item">
            <span v-if="String(item).startsWith('ellipsis')" class="pagination-ellipsis">•••</span>
            <button v-else type="button" class="pagination-button pagination-button--number" :class="{ 'pagination-button--active': currentPage === item }" @click="goToPage(item)">
              {{ item }}
            </button>
          </template>
        </div>
        <button type="button" class="pagination-button" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
          <span>{{ t('jobsPage.nextPage') }}</span>
          <i class="fas fa-arrow-right"></i>
        </button>
      </div>
    </nav>
  </section>
</template>

<style scoped>
.apanel-card {
  position: relative;
  z-index: 5;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(250, 253, 251, 0.98)),
    var(--surface-primary);
  box-shadow: var(--shadow-soft);
  overflow: visible;
}

.apanel-table-wrap {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  overflow-y: visible;
}

.apanel-table {
  width: 100%;
  min-width: 68rem;
  border-collapse: separate;
  border-spacing: 0;
}

.apanel-table th,
.apanel-table td {
  padding: 0.85rem 0.8rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
  vertical-align: middle;
  text-align: left;
  color: var(--text-primary);
}

.apanel-table th {
  background: color-mix(in srgb, var(--brand-soft) 42%, white);
  color: color-mix(in srgb, var(--text-muted) 86%, var(--brand-strong));
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.apanel-table tbody tr:last-child td {
  border-bottom: 0;
}


.apanel-user-row {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.apanel-avatar {
  width: 2.8rem;
  height: 2.8rem;
  border-radius: 0.85rem;
  overflow: hidden;
  background: color-mix(in srgb, var(--brand-soft) 60%, white);
  display: grid;
  place-items: center;
  color: var(--brand-strong);
  font-weight: 800;
}

.apanel-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.apanel-user {
  display: grid;
  gap: 0.2rem;
  min-width: 0;
}

.apanel-user span,
.apanel-email,
.apanel-phone {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.apanel-user small,
.apanel-cell-text {
  color: var(--text-muted);
}

.apanel-pill,
.apanel-status-pill,
.apanel-plan {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2rem;
  padding: 0.35rem 0.65rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.06);
  font-size: 0.76rem;
  font-weight: 800;
}

.apanel-pill,
.apanel-status-pill {
  min-width: 5.75rem;
}

.apanel-status-pill--active,
.apanel-plan--active {
  background: color-mix(in srgb, var(--brand-soft) 72%, white);
  color: var(--brand-strong);
}

.apanel-subscription--expired {
  color: #dc2626;
  font-weight: 800;
}

.apanel-cell-text.apanel-days-zero {
  color: var(--text-primary);
  font-weight: 700;
}

.apanel-status-pill--inactive {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.apanel-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 20;
  justify-content: center;
}

.apanel-icon-button {
  width: 2.35rem;
  height: 2.35rem;
  border: 0;
  border-radius: 0.72rem;
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
  box-shadow: 0 0.625rem 1.2rem rgba(21, 149, 93, 0.18);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.apanel-icon-button:hover {
  transform: translateY(-0.0625rem);
  filter: brightness(1.03);
}

.apanel-icon-button:focus-visible {
  outline: 0.1875rem solid rgba(21, 149, 93, 0.18);
  outline-offset: 0.125rem;
}

.apanel-icon-button:active {
  transform: translateY(0);
}

.apanel-icon-button--danger {
  background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
  box-shadow: 0 0.625rem 1.2rem rgba(220, 38, 38, 0.18);
}

.apanel-icon-button--danger:focus-visible {
  outline-color: rgba(220, 38, 38, 0.2);
}

.apanel-plan-dropdown {
  width: 9.4rem;
  min-width: 9.4rem;
}

.apanel-plan-dropdown:deep(.dropdown__trigger) {
  min-height: 2.35rem;
  padding: 0.38rem 0.7rem;
  border-radius: 0.72rem;
  border-color: color-mix(in srgb, var(--brand-base) 28%, var(--border-subtle));
  background: color-mix(in srgb, var(--brand-soft) 72%, white);
  color: var(--brand-strong);
  box-shadow: inset 0 0 0 0.0625rem rgba(21, 149, 93, 0.12);
}

.apanel-plan-dropdown:deep(.dropdown__content) {
  gap: 0;
}

.apanel-plan-dropdown:deep(.dropdown__label),
.apanel-plan-dropdown:deep(.dropdown__option-label),
.apanel-plan-dropdown:deep(.dropdown__chevron),
.apanel-plan-dropdown:deep(.dropdown__option-check) {
  color: var(--brand-strong);
}

.apanel-plan-dropdown:deep(.dropdown__label) {
  font-size: 0.88rem;
  font-weight: 700;
}

.apanel-plan-dropdown:deep(.dropdown__chevron) {
  font-size: 0.82rem;
}

:global(.apanel-plan-menu .dropdown__option-label) {
  font-size: 0.88rem;
}

.apanel-empty {
  margin: 0;
  padding: 1rem 1.1rem;
  color: var(--text-muted);
}

.jobs-pagination {
  display: grid;
  gap: 0.95rem;
  padding: 1rem;
  border-top: 0.0625rem solid var(--border-subtle);
}

.jobs-pagination__summary {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.jobs-pagination__controls,
.pagination-numbers {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.jobs-pagination__controls {
  justify-content: space-between;
}

.pagination-button {
  min-height: 2.85rem;
  padding: 0.72rem 1rem;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 18%, var(--border-subtle));
  border-radius: 999rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(241, 249, 245, 0.98));
  color: var(--text-primary);
  font: inherit;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  cursor: pointer;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-button--ghost {
  background: var(--surface-secondary);
}

.pagination-button--number {
  min-width: 2.85rem;
  padding-inline: 0.75rem;
}

.pagination-button--active {
  border-color: color-mix(in srgb, var(--brand-base) 60%, white);
  background: linear-gradient(135deg, color-mix(in srgb, var(--brand-base) 95%, white), color-mix(in srgb, var(--brand-strong) 90%, white));
  color: #fff;
}

.pagination-ellipsis {
  color: var(--text-muted);
  font-weight: 800;
  letter-spacing: 0.12em;
}

@container (max-width: 67.999rem) {
  .apanel-card {
    display: none;
  }
}

</style>
