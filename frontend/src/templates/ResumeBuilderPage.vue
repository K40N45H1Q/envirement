<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import BaseDropdown from '@/components/BaseDropdown.vue'
import { getProfile, updateProfile } from '@/api/profile'
import { useAuth } from '@/stores/auth'

const languageNames = ['Английский', 'Русский', 'Немецкий', 'Польский', 'Латышский', 'Литовский', 'Эстонский', 'Французский']
const languageLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const experienceLabels = ['1-3 года', '3-5 лет', '5+ лет']

const languageOptions = languageNames.map((label) => ({ value: label, label }))
const languageLevelOptions = languageLevels.map((label) => ({ value: label, label }))
const experienceOptions = experienceLabels.map((label) => ({ value: label, label }))
const mobilityOptions = [
  { value: '', label: 'Выберите вариант' },
  { value: 'Максимальная мобильность EU', label: 'Максимальная мобильность EU' },
  { value: 'Готов к переезду', label: 'Готов к переезду' },
  { value: 'Только своя страна', label: 'Только своя страна' },
]
const preferredMobilityOptions = [
  { value: '', label: 'Выберите регион' },
  { value: 'Регион', label: 'Регион' },
  { value: 'Европа', label: 'Европа' },
  { value: 'Удалённо', label: 'Удалённо' },
]
const permitOptions = [
  { value: '', label: 'Выберите вариант' },
  { value: 'EU гражданин', label: 'EU гражданин' },
  { value: 'Есть виза', label: 'Есть виза' },
  { value: 'Нужен sponsorship', label: 'Нужен sponsorship' },
]

const { state } = useAuth()

const step = ref(1)
const isLoaded = ref(false)
const isSaving = ref(false)
const isLoading = ref(false)
const status = ref('')
const avatarFile = ref(null)
const resumeFile = ref(null)
const avatarObjectUrl = ref('')
const newSector = ref('')
const newLanguage = ref(languageOptions[0].value)
const newLanguageLevel = ref(languageLevelOptions[2].value)
const newLicense = ref('')

const profile = ref({
  first_name: '',
  last_name: '',
  phone: '',
  summary: '',
  current_role: '',
  skills: '',
  sectors: [],
  languages: [],
  licenses: [],
  mobility: '',
  preferred_mobility: '',
  work_permit: '',
  availability: '',
  resume_name: '',
  resume_url: '',
  avatar_url: '',
})

let autosaveTimer = null

const user = computed(() => state.user)
const fullName = computed(() => `${profile.value.first_name} ${profile.value.last_name}`.trim())
const avatarPreview = computed(() => avatarObjectUrl.value || profile.value.avatar_url || '')
const profileEmail = computed(() => user.value?.email || '')

const avatarInitials = computed(() => {
  if (fullName.value) {
    return fullName.value
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0])
      .join('')
      .toUpperCase()
  }

  return (profileEmail.value || 'CV').slice(0, 2).toUpperCase()
})

const filledFields = computed(() => {
  const checks = [
    profile.value.first_name,
    profile.value.last_name,
    profile.value.phone,
    profile.value.current_role,
    profile.value.summary,
    profile.value.skills,
    profile.value.sectors.length,
    profile.value.languages.length,
    profile.value.mobility,
    profile.value.work_permit,
    profile.value.availability,
    profile.value.avatar_url || avatarFile.value,
    profile.value.resume_name || resumeFile.value,
  ]

  return checks.filter(Boolean).length
})

const progress = computed(() => Math.round((filledFields.value / 13) * 100))
const canAddLanguage = computed(() => !profile.value.languages.some((language) => (
  language.name === newLanguage.value && language.level === newLanguageLevel.value
)))

const steps = [
  { id: 1, title: 'Основное', subtitle: 'Контакты и позиция' },
  { id: 2, title: 'Опыт', subtitle: 'Навыки и мобильность' },
  { id: 3, title: 'Файлы', subtitle: 'Фото, CV и проверка' },
]

