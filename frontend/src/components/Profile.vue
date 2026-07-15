<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { getProfile } from '@/api/profile'
import { translate, useI18n } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useCvBuilderStore } from '@/stores/cvBuilder'

defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
})

const { state } = useAuth()
const cvBuilder = useCvBuilderStore()
const { language } = useI18n()
const profileCopy = computed(() => translate('profilePage', {}, language.value))

const profile = ref({ resume_data: {} })
const cvDocument = ref(null)
const isLoading = ref(false)
const isPrinting = ref(false)
const errorMessage = ref('')
let printFrame = null

const user = computed(() => state.user)
const resume = computed(() => (
  profile.value.resume_data && typeof profile.value.resume_data === 'object'
    ? profile.value.resume_data
    : {}
))
const cvLocale = computed(() => {
  const selected = String(resume.value.cv_language || '').toLowerCase()
  if (selected === 'ru' || selected === 'russian') return 'ru'
  if (selected === 'en' || selected === 'english') return 'en'
  if (selected === 'lv' || selected === 'latvian') return 'lv'
  return language.value
})
const cvCopy = computed(() => translate('resumeBuilderPage', {}, cvLocale.value))
const cvSectionTitle = (key) => translate(`resumeBuilderPage.${key}`, {}, cvLocale.value)
const hasCv = computed(() => Object.keys(resume.value).length > 0)
const fullName = computed(() => (
  `${profile.value.first_name || ''} ${profile.value.last_name || ''}`.trim()
  || user.value?.email
  || cvCopy.value.candidateName
))
const initials = computed(() => fullName.value
  .split(/\s+/)
  .slice(0, 2)
  .map((part) => part[0])
  .join('')
  .toUpperCase())
const workEntries = computed(() => (
  resume.value.no_work_experience
    ? []
    : (Array.isArray(resume.value.work_experiences) ? resume.value.work_experiences : [])
      .filter((item) => item?.position || item?.company_name || item?.description)
))
const educationEntries = computed(() => (
  (Array.isArray(resume.value.educations) ? resume.value.educations : [])
    .filter((item) => item?.level || item?.institution || item?.speciality)
))
const mainRole = computed(() => (
  workEntries.value[0]?.position
  || profile.value.current_role
  || cvCopy.value.candidateRole
))
const contacts = computed(() => [
  profile.value.email || user.value?.email,
  ...(Array.isArray(resume.value.additional_emails) ? resume.value.additional_emails : []),
  profile.value.phone,
  ...(Array.isArray(resume.value.additional_phones) ? resume.value.additional_phones : []),
].filter(Boolean))
const skills = computed(() => {
  if (Array.isArray(profile.value.skills)) return profile.value.skills.filter(Boolean)
  return String(profile.value.skills || '').split(/[,;\n]/).map((item) => item.trim()).filter(Boolean)
})
const languages = computed(() => (
  Array.isArray(profile.value.languages) ? profile.value.languages.filter((item) => item?.name) : []
))
const licenses = computed(() => (
  [...new Set([
    ...(Array.isArray(resume.value.driving_licenses) ? resume.value.driving_licenses : []),
    ...(Array.isArray(profile.value.licenses) ? profile.value.licenses : []),
  ])].filter(Boolean)
))

const localeValue = (catalog, value) => {
  const item = catalog[value]
  if (!item) return value || cvCopy.value.notSpecified
  return item[cvLocale.value] || item.en
}

const languageNames = {
  lv: { ru: 'Латышский', en: 'Latvian', lv: 'Latviešu' },
  latvian: { ru: 'Латышский', en: 'Latvian', lv: 'Latviešu' },
  ru: { ru: 'Русский', en: 'Russian', lv: 'Krievu' },
  russian: { ru: 'Русский', en: 'Russian', lv: 'Krievu' },
  en: { ru: 'Английский', en: 'English', lv: 'Angļu' },
  english: { ru: 'Английский', en: 'English', lv: 'Angļu' },
  german: { ru: 'Немецкий', en: 'German', lv: 'Vācu' },
  polish: { ru: 'Польский', en: 'Polish', lv: 'Poļu' },
  lithuanian: { ru: 'Литовский', en: 'Lithuanian', lv: 'Lietuviešu' },
  estonian: { ru: 'Эстонский', en: 'Estonian', lv: 'Igauņu' },
  french: { ru: 'Французский', en: 'French', lv: 'Franču' },
}
const educationNames = {
  primary: { ru: 'Начальное', en: 'Primary', lv: 'Pamatizglītība' },
  secondary: { ru: 'Среднее', en: 'Secondary', lv: 'Vidējā izglītība' },
  vocational: { ru: 'Профессиональное', en: 'Vocational', lv: 'Profesionālā izglītība' },
  bachelor: { ru: 'Бакалавр', en: 'Bachelor', lv: 'Bakalaurs' },
  master: { ru: 'Магистр', en: 'Master', lv: 'Maģistrs' },
  phd: { ru: 'PhD', en: 'PhD', lv: 'PhD' },
}
const genderNames = {
  female: { ru: 'Женщина', en: 'Female', lv: 'Sieviete' },
  male: { ru: 'Мужчина', en: 'Male', lv: 'Vīrietis' },
  other: { ru: 'Другой', en: 'Other', lv: 'Cits' },
}

