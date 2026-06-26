<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { getProfile, updateProfile } from '@/api/profile'

const languageOptions = [
  'Английский',
  'Русский',
  'Немецкий',
  'Польский',
  'Латышский',
  'Литовский',
  'Эстонский',
  'Французский',
]

const languageLevelOptions = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const experienceOptions = ['1-3 года', '3-5 лет', '5+ лет']

const defaultCv = () => ({
  name: '',
  role: '',
  email: '',
  phone: '',
  summary: '',
  skills: '',
  sectors: [],
  languages: [],
  mobility: '',
  preferredMobility: '',
  licenses: [],
  workPermit: '',
  availability: '',
})

const cv = ref(defaultCv())
const newSector = ref('')
const newLanguage = ref(languageOptions[0])
const newLanguageLevel = ref(languageLevelOptions[3])
const isLoaded = ref(false)
const isSaving = ref(false)
const status = ref('')
let saveTimer = null

const avatarInitials = computed(() => {
  const parts = (cv.value.name || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  if (!parts.length) return 'CV'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return `${parts[0][0] || ''}${parts[1][0] || ''}`.toUpperCase()
})

const filledFields = computed(() => {
  const checks = [
    cv.value.name,
    cv.value.role,
    cv.value.email,
    cv.value.phone,
    cv.value.summary,
    cv.value.sectors.length,
    cv.value.languages.length,
    cv.value.mobility,
    cv.value.workPermit,
    cv.value.availability,
  ]

  return checks.filter(Boolean).length
})

const progress = computed(() => Math.round((filledFields.value / 10) * 100))
const canAddLanguage = computed(() => !cv.value.languages.some(language =>
  language.name === newLanguage.value && language.level === newLanguageLevel.value))

const addSector = () => {
  if (!newSector.value.trim()) return

  cv.value.sectors.push({
    name: newSector.value.trim(),
    experience: experienceOptions[0],
  })
  newSector.value = ''
}

const removeSector = (index) => {
  cv.value.sectors.splice(index, 1)
}

const addLanguage = () => {
  if (!canAddLanguage.value) return

  cv.value.languages.push({
    name: newLanguage.value,
    level: newLanguageLevel.value,
  })

  newLanguage.value = languageOptions[0]
  newLanguageLevel.value = languageLevelOptions[3]
}

const removeLanguage = (index) => {
  cv.value.languages.splice(index, 1)
}

const syncProfile = async () => {
  if (!isLoaded.value) return

  isSaving.value = true

  try {
    await updateProfile({
      first_name: cv.value.name.split(' ')[0] || '',
      last_name: cv.value.name.split(' ').slice(1).join(' ') || '',
      phone: cv.value.phone,
      summary: cv.value.summary,
      current_role: cv.value.role,
      skills: cv.value.skills,
      sectors_json: cv.value.sectors,
      languages_json: cv.value.languages,
      licenses_json: cv.value.licenses,
      mobility: cv.value.mobility,
      preferred_mobility: cv.value.preferredMobility,
      work_permit: cv.value.workPermit,
      availability: cv.value.availability,
    })
    status.value = 'Изменения сохранены в backend.'
  } catch {
    status.value = 'Не удалось сохранить изменения в backend.'
  } finally {
    isSaving.value = false
  }
}

watch(cv, () => {
  if (!isLoaded.value) return
  clearTimeout(saveTimer)
  saveTimer = setTimeout(syncProfile, 500)
}, { deep: true })

onMounted(async () => {
  try {
    const profile = await getProfile()
    cv.value = {
      name: [profile.first_name, profile.last_name].filter(Boolean).join(' '),
      role: profile.current_role || '',
      email: '',
      phone: profile.phone || '',
      summary: profile.summary || '',
      skills: profile.skills || '',
      sectors: Array.isArray(profile.sectors) ? profile.sectors : [],
      languages: Array.isArray(profile.languages) ? profile.languages : [],
      mobility: profile.mobility || '',
      preferredMobility: profile.preferred_mobility || '',
      licenses: Array.isArray(profile.licenses) ? profile.licenses : [],
      workPermit: profile.work_permit || '',
      availability: profile.availability || '',
    }
  } catch {
    status.value = 'Не удалось загрузить профиль из backend.'
  } finally {
    isLoaded.value = true
  }
})
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="hero">
        <div>
          <div class="title-row">
            <h1>Создать профиль</h1>
            <span class="badge">Кандидат</span>
          </div>

          <div class="steps">
            <div class="step step--done">
              <span class="step-index">1</span>
              <div>
                <strong>Аккаунт</strong>
                <small>Завершено</small>
              </div>
            </div>
            <div class="step-line step-line--active"></div>
            <div class="step step--active">
              <span class="step-index">2</span>
              <div>
                <strong>Основное</strong>
                <small>Заполняется</small>
              </div>
            </div>
            <div class="step-line"></div>
            <div class="step">
              <span class="step-index">3</span>
              <div>
                <strong>Детали</strong>
                <small>Ожидает</small>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="builder">
        <div class="main-card">
          <div class="card-head">
            <h2>Шаг 2 — Опыт работы</h2>
            <p>Укажите свой опыт работы и основную информацию о себе.</p>
            <p v-if="status" class="hint">{{ isSaving ? 'Сохранение...' : status }}</p>
          </div>

          <div class="section">
            <label class="section-label">Опыт работы — сферы и стаж</label>

            <div v-for="(sector, index) in cv.sectors" :key="`${sector.name}-${index}`" class="list-row">
              <div class="list-row__title">
                <span class="dot">{{ index + 1 }}</span>
                <strong>{{ sector.name }}</strong>
              </div>

              <div class="list-row__actions">
                <select v-model="sector.experience">
                  <option v-for="experience in experienceOptions" :key="experience" :value="experience">{{ experience }}</option>
                </select>
                <button type="button" class="ghost-icon" @click="removeSector(index)">×</button>
              </div>
            </div>

            <div class="inline-add">
              <input v-model="newSector" placeholder="Добавить ещё сферу" />
              <button type="button" class="ghost-button" @click="addSector">Добавить</button>
            </div>
          </div>

          <div class="section grid-two">
            <label>
              Полное имя
              <input v-model="cv.name" placeholder="Имя и фамилия" />
            </label>
            <label>
              Профессия
              <input v-model="cv.role" placeholder="Профессия" />
            </label>
            <label>
              Email
              <input v-model="cv.email" placeholder="Email" />
            </label>
            <label>
              Телефон
              <input v-model="cv.phone" placeholder="Телефон" />
            </label>
          </div>

          <div class="section">
            <label>
              О себе
              <textarea v-model="cv.summary" rows="4" placeholder="Кратко опишите опыт и цели"></textarea>
            </label>
          </div>

          <div class="section">
            <label class="section-label">Языки</label>

            <div class="chips">
              <span v-for="(language, index) in cv.languages" :key="`${language.name}-${language.level}-${index}`" class="chip">
                <span>{{ language.name }}</span>
                <b>{{ language.level }}</b>
                <button type="button" @click="removeLanguage(index)">×</button>
              </span>
            </div>

            <div class="grid-two">
              <select v-model="newLanguage">
                <option v-for="language in languageOptions" :key="language" :value="language">{{ language }}</option>
              </select>
              <select v-model="newLanguageLevel">
                <option v-for="level in languageLevelOptions" :key="level" :value="level">{{ level }}</option>
              </select>
            </div>

            <button
              type="button"
              class="ghost-button ghost-button--small"
              :disabled="!canAddLanguage"
              @click="addLanguage"
            >
              Добавить язык
            </button>
            <p v-if="!canAddLanguage" class="hint">Такой язык с этим уровнем уже добавлен.</p>
          </div>

          <div class="section grid-two">
            <label>
              Максимальная мобильность
              <select v-model="cv.mobility">
                <option>Максимальная мобильность EU</option>
                <option>Готов к переезду</option>
                <option>Только своя страна</option>
              </select>
            </label>
            <label>
              Предпочтительная мобильность
              <select v-model="cv.preferredMobility">
                <option>Регион</option>
                <option>Европа</option>
                <option>Удалённо</option>
              </select>
            </label>
            <label>
              Навыки
              <input v-model="cv.skills" placeholder="Навыки через запятую" />
            </label>
            <label>
              Разрешение на работу
              <select v-model="cv.workPermit">
                <option>EU гражданин</option>
                <option>Есть виза</option>
                <option>Нужен sponsorship</option>
              </select>
            </label>
            <label>
              Водительские права
              <input v-model="cv.licenses[0]" placeholder="Например B, C" />
            </label>
            <label>
              Дата доступности
              <input v-model="cv.availability" type="text" placeholder="01.07.2026" />
            </label>
          </div>

          <div class="footer-actions">
            <button type="button" class="btn-light">Назад</button>
            <button type="button" class="btn-primary">Далее: Детали профиля</button>
          </div>
        </div>

        <aside class="sidebar">
          <div class="side-card profile-card">
            <div class="profile-card__top">
              <div class="profile-avatar">{{ avatarInitials }}</div>
              <div>
                <strong>{{ cv.name || 'Ваше имя' }}</strong>
                <p>{{ cv.role || 'Профессия' }}</p>
              </div>
            </div>
            <div class="profile-meta">
              <span>{{ cv.email || 'email@example.com' }}</span>
              <span>{{ cv.phone || '+000 00 000 000' }}</span>
            </div>
          </div>

          <div class="side-card">
            <div class="side-card__head">
              <strong>Заполненность профиля</strong>
              <span class="shield">✓</span>
            </div>
            <div class="progress-value">{{ progress }}%</div>
            <div class="progress-track">
              <span class="progress-bar" :style="{ width: `${progress}%` }"></span>
            </div>
            <p>Чтобы откликаться на вакансии, заполните все обязательные поля.</p>
          </div>

          <div class="side-card side-card--dashed">
            <h3>Далее: Детали профиля</h3>
            <p>На следующем шаге вы сможете добавить:</p>

            <div class="feature">
              <span class="feature-icon">◌</span>
              <div>
                <strong>Фото профиля</strong>
                <small>Загрузите своё фото</small>
              </div>
            </div>
            <div class="feature">
              <span class="feature-icon">PDF</span>
              <div>
                <strong>Резюме (PDF)</strong>
                <small>Прикрепите ваше резюме</small>
              </div>
            </div>
            <div class="feature">
              <span class="feature-icon">◎</span>
              <div>
                <strong>Сертификаты и лицензии</strong>
                <small>Добавьте документы и подтверждения квалификации</small>
              </div>
            </div>
          </div>
        </aside>
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 100rem;
  margin: 0 auto;
  padding: 2rem 1rem 4rem;
  color: #18212b;
  position: relative;
}

