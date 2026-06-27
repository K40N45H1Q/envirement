<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuth } from '@/stores/auth'
import { getProfile, updateProfile } from '@/api/profile'

const { state } = useAuth()

const profile = ref({
  first_name: '',
  last_name: '',
  phone: '',
  resume_name: '',
  resume_url: '',
  avatar_url: '',
  summary: '',
  current_role: '',
})
const avatarFile = ref(null)
const resumeFile = ref(null)
const isSaving = ref(false)
const isLoading = ref(false)
const saveMessage = ref('')
const errorMessage = ref('')
const avatarObjectUrl = ref('')

const user = computed(() => state.user)
const fullName = computed(() => `${profile.value.first_name || ''} ${profile.value.last_name || ''}`.trim())
const initials = computed(() => {
  if (fullName.value) {
    return fullName.value
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0])
      .join('')
      .toUpperCase()
  }

  return (user.value?.email || 'CV').slice(0, 2).toUpperCase()
})

const accountTypeLabel = computed(() => {
  const type = user.value?.account_type
  if (type === 'user') return 'Соискатель'
  if (type === 'employer') return 'Работодатель'
  if (type === 'admin') return 'Администратор'
  return 'Неизвестно'
})

const avatarPreview = computed(() => avatarObjectUrl.value || profile.value.avatar_url || '')
const profileProgress = computed(() => {
  const fields = [
    profile.value.first_name,
    profile.value.last_name,
    profile.value.phone,
    profile.value.current_role,
    profile.value.summary,
    profile.value.resume_name,
    profile.value.avatar_url || avatarFile.value,
  ]
  const filled = fields.filter(Boolean).length
  return Math.round((filled / fields.length) * 100)
})

const loadProfile = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    profile.value = await getProfile()
  } catch {
    errorMessage.value = 'Не удалось загрузить профиль.'
  } finally {
    isLoading.value = false
  }
}