const revokeAvatarPreview = () => {
  if (avatarObjectUrl.value) {
    URL.revokeObjectURL(avatarObjectUrl.value)
    avatarObjectUrl.value = ''
  }
}

const loadProfile = async () => {
  isLoading.value = true
  status.value = ''

  try {
    profile.value = await getProfile()
  } catch {
    status.value = 'Не удалось загрузить профиль.'
  } finally {
    isLoading.value = false
    isLoaded.value = true
  }
}

const buildPayload = () => ({
  first_name: profile.value.first_name,
  last_name: profile.value.last_name,
  phone: profile.value.phone,
  summary: profile.value.summary,
  current_role: profile.value.current_role,
  skills: profile.value.skills,
  sectors_json: profile.value.sectors,
  languages_json: profile.value.languages,
  licenses_json: profile.value.licenses,
  mobility: profile.value.mobility,
  preferred_mobility: profile.value.preferred_mobility,
  work_permit: profile.value.work_permit,
  availability: profile.value.availability,
  avatar: avatarFile.value,
  resume: resumeFile.value,
})

const saveProfile = async ({ silent = false } = {}) => {
  if (!isLoaded.value) return false

  isSaving.value = true
  if (!silent) {
    status.value = ''
  }

  try {
    profile.value = await updateProfile(buildPayload())
    avatarFile.value = null
    resumeFile.value = null
    revokeAvatarPreview()
    status.value = silent ? 'Изменения сохранены автоматически.' : 'Профиль успешно сохранён.'
    return true
  } catch {
    status.value = 'Не удалось сохранить профиль.'
    return false
  } finally {
    isSaving.value = false
  }
}

const scheduleAutosave = () => {
  if (!isLoaded.value) return
  if (autosaveTimer) {
    window.clearTimeout(autosaveTimer)
  }

  autosaveTimer = window.setTimeout(() => {
    saveProfile({ silent: true })
  }, 700)
}

const addSector = () => {
  const name = newSector.value.trim()
  if (!name) return

  profile.value.sectors.push({
    name,
    experience: experienceOptions[0].value,
  })
  newSector.value = ''
}

const removeSector = (index) => {
  profile.value.sectors.splice(index, 1)
}

const addLanguage = () => {
  if (!canAddLanguage.value) return

  profile.value.languages.push({
    name: newLanguage.value,
    level: newLanguageLevel.value,
  })
}

const removeLanguage = (index) => {
  profile.value.languages.splice(index, 1)
}

const addLicense = () => {
  const value = newLicense.value.trim()
  if (!value) return
  profile.value.licenses.push(value)
  newLicense.value = ''
}

const removeLicense = (index) => {
  profile.value.licenses.splice(index, 1)
}

const onAvatarChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  avatarFile.value = file
  revokeAvatarPreview()
  avatarObjectUrl.value = URL.createObjectURL(file)
}

const onResumeChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  resumeFile.value = file
  profile.value.resume_name = file.name
}

const goNext = async () => {
  const saved = await saveProfile()
  if (saved && step.value < 3) {
    step.value += 1
  }
}

const goPrev = () => {
  if (step.value > 1) {
    step.value -= 1
  }
}

watch(
  profile,
  () => {
    scheduleAutosave()
  },
  { deep: true },
)

onMounted(loadProfile)

