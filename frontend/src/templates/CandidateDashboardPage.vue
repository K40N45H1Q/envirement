<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import DashboardShell from '@/components/dashboard/DashboardShell.vue'
import { getJobs, getMyApplications } from '@/api/jobs'
import { getProfile } from '@/api/profile'
import { useAuth } from '@/stores/auth'
import { normalizeJob } from '@/utils/jobs'

const { state } = useAuth()
const jobs = ref([])
const applications = ref([])
const profile = ref(null)
const isLoading = ref(false)
const notice = ref('')

const shellSections = [
  { id: 'dashboard', label: 'Дашборд', icon: 'fas fa-table-columns', to: '/dashboard' },
  { id: 'profile', label: 'Профиль', icon: 'fas fa-user', to: '/profile' },
  { id: 'jobs', label: 'Вакансии', icon: 'fas fa-briefcase', to: '/jobs' },
  { id: 'resume', label: 'Резюме', icon: 'fas fa-file-lines', to: '/resume-builder' },
  { id: 'messages', label: 'Сообщения', icon: 'fas fa-message', to: '/messages' },
]

const userName = computed(() => state.user?.email?.split('@')[0] || 'кандидат')
const appliedJobIds = computed(() => new Set(applications.value.map((item) => item.job_id)))
const recommendedJobs = computed(() => jobs.value.filter((job) => !appliedJobIds.value.has(job.id)).slice(0, 3))
const profileScore = computed(() => {
  const fields = [
    profile.value?.first_name,
    profile.value?.last_name,
    profile.value?.phone,
    profile.value?.resume_name,
  ]
  return Math.round((fields.filter(Boolean).length / fields.length) * 100)
})
const activeApplications = computed(() => applications.value.length)
const shellStats = computed(() => ([
  { value: `${profileScore.value}%`, label: 'Заполнение профиля' },
  { value: activeApplications.value, label: 'Моих откликов' },
  { value: recommendedJobs.value.length, label: 'Новых вакансий' },
]))

const loadRecommendations = async () => {
  isLoading.value = true
  notice.value = ''

  try {
    const [jobsData, applicationsData, profileData] = await Promise.all([
      getJobs(),
      getMyApplications(),
      getProfile(),
    ])

    jobs.value = Array.isArray(jobsData) ? jobsData.map(normalizeJob) : []
    applications.value = Array.isArray(applicationsData) ? applicationsData : []
    profile.value = profileData

    if (!jobs.value.length) {
      notice.value = 'Пока опубликованных вакансий нет.'
    }
  } catch {
    jobs.value = []
    applications.value = []
    profile.value = null
    notice.value = 'Не удалось загрузить данные кабинета.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadRecommendations)
</script>

<template>
  <AppLayout>
    <DashboardShell
      :sections="shellSections"
      active-section="dashboard"
      eyebrow="Личный кабинет соискателя"
      :title="`Привет, ${userName}`"
      description="Следите за откликами, обновляйте профиль и быстро возвращайтесь к подходящим вакансиям."
      :stats="shellStats"
    >
      <template #actions>
        <RouterLink to="/jobs" class="btn-primary">
          <i class="fas fa-magnifying-glass"></i>
          Найти работу
        </RouterLink>
      </template>

      <section class="workspace">
        <div class="panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow compact">Рекомендации</p>
              <h2>Вакансии для отклика</h2>
            </div>
            <button class="icon-button" type="button" aria-label="Обновить" @click="loadRecommendations">
              <i class="fas fa-rotate-right"></i>
            </button>
          </div>

          <p v-if="notice" class="notice">{{ notice }}</p>
          <p v-else-if="isLoading" class="state">Загрузка вакансий...</p>

          <div v-else-if="recommendedJobs.length" class="jobs-list">
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
                <p>{{ job.company }} · {{ job.location }}</p>
                <strong>{{ job.salary }}</strong>
              </div>
              <span class="job-action">Откликнуться</span>
            </RouterLink>
          </div>

          <p v-else class="state">Новых вакансий для отклика пока нет.</p>
        </div>

        <div class="panel panel-activity">
          <div class="panel-header">
            <div>
              <p class="eyebrow compact">Мои отклики</p>
              <h2>Последняя активность</h2>
            </div>
          </div>

          <div class="activity-list">
            <RouterLink
              v-for="application in applications.slice(0, 3)"
              :key="application.id"
              :to="`/messages?application=${application.id}`"
              class="activity-item"
            >
              <i class="fas fa-message"></i>
              <div class="activity-info">
                <span class="activity-title">{{ application.job_title }}</span>
                <span class="activity-company">{{ application.job_company }}</span>
              </div>
            </RouterLink>

            <RouterLink v-if="!applications.length" to="/profile" class="activity-item empty">
              <i class="fas fa-user-pen"></i>
              <span>Заполнить профиль и начать откликаться</span>
            </RouterLink>
          </div>
        </div>
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
.activity-list {
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

@media (max-width: 72rem) {
  .workspace {
    grid-template-columns: 1fr;
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
}
</style>