const revokeAvatarPreview = () => {
  if (avatarObjectUrl.value) {
    URL.revokeObjectURL(avatarObjectUrl.value)
    avatarObjectUrl.value = ''
  }
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

const onDropResume = (event) => {
  const file = event.dataTransfer.files?.[0]
  if (!file) return
  resumeFile.value = file
  profile.value.resume_name = file.name
}

const saveProfileData = async () => {
  isSaving.value = true
  saveMessage.value = ''
  errorMessage.value = ''

  try {
    profile.value = await updateProfile({
      first_name: profile.value.first_name,
      last_name: profile.value.last_name,
      phone: profile.value.phone,
      current_role: profile.value.current_role,
      summary: profile.value.summary,
      avatar: avatarFile.value,
      resume: resumeFile.value,
    })
    avatarFile.value = null
    resumeFile.value = null
    revokeAvatarPreview()
    saveMessage.value = 'Профиль успешно сохранён.'
  } catch {
    errorMessage.value = 'Не удалось сохранить профиль.'
  } finally {
    isSaving.value = false
  }
}

onMounted(loadProfile)
onBeforeUnmount(revokeAvatarPreview)
</script>

<template>
  <main class="page">
    <div v-if="!user" class="not-auth">
      Войдите в аккаунт, чтобы заполнить профиль кандидата.
    </div>

    <template v-else>
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
            <p class="eyebrow">Профиль кандидата</p>
            <h1>{{ fullName || 'Заполните профиль' }}</h1>
            <p>
              Добавьте основную информацию, аватар и резюме, чтобы быстрее откликаться
              на вакансии и выглядеть полноценным кандидатом в кабинете работодателя.
            </p>
          </div>
          <div class="head-badge">
            <strong>{{ profileProgress }}%</strong>
            <span>заполнено</span>
          </div>
        </section>

        <section class="cards">
          <article>
            <strong>{{ accountTypeLabel }}</strong>
            <span>Тип аккаунта</span>
          </article>
          <article>
            <strong>{{ profile.resume_name ? 'Есть' : 'Нет' }}</strong>
            <span>Резюме в профиле</span>
          </article>
          <article>
            <strong>{{ profile.phone ? 'Да' : 'Нет' }}</strong>
            <span>Контактный номер</span>
          </article>
        </section>

        <section class="workspace">
          <section class="panel profile-panel">
            <div class="panel-title">
              <div>
                <p class="eyebrow compact">Основные данные</p>
                <h2>Личная информация</h2>
              </div>
            </div>

            <div v-if="isLoading" class="notice">Загрузка профиля...</div>

            <template v-else>
              <div class="avatar-row">
                <label class="avatar" aria-label="Загрузить аватар">
                  <img v-if="avatarPreview" :src="avatarPreview" alt="Аватар профиля" />
                  <span v-else class="avatar-fallback">{{ initials }}</span>
                  <div class="avatar-hover">Загрузить фото</div>
                  <input type="file" accept="image/*" hidden @change="onAvatarChange" />
                </label>

                <div class="identity">
                  <strong>{{ fullName || user.email }}</strong>
                  <span>{{ user.email }}</span>
                  <span class="identity-role">{{ accountTypeLabel }}</span>
                </div>
              </div>

              <div class="field-grid">
                <label>
                  Имя
                  <input v-model="profile.first_name" type="text" placeholder="Имя" class="input" />
                </label>
                <label>
                  Фамилия
                  <input v-model="profile.last_name" type="text" placeholder="Фамилия" class="input" />
                </label>
              </div>

              <div class="field-grid">
                <label>
                  Номер телефона
                  <input v-model="profile.phone" type="text" placeholder="Номер телефона" class="input" />
                </label>
                <label>
                  Текущая роль
                  <input v-model="profile.current_role" type="text" placeholder="Например, Сварщик MIG/MAG" class="input" />
                </label>
              </div>

              <label>
                О себе
                <textarea
                  v-model="profile.summary"
                  rows="5"
                  placeholder="Коротко опишите опыт, навыки и желаемый тип работы"
                  class="input textarea"
                ></textarea>
              </label>

              <button class="save-btn" :disabled="isSaving" @click="saveProfileData">
                {{ isSaving ? 'Сохранение...' : 'Сохранить профиль' }}
              </button>

              <p v-if="saveMessage" class="status status--success">{{ saveMessage }}</p>
              <p v-if="errorMessage" class="status status--error">{{ errorMessage }}</p>
            </template>
          </section>

          <aside class="side-column">
            <section class="panel side-card">
              <div class="panel-title">
                <div>
                  <p class="eyebrow compact">Резюме</p>
                  <h2>Файлы кандидата</h2>
                </div>
              </div>

              <label
                class="resume-dropzone"
                @dragover.prevent
                @drop.prevent="onDropResume"
              >
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  hidden
                  @change="onResumeChange"
                />

                <div class="drop-title">
                  {{ profile.resume_name || 'Загрузите резюме или сертификаты' }}
                </div>
                <span>PDF, DOC, DOCX. Можно перетащить файл в эту область.</span>
              </label>

              <a
                v-if="profile.resume_url"
                :href="profile.resume_url"
                target="_blank"
                rel="noreferrer"
                class="btn-secondary resume-link"
              >
                Открыть текущее резюме
              </a>
            </section>

            <section class="panel side-card">
              <div class="panel-title">
                <div>
                  <p class="eyebrow compact">Подсказки</p>
                  <h2>Что улучшить</h2>
                </div>
              </div>

              <div class="hint-list">
                <div class="hint-item" :class="{ 'hint-item--done': !!profile.first_name && !!profile.last_name }">
                  <i class="fas fa-circle-check"></i>
                  <span>Добавьте имя и фамилию</span>
                </div>
                <div class="hint-item" :class="{ 'hint-item--done': !!profile.phone }">
                  <i class="fas fa-phone"></i>
                  <span>Укажите номер телефона</span>
                </div>
                <div class="hint-item" :class="{ 'hint-item--done': !!profile.resume_name }">
                  <i class="fas fa-file-arrow-up"></i>
                  <span>Прикрепите резюме</span>
                </div>
                <div class="hint-item" :class="{ 'hint-item--done': !!profile.summary }">
                  <i class="fas fa-user-pen"></i>
                  <span>Добавьте короткое описание о себе</span>
                </div>
              </div>
            </section>
          </aside>
        </section>
      </section>
    </template>
  </main>
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
  transition: background 0.2s ease, color 0.2s ease;
}

.sidebar a:hover,
.sidebar a:focus-visible {
  background: color-mix(in srgb, var(--brand-soft) 60%, transparent);
  color: var(--brand-strong);
}

.sidebar a.router-link-active {
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--brand-base) 22%, transparent),
    color-mix(in srgb, var(--brand-strong) 14%, transparent)
  );
  color: var(--text-primary);
  border: 0.0625rem solid var(--border-strong);
}