const formatDate = (value) => {
  const text = String(value || '').trim()
  if (!text) return ''
  if (/^\d{4}-\d{2}-\d{2}$/.test(text)) {
    const [year, month, day] = text.split('-')
    return `${day}.${month}.${year}`
  }
  return text
}
const dateRange = (entry) => {
  const start = formatDate(entry?.start_date)
  const end = entry?.current ? cvCopy.value.present : formatDate(entry?.end_date)
  return [start, end].filter(Boolean).join(' — ')
}
const formatExperience = (value) => String(value || '')
  .replace(/_years?$/, '')
  .replace('_year', '')
  .replaceAll('_', ' ')
  .replace(/^(\d+)$/, '$1+')

const additionalDetails = computed(() => [
  !resume.value.hide_birth_date && resume.value.birth_date && {
    label: cvCopy.value.birthDate,
    value: formatDate(resume.value.birth_date),
  },
  !resume.value.hide_gender && resume.value.gender && {
    label: cvCopy.value.gender,
    value: localeValue(genderNames, resume.value.gender),
  },
  resume.value.communication_language && {
    label: cvCopy.value.communicationLanguage,
    value: localeValue(languageNames, resume.value.communication_language),
  },
  resume.value.citizenship && {
    label: cvCopy.value.citizenship,
    value: resume.value.citizenship,
  },
  resume.value.no_driving_license && {
    label: cvCopy.value.drivingLicenses,
    value: cvCopy.value.noDrivingLicense,
  },
].filter(Boolean))

const avatarPreview = computed(() => profile.value.avatar_url || '')
const displayCvName = fullName
const avatarInitials = initials
const displayCvRole = mainRole
const cvWorkExperiences = workEntries
const cvEducations = educationEntries
const cvContactItems = computed(() => contacts.value.map((value) => ({
  value,
  icon: String(value).includes('@') ? 'far fa-envelope' : 'fas fa-phone',
})))
const cvSummaryParagraphs = computed(() => {
  const text = String(workEntries.value[0]?.description || profile.value.summary || '').trim()
  return text ? text.split(/\n{2,}/).filter(Boolean).slice(0, 2) : [cvCopy.value.summaryFallback]
})
const cvVisibleSectors = computed(() => (
  Array.isArray(profile.value.sectors) ? profile.value.sectors : []
).filter(Boolean).slice(0, 6).map((sector) => ({
  value: sector?.value || sector?.id || sector?.label || String(sector),
  label: sector?.label || sector?.name || sector?.value || String(sector),
  experience: formatExperience(sector?.experience),
  iconClass: sector?.iconClass || 'fas fa-layer-group',
})))
const cvMoreSectorsCount = computed(() => Math.max(0, (profile.value.sectors?.length || 0) - cvVisibleSectors.value.length))
const cvVisibleSkills = computed(() => skills.value.slice(0, 10))
const cvMoreSkillsCount = computed(() => Math.max(0, skills.value.length - cvVisibleSkills.value.length))
const cvVisibleLanguages = computed(() => languages.value.slice(0, 5))
const cvMoreLanguagesCount = computed(() => Math.max(0, languages.value.length - cvVisibleLanguages.value.length))
const cvVisibleLicenses = computed(() => licenses.value.slice(0, 5))
const cvMoreLicensesCount = computed(() => Math.max(0, licenses.value.length - cvVisibleLicenses.value.length))
const cvAdditionalItems = computed(() => additionalDetails.value.map((item, index) => ({
  ...item,
  icon: ['far fa-calendar', 'fas fa-user', 'fas fa-globe', 'fas fa-passport', 'fas fa-car-side'][index] || 'fas fa-circle-info',
})))
const displayLanguageName = (value) => localeValue(languageNames, value)
const displayEducation = (value) => localeValue(educationNames, value)
const displaySectorExperience = formatExperience
const categoryLabel = (value) => value
const cvId = computed(() => {
  const source = `${fullName.value}|${profile.value.email || user.value?.email || ''}`
  let hash = 0
  for (let index = 0; index < source.length; index += 1) hash = ((hash << 5) - hash) + source.charCodeAt(index)
  return `CVH-${(Math.abs(hash) % 900000) + 100000}`
})
const cvQrCells = computed(() => Array.from({ length: 121 }, (_, index) => {
  const row = Math.floor(index / 11)
  const column = index % 11
  const corner = (row < 3 && column < 3) || (row < 3 && column > 7) || (row > 7 && column < 3)
  return corner || ((index * 17 + Number(cvId.value.slice(-3))) % 7 < 3)
}))
const formatMore = (_key, count) => `+${count}`