onBeforeUnmount(() => {
  if (autosaveTimer) {
    window.clearTimeout(autosaveTimer)
  }
  revokeAvatarPreview()
})
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="hero">
        <div class="hero-copy">
          <div class="title-row">
            <h1>Резюме кандидата</h1>
            <span class="badge">Пошаговое заполнение</span>
          </div>

          <p>
            Заполните профиль по шагам: основная информация, опыт и навыки, затем реальные файлы.
            Всё сохраняется в аккаунт и используется в откликах на вакансии.
          </p>
        </div>

        <div class="steps">
          <button
            v-for="item in steps"
            :key="item.id"
            type="button"
            class="step"
            :class="{ 'step--active': step === item.id, 'step--done': step > item.id }"
            @click="step = item.id"
          >
            <span class="step-index">{{ item.id }}</span>
            <span class="step-copy">
              <strong>{{ item.title }}</strong>
              <small>{{ item.subtitle }}</small>
            </span>
          </button>
        </div>
      </section>

      <section class="builder">
        <div class="main-card">
          <div class="card-head">
            <h2 v-if="step === 1">Шаг 1. Основная информация</h2>
            <h2 v-else-if="step === 2">Шаг 2. Опыт и навыки</h2>
            <h2 v-else>Шаг 3. Фото, CV и финальная проверка</h2>
            <p v-if="isLoading">Загрузка профиля...</p>
            <p v-else-if="status" class="hint">{{ isSaving ? 'Сохранение...' : status }}</p>
          </div>

          <template v-if="step === 1">
            <div class="grid-two">
              <label>
                Имя
                <input v-model="profile.first_name" placeholder="Иван" />
              </label>
              <label>
                Фамилия
                <input v-model="profile.last_name" placeholder="Иванов" />
              </label>
              <label>
                Email
                <input :value="profileEmail" disabled />
              </label>
              <label>
                Телефон
                <input v-model="profile.phone" placeholder="+371 2X XXX XXX" />
              </label>
              <label class="grid-span-2">
                Желаемая позиция
                <input v-model="profile.current_role" placeholder="Например, Сварщик MIG/MAG" />
              </label>
              <label class="grid-span-2">
                Ключевые навыки
                <input v-model="profile.skills" placeholder="MIG/MAG, TIG, монтаж, чтение чертежей" />
              </label>
            </div>

            <label>
              О себе
              <textarea
                v-model="profile.summary"
                rows="6"
                placeholder="Кратко опишите ваш опыт, сильные стороны и формат работы, который ищете."
              ></textarea>
            </label>
          </template>

          <template v-else-if="step === 2">
            <div class="section">
              <label class="section-label">Сферы и стаж</label>
              <div v-for="(sector, index) in profile.sectors" :key="`${sector.name}-${index}`" class="list-row">
                <div class="list-row__title">
                  <span class="dot">{{ index + 1 }}</span>
                  <strong>{{ sector.name }}</strong>
                </div>

                <div class="list-row__actions">
                  <BaseDropdown
                    v-model="sector.experience"
                    aria-label="Опыт в сфере"
                    class="inline-dropdown"
                    :options="experienceOptions"
                  />
                  <button type="button" class="ghost-icon" @click="removeSector(index)">×</button>
                </div>
              </div>

              <div class="inline-add">
                <input v-model="newSector" placeholder="Добавить ещё сферу" />
                <button type="button" class="ghost-button" @click="addSector">Добавить</button>
              </div>
            </div>

            <div class="section">
              <label class="section-label">Языки</label>
              <div class="chips">
                <span v-for="(language, index) in profile.languages" :key="`${language.name}-${language.level}-${index}`" class="chip">
                  <span>{{ language.name }}</span>
                  <b>{{ language.level }}</b>
                  <button type="button" @click="removeLanguage(index)">×</button>
                </span>
              </div>

              <div class="grid-two">
                <BaseDropdown
                  v-model="newLanguage"
                  aria-label="Язык"
                  full-width
                  :options="languageOptions"
                />
                <BaseDropdown
                  v-model="newLanguageLevel"
                  aria-label="Уровень языка"
                  full-width
                  :options="languageLevelOptions"
                />
              </div>

              <button type="button" class="ghost-button ghost-button--small" :disabled="!canAddLanguage" @click="addLanguage">
                Добавить язык
              </button>
            </div>

            <div class="grid-two">
              <label>
                Максимальная мобильность
                <BaseDropdown
                  v-model="profile.mobility"
                  aria-label="Максимальная мобильность"
                  full-width
                  :options="mobilityOptions"
                />
              </label>
              <label>
                Предпочтительная мобильность
                <BaseDropdown
                  v-model="profile.preferred_mobility"
                  aria-label="Предпочтительная мобильность"
                  full-width
                  :options="preferredMobilityOptions"
                />
              </label>
              <label>
                Разрешение на работу
                <BaseDropdown
                  v-model="profile.work_permit"
                  aria-label="Разрешение на работу"
                  full-width
                  :options="permitOptions"
                />
              </label>
              <label>
                Дата доступности
                <input v-model="profile.availability" placeholder="01.07.2026" />
              </label>
            </div>

            <div class="section">
              <label class="section-label">Права, лицензии и сертификаты</label>
              <div class="chips">
                <span v-for="(license, index) in profile.licenses" :key="`${license}-${index}`" class="chip">
                  <span>{{ license }}</span>
                  <button type="button" @click="removeLicense(index)">×</button>
                </span>
              </div>

              <div class="inline-add">
                <input v-model="newLicense" placeholder="Например, B, CE, VCA, Forklift" />
                <button type="button" class="ghost-button" @click="addLicense">Добавить</button>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="upload-grid">
              <label class="upload-card avatar-upload">
                <span class="upload-card__title">Аватар кандидата</span>
                <div class="avatar">
                  <img v-if="avatarPreview" class="avatar__image" :src="avatarPreview" alt="Аватар кандидата" />
                  <span v-else>{{ avatarInitials }}</span>
                </div>
                <small>JPG, PNG или WEBP</small>
                <input type="file" accept="image/*" hidden @change="onAvatarChange" />
              </label>

              <label class="upload-card">
                <span class="upload-card__title">CV / документы</span>
                <strong>{{ profile.resume_name || 'Файл ещё не загружен' }}</strong>
                <small>PDF, DOC, DOCX</small>
                <input type="file" accept=".pdf,.doc,.docx" hidden @change="onResumeChange" />
              </label>
            </div>

            <div class="review-card">
              <h3>Проверка перед завершением</h3>
              <ul class="review-list">
                <li><strong>Кандидат:</strong> {{ fullName || 'Не заполнено' }}</li>
                <li><strong>Позиция:</strong> {{ profile.current_role || 'Не заполнено' }}</li>
                <li><strong>Телефон:</strong> {{ profile.phone || 'Не заполнено' }}</li>
                <li><strong>Сфер:</strong> {{ profile.sectors.length }}</li>
                <li><strong>Языков:</strong> {{ profile.languages.length }}</li>
                <li><strong>Документ:</strong> {{ profile.resume_name || 'Не загружен' }}</li>
              </ul>

              <button type="button" class="btn-primary" :disabled="isSaving" @click="saveProfile()">
                {{ isSaving ? 'Сохраняем...' : 'Сохранить резюме' }}
              </button>
            </div>
          </template>

          <div class="footer-actions">
            <button type="button" class="btn-light" :disabled="step === 1" @click="goPrev">Назад</button>
            <button v-if="step < 3" type="button" class="btn-primary" :disabled="isSaving" @click="goNext">
              {{ isSaving ? 'Сохраняем...' : 'Далее' }}
            </button>
          </div>
        </div>

        <aside class="sidebar">
          <div class="side-card profile-card">
            <div class="profile-card__top">
              <div class="profile-avatar">
                <img v-if="avatarPreview" class="profile-avatar__image" :src="avatarPreview" alt="Аватар" />
                <span v-else>{{ avatarInitials }}</span>
              </div>
              <div>
                <strong>{{ fullName || 'Ваше имя' }}</strong>
                <p>{{ profile.current_role || 'Профессия' }}</p>
              </div>
            </div>
            <div class="profile-meta">
              <span>{{ profileEmail || 'email@example.com' }}</span>
              <span>{{ profile.phone || '+000 00 000 000' }}</span>
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
            <p>Готовый профиль ускоряет отклик на вакансии и делает кандидата понятнее работодателю.</p>
          </div>

          <div class="side-card side-card--dashed">
            <h3>Что должно быть в хорошем CV</h3>

            <div class="feature">
              <span class="feature-icon">1</span>
              <div>
                <strong>Понятная роль</strong>
                <small>Укажите специализацию и сильные стороны в нескольких словах.</small>
              </div>
            </div>

            <div class="feature">
              <span class="feature-icon">2</span>
              <div>
                <strong>Опыт и мобильность</strong>
                <small>Добавьте направления, стаж, языки и готовность к переезду.</small>
              </div>
            </div>

            <div class="feature">
              <span class="feature-icon">3</span>
              <div>
                <strong>Реальные файлы</strong>
                <small>Загрузите фото и CV, чтобы профиль был полноценным и готовым к откликам.</small>
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
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 2rem var(--shell-gutter) 4rem;
  display: grid;
  gap: 1.25rem;
}

