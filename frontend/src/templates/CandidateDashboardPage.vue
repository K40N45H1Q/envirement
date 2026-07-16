<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import DashboardShell from '@/components/dashboard/DashboardShell.vue'
import MessagesPanel from '@/components/messages/MessagesPanel.vue'
import Profile from '@/components/Profile.vue'
import { deleteAccount as deleteAccountRequest } from '@/api/auth'
import { getJobs, getMyApplications } from '@/api/jobs'
import { getProfile } from '@/api/profile'
import { translate, useI18n } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useMessagingStore } from '@/stores/messaging'
import { localizeJobTitle, normalizeJob } from '@/utils/jobs'
import { localizeFullPath } from '@/router/locale'

const route = useRoute()
const router = useRouter()
const auth = useAuth()
const { state } = auth
const messaging = useMessagingStore()
const { language, t } = useI18n()

const copy = computed(() => translate('candidateDashboardPage', {}, language.value))
const interpolate = (template, params = {}) => String(template).replace(/\{(\w+)\}/g, (_, key) => String(params[key] ?? ''))
const displayJobTitle = (job) => localizeJobTitle(job, language.value)

const jobs = ref([])
const applications = ref([])
const profile = ref(null)
const isLoading = ref(false)
const isRefreshingApplications = ref(false)
const notice = ref('')
const showDeleteAccountConfirm = ref(false)
const isDeletingAccount = ref(false)
const deleteAccountError = ref('')
const applicationsRefreshTimer = ref(null)
const validSectionIds = ['dashboard', 'messages', 'profile', 'settings']
const normalizeSection = (section) => (validSectionIds.includes(section) ? section : 'profile')
const activeSection = ref(normalizeSection(typeof route.query.section === 'string' ? route.query.section : 'profile'))

const shellSections = computed(() => ([
  { id: 'messages', label: copy.value.sections.messages, icon: 'fas fa-message', to: '/dashboard?section=messages' },
  { id: 'profile', label: copy.value.sections.profile, icon: 'fas fa-user', to: '/dashboard?section=profile' },
  { id: 'settings', label: copy.value.sections.settings, icon: 'fas fa-gear', to: '/dashboard?section=settings' },
  { id: 'logout', label: t('common.logout'), icon: 'fas fa-right-from-bracket', danger: true },
]))

const normalizeAccountType = (accountType) => {
  if (accountType === 'user') return 'candidate'
  return accountType || ''
}

const currentAccountType = computed(() => normalizeAccountType(state.user?.account_type))
const isCandidateAccount = computed(() => currentAccountType.value === 'candidate')
const conversations = computed(() => messaging.conversations)

const userName = computed(() => {
  const profileName = [profile.value?.first_name, profile.value?.last_name].filter(Boolean).join(' ').trim()
  if (profileName) return profileName
  return state.user?.email?.split('@')[0] || copy.value.fallbackCandidate
})

const appliedJobIds = computed(() => new Set(applications.value.map((item) => item.job_id)))
const availableJobs = computed(() => jobs.value.filter((job) => !appliedJobIds.value.has(job.id)))
const recommendedJobs = computed(() => availableJobs.value.slice(0, 3))

const profileScore = computed(() => {
  const resume = profile.value?.resume_data || {}
  const workExperience = resume.work_experiences?.[0] || {}
  const education = resume.educations?.[0] || {}
  const fields = [
    resume.cv_language,
    state.user?.email,
    profile.value?.first_name,
    profile.value?.last_name,
    profile.value?.phone,
    resume.birth_date,
    resume.gender,
    workExperience.position,
    workExperience.company_name,
    education.level,
    education.institution,
  ]

  return Math.round((fields.filter(Boolean).length / fields.length) * 100)
})

const shellStats = computed(() => ([
  { value: `${profileScore.value}%`, label: copy.value.stats.profile },
  { value: applications.value.length, label: copy.value.stats.applications },
  { value: conversations.value.length, label: copy.value.stats.conversations },
  { value: availableJobs.value.length, label: copy.value.stats.recommendations },
]))

const dashboardTitle = computed(() => (
  activeSection.value === 'messages'
    ? copy.value.titleMessages
    : activeSection.value === 'profile'
      ? copy.value.sections.profile
      : activeSection.value === 'settings'
        ? copy.value.settingsTitle
        : interpolate(copy.value.titleGreeting, { name: userName.value })
))

