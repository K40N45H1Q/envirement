<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { applyToJob, getJob } from '@/api/jobs'
import { getProfile } from '@/api/profile'
import { useAuth } from '@/stores/auth'
import { normalizeJob } from '@/utils/jobs'

const route = useRoute()
const { state } = useAuth()

const job = ref(null)
const isLoading = ref(false)
const error = ref('')
const applyStatus = ref('')
const appliedApplicationId = ref(null)
const brokenLogo = ref(false)
const form = ref({
  name: '',
  surname: '',
  phone: '',
  email: '',
  nationality: '',
  message: '',
})

const user = computed(() => state.user)
const hasLogo = computed(() => !!job.value?.logo && !brokenLogo.value)

const tagSet = computed(() => {
  if (!job.value) return []
  const haystack = `${job.value.title} ${job.value.description} ${job.value.location}`.toLowerCase()
  const tags = ['Официальное трудоустройство']

  if (/(монтаж|свар|electric|technician|repair|стро)/.test(haystack)) tags.push('Техническая роль')
  if (/(latvia|riga|герман|germany|netherlands|poland|belgium|france)/.test(haystack)) tags.push('Работа в Европе')
  if (job.value.salary) tags.push('Конкурентная оплата')

  return tags
})

const featureList = computed(() => {
  if (!job.value) return []
  return [
    `Компания: ${job.value.company}`,
    `Локация: ${job.value.location}`,
    `Формат оплаты: ${job.value.salary || 'по договоренности'}`,
    'Отклик сразу попадает работодателю в рабочий кабинет',
  ]
})

const quickFacts = computed(() => {
  if (!job.value) return []

  return [
    {
      label: 'Формат',
      value: 'Прямая вакансия',
      icon: 'fas fa-briefcase',
    },
    {
      label: 'Локация',
      value: job.value.location,
      icon: 'fas fa-location-dot',
    },
    {
      label: 'Оплата',
      value: job.value.salary,
      icon: 'fas fa-wallet',
    },
    {
      label: 'Статус',
      value: 'Можно откликнуться сейчас',
      icon: 'fas fa-circle-check',
    },
  ]
})

const requirementList = computed(() => {
  if (!job.value) return []

  const base = [
    'Опыт работы по специальности',
    'Готовность к стабильному графику и командной работе',
  ]

  const haystack = `${job.value.title} ${job.value.description}`.toLowerCase()
  if (/(ce|driver|водител)/.test(haystack)) base.push('Наличие действующих прав и аккуратное ведение документации')
  if (/(свар|mig|mag|tig)/.test(haystack)) base.push('Навыки чтения чертежей и контроля качества швов')
  if (/(electric|элект|technician|repair)/.test(haystack)) base.push('Базовые знания техники безопасности и профильного оборудования')
  if (!base.some((item) => item.includes('документ'))) base.push('Документы для легального трудоустройства в ЕС')

  return base
})

const loadJob = async () => {
  isLoading.value = true
  error.value = ''
  brokenLogo.value = false

  try {
    const data = await getJob(route.params.id)
    job.value = normalizeJob(data)
  } catch {
    job.value = null
    error.value = 'Вакансия не найдена или больше не опубликована.'
  } finally {
    isLoading.value = false
  }
}

const submitApplication = async () => {
  applyStatus.value = ''
  appliedApplicationId.value = null

  if (!user.value) {
    applyStatus.value = 'Войдите в аккаунт, чтобы отправить отклик.'
    return
  }

  try {
    const result = await applyToJob({
      ...form.value,
      username: user.value.email,
      email: form.value.email || user.value.email,
      job_id: Number(job.value.id),
    })
    appliedApplicationId.value = result?.application_id ?? null
    applyStatus.value = 'Отклик отправлен работодателю.'
  } catch (err) {
    applyStatus.value = err?.key === 'duplicate_application'
      ? 'Вы уже откликались на эту вакансию.'
      : 'Не удалось отправить отклик. Проверьте поля и повторите попытку.'
  }
}

onMounted(async () => {
  if (user.value?.email) form.value.email = user.value.email

  if (user.value) {
    try {
      const profile = await getProfile()
      form.value.name = profile.first_name || ''
      form.value.surname = profile.last_name || ''
      form.value.phone = profile.phone || ''
      form.value.email = form.value.email || user.value.email
    } catch {}
  }

  await loadJob()
})

watch(() => route.params.id, loadJob)
</script>

