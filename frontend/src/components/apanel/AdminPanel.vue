<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/i18n'
import AppLayout from '@/components/AppLayout.vue'
import DashboardShell from '@/components/dashboard/DashboardShell.vue'
import APanelJobs from './APanelJobs.vue'
import APanelSettings from './APanelSettings.vue'
import APanelUsers from './APanelUsers.vue'
import { useAuth } from '@/stores/auth'
import {
  approveAdminJob,
  createAdminBetaToken,
  deleteAdminBetaToken,
  deleteAdminJob,
  getAdminBetaSettings,
  getAdminBetaTokens,
  getAdminJobs,
  getAdminModerationJobs,
  getAdminSummary,
  getAdminUsers,
  rejectAdminJob,
  updateAdminBetaSettings,
  updateAdminUserSubscription,
} from './api'
import { localizeFullPath } from '@/router/locale'

const route = useRoute()
const router = useRouter()
const { language, t } = useI18n()
const auth = useAuth()

const sections = computed(() => [
  { id: 'users', label: t('adminPanel.sections.users'), icon: 'fas fa-users' },
  { id: 'employers', label: t('adminPanel.sections.employers'), icon: 'fas fa-building' },
  { id: 'moderation', label: t('adminPanel.sections.moderation'), icon: 'fas fa-shield-halved' },
  { id: 'vacancies', label: t('adminPanel.sections.vacancies'), icon: 'fas fa-briefcase' },
  { id: 'settings', label: t('adminPanel.sections.settings'), icon: 'fas fa-gear' },
  { id: 'logout', label: t('common.logout'), icon: 'fas fa-right-from-bracket', danger: true },
])

const validSections = computed(() => sections.value.map((section) => section.id))
const normalizeSection = (value) => (validSections.value.includes(value) ? value : 'users')

const activeSection = ref(normalizeSection(route.query.section))
const summary = ref(null)
const users = ref([])
const employers = ref([])
const jobs = ref([])
const moderationJobs = ref([])
const tokens = ref([])
const betaAccessEnabled = ref(false)
const isLoading = ref(false)
const isRefreshing = ref(false)
const isSaving = ref(false)
const isSavingSettings = ref(false)
const error = ref('')
const adminRefreshTimer = ref(null)

const stats = computed(() => [
  { label: t('adminPanel.stats.totalUsers'), value: summary.value?.total_users ?? users.value.length + employers.value.length, section: 'users' },
  { label: t('adminPanel.stats.activeEmployers'), value: summary.value?.employers ?? employers.value.length, section: 'employers' },
  { label: t('adminPanel.stats.pendingVacancies'), value: summary.value?.pending_vacancies ?? moderationJobs.value.length, section: 'moderation' },
  { label: t('adminPanel.stats.totalVacancies'), value: summary.value?.vacancies ?? jobs.value.length, section: 'vacancies' },
])

const activeTitle = computed(() => sections.value.find((section) => section.id === activeSection.value)?.label || t('adminPanel.fallbackTitle'))

const setSection = async (sectionId) => {
  if (sectionId === 'logout') {
    auth.logout()
    await router.replace(localizeFullPath('/', language.value))
    return
  }

  activeSection.value = normalizeSection(sectionId)
  await router.replace({
    path: route.path,
    query: { section: activeSection.value },
  })
}

const loadAdminData = async ({ silent = false } = {}) => {
  if (silent) {
    if (isRefreshing.value) return
    isRefreshing.value = true
  } else {
    isLoading.value = true
    error.value = ''
  }

  try {
    const [summaryData, userData, employerData, jobsData, moderationData, tokenData, betaSettingsData] = await Promise.all([
      getAdminSummary(),
      getAdminUsers('candidate'),
      getAdminUsers('employer'),
      getAdminJobs(),
      getAdminModerationJobs(),
      getAdminBetaTokens(),
      getAdminBetaSettings(),
    ])

    summary.value = summaryData
    users.value = Array.isArray(userData) ? userData : []
    employers.value = Array.isArray(employerData) ? employerData : []
    jobs.value = Array.isArray(jobsData) ? jobsData : []
    moderationJobs.value = Array.isArray(moderationData) ? moderationData : []
    if (!moderationJobs.value.length && Array.isArray(jobsData)) {
      moderationJobs.value = jobsData.filter((job) => job?.status === 'pending')
    }
    tokens.value = Array.isArray(tokenData) ? tokenData : []
    betaAccessEnabled.value = Boolean(betaSettingsData?.enabled)
  } catch (caughtError) {
    if (caughtError?.status === 401) {
      stopAdminRealtime()
      auth.resetState()
      return
    }

    if (!silent) error.value = t('adminPanel.loadError')
  } finally {
    if (silent) {
      isRefreshing.value = false
    } else {
      isLoading.value = false
    }
  }
}