async function loadProfile() {
  if (!user.value) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    profile.value = await getProfile()
  } catch {
    errorMessage.value = profileCopy.value.loadProfileError
  } finally {
    isLoading.value = false
  }
}

function cleanupPrintFrame() {
  if (!printFrame) return
  printFrame.remove()
  printFrame = null
}

async function downloadCv() {
  if (!cvDocument.value || isPrinting.value) return
  isPrinting.value = true
  await nextTick()
  cleanupPrintFrame()

  const iframe = document.createElement('iframe')
  iframe.setAttribute('aria-hidden', 'true')
  iframe.style.cssText = 'position:fixed;left:-10000px;top:0;width:210mm;height:297mm;border:0;opacity:0;pointer-events:none;background:#fff;'
  document.body.appendChild(iframe)
  printFrame = iframe

  const printWindow = iframe.contentWindow
  const printDocument = printWindow?.document
  if (!printWindow || !printDocument) {
    cleanupPrintFrame()
    isPrinting.value = false
    return
  }

  printDocument.open()
  printDocument.write('<!doctype html><html><head><title>CV</title></head><body></body></html>')
  printDocument.close()
  document.querySelectorAll('link[rel="stylesheet"], style').forEach((node) => {
    printDocument.head.appendChild(node.cloneNode(true))
  })
  const printStyle = printDocument.createElement('style')
  printStyle.textContent = '@page{size:A4;margin:0}html,body{margin:0!important;padding:0!important;background:#fff!important}.cv-document{width:210mm!important;min-width:210mm!important;height:auto!important;min-height:0!important;margin:0!important;padding:1.45rem 1.7rem 1.15rem!important;border:0!important;border-radius:0!important;box-shadow:none!important;overflow:visible!important}.cv-header,.cv-top,.cv-footer{display:flex!important;flex-direction:row!important;justify-content:space-between!important}.cv-header,.cv-footer{align-items:center!important}.cv-top{align-items:flex-start!important}.cv-brand{flex-direction:row!important;flex-wrap:nowrap!important}.cv-header .cv-brand__logo{width:34mm!important;max-width:34mm!important;height:9mm!important;max-height:9mm!important;object-fit:contain!important;object-position:left center!important}.cv-footer .cv-brand__logo{width:24mm!important;max-width:24mm!important;height:6mm!important;max-height:6mm!important;object-fit:contain!important;object-position:left center!important}.cv-person{grid-template-columns:4.25rem minmax(0,1fr)!important}.cv-id{justify-items:center!important}.cv-body{grid-template-columns:minmax(0,1.34fr) minmax(12.5rem,.82fr)!important;overflow:visible!important}.cv-main{padding-right:1.25rem!important;border-right:.0625rem solid #d9dee7!important;overflow:visible!important}.cv-aside{overflow:visible!important}.cv-sector-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}*{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}'
  printDocument.head.appendChild(printStyle)
  printDocument.body.appendChild(cvDocument.value.cloneNode(true))

  try {
    await printDocument.fonts?.ready
  } catch {
    // The browser can still print with its fallback font.
  }

  const finish = () => {
    window.setTimeout(cleanupPrintFrame, 250)
    isPrinting.value = false
  }
  printWindow.addEventListener('afterprint', finish, { once: true })
  printWindow.focus()
  printWindow.print()
  window.setTimeout(() => {
    if (isPrinting.value) finish()
  }, 1500)
}

onMounted(loadProfile)
</script>