<template>
  <AppLayout>
    <main class="page">
      <div v-if="isLoading" class="notice">Загрузка вакансии...</div>
      <div v-else-if="error" class="notice notice--error">{{ error }}</div>

      <template v-else-if="job">
        <section class="hero surface-section">
          <div class="hero-brand">
            <div class="logo" :style="{ background: job.color }">
              <img
                v-if="hasLogo"
                :src="job.logo"
                :alt="job.company"
                @error="brokenLogo = true"
              />
              <span v-else>{{ job.initials }}</span>
            </div>

            <div class="hero-copy">
              <p class="section-eyebrow">Страница вакансии</p>
              <h1>{{ job.title }}</h1>
              <div class="hero-meta">
                <span><i class="fas fa-building"></i>{{ job.company }}</span>
                <span><i class="fas fa-location-dot"></i>{{ job.location }}</span>
              </div>
              <div class="hero-tags">
                <span v-for="tag in tagSet" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>
          </div>

          <div class="hero-side">
            <strong>{{ job.salary }}</strong>
            <span>Актуальная ставка</span>
            <RouterLink to="/jobs" class="btn-secondary back-link">
              <i class="fas fa-arrow-left"></i>
              Все вакансии
            </RouterLink>
          </div>
        </section>

        <section class="facts-grid">
          <article v-for="fact in quickFacts" :key="fact.label" class="fact-card">
            <div class="fact-icon">
              <i :class="fact.icon"></i>
            </div>
            <div>
              <span>{{ fact.label }}</span>
              <strong>{{ fact.value }}</strong>
            </div>
          </article>
        </section>

        <section class="content-grid">
          <div class="main-column">
            <section class="panel">
              <div class="panel-head">
                <div>
                  <p class="section-eyebrow compact">Описание</p>
                  <h2>Что входит в работу</h2>
                </div>
              </div>

              <p class="lead">
                {{ job.description || 'Подробности вакансии уточняются работодателем.' }}
              </p>

              <div class="content-blocks">
                <article class="content-card">
                  <h3>Требования</h3>
                  <ul>
                    <li v-for="item in requirementList" :key="item">{{ item }}</li>
                  </ul>
                </article>

                <article class="content-card">
                  <h3>Что вы получите</h3>
                  <ul>
                    <li v-for="feature in featureList" :key="feature">{{ feature }}</li>
                  </ul>
                </article>
              </div>
            </section>

            <section class="panel company-panel">
              <div class="panel-head">
                <div>
                  <p class="section-eyebrow compact">Компания</p>
                  <h2>{{ job.company }}</h2>
                </div>
              </div>

              <div class="company-grid">
                <div>
                  <span class="company-label">Локация</span>
                  <strong>{{ job.location }}</strong>
                </div>
                <div>
                  <span class="company-label">Зарплата</span>
                  <strong>{{ job.salary }}</strong>
                </div>
                <div>
                  <span class="company-label">Статус</span>
                  <strong>Публичная вакансия</strong>
                </div>
              </div>

              <div class="company-note">
                <i class="fas fa-shield-check"></i>
                <p>Публикация активна на платформе и доступна кандидатам для прямого отклика без лишних шагов.</p>
              </div>
            </section>
          </div>

          <form class="panel apply-form" @submit.prevent="submitApplication">
            <div class="panel-head">
              <div>
                <p class="section-eyebrow compact">Отклик</p>
                <h2>Откликнуться</h2>
              </div>
            </div>

            <p class="form-note">
              Данные отправятся работодателю сразу после отправки формы. Часть полей уже
              предзаполнена из вашего профиля.
            </p>

            <div class="form-chip">
              <i class="fas fa-sparkles"></i>
              <span>Отклик сохраняет связь с аккаунтом кандидата и вакансией.</span>
            </div>

            <input v-model="form.name" required placeholder="Имя" />
            <input v-model="form.surname" required placeholder="Фамилия" />
            <input v-model="form.phone" required placeholder="Телефон" />
            <input v-model="form.email" required type="email" placeholder="Email" />
            <input v-model="form.nationality" placeholder="Гражданство" />
            <textarea v-model="form.message" rows="5" placeholder="Сообщение работодателю"></textarea>

            <button type="submit" class="btn-primary">Отправить отклик</button>
            <p v-if="applyStatus" class="status">{{ applyStatus }}</p>
            <RouterLink
              v-if="appliedApplicationId"
              :to="`/messages?application=${appliedApplicationId}`"
              class="btn-secondary message-link"
            >
              Перейти к диалогу
            </RouterLink>
          </form>
        </section>
      </template>
    </main>
  </AppLayout>
</template>

<style scoped>
.page {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 1.5rem var(--shell-gutter) 4rem;
  display: grid;
  gap: 1.25rem;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 15rem;
  gap: 1.5rem;
  padding: 2rem;
}