.hero,
.main-card,
.side-card {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.25rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.hero {
  padding: 1.6rem;
  display: grid;
  gap: 1.3rem;
}

.hero-copy {
  display: grid;
  gap: 0.85rem;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.title-row h1,
.card-head h2,
.review-card h3,
.side-card h3 {
  margin: 0;
  color: var(--text-primary);
}

.title-row h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.08;
}

.badge {
  padding: 0.45rem 0.9rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, white);
  color: var(--brand-strong);
  font-weight: 700;
}

.hero-copy p,
.hint,
.profile-meta,
.side-card p,
.feature small {
  color: var(--text-muted);
  line-height: 1.65;
}

.steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.85rem;
}

.step {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.85rem;
  align-items: center;
  padding: 1rem 1.05rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.step:hover {
  border-color: color-mix(in srgb, var(--brand-base) 24%, var(--border-subtle));
}

.step-copy,
.main-card,
.section {
  display: grid;
}

.step-copy {
  gap: 0.15rem;
}

.step strong,
.step small {
  display: block;
}

.step small {
  color: var(--text-muted);
}

.step-index {
  width: 2.5rem;
  height: 2.5rem;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: #fff;
  border: 0.0625rem solid var(--border-subtle);
  color: var(--text-primary);
  font-weight: 800;
}

.step--active,
.step--done {
  border-color: color-mix(in srgb, var(--brand-base) 26%, var(--border-subtle));
  background: color-mix(in srgb, var(--brand-soft) 44%, white);
}

.step--active .step-index,
.step--done .step-index {
  background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%);
  border-color: transparent;
  color: #fff;
}