<template>
  <main class="cv-profile-page">
    <div v-if="!user" class="state-card">
      <i class="fas fa-lock"></i>
      <h1>{{ profileCopy.notAuth }}</h1>
    </div>

    <div v-else-if="isLoading" class="state-card">
      <span class="loader" aria-hidden="true"></span>
      <h1>{{ profileCopy.loadingProfile }}</h1>
    </div>

    <div v-else-if="errorMessage" class="state-card state-card--error">
      <i class="fas fa-triangle-exclamation"></i>
      <h1>{{ errorMessage }}</h1>
      <button type="button" class="primary-button" @click="loadProfile">
        <i class="fas fa-rotate-right"></i>{{ profileCopy.tryAgain }}
      </button>
    </div>

    <div v-else-if="!hasCv" class="state-card">
      <i class="far fa-file-lines"></i>
      <h1>{{ profileCopy.cvMissing }}</h1>
      <p>{{ profileCopy.cvMissingDescription }}</p>
      <button type="button" class="primary-button" @click="cvBuilder.open">
        <i class="fas fa-plus"></i>{{ profileCopy.createCv }}
      </button>
    </div>

    <template v-else>
      <div class="cv-toolbar">
        <div>
          <span><i class="fas fa-circle-check"></i>{{ profileCopy.cvReady }}</span>
          <h1>{{ profileCopy.myCv }}</h1>
        </div>
        <button type="button" class="primary-button" :disabled="isPrinting" @click="downloadCv">
          <i :class="isPrinting ? 'fas fa-spinner fa-spin' : 'fas fa-download'"></i>
          {{ cvCopy.downloadPdf }}
        </button>
      </div>

      <article ref="cvDocument" class="cv-document">
        <header class="cv-header">
          <div class="cv-brand" aria-label="CVHOLD">
            <img src="/logo-pdf.png" alt="" class="cv-brand__logo" aria-hidden="true" />
          </div>
          <div class="cv-verified">
            <i class="fas fa-circle-check" aria-hidden="true"></i>
            <span><strong>{{ cvCopy.cvDocument }}</strong><small>{{ cvCopy.verifiedCv }}</small></span>
          </div>
        </header>

        <section class="cv-top">
          <div class="cv-person">
            <div class="cv-avatar">
              <img v-if="avatarPreview" :src="avatarPreview" :alt="displayCvName" />
              <span v-else>{{ avatarInitials }}</span>
            </div>
            <div>
              <h1>{{ displayCvName }}</h1>
              <p>{{ displayCvRole }}</p>
              <ul class="cv-contact-list">
                <li v-for="(item, index) in cvContactItems" :key="`${item.icon}-${index}`">
                  <i :class="item.icon"></i><span>{{ item.value }}</span>
                </li>
              </ul>
            </div>
          </div>

          <div class="cv-id">
            <div class="cv-qr" aria-hidden="true">
              <span v-for="(active, index) in cvQrCells" :key="index" class="cv-qr-cell" :class="{ 'cv-qr-cell--active': active }"></span>
              <strong>CV</strong>
            </div>
            <small>CVHOLD ID</small>
            <strong>{{ cvId }}</strong>
          </div>
        </section>

        <section class="cv-body">
          <main class="cv-main">
            <section class="cv-section cv-section--summary">
              <h2>{{ cvSectionTitle('aboutMe') }}</h2>
              <p v-for="paragraph in cvSummaryParagraphs" :key="paragraph" class="cv-summary-text">{{ paragraph }}</p>
            </section>

            <section v-if="cvWorkExperiences.length" class="cv-section">
              <h2>{{ cvSectionTitle('workExperience') }}</h2>
              <div v-for="(work, index) in cvWorkExperiences" :key="`cv-work-${index}`" class="cv-entry">
                <p class="cv-summary-text"><strong>{{ work.position }}</strong><span v-if="work.company_name"> · {{ work.company_name }}</span></p>
                <p class="cv-summary-text">
                  {{ formatDate(work.start_date) }} — {{ work.current ? cvCopy.present : formatDate(work.end_date) }}
                  <span v-if="work.job_category"> · {{ categoryLabel(work.job_category) }}</span>
                  <span v-if="work.country"> · {{ work.country }}</span>
                  <span v-if="work.experience_years"> · {{ cvCopy.totalExperience }}: {{ displaySectorExperience(work.experience_years) }}</span>
                </p>
                <p v-if="work.description" class="cv-summary-text">{{ work.description }}</p>
              </div>
            </section>

            <section v-if="cvEducations.length" class="cv-section">
              <h2>{{ cvSectionTitle('education') }}</h2>
              <div v-for="(education, index) in cvEducations" :key="`cv-education-${index}`" class="cv-entry">
                <p class="cv-summary-text"><strong>{{ education.institution }}</strong></p>
                <p class="cv-summary-text">
                  {{ displayEducation(education.level) }}
                  <span v-if="education.speciality"> · {{ education.speciality }}</span>
                  <span v-if="education.second_speciality"> · {{ education.second_speciality }}</span>
                  <span v-if="education.country"> · {{ education.country }}</span>
                  <span v-if="education.start_date || education.end_date"> · {{ formatDate(education.start_date) }}—{{ education.current ? cvCopy.present : formatDate(education.end_date) }}</span>
                </p>
                <p v-if="education.additional_information" class="cv-summary-text">{{ education.additional_information }}</p>
              </div>
            </section>

            <section v-if="cvVisibleSectors.length" class="cv-section">
              <h2>{{ cvSectionTitle('workAreas') }}</h2>
              <div class="cv-sector-grid">
                <div v-for="sector in cvVisibleSectors" :key="sector.value" class="cv-sector">
                  <i :class="sector.iconClass"></i>
                  <span class="cv-sector__copy"><strong>{{ sector.label }}</strong><small>{{ sector.experience }}</small></span>
                </div>
                <div v-if="cvMoreSectorsCount" class="cv-sector cv-more-item"><span>{{ formatMore('moreItems', cvMoreSectorsCount) }}</span></div>
              </div>
            </section>

            <section v-if="cvVisibleSkills.length" class="cv-section">
              <h2>{{ cvSectionTitle('skills') }}</h2>
              <ul class="cv-list">
                <li v-for="skill in cvVisibleSkills" :key="skill">{{ skill }}</li>
                <li v-if="cvMoreSkillsCount" class="cv-more-item">{{ formatMore('moreItems', cvMoreSkillsCount) }}</li>
              </ul>
            </section>
          </main>

          <aside class="cv-aside">
            <section v-if="cvVisibleLanguages.length" class="cv-section">
              <h2>{{ cvSectionTitle('languages') }}</h2>
              <ul class="cv-list">
                <li v-for="item in cvVisibleLanguages" :key="`${item.name}-${item.level}`">{{ displayLanguageName(item.name) }} — {{ item.level }}</li>
                <li v-if="cvMoreLanguagesCount" class="cv-more-item">{{ formatMore('moreItems', cvMoreLanguagesCount) }}</li>
              </ul>
            </section>

            <section v-if="cvVisibleLicenses.length" class="cv-section">
              <h2>{{ cvSectionTitle('certificatesAndLicenses') }}</h2>
              <ul class="cv-list">
                <li v-for="license in cvVisibleLicenses" :key="license">{{ license }}</li>
                <li v-if="cvMoreLicensesCount" class="cv-more-item">{{ formatMore('moreItems', cvMoreLicensesCount) }}</li>
              </ul>
            </section>

            <section class="cv-section">
              <h2>{{ cvSectionTitle('additionalDetails') }}</h2>
              <ul class="cv-extra-list">
                <li v-for="item in cvAdditionalItems" :key="item.label"><i :class="item.icon"></i><span>{{ item.label }}: {{ item.value }}</span></li>
              </ul>
            </section>
          </aside>
        </section>

        <footer class="cv-footer">
          <div class="cv-brand cv-brand--small" aria-label="CVHOLD"><img src="/logo-pdf.png" alt="" class="cv-brand__logo" aria-hidden="true" /></div>
          <span>{{ cvCopy.cvFooterTagline }}</span><span>www.cvhold.com</span>
        </footer>
      </article>
    </template>
  </main>