.page::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 18rem;
  border-radius: 1.5rem;
  background:
    radial-gradient(circle at top left, rgba(20, 184, 87, 0.08), transparent 38%),
    linear-gradient(180deg, #fbfdfb 0%, rgba(251, 253, 251, 0) 100%);
  pointer-events: none;
}

.hero,
.builder {
  position: relative;
  z-index: 1;
}

.hero {
  margin-bottom: 1rem;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.title-row h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: #eefaf3;
  color: #179c58;
  font-weight: 700;
}

.steps {
  display: grid;
  grid-template-columns: auto 1fr auto 1fr auto;
  gap: 1rem;
  align-items: center;
  margin-top: 1.5rem;
  padding: 1.1rem 0 0.25rem;
}

.step {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 0;
}

.step strong,
.step small {
  display: block;
}

.step small {
  margin-top: 0.2rem;
  color: #7d8895;
}

.step-index {
  width: 2.6rem;
  height: 2.6rem;
  display: grid;
  place-items: center;
  border: 0.09375rem solid #dbe2ea;
  border-radius: 50%;
  background: #fff;
  font-weight: 800;
}

.step--done .step-index,
.step--active .step-index {
  border-color: transparent;
  background: #14b857;
  color: #fff;
}

.step--active small,
.step--done small {
  color: #14b857;
}

