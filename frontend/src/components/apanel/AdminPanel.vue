<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import DashboardShell from '@/components/dashboard/DashboardShell.vue'
import APanelJobs from './APanelJobs.vue'
import APanelSettings from './APanelSettings.vue'
import APanelUsers from './APanelUsers.vue'
import {
  approveAdminJob,
  createAdminBetaToken,
  deleteAdminJob,
  getAdminBetaSettings,
  getAdminBetaTokens,
  getAdminJobs,
  getAdminModerationJobs,
  getAdminSummary,
  getAdminUsers,
  rejectAdminJob,
  deleteAdminBetaToken,
  updateAdminBetaSettings,
  updateAdminUserSubscription,
} from './api'

const route = useRoute()
const router = useRouter()

const sections = [
  { id: 'users', label: 'Пользователи', icon: 'fas fa-users' },
  { id: 'employers', label: 'Работодатели', icon: 'fas fa-building' },
  { id: 'moderation', label: 'Модерация', icon: 'fas fa-shield-halved' },
  { id: 'vacancies', label: 'Вакансии', icon: 'fas fa-briefcase' },
  { id: 'settings', label: 'Настройки', icon: 'fas fa-gear' },
]

const validSections = sections.map((section) => section.id)
const normalizeSection = (value) => (validSections.includes(value) ? value : 'users')

const activeSection = ref(normalizeSection(route.query.section))
const summary = ref(null)
const users = ref([])
const employers = ref([])
const jobs = ref([])
const moderationJobs = ref([])
const tokens = ref([])
const betaAccessEnabled = ref(false)
const isLoading = ref(false)
const isSaving = ref(false)
const isSavingSettings = ref(false)
const error = ref('')
const createdToken = ref('')

const stats = computed(() => [
  { label: 'Всего пользователей', value: summary.value?.total_users ?? users.value.length + employers.value.length, section: 'users' },
  { label: 'Активных работодателей', value: summary.value?.employers ?? employers.value.length, section: 'employers' },
  { label: 'Ожидают модерации', value: summary.value?.pending_vacancies ?? moderationJobs.value.length, section: 'moderation' },
  { label: 'Всего вакансий', value: summary.value?.vacancies ?? jobs.value.length, section: 'vacancies' },
])

const activeTitle = computed(() => sections.find((section) => section.id === activeSection.value)?.label || 'Админка')

const setSection = async (sectionId) => {
  activeSection.value = normalizeSection(sectionId)
  await router.replace({
    path: route.path,
    query: { section: activeSection.value },
  })
}

const loadAdminData = async () => {
  isLoading.value = true
  error.value = ''

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
    moderationJobs.value = Array.isArray(moderationData)
      ? moderationData
      : []
    if (!moderationJobs.value.length && Array.isArray(jobsData)) {
      moderationJobs.value = jobsData.filter((job) => job?.status === 'pending')
    }
    tokens.value = Array.isArray(tokenData) ? tokenData : []
    betaAccessEnabled.value = Boolean(betaSettingsData?.enabled)
  } catch {
    error.value = 'Не удалось загрузить админку.'
  } finally {
    isLoading.value = false
  }
}

const createToken = async ({ note }) => {
  isSaving.value = true
  error.value = ''
  createdToken.value = ''

  try {
    const token = await createAdminBetaToken({ note })
    createdToken.value = token.token || ''
    await loadAdminData()
  } catch {
    error.value = 'Не удалось создать бета-токен.'
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
    error.value = 'Не удалось удалить токен.'
  }
}

const updateBetaAccess = async (enabled) => {
  isSavingSettings.value = true
  error.value = ''

  try {
    const settings = await updateAdminBetaSettings({ enabled })
    betaAccessEnabled.value = Boolean(settings?.enabled)
  } catch {
    error.value = 'Не удалось изменить режим бета-доступа.'
  } finally {
    isSavingSettings.value = false
  }
}

const updateUserSubscription = async ({ user, plan, revoke = false }) => {
  error.value = ''

  try {
    await updateAdminUserSubscription(user.id, revoke ? { revoke: true } : {
      plan,
    })
    await loadAdminData()
  } catch {
    error.value = 'Не удалось изменить тариф пользователя.'
  }
}

const approveJob = async (job) => {
  error.value = ''

  try {
    await approveAdminJob(job.id)
    await loadAdminData()
  } catch {
    error.value = 'Не удалось одобрить вакансию.'
  }
}

const rejectJob = async (job) => {
  error.value = ''

  try {
    await rejectAdminJob(job.id)
    await loadAdminData()
  } catch {
    error.value = 'Не удалось отклонить вакансию.'
  }
}

const deleteJob = async (job) => {
  error.value = ''

  try {
    await deleteAdminJob(job.id)
    await loadAdminData()
  } catch {
    error.value = 'Не удалось удалить вакансию.'
  }
}

watch(
  () => route.query.section,
  (section) => {
    activeSection.value = normalizeSection(typeof section === 'string' ? section : 'users')
  },
)

onMounted(loadAdminData)
</script>

<template>
  <AppLayout>
    <DashboardShell
      :sections="sections"
      :active-section="activeSection"
      eyebrow="Администрирование"
      :title="activeTitle"
      description="Управление пользователями, работодателями, вакансиями и бета-доступом."
      :stats="stats"
      @select-section="setSection"
      @stat-click="setSection"
    >
      <p v-if="error" class="apanel-status apanel-status--danger">{{ error }}</p>
      <p v-if="isLoading" class="apanel-state">Загрузка...</p>

      <template v-else>
        <APanelUsers
          v-if="activeSection === 'users'"
          :users="users"
          manage-subscriptions
          subscription-mode="assign"
          @update-subscription="updateUserSubscription"
          empty-text="Пользователей пока нет."
        />

        <APanelUsers
          v-else-if="activeSection === 'employers'"
          :users="employers"
          manage-subscriptions
          subscription-mode="revoke"
          @update-subscription="updateUserSubscription"
          empty-text="Работодателей пока нет."
        />

        <APanelJobs
          v-else-if="activeSection === 'vacancies'"
          :jobs="jobs"
          empty-text="Вакансий пока нет."
          @delete="deleteJob"
        />

        <APanelJobs
          v-else-if="activeSection === 'moderation'"
          :jobs="moderationJobs"
          moderation
          empty-text="Вакансий на модерации нет."
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
          :created-token="createdToken"
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