</template>

<style scoped>
.cv-profile-page {
  --green: #10a558;
  --green-dark: #087c40;
  --ink: #17211c;
  --muted: #68736d;
  min-height: 100vh;
  padding: clamp(1rem, 3vw, 2.5rem);
  background: #eef2ef;
  color: var(--ink);
  font-family: inherit;
}

.cv-toolbar {
  width: min(210mm, 100%);
  margin: 0 auto 1rem;
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
}

.cv-toolbar span {
  display: flex;
  align-items: center;
  gap: .45rem;
  color: var(--green-dark);
  font-size: .82rem;
  font-weight: 700;
}

.cv-toolbar h1 {
  margin: .2rem 0 0;
  font-size: clamp(1.45rem, 3vw, 2rem);
}

.primary-button {
  min-height: 3.3rem;
  padding: 0 1.35rem;
  border: 0;
  border-radius: .8rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: .55rem;
  background: linear-gradient(135deg, #16b864, #0a994e);
  box-shadow: 0 10px 24px rgba(10, 153, 78, .2);
  color: #fff;
  font: inherit;
  font-weight: 750;
  text-decoration: none;
  cursor: pointer;
  transition: transform .18s ease, box-shadow .18s ease;
}

.primary-button:hover { transform: translateY(-1px); box-shadow: 0 13px 28px rgba(10, 153, 78, .28); }
.primary-button:disabled { opacity: .7; cursor: wait; transform: none; }

.state-card {
  width: min(36rem, 100%);
  min-height: 22rem;
  margin: clamp(2rem, 10vh, 7rem) auto;
  padding: 2.5rem;
  border: 1px solid #dde5e0;
  border-radius: 1.35rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  background: #fff;
  box-shadow: 0 22px 55px rgba(29, 49, 38, .1);
  text-align: center;
}

.state-card > i { color: var(--green); font-size: 2.5rem; }
.state-card h1 { margin: 0; font-size: 1.5rem; }
.state-card p { max-width: 27rem; margin: 0; color: var(--muted); line-height: 1.55; }
.state-card--error > i { color: #dc2f2f; }
.loader { width: 2.25rem; height: 2.25rem; border: 3px solid #dce9e1; border-top-color: var(--green); border-radius: 50%; animation: spin .75s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.cv-sheet {
  width: min(210mm, 100%);
  min-height: 297mm;
  margin: 0 auto;
  padding: 11mm 12mm 8mm;
  border: 1px solid #dce2de;
  border-radius: .4rem;
  display: flex;
  flex-direction: column;
  background: #fff;
  box-shadow: 0 24px 70px rgba(24, 43, 32, .14);
  overflow: hidden;
}

.cv-sheet__header,
.cv-sheet__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  color: #7a847e;
  font-size: 10px;
  font-weight: 650;
  letter-spacing: .04em;
  text-transform: uppercase;
}

.cv-logo { width: 92px; height: auto; color: var(--green); }
.cv-logo--small { width: 68px; }

.cv-hero {
  margin: 8mm 0 7mm;
  padding: 7mm;
  border-radius: 5mm;
  display: flex;
  align-items: center;
  gap: 6mm;
  background: linear-gradient(135deg, #effaf3, #f8fcf9);
}

.cv-avatar {
  width: 29mm;
  height: 29mm;
  border: 3px solid #fff;
  border-radius: 50%;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: var(--green);
  box-shadow: 0 6px 20px rgba(12, 135, 68, .18);
  color: #fff;
  font-size: 25px;
  font-weight: 800;
}

.cv-avatar img { width: 100%; height: 100%; object-fit: cover; }
.cv-identity { min-width: 0; }
.cv-identity > p { margin: 0 0 1mm; color: var(--green-dark); font-size: 11px; font-weight: 750; text-transform: uppercase; letter-spacing: .07em; }
.cv-identity h1 { margin: 0; font-size: 28px; line-height: 1.1; }
.cv-identity ul { margin: 3mm 0 0; padding: 0; display: flex; flex-wrap: wrap; gap: 1.5mm 5mm; list-style: none; color: #56625b; font-size: 10px; }

.cv-layout { display: grid; grid-template-columns: minmax(0, 1.8fr) minmax(48mm, .8fr); gap: 9mm; flex: 1; }
.cv-main, .cv-aside { min-width: 0; }
.cv-aside { padding-left: 7mm; border-left: 1px solid #dfe6e1; }
.cv-section + .cv-section { margin-top: 7mm; }
.cv-section h2 { margin: 0 0 3.5mm; padding-bottom: 2mm; border-bottom: 2px solid #1aa35a; color: var(--ink); font-size: 13px; line-height: 1.2; text-transform: uppercase; letter-spacing: .045em; }
.cv-entry + .cv-entry { margin-top: 5mm; padding-top: 5mm; border-top: 1px solid #e6ebe8; }
.cv-entry__heading { display: flex; align-items: start; justify-content: space-between; gap: 4mm; }
.cv-entry h3 { margin: 0; font-size: 12px; line-height: 1.3; }
.cv-entry__heading p { margin: 1mm 0 0; color: #4e5b53; font-size: 10px; }
.cv-entry time { flex: 0 0 auto; color: var(--green-dark); font-size: 9px; font-weight: 700; white-space: nowrap; }
.cv-entry__meta { margin: 2mm 0 0; display: flex; gap: 2mm; color: var(--green-dark); font-size: 9px; font-weight: 700; }
.cv-entry__meta span + span::before { content: '·'; margin-right: 2mm; }
.cv-paragraph { margin: 2.5mm 0 0; color: #465149; font-size: 10px; line-height: 1.55; white-space: pre-line; }
.cv-muted { color: #7a847e; font-size: 10px; }
.cv-section dl { margin: 0; }
.cv-section dt { margin-top: 3mm; color: #7a847e; font-size: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
.cv-section dt:first-child { margin-top: 0; }
.cv-section dd { margin: .7mm 0 0; font-size: 10px; font-weight: 650; }
.cv-simple-list, .cv-bullets { margin: 0; padding: 0; list-style: none; font-size: 10px; }
.cv-simple-list li { padding: 1.5mm 0; display: flex; justify-content: space-between; gap: 2mm; border-bottom: 1px solid #edf0ee; }
.cv-simple-list strong { color: var(--green-dark); }
.cv-bullets li { position: relative; padding: 1.2mm 0 1.2mm 4mm; line-height: 1.35; }
.cv-bullets li::before { content: ''; position: absolute; left: 0; top: 2.4mm; width: 1.5mm; height: 1.5mm; border-radius: 50%; background: var(--green); }
.cv-tags { display: flex; flex-wrap: wrap; gap: 1.5mm; }
.cv-tags span { padding: 1.2mm 2mm; border-radius: 2mm; background: #eff8f2; color: #17653c; font-size: 8px; font-weight: 650; }
.cv-sheet__footer { margin-top: 8mm; padding-top: 4mm; border-top: 1px solid #dfe6e1; }

@media (max-width: 600px) {
  .cv-profile-page { padding: .75rem; }
  .cv-toolbar { align-items: stretch; }
  .cv-toolbar .primary-button { min-width: 3.3rem; padding: 0 1rem; }
  .cv-toolbar .primary-button { font-size: 0; }
  .cv-toolbar .primary-button i { font-size: 1rem; }
  .cv-sheet { min-height: 0; padding: 5mm; }
  .cv-hero { margin: 4mm 0; padding: 4mm; gap: 3mm; }
  .cv-avatar { width: 20mm; height: 20mm; font-size: 18px; }
  .cv-identity h1 { font-size: 18px; }
  .cv-layout { grid-template-columns: 1fr; gap: 5mm; }
  .cv-aside { padding: 5mm 0 0; border: 0; border-top: 1px solid #dfe6e1; }
  .cv-entry__heading { display: block; }
  .cv-entry time { display: block; margin-top: 1mm; white-space: normal; }
  .cv-sheet__header > span, .cv-sheet__footer span:first-of-type { display: none; }
}

/* The original CVBuilder document design. Only its fixed A4 height was removed. */
.cv-document {
  --cv-green: #149447;
  --cv-green-dark: #0f7f3c;
  --cv-ink: #101828;
  --cv-muted: #667085;
  --cv-line: #d9dee7;
  --cv-soft: #f3fbf6;
  width: min(100%, 49.625rem);
  height: auto;
  min-height: 0;
  margin: 0 auto;
  padding: 1.45rem 1.7rem 1.15rem;
  background: #fff;
  color: var(--cv-ink);
  border-radius: .8rem;
  box-shadow: 0 1.5rem 3rem rgba(16, 24, 40, .12);
  display: flex;
  flex-direction: column;
  overflow: visible;
  font-family: Inter, Arial, sans-serif;
}

.cv-header, .cv-top, .cv-footer {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex: 0 0 auto;
  min-width: 0;
}
.cv-header { min-height: 3.65rem; padding-bottom: .85rem; border-bottom: .0625rem solid var(--cv-line); }
.cv-brand { display: inline-flex; flex-direction: row; align-items: center; flex-wrap: nowrap; gap: .55rem; min-width: 0; color: var(--cv-ink); }
.cv-brand__logo, .cv-brand__logo svg { width: 8.2rem; max-width: 8.2rem; height: 2.15rem; max-height: 2.15rem; object-fit: contain; object-position: left center; display: block; flex: 0 0 auto; }
.cv-verified { display: inline-flex; align-items: center; gap: .55rem; flex: 0 0 auto; color: var(--cv-green); }
.cv-verified > i { font-size: 1.25rem; }
.cv-verified > span { display: grid; gap: .12rem; text-align: right; }
.cv-verified strong { color: var(--cv-ink); font-size: .72rem; line-height: 1; }
.cv-verified small { color: var(--cv-green-dark); font-size: .55rem; line-height: 1; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; }
.cv-top { padding: 1rem 0 .95rem; border-bottom: .0625rem solid var(--cv-line); align-items: flex-start; }
.cv-person { display: grid; grid-template-columns: 4.25rem minmax(0, 1fr); gap: .85rem; align-items: start; min-width: 0; }
.cv-avatar { width: 4.25rem; height: 4.25rem; display: grid; place-items: center; overflow: hidden; border: 0; border-radius: 50%; background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%); box-shadow: none; color: #fff; font-size: 1.05rem; line-height: 1; font-weight: 900; }
.cv-avatar img { width: 100%; height: 100%; object-fit: cover; display: block; }
.cv-person h1 { margin: 0; color: #05070a; font-size: clamp(2rem, 4vw, 2.45rem); line-height: .95; letter-spacing: -.055em; overflow-wrap: anywhere; }
.cv-person p { margin: .4rem 0 .7rem; color: var(--cv-green); font-size: .95rem; line-height: 1.1; font-weight: 800; }
.cv-contact-list, .cv-list, .cv-extra-list { margin: 0; padding: 0; list-style: none; }
.cv-contact-list { display: grid; gap: .3rem; }
.cv-contact-list li { display: flex; align-items: center; gap: .45rem; color: var(--cv-ink); font-size: .74rem; line-height: 1.22; min-width: 0; }
.cv-contact-list span, .cv-extra-list span, .cv-list li, .cv-sector span { overflow-wrap: anywhere; }
.cv-contact-list i, .cv-extra-list i { width: .95rem; color: var(--cv-green); text-align: center; flex: 0 0 auto; }
.cv-id { display: grid; justify-items: center; gap: .18rem; color: var(--cv-ink); flex: 0 0 auto; }
.cv-id small { margin-top: .18rem; color: var(--cv-green); font-size: .6rem; line-height: 1; font-weight: 900; text-transform: uppercase; }
.cv-id > strong { font-size: .72rem; line-height: 1; }
.cv-qr { position: relative; width: 5.7rem; height: 5.7rem; display: grid; grid-template-columns: repeat(11, 1fr); grid-template-rows: repeat(11, 1fr); gap: .075rem; padding: .32rem; border: .0625rem solid var(--cv-line); border-radius: .32rem; background: #fff; }
.cv-qr-cell { background: transparent; border-radius: .035rem; }
.cv-qr-cell--active { background: #111; }
.cv-qr strong { position: absolute; inset: 50% auto auto 50%; width: 1.48rem; height: 1.48rem; display: grid; place-items: center; transform: translate(-50%, -50%); border-radius: .22rem; background: #111; color: var(--cv-green); font-size: .5rem; line-height: 1; font-weight: 900; }
.cv-body { display: grid; grid-template-columns: minmax(0, 1.34fr) minmax(12.5rem, .82fr); gap: 1.25rem; padding-top: 1rem; flex: 1 1 auto; min-height: 0; overflow: visible; }
.cv-main { min-height: 0; overflow: visible; padding-right: 1.25rem; border-right: .0625rem solid var(--cv-line); }
.cv-aside { min-height: 0; overflow: visible; padding: 0; border: 0; }
.cv-section { padding-bottom: .72rem; margin: 0 0 .72rem; border-bottom: .0625rem solid var(--cv-line); break-inside: avoid; page-break-inside: avoid; }
.cv-section:last-child { margin-bottom: 0; }
.cv-section h2 { margin: 0 0 .48rem; padding: 0; border: 0; color: var(--cv-ink); font-size: .78rem; line-height: 1.1; text-transform: uppercase; letter-spacing: .04em; }
.cv-section p { margin: 0; color: var(--cv-ink); font-size: .72rem; line-height: 1.42; }
.cv-summary-text { display: -webkit-box; -webkit-box-orient: vertical; overflow: visible; white-space: pre-line; }
.cv-section p + p { margin-top: .42rem; }
.cv-entry + .cv-entry { margin-top: .55rem; padding-top: .55rem; border-top: .0625rem solid var(--cv-line); }
.cv-list { display: grid; gap: .3rem; }
.cv-list li { position: relative; padding-left: .78rem; color: var(--cv-ink); font-size: .7rem; line-height: 1.24; }
.cv-list li::before { content: ''; position: absolute; top: .42rem; left: .12rem; width: .22rem; height: .22rem; border-radius: 50%; background: var(--cv-green); }
.cv-sector-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .36rem; }
.cv-sector { display: flex; align-items: center; gap: .36rem; min-height: 1.95rem; padding: .38rem .45rem; border: .0625rem solid #d9f2e2; border-radius: .5rem; background: var(--cv-soft); color: var(--cv-ink); font-size: .66rem; line-height: 1.16; font-weight: 800; break-inside: avoid; page-break-inside: avoid; }
.cv-sector i { color: var(--cv-green); flex: 0 0 auto; }
.cv-sector__copy { display: grid; gap: .08rem; }
.cv-sector__copy strong, .cv-sector__copy small { line-height: 1.12; }
.cv-sector__copy small { color: #557567; font-size: .58rem; font-weight: 700; }
.cv-extra-list { display: grid; gap: .38rem; }
.cv-extra-list li { display: grid; grid-template-columns: .95rem minmax(0, 1fr); gap: .34rem; align-items: start; color: var(--cv-ink); font-size: .69rem; line-height: 1.25; }
.cv-more-item { color: var(--cv-muted) !important; font-weight: 800 !important; }
.cv-footer { margin-top: auto; padding-top: .55rem; border-top: .0625rem solid var(--cv-line); color: var(--cv-muted); font-size: .63rem; line-height: 1.1; break-inside: avoid; page-break-inside: avoid; }
.cv-brand--small .cv-brand__logo { width: 5.8rem; max-width: 5.8rem; height: 1.45rem; max-height: 1.45rem; }

@media (max-width: 72rem) {
  .cv-body { grid-template-columns: 1fr; }
  .cv-main { padding-right: 0; border-right: 0; }
}

@media (max-width: 56rem) {
  .cv-document { padding: 1.35rem; border-radius: 1rem; }
  .cv-header, .cv-top, .cv-footer { flex-direction: column; align-items: flex-start; }
  .cv-person { grid-template-columns: 1fr; }
  .cv-brand { flex-wrap: wrap; }
  .cv-brand__logo { width: 7.4rem; }
  .cv-id { justify-items: start; }
  .cv-sector-grid { grid-template-columns: 1fr; }
}
</style>
