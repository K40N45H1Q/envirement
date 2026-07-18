<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { getProfile } from '@/api/profile'
import { getResponseCv } from '@/api/jobs'
import { translate, useI18n } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useCvBuilderStore } from '@/stores/cvBuilder'
import CvDocument from '@/cv/CvDocument.vue'
import { preparePdfCvDocument } from '@/cv/cvLayout'
import { limitText } from '@/utils/cvBuilderHelpers'
import { createPaginatedCvPdf } from '@/utils/cvPdf'

const MAX_PRINT_WORK_EXPERIENCES = 3
const MAX_PRINT_EDUCATIONS = 3
const MAX_WORK_DESCRIPTION_LENGTH = 420
const MAX_SHORT_FIELD_LENGTH = 120

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
  applicationId: {
    type: [Number, String],
    default: null,
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
const displayLanguageLevel = (value) => (
  value === 'Native'
    ? translate('resumeBuilderPage.nativeLanguageLevel', {}, cvLocale.value)
    : value
)
const hasCv = computed(() => Object.keys(resume.value).length > 0)
const isResponseCv = computed(() => Boolean(props.applicationId))
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
  { value: profile.value.email || user.value?.email, icon: 'far fa-envelope' },
  ...(Array.isArray(resume.value.additional_emails) ? resume.value.additional_emails : []).map((value) => ({
    value,
    icon: 'far fa-envelope',
  })),
  { value: profile.value.phone, icon: 'fas fa-phone' },
  { value: profile.value.residence, icon: 'fas fa-location-dot' },
  ...(Array.isArray(resume.value.additional_phones) ? resume.value.additional_phones : []).map((value) => ({
    value,
    icon: 'fas fa-phone',
  })),
].filter((item) => item.value))
const skills = computed(() => {
  if (Array.isArray(profile.value.skills)) return profile.value.skills.filter(Boolean)
  return String(profile.value.skills || '').split(/[,;\n]/).map((item) => item.trim()).filter(Boolean)
})
const languages = computed(() => (
  Array.isArray(profile.value.languages) ? profile.value.languages.filter((item) => item?.name) : []
))
const drivingLicenses = computed(() => [...new Set(
  Array.isArray(resume.value.driving_licenses) ? resume.value.driving_licenses : [],
)].filter(Boolean))
const certificates = computed(() => (
  Array.isArray(profile.value.licenses) ? profile.value.licenses.filter(Boolean) : []
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
  primary: { ru: 'Основное', en: 'Primary', lv: 'Pamatizglītība' },
  secondary: { ru: 'Среднее', en: 'Secondary', lv: 'Vidējā izglītība' },
  vocational: { ru: 'Профессиональное', en: 'Vocational', lv: 'Profesionālā izglītība' },
  bachelor: { ru: 'Бакалавр', en: 'Bachelor', lv: 'Bakalaurs' },
  master: { ru: 'Магистр', en: 'Master', lv: 'Maģistrs' },
  phd: { ru: 'Доктор наук', en: 'PhD', lv: 'PhD' },
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
    icon: 'far fa-calendar',
    label: cvCopy.value.birthDate,
    value: formatDate(resume.value.birth_date),
  },
  !resume.value.hide_gender && resume.value.gender && {
    icon: 'fas fa-user',
    label: cvCopy.value.gender,
    value: localeValue(genderNames, resume.value.gender),
  },
  resume.value.citizenship && {
    icon: 'fas fa-passport',
    label: cvCopy.value.citizenship,
    value: resume.value.citizenship,
  },
  resume.value.no_driving_license && {
    icon: 'fas fa-car-side',
    label: cvCopy.value.drivingLicenses,
    value: cvCopy.value.noDrivingLicense,
  },
].filter(Boolean))