.step-line {
  height: 0.09375rem;
  background: #e6ecf1;
}

.step-line--active {
  background: #14b857;
}

.builder {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 23rem;
  gap: 1.25rem;
  align-items: start;
}

.main-card,
.side-card {
  background: #fff;
  border: 0.09375rem solid #e6ebf1;
  border-radius: 1rem;
  box-shadow: 0 0.75rem 2rem rgba(16, 24, 40, 0.05);
}

.main-card {
  padding: 1.5rem;
}

.card-head h2,
.side-card h3 {
  margin: 0;
}

.card-head p,
.side-card p,
.feature small,
.hint {
  margin: 0.45rem 0 0;
  color: #6d7885;
  line-height: 1.6;
}

.hint {
  font-size: 0.92rem;
}

.section {
  margin-top: 1.4rem;
  padding-top: 0.1rem;
}

.section-label {
  display: block;
  margin-bottom: 0.7rem;
  font-weight: 700;
}

.list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-height: 4.6rem;
  padding: 0.9rem 1rem;
  border: 0.09375rem solid #e7edf3;
  border-radius: 0.85rem;
  background: linear-gradient(180deg, #ffffff 0%, #fcfdfd 100%);
  box-shadow: 0 0.25rem 0.75rem rgba(16, 24, 40, 0.03);
}