.hero-brand {
  display: grid;
  grid-template-columns: 5.5rem minmax(0, 1fr);
  gap: 1.1rem;
  align-items: start;
}

.logo {
  width: 5rem;
  height: 5rem;
  display: grid;
  place-items: center;
  border-radius: 1rem;
  color: #fff;
  font-size: 1.25rem;
  font-weight: 800;
  overflow: hidden;
}

.logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-copy h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(2rem, 4vw, 3rem);
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  margin-top: 0.55rem;
  color: var(--text-muted);
}

.hero-meta span {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.tag {
  display: inline-flex;
  align-items: center;
  min-height: 2rem;
  padding: 0.2rem 0.7rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 64%, white);
  color: var(--brand-strong);
  font-size: 0.82rem;
  font-weight: 700;
}

.hero-side {
  display: grid;
  align-content: start;
  justify-items: end;
  gap: 0.55rem;
  text-align: right;
}

.hero-side strong {
  color: var(--brand-strong);
  font-size: 2rem;
}

.hero-side span {
  color: var(--text-muted);
}

.back-link {
  margin-top: 0.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.facts-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.fact-card {
  display: flex;
  gap: 0.9rem;
  align-items: center;
  padding: 1rem 1.1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(232, 249, 238, 0.58)),
    var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.fact-icon {
  width: 2.7rem;
  height: 2.7rem;
  display: grid;
  place-items: center;
  border-radius: 0.85rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, white);
  color: var(--brand-strong);
}

.fact-card span {
  display: block;
  color: var(--text-muted);
  font-size: 0.84rem;
}

.fact-card strong {
  display: block;
  margin-top: 0.2rem;
  color: var(--text-primary);
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 24rem;
  gap: 1.25rem;
  align-items: start;
}

.main-column {
  display: grid;
  gap: 1.25rem;
}

.panel {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
  padding: 1.5rem;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.compact {
  font-size: 0.76rem;
}

.lead {
  margin: 1rem 0 0;
  color: var(--text-muted);
  line-height: 1.75;
  font-size: 1.02rem;
}

.content-blocks {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  margin-top: 1.25rem;
}

.content-card {
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
}

.content-card h3 {
  margin: 0 0 0.75rem;
  color: var(--text-primary);
}

.content-card ul {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--text-muted);
  line-height: 1.7;
}

.company-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.company-grid div {
  padding: 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
}

.company-label {
  display: block;
  margin-bottom: 0.4rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.company-grid strong {
  color: var(--text-primary);
}

.company-note {
  display: flex;
  gap: 0.7rem;
  align-items: start;
  margin-top: 1rem;
  padding: 0.95rem 1rem;
  border-radius: 1rem;
  background: color-mix(in srgb, var(--brand-soft) 68%, white);
  color: var(--brand-strong);
}

.company-note p {
  margin: 0;
  line-height: 1.55;
}

.apply-form {
  display: grid;
  gap: 0.8rem;
  position: sticky;
  top: 5.6rem;
}

.form-note {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.6;
}

.form-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.75rem 0.9rem;
  border-radius: 0.9rem;
  background: color-mix(in srgb, var(--brand-soft) 66%, white);
  color: var(--brand-strong);
  font-weight: 600;
  line-height: 1.45;
}

.apply-form input,
.apply-form textarea {
  width: 100%;
  min-height: 3.15rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

.apply-form textarea {
  min-height: 8rem;
  resize: vertical;
}

.notice,
.status {
  padding: 1rem;
  border-radius: 1rem;
  border: 0.0625rem solid var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 68%, white);
  color: var(--brand-strong);
}

.notice--error {
  border-color: rgba(220, 38, 38, 0.14);
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.message-link {
  width: 100%;
}

@media (max-width: 72rem) {
  .facts-grid,
  .content-grid,
  .content-blocks,
  .company-grid {
    grid-template-columns: 1fr;
  }

  .apply-form {
    position: static;
  }
}

@media (max-width: 60rem) {
  .hero {
    grid-template-columns: 1fr;
    padding: 1.25rem;
  }

  .hero-side {
    justify-items: start;
    text-align: left;
    padding-top: 1rem;
    border-top: 0.0625rem solid var(--border-subtle);
  }

  .hero-side strong {
    font-size: 1.85rem;
  }
}

@media (max-width: 48rem) {
  .page {
    padding-top: 1.15rem;
  }

  .hero,
  .panel {
    padding: 1rem;
  }

  .hero-brand {
    grid-template-columns: 1fr;
  }

  .hero-meta,
  .hero-tags {
    gap: 0.65rem;
  }
}
</style>