const avatarPreview = computed(() => profile.value.avatar_url || '')
const displayCvName = fullName
const avatarInitials = initials
const displayCvRole = mainRole
const cvWorkExperiences = computed(() => workEntries.value.slice(0, MAX_PRINT_WORK_EXPERIENCES).map((entry) => ({
  ...entry,
  position: limitText(entry.position, MAX_SHORT_FIELD_LENGTH),
  company_name: limitText(entry.company_name, MAX_SHORT_FIELD_LENGTH),
  description: limitText(entry.description, MAX_WORK_DESCRIPTION_LENGTH, { preserveLineBreaks: true }),
})))
const cvMoreWorkExperiencesCount = computed(() => Math.max(0, workEntries.value.length - MAX_PRINT_WORK_EXPERIENCES))
const cvEducations = computed(() => educationEntries.value.slice(0, MAX_PRINT_EDUCATIONS).map((entry) => ({
  ...entry,
  institution: limitText(entry.institution, MAX_SHORT_FIELD_LENGTH),
  speciality: limitText(entry.speciality, MAX_SHORT_FIELD_LENGTH),
  second_speciality: limitText(entry.second_speciality, MAX_SHORT_FIELD_LENGTH),
  additional_information: limitText(entry.additional_information, MAX_WORK_DESCRIPTION_LENGTH, { preserveLineBreaks: true }),
})))
const cvMoreEducationsCount = computed(() => Math.max(0, educationEntries.value.length - MAX_PRINT_EDUCATIONS))
const cvContactItems = computed(() => contacts.value.map((value) => ({
  value: value.value,
  icon: value.icon,
})))
const cvSummaryParagraphs = computed(() => {
  const text = String(profile.value.summary || '').trim()
  return text
    ? text.split(/\n{2,}/).map((paragraph) => paragraph.trim()).filter(Boolean)
    : [cvCopy.value.summaryFallback]
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
const cvLicenses = computed(() => drivingLicenses.value)
const cvAdditionalItems = computed(() => additionalDetails.value)
const displayLanguageName = (value) => localeValue(languageNames, value)
const displayEducation = (value) => localeValue(educationNames, value)
const categoryLabel = (value) => value
const cvId = computed(() => {
  const source = `${fullName.value}|${profile.value.email || user.value?.email || ''}`
  let hash = 0
  for (let index = 0; index < source.length; index += 1) hash = ((hash << 5) - hash) + source.charCodeAt(index)
  return `CVH-${(Math.abs(hash) % 900000) + 100000}`
})
const formatMore = (_key, count) => `+${count}`

async function loadProfile() {
  if (!user.value) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    profile.value = props.applicationId
      ? await getResponseCv(props.applicationId)
      : await getProfile()
  } catch {
    errorMessage.value = profileCopy.value.loadProfileError
  } finally {
    isLoading.value = false
  }
}

async function downloadCv() {
  const sourceDocument = cvDocument.value?.$el || cvDocument.value
  if (!sourceDocument || isPrinting.value) return
  isPrinting.value = true
  await nextTick()

  const renderHost = document.createElement('div')
  renderHost.style.cssText = 'position:fixed;left:-10000px;top:0;width:49.625rem;background:#fff;pointer-events:none;'
  const printableClone = sourceDocument.cloneNode(true)
  printableClone.style.transform = 'none'
  printableClone.style.margin = '0'
  renderHost.appendChild(printableClone)
  document.body.appendChild(renderHost)
  // Keep PDF-specific DOM mutations centralized in the CV layout module.
  preparePdfCvDocument(printableClone)

  try {
    const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
      import('html2canvas'),
      import('jspdf'),
    ])
    const images = Array.from(printableClone.querySelectorAll('img'))
    await Promise.all(images.map(async (image) => {
      try {
        await image.decode?.()
      } catch {
        // html2canvas will use the image state available in the document.
      }
    }))
    await document.fonts?.ready

    const canvas = await html2canvas(printableClone, {
      scale: 2,
      useCORS: true,
      backgroundColor: null,
      logging: false,
      windowWidth: 1280,
    })
    const pdf = await createPaginatedCvPdf(canvas, printableClone, jsPDF)
    pdf.save('CVHOLD-CV.pdf')
  } finally {
    renderHost.remove()
    isPrinting.value = false
  }
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
      <button v-if="!isResponseCv" type="button" class="primary-button" @click="cvBuilder.open">
        <i class="fas fa-plus"></i>{{ profileCopy.createCv }}
      </button>
    </div>

    <template v-else>
      <div class="cv-toolbar">
        <div>
          <span><i class="fas fa-circle-check"></i>{{ profileCopy.cvReady }}</span>
          <h1>{{ isResponseCv ? fullName : profileCopy.myCv }}</h1>
        </div>
        <button type="button" class="primary-button" :disabled="isPrinting" @click="downloadCv">
          <i :class="isPrinting ? 'fas fa-spinner fa-spin' : 'fas fa-download'"></i>
          {{ cvCopy.downloadPdf }}
        </button>
      </div>

      <CvDocument
        ref="cvDocument"
        :avatar-preview="avatarPreview"
        :avatar-initials="avatarInitials"
        :display-name="displayCvName"
        :display-role="displayCvRole"
        :contact-items="cvContactItems"
        :additional-items="cvAdditionalItems"
        :summary-paragraphs="cvSummaryParagraphs"
        :work-experiences="cvWorkExperiences"
        :more-work-experiences-count="cvMoreWorkExperiencesCount"
        :languages="cvVisibleLanguages"
        :more-languages-count="cvMoreLanguagesCount"
        :licenses="cvLicenses"
        :skills="cvVisibleSkills"
        :more-skills-count="cvMoreSkillsCount"
        :sectors="cvVisibleSectors"
        :more-sectors-count="cvMoreSectorsCount"
        :certificates="certificates"
        :educations="cvEducations"
        :more-educations-count="cvMoreEducationsCount"
        :cv-id="cvId"
        :copy="cvCopy"
        :section-title="cvSectionTitle"
        :format-date="formatDate"
        :format-more="formatMore"
        :category-label="categoryLabel"
        :display-language-name="displayLanguageName"
        :display-language-level="displayLanguageLevel"
        :display-education="displayEducation"
      />
    </template>
  </main>
</template>

<style scoped src="./Profile.css"></style>
