<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import Profile from '@/components/Profile.vue'
import DashboardShell from '@/components/dashboard/DashboardShell.vue'
import MessagesPanel from '@/components/messages/MessagesPanel.vue'
import { getJobs, getMyApplications } from '@/api/jobs'
import { getProfile } from '@/api/profile'
import { useI18n } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useMessagingStore } from '@/stores/messaging'
import { normalizeJob } from '@/utils/jobs'

const route = useRoute()
const router = useRouter()
const { state } = useAuth()
const messaging = useMessagingStore()
const { language } = useI18n()

const isEnglish = computed(() => language.value === 'en')
const copy = computed(() => (
  isEnglish.value
    ? {
      sections: {
        messages: 'Messages',
        profile: 'Profile',
        jobs: 'Jobs',
        resume: 'Resume',
      },
      fallbackCandidate: 'candidate',
      stats: {
        profile: 'Profile completion',
        applications: 'My applications',
        conversations: 'Conversations',
        recommendations: 'Recommendations',
      },
      onlyCandidate: 'This dashboard is available to candidates only.',
      loadJobsError: 'Failed to load the jobs list.',
      loadCandidateDataError: 'Part of the profile data could not be loaded. Please verify the candidate account type.',
      noPublishedJobs: 'There are no published vacancies yet.',
      loadDashboardError: 'Failed to load the dashboard data.',
      eyebrow: 'Candidate dashboard',
      titleMessages: 'Messages',
      titleGreeting: 'Hello, {name}',
      description: 'Track applications, update your profile, and keep your conversations in one place.',
      findJob: 'Find a job',
      recommendationsEyebrow: 'Recommendations',
      recommendationsTitle: 'Jobs to apply for',
      refresh: 'Refresh',
      loadingJobs: 'Loading jobs...',
      apply: 'Apply now',
      noRecommendations: 'There are no new jobs to apply for yet.',
      activityEyebrow: 'My applications',
      activityTitle: 'Latest activity',
      chatPending: 'Chat is awaiting approval',
      completeProfile: 'Complete your profile and start applying',
      messagesHint: 'All active conversations for approved applications',
    }
    : {
      sections: {
        messages: 'Сообщения',
        profile: 'Профиль',
        jobs: 'Вакансии',
        resume: 'Резюме',
      },
      fallbackCandidate: 'кандидат',
      stats: {
        profile: 'Заполнение профиля',
        applications: 'Моих откликов',
        conversations: 'Диалогов',
        recommendations: 'Рекомендаций',
      },
      onlyCandidate: 'Этот кабинет доступен только кандидату.',
      loadJobsError: 'Не удалось загрузить список вакансий.',
      loadCandidateDataError: 'Часть данных профиля не загрузилась. Проверьте тип аккаунта кандидата.',
      noPublishedJobs: 'Пока опубликованных вакансий нет.',
      loadDashboardError: 'Не удалось загрузить данные кабинета.',
      eyebrow: 'Личный кабинет соискателя',
      titleMessages: 'Сообщения',
      titleGreeting: 'Привет, {name}',
      description: 'Следите за откликами, обновляйте профиль и держите переписку внутри одного кабинета.',
      findJob: 'Найти работу',
      recommendationsEyebrow: 'Рекомендации',
      recommendationsTitle: 'Вакансии для отклика',
      refresh: 'Обновить',
      loadingJobs: 'Загрузка вакансий...',
      apply: 'Откликнуться',
      noRecommendations: 'Новых вакансий для отклика пока нет.',
      activityEyebrow: 'Мои отклики',
      activityTitle: 'Последняя активность',
      chatPending: 'Чат ждёт подтверждения',
      completeProfile: 'Заполнить профиль и начать откликаться',
      messagesHint: 'Все активные диалоги по подтверждённым откликам',
    }
))

const interpolate = (template, params = {}) => String(template).replace(/\{(\w+)\}/g, (_, key) => String(params[key] ?? ''))

const jobs = ref([])
const applications = ref([])
const profile = ref(null)
const isLoading = ref(false)
const isRefreshingApplications = ref(false)
const notice = ref('')
const applicationsRefreshTimer = ref(null)
const validSectionIds = ['dashboard', 'messages', 'profile']
const normalizeSection = (section) => (validSectionIds.includes(section) ? section : 'dashboard')
const activeSection = ref(normalizeSection(typeof route.query.section === 'string' ? route.query.section : 'dashboard'))

const shellSections = computed(() => ([
  { id: 'messages', label: copy.value.sections.messages, icon: 'fas fa-message', to: '/dashboard?section=messages' },
  { id: 'profile', label: copy.value.sections.profile, icon: 'fas fa-user', to: '/dashboard?section=profile' },
  { id: 'jobs', label: copy.value.sections.jobs, icon: 'fas fa-briefcase', to: '/jobs' },
  { id: 'resume', label: copy.value.sections.resume, icon: 'fas fa-file-lines', to: '/resume-builder' },
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
  const fields = [profile.value?.first_name, profile.value?.last_name, profile.value?.phone, profile.value?.resume_name]
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
      : interpolate(copy.value.titleGreeting, { name: userName.value })
))

const getSettledValue = (result, fallback) => (result.status === 'fulfilled' ? result.value : fallback)

const setSection = async (sectionId) => {
  activeSection.value = sectionId
  await router.replace({
    path: '/dashboard',
    query: sectionId === 'dashboard' ? {} : { section: sectionId },
  })
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
  } catch {
    // Silent refresh should not break the dashboard UI.
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
  activeSection.value = normalizeSection(typeof section === 'string' ? section : 'dashboard')
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
                <img v-if="job.logo" :src="job.logo" :alt="job.company" />
                <span v-else>{{ job.initials }}</span>
              </div>

              <div class="job-info">
                <h3>{{ job.title }}</h3>
                <p>{{ job.company }} · {{ job.displayLocation || job.location }}</p>
                <strong>{{ job.salary }}</strong>
              </div>

              <span class="job-action">{{ copy.apply }}</span>
            </RouterLink>
          </div>

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
                <span class="activity-title">{{ application.job_title }}</span>
                <span class="activity-company">
                  {{ application.job_company }}{{ application.chat_approved ? '' : ` · ${copy.chatPending}` }}
                </span>
              </div>
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

      <section v-else class="message-shell">
        <MessagesPanel
          embedded
          :hint="copy.messagesHint"
          @open="openDashboardConversation"
        />
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
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.job-row:hover,
.job-row:focus-visible,
.activity-item:hover,
.activity-item:focus-visible {
  transform: translateY(-0.125rem);
  border-color: var(--border-strong);
  box-shadow: var(--shadow-soft);
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
    grid-template-columns: 1fr !important;
  }
}
</style>