const getSettledValue = (result, fallback) => (result.status === 'fulfilled' ? result.value : fallback)

const setSection = async (sectionId) => {
  if (sectionId === 'logout') {
    auth.logout()
    await router.replace(localizeFullPath('/', language.value))
    return
  }

  activeSection.value = sectionId
  await router.replace({
    path: '/dashboard',
    query: { section: sectionId },
  })
}

const deleteAccount = async () => {
  if (isDeletingAccount.value) return

  isDeletingAccount.value = true
  deleteAccountError.value = ''

  try {
    await deleteAccountRequest()
    auth.logout()
    await router.replace(localizeFullPath('/', language.value))
  } catch {
    deleteAccountError.value = copy.value.deleteAccountError
  } finally {
    isDeletingAccount.value = false
  }
}

const openDashboardConversation = async (applicationId) => {
  await router.replace({
    path: '/dashboard',
    query: { section: 'messages', application: String(applicationId) },
  })
}

const loadRecommendations = async () => {
  isLoading.value = true
  notice.value = ''

  try {
    const [jobsResult, applicationsResult, profileResult] = await Promise.allSettled([
      getJobs(),
      isCandidateAccount.value ? getMyApplications() : Promise.resolve([]),
      isCandidateAccount.value ? getProfile() : Promise.resolve(null),
    ])

    const jobsData = getSettledValue(jobsResult, [])
    const applicationsData = getSettledValue(applicationsResult, [])
    const profileData = getSettledValue(profileResult, null)

    jobs.value = Array.isArray(jobsData) ? jobsData.map(normalizeJob) : []
    applications.value = Array.isArray(applicationsData) ? applicationsData : []
    profile.value = profileData && typeof profileData === 'object' ? profileData : null

    if (isCandidateAccount.value) {
      await messaging.loadConversations(route.query.application, { silent: true })
    }

    const hasCandidateDataError = isCandidateAccount.value && (
      applicationsResult.status === 'rejected' || profileResult.status === 'rejected'
    )

    if (!isCandidateAccount.value && state.user) {
      notice.value = copy.value.onlyCandidate
      return
    }

    if (jobsResult.status === 'rejected') {
      notice.value = copy.value.loadJobsError
      return
    }

    if (hasCandidateDataError) {
      notice.value = copy.value.loadCandidateDataError
      return
    }

    if (!jobs.value.length && activeSection.value === 'dashboard') {
      notice.value = copy.value.noPublishedJobs
    }
  } catch {
    jobs.value = []
    applications.value = []
    profile.value = null
    notice.value = copy.value.loadDashboardError
  } finally {
    isLoading.value = false
  }
}

const refreshApplicationsSilently = async () => {
  if (!isCandidateAccount.value || isRefreshingApplications.value) return

  isRefreshingApplications.value = true

  try {
    const applicationsData = await getMyApplications()
    applications.value = Array.isArray(applicationsData) ? applicationsData : []
  } finally {
    isRefreshingApplications.value = false
  }
}

const startApplicationsRealtime = () => {
  if (applicationsRefreshTimer.value || !isCandidateAccount.value) return

  applicationsRefreshTimer.value = window.setInterval(() => {
    refreshApplicationsSilently()
  }, 5000)
}

const stopApplicationsRealtime = () => {
  if (!applicationsRefreshTimer.value) return
  window.clearInterval(applicationsRefreshTimer.value)
  applicationsRefreshTimer.value = null
}

watch(() => route.query.section, (section) => {
  activeSection.value = normalizeSection(typeof section === 'string' ? section : 'profile')
})

watch(() => route.query.application, async (application) => {
  if (activeSection.value !== 'messages') return

  const applicationId = Number(application)
  if (!applicationId || applicationId === messaging.activeApplicationId) return

  const exists = messaging.conversations.some((item) => item.application_id === applicationId)
  if (exists) {
    await messaging.openConversation(applicationId)
  }
})

onMounted(async () => {
  await loadRecommendations()
  startApplicationsRealtime()
  messaging.startRealtime()
})

onBeforeUnmount(() => {
  stopApplicationsRealtime()
  messaging.stopRealtime()
})
</script>