const refreshAdminDataSilently = () => {
  if (isSaving.value || isSavingSettings.value) return
  loadAdminData({ silent: true })
}

const startAdminRealtime = () => {
  if (adminRefreshTimer.value) return
  adminRefreshTimer.value = window.setInterval(refreshAdminDataSilently, 5000)
}

const stopAdminRealtime = () => {
  if (!adminRefreshTimer.value) return
  window.clearInterval(adminRefreshTimer.value)
  adminRefreshTimer.value = null
}

const createToken = async ({ email }) => {
  isSaving.value = true
  error.value = ''

  try {
    await createAdminBetaToken({ email })
    await loadAdminData()
  } catch {
    error.value = t('adminPanel.createTokenError')
  } finally {
    isSaving.value = false
  }
}

const deleteToken = async (token) => {
  error.value = ''

  try {
    await deleteAdminBetaToken(token.id)
    await loadAdminData()
  } catch {
    error.value = t('adminPanel.deleteTokenError')
  }
}

const updateBetaAccess = async (enabled) => {
  isSavingSettings.value = true
  error.value = ''

  try {
    const settings = await updateAdminBetaSettings({ enabled })
    betaAccessEnabled.value = Boolean(settings?.enabled)
  } catch {
    error.value = t('adminPanel.updateBetaError')
  } finally {
    isSavingSettings.value = false
  }
}

const updateUserSubscription = async ({ user, plan, revoke = false }) => {
  error.value = ''

  try {
    await updateAdminUserSubscription(user.id, revoke ? { revoke: true } : { plan })
    await loadAdminData()
  } catch {
    error.value = t('adminPanel.updateSubscriptionError')
  }
}

const approveJob = async (job) => {
  error.value = ''

  try {
    await approveAdminJob(job.id)
    await loadAdminData()
  } catch {
    error.value = t('adminPanel.approveError')
  }
}

const rejectJob = async ({ job, reason }) => {
  error.value = ''

  try {
    await rejectAdminJob(job.id, reason)
    await loadAdminData()
  } catch {
    error.value = t('adminPanel.rejectError')
  }
}

const deleteJob = async (job) => {
  error.value = ''

  try {
    await deleteAdminJob(job.id)
    await loadAdminData()
  } catch {
    error.value = t('adminPanel.deleteError')
  }
}

watch(
  () => route.query.section,
  (section) => {
    activeSection.value = normalizeSection(typeof section === 'string' ? section : 'users')
  },
)

onMounted(async () => {
  await loadAdminData()
  startAdminRealtime()
})

onBeforeUnmount(stopAdminRealtime)
</script>

<template>
  <AppLayout>
    <DashboardShell
      :sections="sections"
      :active-section="activeSection"
      :eyebrow="t('adminPanel.eyebrow')"
      :title="activeTitle"
      :description="t('adminPanel.description')"
      :stats="stats"
      @select-section="setSection"
      @stat-click="setSection"
    >
      <p v-if="error" class="apanel-status apanel-status--danger">{{ error }}</p>
      <p v-if="isLoading" class="apanel-state">{{ t('adminPanel.loading') }}</p>

      <template v-else>
        <APanelUsers
          v-if="activeSection === 'users'"
          :users="users"
          :empty-text="t('adminPanel.emptyUsers')"
        />

        <APanelUsers
          v-else-if="activeSection === 'employers'"
          :users="employers"
          manage-subscriptions
          subscription-mode="manage"
          :empty-text="t('adminPanel.emptyEmployers')"
          @update-subscription="updateUserSubscription"
        />

        <APanelJobs
          v-else-if="activeSection === 'vacancies'"
          :jobs="jobs"
          :empty-text="t('adminPanel.emptyJobs')"
          @delete="deleteJob"
        />

        <APanelJobs
          v-else-if="activeSection === 'moderation'"
          :jobs="moderationJobs"
          moderation
          :empty-text="t('adminPanel.emptyModeration')"
          @approve="approveJob"
          @reject="rejectJob"
          @delete="deleteJob"
        />

        <APanelSettings
          v-else
          :tokens="tokens"
          :beta-access-enabled="betaAccessEnabled"
          :is-saving="isSaving"
          :is-saving-settings="isSavingSettings"
          @create-token="createToken"
          @delete-token="deleteToken"
          @update-beta-access="updateBetaAccess"
        />
      </template>
    </DashboardShell>
  </AppLayout>
</template>

<style scoped>
.apanel-status,
.apanel-state {
  margin: 0;
  padding: 0.85rem 1rem;
  border-radius: 0.8rem;
  font-weight: 700;
}

.apanel-status--success {
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
}

.apanel-status--danger {
  background: #fff1f2;
  color: #be123c;
}

.apanel-state {
  background: var(--surface-primary);
  color: var(--text-muted);
  border: 0.0625rem solid var(--border-subtle);
}
</style>