.builder {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 23rem;
  gap: 1.25rem;
  align-items: start;
}

.main-card,
.side-card {
  padding: 1.35rem;
}

.main-card {
  gap: 1.35rem;
}

.card-head {
  display: grid;
  gap: 0.4rem;
}

.grid-two,
.inline-add,
.upload-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.grid-span-2 {
  grid-column: 1 / -1;
}

.section {
  gap: 0.85rem;
}

.section-label {
  font-weight: 700;
  color: var(--text-primary);
}

label {
  display: grid;
  gap: 0.45rem;
  color: var(--text-primary);
  font-weight: 600;
}

input,
textarea {
  width: 100%;
  min-width: 0;
  min-height: 3.2rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

textarea {
  min-height: 8rem;
  resize: vertical;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: var(--brand-strong);
  box-shadow: 0 0 0 0.1875rem rgba(20, 184, 87, 0.12);
}

.inline-dropdown {
  min-width: 10rem;
}

.list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background: var(--surface-secondary);
}

.list-row__title,
.list-row__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.dot,
.feature-icon,
.shield {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
}

.dot {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: color-mix(in srgb, var(--brand-soft) 70%, white);
  color: var(--brand-strong);
  font-weight: 800;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 2.8rem;
  padding: 0.7rem 0.85rem;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 14%, var(--border-subtle));
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
  color: var(--brand-strong);
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
  color: var(--text-muted);
}

