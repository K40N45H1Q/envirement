<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { getProfile, updateProfile } from '@/api/profile'
import { translate, useI18n } from '@/i18n'
import { useAuth } from '@/stores/auth'

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
})

const auth = useAuth()
const { state } = auth
const { language } = useI18n()

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
const avatarObjectUrl = ref('')
const isLoading = ref(false)
const isSaving = ref(false)
const saveMessage = ref('')
const errorMessage = ref('')

const user = computed(() => state.user)

const copy = computed(() => translate('profilePage', {}, language.value))

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
  if (type === 'user') return copy.value.accountCandidate
  if (type === 'employer') return copy.value.accountEmployer
  if (type === 'admin') return copy.value.accountAdmin
  return copy.value.accountFallback
})

const profileEyebrow = computed(() => {
  if (user.value?.account_type === 'employer') return copy.value.employerProfile
  if (user.value?.account_type === 'admin') return copy.value.adminProfile
  return copy.value.candidateProfile
})

const profileDescription = computed(() => {
  if (user.value?.account_type === 'employer') {
    return copy.value.profileDescriptionEmployer
  }
  if (user.value?.account_type === 'admin') {
    return copy.value.profileDescriptionAdmin
  }
  return copy.value.profileDescriptionCandidate
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
  return Math.round((fields.filter(Boolean).length / fields.length) * 100)
})

const profileHints = computed(() => [
  {
    icon: 'fas fa-circle-check',
    text:
      profile.value.first_name && profile.value.last_name
        ? copy.value.hintNameDone
        : copy.value.hintNameTodo,
    done: !!profile.value.first_name && !!profile.value.last_name,
  },
  {
    icon: 'fas fa-phone',
    text: profile.value.phone ? copy.value.hintPhoneDone : copy.value.hintPhoneTodo,
    done: !!profile.value.phone,
  },
  {
    icon: 'fas fa-file-arrow-up',
    text: profile.value.resume_name ? copy.value.hintResumeDone : copy.value.hintResumeTodo,
    done: !!profile.value.resume_name,
  },
  {
    icon: 'fas fa-user-pen',
    text: profile.value.summary ? copy.value.hintSummaryDone : copy.value.hintSummaryTodo,
    done: !!profile.value.summary,
  },
])

async function loadProfile() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    profile.value = await getProfile()
  } catch {
    errorMessage.value = copy.value.loadProfileError
  } finally {
    isLoading.value = false
  }
}

function revokeAvatarPreview() {
  if (avatarObjectUrl.value) {
    URL.revokeObjectURL(avatarObjectUrl.value)
    avatarObjectUrl.value = ''
  }
}

function onAvatarChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  avatarFile.value = file
  revokeAvatarPreview()
  avatarObjectUrl.value = URL.createObjectURL(file)
}

function onResumeChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  resumeFile.value = file
  profile.value.resume_name = file.name
}

function onDropResume(event) {
  const file = event.dataTransfer.files?.[0]
  if (!file) return
  resumeFile.value = file
  profile.value.resume_name = file.name
}

async function saveProfileData() {
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
    await auth.loadUser({ force: true })
    avatarFile.value = null
    resumeFile.value = null
    revokeAvatarPreview()
    saveMessage.value = copy.value.saveProfileSuccess
  } catch {
    errorMessage.value = copy.value.saveProfileError
  } finally {
    isSaving.value = false
  }
}

onMounted(loadProfile)
onBeforeUnmount(revokeAvatarPreview)
</script>