<template>
  <AppLayout>
    <DashboardShell
      class="candidate-dashboard-shell"
      :sections="shellSections"
      :active-section="activeSection"
      :eyebrow="copy.eyebrow"
      :title="dashboardTitle"
      :description="copy.description"
      :stats="shellStats"
      @select-section="setSection"
    >
      <template #actions>
        <RouterLink v-if="activeSection === 'dashboard'" to="/jobs" class="btn-primary">
          <i class="fas fa-magnifying-glass"></i>
          {{ copy.findJob }}
        </RouterLink>
      </template>

      <section v-if="activeSection === 'dashboard'" class="workspace">
        <div class="panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow compact">{{ copy.recommendationsEyebrow }}</p>
              <h2>{{ copy.recommendationsTitle }}</h2>
            </div>

            <button class="icon-button" type="button" :aria-label="copy.refresh" @click="loadRecommendations">
              <i class="fas fa-rotate-right"></i>
            </button>
          </div>

          <div v-if="recommendedJobs.length" class="jobs-list">
            <RouterLink
              v-for="job in recommendedJobs"
              :key="job.id"
              :to="`/jobs/${job.id}`"
              class="job-row"
            >
              <div class="job-logo" :style="{ background: job.color }">
                <img v-if="job.logo" :src="job.logo" :alt="job.company">
                <span v-else>{{ job.initials }}</span>
              </div>

              <div class="job-info">
                <h3>{{ displayJobTitle(job) }}</h3>
                <p>{{ job.company }} · {{ job.displayLocation || job.location }}</p>
                <strong>{{ job.salary }}</strong>
              </div>

              <span class="job-action">{{ copy.apply }}</span>
            </RouterLink>
          </div>

          <p v-else class="notice">{{ copy.noRecommendations }}</p>
        </div>

        <div class="panel panel-activity">
          <div class="panel-header">
            <div>
              <p class="eyebrow compact">{{ copy.activityEyebrow }}</p>
              <h2>{{ copy.activityTitle }}</h2>
            </div>
          </div>

          <div class="activity-list">
            <button
              v-for="application in applications.slice(0, 3)"
              :key="application.id"
              type="button"
              class="activity-item"
              @click="application.chat_approved ? openDashboardConversation(application.id) : router.push('/jobs')"
            >
              <i class="fas fa-message"></i>

              <div class="activity-info">
                <span class="activity-title">{{ displayJobTitle(application) }}</span>
                <span class="activity-company">
                  {{ application.job_company }}{{ application.chat_approved ? '' : ` · ${copy.chatPending}` }}
                </span>
              </div>
              <strong v-if="application.match_score != null" class="activity-score">{{ application.match_score }}/100</strong>
            </button>

            <RouterLink v-if="!applications.length" to="/dashboard?section=profile" class="activity-item empty">
              <i class="fas fa-user-pen"></i>
              <span>{{ copy.completeProfile }}</span>
            </RouterLink>
          </div>
        </div>
      </section>

      <section v-else-if="activeSection === 'profile'" class="message-shell">
        <Profile embedded />
      </section>

      <section v-else-if="activeSection === 'settings'" class="message-shell">
        <article class="panel settings-panel">
          <div class="settings-panel__heading">
            <span class="settings-panel__icon" aria-hidden="true">
              <i class="fas fa-gear"></i>
            </span>
            <div>
              <h2>{{ copy.settingsTitle }}</h2>
              <p>{{ copy.settingsDescription }}</p>
            </div>
          </div>

          <div class="settings-panel__row">
            <span>{{ copy.accountEmail }}</span>
            <strong>{{ state.user?.email }}</strong>
          </div>

          <section class="settings-danger-zone">
            <div class="settings-danger-zone__copy">
              <h3>{{ copy.deleteAccountTitle }}</h3>
              <p>{{ copy.deleteAccountDescription }}</p>
            </div>

            <button
              v-if="!showDeleteAccountConfirm"
              type="button"
              class="delete-account-button"
              @click="showDeleteAccountConfirm = true; deleteAccountError = ''"
            >
              <i class="fas fa-user-xmark"></i>
              {{ copy.deleteAccount }}
            </button>

            <div v-else class="delete-account-confirmation">
              <strong>{{ copy.deleteAccountConfirm }}</strong>
              <p>{{ copy.deleteAccountWarning }}</p>

              <p v-if="deleteAccountError" class="delete-account-error" role="alert">
                {{ deleteAccountError }}
              </p>

              <div class="delete-account-confirmation__actions">
                <button
                  type="button"
                  class="cancel-delete-button"
                  :disabled="isDeletingAccount"
                  @click="showDeleteAccountConfirm = false; deleteAccountError = ''"
                >
                  {{ copy.cancel }}
                </button>
                <button
                  type="button"
                  class="confirm-delete-button"
                  :disabled="isDeletingAccount"
                  @click="deleteAccount"
                >
                  <i :class="isDeletingAccount ? 'fas fa-spinner fa-spin' : 'fas fa-trash-can'"></i>
                  {{ isDeletingAccount ? copy.deletingAccount : copy.deletePermanently }}
                </button>
              </div>
            </div>
          </section>
        </article>
      </section>

      <section v-else class="message-shell">
        <MessagesPanel embedded :hint="copy.messagesHint" @open="openDashboardConversation" />
      </section>
    </DashboardShell>
  </AppLayout>