.ghost-button,
.btn-light,
.btn-primary {
  min-height: 3.1rem;
  padding: 0 1.2rem;
  border-radius: 0.875rem;
  font-weight: 700;
}

.ghost-button {
  border: 0.0625rem dashed color-mix(in srgb, var(--brand-base) 24%, var(--border-subtle));
  background: #fff;
  color: var(--brand-strong);
}

.ghost-button--small {
  width: fit-content;
}

.btn-light {
  border: 0.0625rem solid var(--border-subtle);
  background: #fff;
  color: var(--text-primary);
}

.btn-primary {
  background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%);
  color: #fff;
  box-shadow: 0 0.75rem 1.5rem rgba(20, 184, 87, 0.18);
}

.upload-card {
  display: grid;
  gap: 0.65rem;
  padding: 1.1rem;
  border: 0.0625rem dashed color-mix(in srgb, var(--brand-base) 22%, var(--border-subtle));
  border-radius: 1rem;
  background: color-mix(in srgb, var(--brand-soft) 38%, white);
  cursor: pointer;
}

.upload-card__title {
  color: var(--text-primary);
  font-weight: 700;
}

.avatar,
.profile-avatar {
  width: 5.2rem;
  height: 5.2rem;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 50%;
  background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%);
  color: #fff;
  font-size: 1.3rem;
  font-weight: 800;
  flex: 0 0 5.2rem;
}

.avatar__image,
.profile-avatar__image {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover;
  display: block;
}

.review-card {
  display: grid;
  gap: 1rem;
  padding: 1.1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--surface-secondary) 84%, white);
}

.review-list {
  margin: 0;
  padding-left: 1.2rem;
  color: var(--text-primary);
  line-height: 1.7;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 0.4rem;
}

.sidebar {
  display: grid;
  gap: 1rem;
  position: sticky;
  top: 5.75rem;
}

.profile-card {
  display: grid;
  gap: 0.9rem;
}

.profile-card__top {
  display: grid;
  grid-template-columns: 5.2rem minmax(0, 1fr);
  gap: 0.9rem;
  align-items: center;
}

.profile-card__top p {
  margin: 0.25rem 0 0;
}

.profile-meta {
  display: grid;
  gap: 0.35rem;
}

.side-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.shield {
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 50%;
  background: color-mix(in srgb, var(--brand-soft) 70%, white);
  color: var(--brand-strong);
  font-weight: 800;
}

.progress-value {
  margin-top: 0.9rem;
  color: var(--brand-strong);
  font-size: 2.2rem;
  font-weight: 800;
}

.progress-track {
  height: 0.7rem;
  margin-top: 0.8rem;
  overflow: hidden;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--surface-secondary) 90%, black 4%);
}

.progress-bar {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #0fb152 0%, #17c660 100%);
}

.side-card--dashed {
  border-style: dashed;
}

.feature {
  display: grid;
  grid-template-columns: 3rem minmax(0, 1fr);
  gap: 0.9rem;
  align-items: center;
  padding: 0.85rem 0;
}

.feature + .feature {
  border-top: 0.0625rem solid var(--border-subtle);
}

.feature-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: color-mix(in srgb, var(--brand-soft) 70%, white);
  color: var(--brand-strong);
  font-weight: 800;
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
  .upload-grid {
    grid-template-columns: 1fr;
  }

  .footer-actions,
  .list-row,
  .list-row__actions {
    flex-direction: column;
    align-items: stretch;
  }

  .main-card,
  .side-card,
  .hero {
    padding: 1rem;
  }

  .ghost-button,
  .btn-light,
  .btn-primary,
  .inline-dropdown {
    width: 100%;
  }
}
</style>