<template>
  <main class="page" :class="{ 'page--embedded': props.embedded }">
    <div v-if="!user" class="not-auth">{{ copy.notAuth }}</div>

    <template v-else>
      <aside v-if="!props.embedded" class="sidebar">
        <RouterLink to="/messages"><i class="fas fa-message"></i> {{ copy.navMessages }}</RouterLink>
        <RouterLink to="/profile"><i class="fas fa-user"></i> {{ copy.navProfile }}</RouterLink>
        <RouterLink to="/jobs"><i class="fas fa-briefcase"></i> {{ copy.navJobs }}</RouterLink>
        <RouterLink to="/createcv"><i class="fas fa-file-lines"></i> {{ copy.navResume }}</RouterLink>
      </aside>

      <section class="content">
        <section v-if="!props.embedded" class="head">
          <div>
            <p class="eyebrow">{{ profileEyebrow }}</p>
            <h1>{{ fullName || copy.fillProfile }}</h1>
            <p>{{ profileDescription }}</p>
          </div>
          <div class="head-badge">
            <strong>{{ profileProgress }}%</strong>
            <span>{{ copy.completed }}</span>
          </div>
        </section>

        <section v-if="!props.embedded" class="cards">
          <article>
            <strong>{{ accountTypeLabel }}</strong>
            <span>{{ copy.accountType }}</span>
          </article>
          <article>
            <strong>{{ profile.resume_name ? copy.present : copy.no }}</strong>
            <span>{{ copy.filesInProfile }}</span>
          </article>
          <article>
            <strong>{{ profile.phone ? copy.yes : copy.no }}</strong>
            <span>{{ copy.contactPhone }}</span>
          </article>
        </section>

        <section class="workspace">
          <section class="panel profile-panel">
            <div class="panel-title">
              <div>
                <p class="eyebrow compact">{{ copy.mainData }}</p>
                <h2>{{ copy.personalInformation }}</h2>
              </div>
            </div>

            <div v-if="isLoading" class="notice">{{ copy.loadingProfile }}</div>

            <template v-else>
              <div class="avatar-row">
                <label class="avatar" :aria-label="copy.uploadAvatar">
                  <img v-if="avatarPreview" :src="avatarPreview" :alt="copy.profileAvatar" />
                  <span v-else class="avatar-fallback">{{ initials }}</span>
                  <div class="avatar-hover">{{ copy.uploadPhoto }}</div>
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
                  {{ copy.firstName }}
                  <input v-model="profile.first_name" type="text" :placeholder="copy.firstName" class="input" />
                </label>
                <label>
                  {{ copy.lastName }}
                  <input v-model="profile.last_name" type="text" :placeholder="copy.lastName" class="input" />
                </label>
              </div>

              <div class="field-grid">
                <label>
                  {{ copy.phone }}
                  <input v-model="profile.phone" type="text" :placeholder="copy.phone" class="input" />
                </label>
                <label>
                  {{ copy.currentRole }}
                  <input
                    v-model="profile.current_role"
                    type="text"
                    :placeholder="copy.currentRolePlaceholder"
                    class="input"
                  />
                </label>
              </div>

              <label class="summary-label">
                {{ copy.about }}
                <textarea
                  v-model="profile.summary"
                  rows="5"
                  :placeholder="copy.aboutPlaceholder"
                  class="input textarea"
                ></textarea>
              </label>

              <button class="btn-primary save-btn" :disabled="isSaving" @click="saveProfileData">
                {{ isSaving ? copy.saving : copy.saveProfile }}
              </button>

              <p v-if="errorMessage" class="status status--error">{{ errorMessage }}</p>
            </template>
          </section>

          <aside class="side-column">
            <section class="panel side-card">
              <div class="panel-title">
                <div>
                  <p class="eyebrow compact">{{ copy.files }}</p>
                  <h2>{{ copy.resumeAndDocuments }}</h2>
                </div>
              </div>

              <label class="resume-dropzone" @dragover.prevent @drop.prevent="onDropResume">
                <input type="file" accept=".pdf,.doc,.docx" hidden @change="onResumeChange" />
                <div class="drop-title">{{ profile.resume_name || copy.uploadResume }}</div>
                <span>{{ copy.dropHint }}</span>
              </label>

              <a
                v-if="profile.resume_url"
                :href="profile.resume_url"
                target="_blank"
                rel="noreferrer"
                class="btn-secondary resume-link"
              >
                {{ copy.openCurrentFile }}
              </a>
            </section>

            <section class="panel side-card">
              <div class="panel-title">
                <div>
                  <p class="eyebrow compact">{{ copy.hints }}</p>
                  <h2>{{ copy.improve }}</h2>
                </div>
              </div>

              <div class="hint-list">
                <div v-for="hint in profileHints" :key="hint.text" class="hint-item" :class="{ 'hint-item--done': hint.done }">
                  <i :class="hint.icon"></i>
                  <span>{{ hint.text }}</span>
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
  gap: 1.5rem;
}

.page--embedded {
  width: 100%;
  padding: 0;
  grid-template-columns: 1fr;
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
  border: 0.0625rem solid var(--border-strong);
}

.content {
  display: grid;
  gap: 1.5rem;
}

.head {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  align-items: center;
  padding: 1.75rem;
  background: radial-gradient(circle at top right, rgba(26, 177, 111, 0.14), transparent 28%), var(--surface-primary);
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

h2 {
  font-size: 1.35rem;
  font-weight: 700;
}

.head-badge {
  min-width: 9rem;
  padding: 1rem 1.1rem;
  border: 0.0625rem solid var(--border-strong);
  border-radius: 1rem;
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
  text-align: center;
  flex-shrink: 0;
}

.head-badge strong {
  display: block;
  color: var(--brand-strong);
  font-size: 2rem;
}

.head-badge span,
.cards span,
.identity span,
.resume-dropzone span {
  color: var(--text-muted);
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.cards article {
  padding: 1.5rem;
}

.cards strong {
  display: block;
  color: var(--brand-strong);
  font-size: 1.4rem;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 22rem;
  gap: 1.5rem;
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.5rem;
}

.side-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.side-card {
  height: 100%;
  display: flex;
  justify-content: center;
}

.panel-title {
  display: flex;
  justify-content: space-between;
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
  overflow: hidden;
  position: relative;
  color: #fff;
  cursor: pointer;
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

label,
.summary-label {
  display: grid;
  gap: 0.45rem;
  color: var(--text-primary);
  font-weight: 700;
}

.input {
  width: 100%;
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
  min-height: 3rem;
}

.status {
  padding: 0.9rem 1rem;
  border-radius: 0.875rem;
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

.resume-dropzone {
  padding: 1.15rem;
  border-radius: 1rem;
  border: 0.09375rem dashed var(--border-strong);
  background: color-mix(in srgb, var(--brand-soft) 55%, white);
  cursor: pointer;
  text-align: center;
}

.drop-title {
  color: var(--text-primary);
  font-weight: 700;
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
    display: none;
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

  .head,
  .panel,
  .cards article {
    padding: 1.25rem;
  }

  .save-btn,
  .resume-link {
    width: 100%;
  }
}
</style>
