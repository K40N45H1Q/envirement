<script setup>
import { computed, onMounted, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
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
  const filled = fields.filter(Boolean).length
  return Math.round((filled / fields.length) * 100)
})
const activeApplications = computed(() => applications.value.length)

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
    <main class="page">
      <aside class="sidebar">
        <RouterLink to="/dashboard"><i class="fas fa-table-columns"></i> Дашборд</RouterLink>
        <RouterLink to="/profile"><i class="fas fa-user"></i> Профиль</RouterLink>
        <RouterLink to="/jobs"><i class="fas fa-briefcase"></i> Вакансии</RouterLink>
        <RouterLink to="/resume-builder"><i class="fas fa-file-lines"></i> Резюме</RouterLink>
        <RouterLink to="/messages"><i class="fas fa-message"></i> Сообщения</RouterLink>
      </aside>

      <section class="content">
        <section class="head">
          <div>
            <p class="eyebrow">Личный кабинет соискателя</p>
            <h1>Привет, {{ userName }}</h1>
            <p>Следите за откликами, обновляйте профиль и быстро возвращайтесь к подходящим вакансиям.</p>
          </div>
          <RouterLink to="/jobs" class="btn-primary">
            <i class="fas fa-magnifying-glass"></i>
            Найти работу
          </RouterLink>
        </section>

        <section class="cards">
          <article>
            <strong>{{ profileScore }}%</strong>
            <span>Заполнение профиля</span>
          </article>
          <article>
            <strong>{{ activeApplications }}</strong>
            <span>Моих откликов</span>
          </article>
          <article>
            <strong>{{ recommendedJobs.length }}</strong>
            <span>Новых вакансий</span>
          </article>
        </section>

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

            <p v-else class="state">
              Новых вакансий для отклика пока нет.
            </p>
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
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.page {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 2rem var(--shell-gutter) 4rem;
  display: grid;
  grid-template-columns: 16rem minmax(0, 1fr);
  gap: 1.5rem;
}

.sidebar,
.head,
.panel,
.cards article {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.sidebar {
  display: grid;
  align-content: start;
  gap: 0.45rem;
  padding: 1rem;
  position: sticky;
  top: 5.5rem;
}

.sidebar a {
  display: flex;
  gap: 0.65rem;
  align-items: center;
  min-height: 3rem;
  padding: 0.75rem 0.9rem;
  border-radius: 0.875rem;
  color: var(--text-primary);
  text-decoration: none;
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.sidebar a:hover,
.sidebar a:focus-visible {
  background: color-mix(in srgb, var(--brand-soft) 60%, transparent);
  color: var(--brand-strong);
}

.sidebar a.router-link-active {
  background: linear-gradient(180deg, color-mix(in srgb, var(--brand-base) 22%, transparent), color-mix(in srgb, var(--brand-strong) 14%, transparent));
  color: var(--text-primary);
  border: 0.0625rem solid var(--border-strong);
}

.content {
  display: grid;
  gap: 1.5rem;
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.75rem;
  background:
    radial-gradient(circle at top right, rgba(26, 177, 111, 0.14), transparent 28%),
    var(--surface-primary);
}

.head p:not(.eyebrow) {
  max-width: 44rem;
  margin: 0.7rem 0 0;
  color: var(--text-muted);
}

.eyebrow {
  margin: 0 0 0.45rem;
  color: #19785a;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

.compact {
  font-size: 0.76rem;
}

h1,
h2,
h3 {
  margin: 0;
  color: var(--text-primary);
}

h1 {
  font-size: clamp(2rem, 4vw, 3rem);
}

h2 {
  font-size: 1.35rem;
  font-weight: 700;
}

.btn-primary {
  display: inline-flex;
  gap: 0.5rem;
  align-items: center;
  justify-content: center;
  min-height: 3rem;
  padding: 0 1.15rem;
  border-radius: 0.875rem;
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
  box-shadow: 0 0.875rem 1.8rem rgba(21, 149, 93, 0.18);
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.cards article {
  padding: 1.5rem;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 94%, transparent), var(--surface-primary)),
    var(--surface-primary);
}

.cards strong {
  display: block;
  color: var(--brand-strong);
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 0.35rem;
}

.cards span {
  color: var(--text-muted);
  font-size: 0.9rem;
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
  flex-shrink: 0;
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
  transition: all 0.2s ease;
}

.icon-button:hover {
  background: color-mix(in srgb, var(--brand-soft) 90%, transparent);
  transform: rotate(180deg);
}

.notice,
.state {
  margin: 0;
  padding: 0.85rem;
  border: 0.0625rem solid var(--border-strong);
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
}

.jobs-list {
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
.job-row:focus-visible {
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
  flex-shrink: 0;
}

.job-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.job-info h3 {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 0.25rem;
  color: var(--text-primary);
}

.job-info p {
  margin: 0 0 0.4rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.job-info strong {
  color: var(--brand-strong);
  font-weight: 800;
  font-size: 0.95rem;
}

.job-action {
  color: var(--brand-strong);
  font-weight: 700;
  font-size: 0.9rem;
  white-space: nowrap;
  margin-left: 1rem;
}

.panel-activity {
  gap: 1.25rem;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
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
  transition: all 0.2s ease;
}

.activity-item i {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  color: var(--brand-strong);
  font-size: 1rem;
  flex-shrink: 0;
}

.activity-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.activity-title {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-company {
  font-size: 0.825rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-item.empty {
  justify-content: center;
  text-align: center;
  padding: 1.5rem 1rem;
}

.activity-item.empty i {
  width: auto;
  height: auto;
  font-size: 1.25rem;
}

.activity-item:hover,
.activity-item:focus-visible {
  border-color: var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 52%, transparent);
}

@media (max-width: 72rem) {
  .page,
  .workspace {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    grid-auto-flow: column;
    grid-auto-columns: minmax(10.5rem, 1fr);
    overflow-x: auto;
    padding-bottom: 0.9rem;
    scrollbar-width: thin;
  }
}

@media (max-width: 48rem) {
  .head {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .head > div {
    display: grid;
    gap: 0.5rem;
  }

  .job-row {
    grid-template-columns: 3rem minmax(0, 1fr);
    gap: 0.75rem;
  }

  .job-action {
    grid-column: 2;
    margin-left: 0;
    font-size: 0.85rem;
  }

  .cards {
    grid-template-columns: 1fr;
  }

  .sidebar {
    grid-auto-columns: minmax(12rem, 1fr);
  }

  .btn-primary {
    width: 100%;
  }

  .page {
    padding-top: 1.25rem;
  }

  .head,
  .panel,
  .cards article {
    padding: 1.25rem;
  }
}
</style>