</template>

<style scoped>
.workspace,
.panel,
.btn-primary {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 22rem;
  gap: 1.5rem;
  align-items: stretch;
  background-color: transparent;
  border: none;
  box-shadow: none;
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.5rem;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 92%, transparent), var(--surface-primary)),
    var(--surface-primary);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.eyebrow {
  margin: 0 0 0.45rem;
  color: var(--brand-strong);
  font-weight: 700;
  text-transform: uppercase;
}

.compact {
  font-size: 0.76rem;
}

h2,
h3,
p {
  margin: 0;
}

h2 {
  font-size: 1.35rem;
  font-weight: 700;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 3rem;
  padding: 0.75rem 1.15rem;
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
  font-weight: 800;
  text-decoration: none;
}

.icon-button {
  width: 2.5rem;
  height: 2.5rem;
  display: grid;
  place-items: center;
  border: 0.0625rem solid var(--border-strong);
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 70%, transparent);
  color: var(--brand-strong);
  cursor: pointer;
}

.notice,
.state {
  padding: 0.95rem 1rem;
  border: 0.0625rem solid var(--border-strong);
  border-radius: 0.875rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
}

.jobs-list,
.activity-list,
.message-shell {
  display: grid;
  gap: 0.85rem;
}

.settings-panel {
  display: grid;
  gap: 1.25rem;
  padding: clamp(1.1rem, 2.5vw, 1.5rem);
}

.settings-panel__heading {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.settings-panel__heading h2,
.settings-panel__heading p {
  margin: 0;
}

.settings-panel__heading p {
  margin-top: 0.25rem;
  color: var(--text-muted);
}

.settings-panel__icon {
  width: 2.75rem;
  height: 2.75rem;
  flex: 0 0 2.75rem;
  display: grid;
  place-items: center;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 28%, transparent);
  border-radius: 50%;
  background: color-mix(in srgb, var(--brand-base) 10%, transparent);
  color: var(--brand-strong);
}

.settings-panel__row {
  display: grid;
  gap: 0.3rem;
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: var(--surface-muted);
}

.settings-panel__row span {
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 700;
}

