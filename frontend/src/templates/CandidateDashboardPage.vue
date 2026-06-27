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
            <div class="panel-title">
              <div>
                <p class="eyebrow compact">Рекомендации</p>
                <h2>Вакансии для отклика</h2>
              </div>
              <button class="icon-button" type="button" aria-label="Обновить" @click="loadRecommendations">
                <i class="fas fa-rotate-right"></i>
              </button>
            </div>

            <p v-if="notice" class="notice">{{ notice }}</p>
            <p v-if="isLoading" class="state">Загрузка вакансий...</p>

            <RouterLink
              v-for="job in recommendedJobs"
              v-else
              :key="job.id"
              :to="`/jobs/${job.id}`"
              class="job-row"
            >
              <div class="job-logo" :style="{ background: job.color }">
                <img v-if="job.logo" :src="job.logo" :alt="job.company" />
                <span v-else>{{ job.initials }}</span>
              </div>
              <div>
                <h3>{{ job.title }}</h3>
                <p>{{ job.company }} · {{ job.location }}</p>
                <strong>{{ job.salary }}</strong>
              </div>
              <span>Откликнуться</span>
            </RouterLink>

            <p v-if="!isLoading && !recommendedJobs.length" class="state">
              Новых вакансий для отклика пока нет.
            </p>
          </div>

          <div class="panel steps">
            <div>
              <p class="eyebrow compact">Мои отклики</p>
              <h2>Последняя активность</h2>
            </div>

            <RouterLink
              v-for="application in applications.slice(0, 3)"
              :key="application.id"
              :to="`/messages?application=${application.id}`"
              class="step"
            >
              <i class="fas fa-message"></i>
              <span>{{ application.job_title }} · {{ application.job_company }}</span>
            </RouterLink>

            <RouterLink v-if="!applications.length" to="/profile" class="step">
              <i class="fas fa-user-pen"></i>
              <span>Заполнить профиль и начать откликаться</span>
            </RouterLink>
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
  gap: 1.25rem;
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
  gap: 1.25rem;
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.6rem;
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
  gap: 1.25rem;
}

.cards article {
  padding: 1.25rem;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 94%, transparent), var(--surface-primary)),
    var(--surface-primary);
}

.cards strong {
  display: block;
  color: var(--brand-strong);
  font-size: 2rem;
}

.cards span,
.job-row p,
.state {
  color: var(--text-muted);
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(18rem, 24rem);
  gap: 1.25rem;
  align-items: start;
}

.panel {
  display: grid;
  gap: 1rem;
  padding: 1.5rem;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 92%, transparent), var(--surface-primary)),
    var(--surface-primary);
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.icon-button {
  width: 2.7rem;
  height: 2.7rem;
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
  margin: 0;
  padding: 0.85rem;
  border: 0.0625rem solid var(--border-strong);
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
}

.job-row {
  display: grid;
  grid-template-columns: 4rem minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  color: inherit;
  text-decoration: none;
  background: color-mix(in srgb, var(--surface-secondary) 84%, transparent);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.job-row:hover,
.job-row:focus-visible {
  transform: translateY(-0.0625rem);
  border-color: var(--border-strong);
  box-shadow: var(--shadow-soft);
}

.job-logo {
  width: 4rem;
  height: 4rem;
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

.job-row p {
  margin: 0.25rem 0;
}

.job-row strong,
.job-row > span {
  color: var(--brand-strong);
  font-weight: 800;
}

.steps {
  gap: 0.75rem;
}

.step {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  padding: 0.9rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: color-mix(in srgb, var(--surface-secondary) 86%, transparent);
  color: var(--text-primary);
  font-weight: 800;
  text-decoration: none;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.step i {
  color: var(--brand-strong);
}

.step:hover,
.step:focus-visible {
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
  .head,
  .job-row {
    display: grid;
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
    padding: 1.15rem;
  }
}
</style>
