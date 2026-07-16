<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { resolveApiUrl } from '@/api/client'
import { useI18n } from '@/i18n'
import AppLayout from '@/components/AppLayout.vue'
import { approveResponseChat, deleteResponse, getResponses } from '@/api/jobs'
import { localizeFullPath } from '@/router/locale'
import { localizeJobTitle } from '@/utils/jobs'

const router = useRouter()
const { language, t } = useI18n()
const responses = ref([])
const status = ref('')
const isLoading = ref(false)
const approvingId = ref(null)

const formatDate = (value) => {
  if (!value) return t('responsesPage.dateMissing')
  const locale = language.value === 'lv' ? 'lv-LV' : language.value === 'en' ? 'en-GB' : 'ru-RU'
  return new Date(value).toLocaleDateString(locale)
}

const resolveResumeUrl = (value) => resolveApiUrl(value)
const resolveSiteCvUrl = (id) => localizeFullPath(`/responses/${id}/cv`, language.value)
const displayJobTitle = (job) => localizeJobTitle(job, language.value)

const loadResponses = async () => {
  isLoading.value = true
  status.value = ''
  try {
    const data = await getResponses()
    responses.value = Array.isArray(data) ? data : []
  } catch {
    status.value = t('responsesPage.loadError')
  } finally {
    isLoading.value = false
  }
}

const approveChat = async (id) => {
  approvingId.value = id
  try {
    await approveResponseChat(id)
    await loadResponses()
    await router.push(`/dashboard?section=messages&application=${id}`)
  } catch {
    status.value = t('responsesPage.approveError')
  } finally {
    approvingId.value = null
  }
}

const remove = async (id) => {
  try {
    await deleteResponse(id)
    responses.value = responses.value.filter((item) => item.id !== id)
  } catch {
    status.value = t('responsesPage.deleteError')
  }
}

onMounted(loadResponses)
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="head">
        <p class="eyebrow">{{ t('responsesPage.eyebrow') }}</p>
        <h1>{{ t('responsesPage.title') }}</h1>
        <p>{{ t('responsesPage.description') }}</p>
      </section>

      <p v-if="status" class="notice">{{ status }}</p>
      <p v-if="isLoading" class="notice">{{ t('responsesPage.loading') }}</p>

      <section class="list">
        <article v-for="item in responses" :key="item.id" class="response-card">
          <div class="avatar">{{ (item.name || 'C')[0] }}{{ (item.surname || 'V')[0] }}</div>

          <div class="main">
            <h2>{{ item.name }} {{ item.surname }}</h2>
            <p>{{ displayJobTitle(item) }} · {{ item.job_company }}</p>
            <span>{{ item.phone }} · {{ item.email }} · {{ t('responsesPage.appliedOn', { date: formatDate(item.created_at) }) }}</span>
            <p v-if="item.message" class="message">{{ item.message }}</p>
            <div v-if="item.candidate_resume_url" class="resume-actions">
              <a
                :href="resolveResumeUrl(item.candidate_resume_url)"
                target="_blank"
                rel="noopener noreferrer"
              >
                {{ t('responsesPage.openResume') }}
              </a>
              <a
                :href="resolveResumeUrl(item.candidate_resume_url)"
                :download="item.candidate_resume_name || true"
                target="_blank"
                rel="noopener noreferrer"
              >
                {{ t('responsesPage.downloadResume') }}
              </a>
            </div>
            <div v-if="item.candidate_has_site_cv" class="resume-actions">
              <a :href="resolveSiteCvUrl(item.id)" target="_blank" rel="noopener noreferrer">
                {{ t('responsesPage.openSiteCv') }}
              </a>
            </div>
          </div>

          <div class="side">
            <strong>{{ item.job_location }}</strong>
            <span>{{ item.job_salary || t('responsesPage.salaryMissing') }}</span>
            <span class="badge" :class="item.chat_approved ? 'active' : 'pending'">
              {{ item.chat_approved ? t('responsesPage.chatActive') : t('responsesPage.chatPending') }}
            </span>
            <button v-if="!item.chat_approved" type="button" @click="approveChat(item.id)">
              {{ approvingId === item.id ? t('responsesPage.approving') : t('responsesPage.approveChat') }}
            </button>
            <button v-else type="button" @click="router.push(`/dashboard?section=messages&application=${item.id}`)">
              {{ t('responsesPage.openMessages') }}
            </button>
            <button type="button" class="danger" @click="remove(item.id)">{{ t('responsesPage.delete') }}</button>
          </div>
        </article>

        <p v-if="!isLoading && !responses.length" class="notice">{{ t('responsesPage.empty') }}</p>
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.page { max-width: 100rem; margin: 0 auto; padding: 2rem 1rem 4rem; }
.head, .response-card, .notice { border: 0.0625rem solid var(--border-subtle); border-radius: 1rem; background: var(--surface-primary); box-shadow: var(--shadow-soft); }
.head, .notice { padding: 1.5rem; }
.eyebrow { margin: 0 0 0.5rem; color: var(--brand-strong); font-weight: 800; text-transform: uppercase; }
h1, h2, p { margin: 0; }
h1 { font-size: clamp(2rem, 4vw, 3rem); }
.list { display: grid; gap: 1rem; margin-top: 1rem; }
.response-card { display: grid; grid-template-columns: 4rem minmax(0, 1fr) 18rem; gap: 1rem; padding: 1.25rem; align-items: center; }
.avatar { width: 4rem; height: 4rem; border-radius: 50%; display: grid; place-items: center; background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%); color: #fff; font-weight: 800; }
.main, .side { display: grid; gap: 0.35rem; }
.main p, .main span, .side span { color: var(--text-muted); }
.message { margin-top: 0.5rem; }
.resume-actions { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 0.35rem; }
.resume-actions a { color: var(--brand-strong); font-weight: 700; text-decoration: none; }
.side strong { color: var(--brand-strong); font-size: 1.05rem; }
.badge { width: fit-content; min-height: 2rem; padding: 0.35rem 0.7rem; border-radius: 999rem; font-size: 0.78rem; font-weight: 800; }
.badge.pending { background: rgba(180, 83, 9, 0.1); color: #92400e; }
.badge.active { background: color-mix(in srgb, var(--brand-soft) 70%, white); color: var(--brand-strong); }
.side button { min-height: 2.8rem; border: 0.0625rem solid var(--border-subtle); border-radius: 0.85rem; background: color-mix(in srgb, var(--brand-soft) 70%, white); color: var(--brand-strong); font: inherit; font-weight: 800; cursor: pointer; }
.side .danger { background: rgba(220, 38, 38, 0.08); color: #b91c1c; }
@media (max-width: 56rem) { .response-card { grid-template-columns: 1fr; } }
</style>