.settings-danger-zone {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 0.0625rem solid color-mix(in srgb, #dc2626 28%, transparent);
  border-radius: 0.875rem;
  background: color-mix(in srgb, #dc2626 5%, var(--surface-primary));
}

.settings-danger-zone__copy h3,
.settings-danger-zone__copy p,
.delete-account-confirmation p {
  margin: 0;
}

.settings-danger-zone__copy h3 {
  color: #b91c1c;
  font-size: 1rem;
}

.settings-danger-zone__copy p,
.delete-account-confirmation p {
  margin-top: 0.3rem;
  color: var(--text-muted);
  line-height: 1.45;
}

.delete-account-button,
.confirm-delete-button,
.cancel-delete-button {
  min-height: 3rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.7rem 1rem;
  border-radius: 0.875rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.delete-account-button,
.confirm-delete-button {
  border: 0.0625rem solid #dc2626;
  background: #dc2626;
  color: #fff;
}

.delete-account-button:hover,
.delete-account-button:focus-visible,
.confirm-delete-button:hover,
.confirm-delete-button:focus-visible {
  background: #b91c1c;
}

.delete-account-confirmation {
  grid-column: 1 / -1;
  display: grid;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 0.0625rem solid color-mix(in srgb, #dc2626 22%, transparent);
}

.delete-account-confirmation__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.65rem;
}

.cancel-delete-button {
  border: 0.0625rem solid var(--border-subtle);
  background: var(--surface-primary);
  color: var(--text-primary);
}

.delete-account-error {
  color: #b91c1c !important;
  font-weight: 700;
}

.delete-account-button:disabled,
.confirm-delete-button:disabled,
.cancel-delete-button:disabled {
  cursor: wait;
  opacity: 0.65;
}

@media (max-width: 32rem) {
  .settings-danger-zone {
    grid-template-columns: 1fr;
  }

  .delete-account-button,
  .delete-account-confirmation__actions,
  .delete-account-confirmation__actions button {
    width: 100%;
  }

  .delete-account-confirmation__actions {
    display: grid;
  }
}

.job-row {
  display: grid;
  grid-template-columns: 3.5rem minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  color: inherit;
  text-decoration: none;
  background: color-mix(in srgb, var(--surface-secondary) 84%, transparent);
  transition: border-color 0.2s ease, background 0.2s ease, color 0.2s ease;
}

.job-row:hover,
.job-row:focus-visible,
.activity-item:hover,
.activity-item:focus-visible {
  border-color: var(--border-strong);
  box-shadow: none;
}

.job-logo {
  width: 3.5rem;
  height: 3.5rem;
  display: grid;
  place-items: center;
  border-radius: 0.75rem;
  color: #fff;
  font-weight: 800;
  overflow: hidden;
}

.job-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.job-info {
  display: grid;
  gap: 0.3rem;
}

.job-info p {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.job-info strong,
.job-action {
  color: var(--brand-strong);
  font-weight: 800;
}

.activity-item {
  display: flex;
  gap: 0.85rem;
  align-items: center;
  padding: 0.95rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: color-mix(in srgb, var(--surface-secondary) 86%, transparent);
  color: var(--text-primary);
  text-decoration: none;
  font: inherit;
  cursor: pointer;
}

.activity-score {
  margin-left: auto;
  color: var(--brand-strong);
  font-size: 0.82rem;
  white-space: nowrap;
}

.activity-item i {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  color: var(--brand-strong);
}

.activity-info {
  display: grid;
  gap: 0.15rem;
  text-align: left;
}

.activity-title {
  font-weight: 700;
}

.activity-company {
  font-size: 0.825rem;
  color: var(--text-muted);
}

.activity-item.empty {
  justify-content: center;
  text-align: center;
  padding: 1.5rem 1rem;
}

.candidate-dashboard-shell :deep(.shell-stats),
.candidate-dashboard-shell :deep(.dashboard-stats),
.candidate-dashboard-shell :deep(.dashboard-shell-stats),
.candidate-dashboard-shell :deep(.dashboard-shell__stats),
.candidate-dashboard-shell :deep(.stats-grid) {
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  gap: 1rem !important;
  align-items: stretch;
}

.candidate-dashboard-shell :deep(.shell-stat),
.candidate-dashboard-shell :deep(.dashboard-stat),
.candidate-dashboard-shell :deep(.stat-card),
.candidate-dashboard-shell :deep(.stats-card) {
  min-width: 0;
  width: 100%;
}

@media (max-width: 72rem) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .candidate-dashboard-shell :deep(.shell-stats),
  .candidate-dashboard-shell :deep(.dashboard-stats),
  .candidate-dashboard-shell :deep(.dashboard-shell-stats),
  .candidate-dashboard-shell :deep(.dashboard-shell__stats),
  .candidate-dashboard-shell :deep(.stats-grid) {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@media (max-width: 48rem) {
  .job-row {
    grid-template-columns: 3rem minmax(0, 1fr);
  }

  .job-action {
    grid-column: 2;
  }

  .panel,
  .btn-primary {
    padding: 1.25rem;
  }

  .candidate-dashboard-shell :deep(.shell-stats),
  .candidate-dashboard-shell :deep(.dashboard-stats),
  .candidate-dashboard-shell :deep(.dashboard-shell-stats),
  .candidate-dashboard-shell :deep(.dashboard-shell__stats),
  .candidate-dashboard-shell :deep(.stats-grid) {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}
</style>