.list-row + .list-row {
  margin-top: 0.75rem;
}

.list-row__title,
.list-row__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.list-row__actions {
  flex: 0 0 auto;
}

.list-row__actions select {
  min-width: 9rem;
}

.dot {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: #eefaf3;
  color: #18a957;
  font-weight: 800;
}

.inline-add,
.grid-two {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.inline-add {
  margin-top: 0.85rem;
}

label {
  display: grid;
  gap: 0.45rem;
  color: #27313c;
  font-weight: 600;
}

input,
textarea,
select {
  width: 100%;
  min-width: 0;
  min-height: 3.2rem;
  padding: 0.9rem 1rem;
  border: 0.09375rem solid #dde5ec;
  border-radius: 0.75rem;
  background: linear-gradient(180deg, #ffffff 0%, #fcfdfd 100%);
  color: #18212b;
  font: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

textarea {
  resize: vertical;
  min-height: 7rem;
}

input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: #14b857;
  box-shadow: 0 0 0 0.1875rem rgba(20, 184, 87, 0.1);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 2.8rem;
  padding: 0.7rem 0.85rem;
  border: 0.09375rem solid #dfe8df;
  border-radius: 0.75rem;
  background: #f6fbf7;
  color: #276145;
}

.chip b {
  color: #1a8d4f;
}

.chip button,
.ghost-icon,
.ghost-button,
.btn-light,
.btn-primary {
  border: 0;
  cursor: pointer;
  font: inherit;
}

.chip button,
.ghost-icon {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.5rem;
  background: #fff;
  color: #8892a0;
}

.ghost-button {
  min-height: 3.2rem;
  padding: 0 1rem;
  border: 0.09375rem dashed #b8d4c0;
  border-radius: 0.75rem;
  background: #fff;
  color: #169b57;
  font-weight: 700;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.ghost-button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.ghost-button--small {
  margin-top: 0.75rem;
  min-height: 3rem;
  justify-self: start;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.8rem;
}

.btn-light,
.btn-primary {
  min-height: 3.1rem;
  padding: 0 1.35rem;
  border-radius: 0.75rem;
  font-weight: 700;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.btn-light {
  border: 0.09375rem solid #dde5ec;
  background: #fff;
  color: #27313c;
}

.btn-primary {
  background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%);
  color: #fff;
  box-shadow: 0 0.75rem 1.5rem rgba(20, 184, 87, 0.18);
}

.sidebar {
  display: grid;
  gap: 1rem;
  position: sticky;
  top: 6rem;
}

.side-card {
  padding: 1.35rem;
}

.profile-card {
  display: grid;
  gap: 1rem;
}

.profile-card__top {
  display: grid;
  grid-template-columns: 4.5rem minmax(0, 1fr);
  gap: 0.9rem;
  align-items: center;
}

.profile-card__top p {
  margin: 0.35rem 0 0;
}

.profile-avatar {
  width: 4.5rem;
  height: 4.5rem;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%);
  color: #fff;
  font-size: 1.3rem;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.profile-meta {
  display: grid;
  gap: 0.45rem;
  color: #6d7885;
  font-size: 0.95rem;
}

.side-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.shield,
.feature-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
}

.shield {
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 50%;
  background: #eefaf3;
  color: #14b857;
  font-weight: 800;
}

.progress-value {
  margin-top: 0.9rem;
  color: #14a750;
  font-size: 2.2rem;
  font-weight: 800;
}

.progress-track {
  height: 0.7rem;
  margin-top: 0.8rem;
  overflow: hidden;
  border-radius: 999px;
  background: #edf1f3;
}

.progress-bar {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #0fb152 0%, #17c660 100%);
}

.side-card--dashed {
  border-style: dashed;
  border-color: #98d6b0;
}

.feature {
  display: grid;
  grid-template-columns: 3rem minmax(0, 1fr);
  gap: 0.9rem;
  align-items: center;
  padding: 1rem 0;
}

.feature + .feature {
  border-top: 0.09375rem solid #edf1f4;
}

.feature-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: #eefaf3;
  color: #169b57;
  font-weight: 800;
}

.main-card:hover,
.side-card:hover {
  box-shadow: 0 1rem 2.4rem rgba(16, 24, 40, 0.08);
}

.ghost-button:hover,
.btn-light:hover,
.ghost-icon:hover,
.chip button:hover {
  background: #f7faf8;
}

.btn-primary:hover {
  transform: translateY(-0.0625rem);
  box-shadow: 0 1rem 1.8rem rgba(20, 184, 87, 0.22);
}

.btn-light:hover {
  border-color: #cfd8e2;
}

.ghost-button:hover {
  border-color: #8fc8a5;
  color: #12884a;
}

select {
  appearance: none;
  background-image:
    linear-gradient(45deg, transparent 50%, #7d8895 50%),
    linear-gradient(135deg, #7d8895 50%, transparent 50%);
  background-position:
    calc(100% - 1.15rem) calc(50% - 0.12rem),
    calc(100% - 0.8rem) calc(50% - 0.12rem);
  background-size: 0.4rem 0.4rem, 0.4rem 0.4rem;
  background-repeat: no-repeat;
}

@media (max-width: 72rem) {
  .builder {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
  }
}

@media (max-width: 56rem) {
  .steps,
  .grid-two,
  .inline-add,
  .footer-actions,
  .profile-card__top {
    grid-template-columns: 1fr;
  }

  .steps {
    gap: 0.75rem;
    padding-top: 0.75rem;
  }

  .step-line {
    display: none;
  }

  .list-row,
  .list-row__actions,
  .footer-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .title-row {
    align-items: flex-start;
  }

  .main-card,
  .side-card {
    padding: 1rem;
  }

  .chips {
    gap: 0.5rem;
  }

  .chip,
  .ghost-button--small,
  .btn-primary,
  .btn-light {
    width: 100%;
  }

  .chip {
    justify-content: space-between;
  }
}
</style>