.content {
  display: grid;
  gap: 1.25rem;
}

.head {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  align-items: center;
  padding: 1.6rem;
  background:
    radial-gradient(circle at top right, rgba(26, 177, 111, 0.14), transparent 28%),
    var(--surface-primary);
}

.head p:not(.eyebrow) {
  max-width: 46rem;
  margin: 0.7rem 0 0;
  color: var(--text-muted);
  line-height: 1.65;
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

h1,
h2 {
  margin: 0;
  color: var(--text-primary);
}

h1 {
  font-size: clamp(2rem, 4vw, 3rem);
}

.head-badge {
  min-width: 9rem;
  padding: 1rem 1.1rem;
  border: 0.0625rem solid var(--border-strong);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
  text-align: center;
}

.head-badge strong {
  display: block;
  color: var(--brand-strong);
  font-size: 2rem;
}

.head-badge span {
  color: var(--text-muted);
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.cards article {
  padding: 1.25rem;
}

.cards strong {
  display: block;
  color: var(--brand-strong);
  font-size: 1.4rem;
}

.cards span {
  color: var(--text-muted);
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 21rem;
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
  justify-content: space-between;
  align-items: start;
  gap: 1rem;
}

.notice {
  padding: 0.95rem 1rem;
  border: 0.0625rem solid var(--border-strong);
  border-radius: 0.875rem;
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
}

.avatar-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 1rem;
  align-items: center;
}

.avatar {
  width: 6.5rem;
  height: 6.5rem;
  border-radius: 50%;
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  position: relative;
  color: #fff;
  box-shadow: 0 1rem 2rem rgba(21, 149, 93, 0.18);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-fallback {
  font-size: 1.3rem;
  font-weight: 800;
}

.avatar-hover {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.42);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.82rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.avatar:hover .avatar-hover {
  opacity: 1;
}

.identity {
  display: grid;
  gap: 0.25rem;
}

.identity strong {
  font-size: 1.2rem;
  color: var(--text-primary);
}

.identity span {
  color: var(--text-muted);
}

.identity-role {
  color: var(--brand-strong) !important;
  font-weight: 700;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

label {
  display: grid;
  gap: 0.45rem;
  color: var(--text-primary);
  font-weight: 700;
}

.input {
  width: 100%;
  min-width: 0;
  min-height: 3.15rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

.textarea {
  min-height: 8rem;
  resize: vertical;
}

.save-btn,
.resume-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 3rem;
  padding: 0.8rem 1rem;
  border-radius: 0.875rem;
  text-decoration: none;
  font-weight: 800;
}

.save-btn {
  border: none;
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 0.875rem 1.8rem rgba(21, 149, 93, 0.18);
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: wait;
}

.status {
  padding: 0.9rem 1rem;
  border-radius: 0.875rem;
  font-size: 0.95rem;
}

.status--success {
  border: 0.0625rem solid var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 72%, transparent);
  color: var(--brand-strong);
}

.status--error {
  border: 0.0625rem solid rgba(220, 38, 38, 0.14);
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.side-column {
  display: grid;
  gap: 1.25rem;
}

.resume-dropzone {
  padding: 1.15rem;
  border-radius: 1rem;
  border: 0.09375rem dashed var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 55%, white);
  cursor: pointer;
}

.drop-title {
  color: var(--text-primary);
  font-weight: 700;
}

.resume-dropzone span {
  margin-top: 0.35rem;
  color: var(--text-muted);
  line-height: 1.55;
}

.hint-list {
  display: grid;
  gap: 0.75rem;
}

.hint-item {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  padding: 0.85rem 0.95rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  color: var(--text-muted);
  background: color-mix(in srgb, var(--surface-secondary) 88%, transparent);
}

.hint-item i {
  color: var(--brand-strong);
}

.hint-item--done {
  border-color: var(--border-strong);
  color: var(--brand-strong);
}

.not-auth {
  color: var(--text-muted);
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
  .cards,
  .field-grid,
  .avatar-row {
    grid-template-columns: 1fr;
    display: grid;
  }

  .sidebar {
    grid-auto-columns: minmax(12rem, 1fr);
  }

  .page {
    padding-top: 1.25rem;
  }

  .head,
  .panel,
  .cards article {
    padding: 1.15rem;
  }

  .save-btn,
  .resume-link {
    width: 100%;
  }
}
</style>
