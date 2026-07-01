import { normalizeLanguages, normalizeLicenses } from './jobRequirements'
import { useUiStore } from '@/stores/ui'

const CEFR_RANK = {
  A1: 1,
  A2: 2,
  B1: 3,
  B2: 4,
  C1: 5,
  C2: 6,
}

const getLanguage = () => {
  try {
    return useUiStore().language
  } catch {
    return 'ru'
  }
}

const copy = () => {
  const language = getLanguage()

  if (language === 'en') {
    return {
      strongMatch: 'Strong match',
      goodMatch: 'Good match',
      partialMatch: 'Partial match',
      weakMatch: 'Weak match',
      failMatch: 'Not a fit',
      strong: 'Strong',
      good: 'Good',
      partial: 'Partial',
      weak: 'Weak',
      fail: 'Fail',
      experience: 'Experience',
      language: 'Language',
      license: 'Licences',
      readiness: 'Readiness',
      candidateProfileWeak: 'The candidate profile is too thin: not enough experience details.',
      roleMatch: 'Role overlap: {value}.',
      roleWeak: 'Direct role-title overlap is limited.',
      descriptionMatch: 'Job description overlap: {value}.',
      currentRole: 'Current role: {value}.',
      noLanguageRequirements: 'This job has no mandatory language requirements.',
      requiredLanguages: 'Required languages: {value}.',
      candidateLanguagesMissing: 'The candidate has no listed languages.',
      languageMatched: 'Matched: {value}.',
      languageMissing: 'Missing: {value}.',
      requiredVsCandidate: '{name}: required {required}, candidate has {actual}',
      noLicenseRequirements: 'This job has no mandatory licence requirements.',
      requiredLicenses: 'Required licences: {value}.',
      candidateLicensesMissing: 'The candidate has no listed licences.',
      licenseMatched: 'Matched: {value}.',
      licenseMissing: 'Missing: {value}.',
      noWorkPermit: 'No explicit work permit information provided.',
      workPermit: 'Work permit noted: {value}.',
      availability: 'Available to start: {value}.',
      resumeAttached: 'Resume attached.',
      resumeMissing: 'Resume not attached.',
      contactsFilled: 'Contact details are filled in.',
      contactsMissing: 'Contact details are incomplete for quick follow-up.',
      matchedArrow: '{required} -> {actual}',
    }
  }

  return {
    strongMatch: 'Сильное совпадение',
    goodMatch: 'Хорошее совпадение',
    partialMatch: 'Частичное совпадение',
    weakMatch: 'Слабое совпадение',
    failMatch: 'Не соответствует',
    strong: 'Сильное',
    good: 'Хорошее',
    partial: 'Частичное',
    weak: 'Слабое',
    fail: 'Нет',
    experience: 'Опыт',
    language: 'Язык',
    license: 'Права',
    readiness: 'Готовность',
    candidateProfileWeak: 'Профиль кандидата заполнен слабо: мало данных по опыту.',
    roleMatch: 'Совпадение по роли: {value}.',
    roleWeak: 'Прямое совпадение по названию роли слабое.',
    descriptionMatch: 'Есть совпадения по описанию вакансии: {value}.',
    currentRole: 'Текущая роль: {value}.',
    noLanguageRequirements: 'В вакансии нет обязательных требований по языкам.',
    requiredLanguages: 'Требуются языки: {value}.',
    candidateLanguagesMissing: 'У кандидата языки не указаны.',
    languageMatched: 'Совпало: {value}.',
    languageMissing: 'Не хватает: {value}.',
    requiredVsCandidate: '{name}: нужно {required}, у кандидата {actual}',
    noLicenseRequirements: 'В вакансии нет обязательных требований по правам или лицензиям.',
    requiredLicenses: 'Требуются права/лицензии: {value}.',
    candidateLicensesMissing: 'У кандидата права или лицензии не указаны.',
    licenseMatched: 'Совпало: {value}.',
    licenseMissing: 'Не хватает: {value}.',
    noWorkPermit: 'Нет явной информации о разрешении на работу.',
    workPermit: 'Разрешение на работу указано: {value}.',
    availability: 'Готовность выйти: {value}.',
    resumeAttached: 'Резюме приложено.',
    resumeMissing: 'Резюме не приложено.',
    contactsFilled: 'Контакты заполнены.',
    contactsMissing: 'Не хватает контактов для быстрого выхода на связь.',
    matchedArrow: '{required} -> {actual}',
  }
}

const interpolate = (template, params = {}) => template.replace(/\{(\w+)\}/g, (_, key) => String(params[key] ?? ''))
const text = (key, params = {}) => interpolate(copy()[key], params)

const MATCH_META = {
  strong: {
    key: 'strong',
    textColor: '#19785a',
    badgeBackground: '#e6f0ec',
    accentBackground: 'rgba(25, 120, 90, 0.12)',
  },
  good: {
    key: 'good',
    textColor: '#4a90e2',
    badgeBackground: '#e8f0fe',
    accentBackground: 'rgba(74, 144, 226, 0.12)',
  },
  partial: {
    key: 'partial',
    textColor: '#d68a12',
    badgeBackground: '#fef3e2',
    accentBackground: 'rgba(245, 166, 35, 0.12)',
  },
  weak: {
    key: 'weak',
    textColor: '#6b7280',
    badgeBackground: '#f3f4f6',
    accentBackground: 'rgba(107, 114, 128, 0.12)',
  },
  fail: {
    key: 'fail',
    textColor: '#dc2626',
    badgeBackground: '#fee2e2',
    accentBackground: 'rgba(220, 38, 38, 0.12)',
  },
}

const STOPWORDS = new Set([
  'and', 'the', 'for', 'with', 'from', 'into', 'that', 'this', 'your', 'you', 'или',
  'для', 'как', 'что', 'это', 'при', 'без', 'под', 'над', 'work', 'works', 'работа',
  'работы', 'опыт', 'candidate', 'кандидат', 'company', 'компания', 'job', 'role',
  'position', 'позиция', 'специалист', 'worker', 'service', 'services', 'требования',
])

const normalizeText = (value) => String(value || '')
  .toLowerCase()
  .replace(/ё/g, 'е')
  .replace(/[^a-zа-я0-9+#./ -]+/gi, ' ')

const unique = (values) => [...new Set(values.filter(Boolean))]

const tokenize = (...values) => unique(values
  .flatMap((value) => normalizeText(value).split(/[\s,/|().-]+/))
  .map((token) => token.trim())
  .filter((token) => token.length >= 2 && !STOPWORDS.has(token)))

const clamp = (value, min = 0, max = 100) => Math.max(min, Math.min(max, value))
const levelRank = (value) => CEFR_RANK[String(value || '').toUpperCase()] || 0

const getMatchMeta = (score) => {
  const localized = copy()

  if (score >= 85) return { ...MATCH_META.strong, label: localized.strongMatch, shortLabel: localized.strong }
  if (score >= 70) return { ...MATCH_META.good, label: localized.goodMatch, shortLabel: localized.good }
  if (score >= 50) return { ...MATCH_META.partial, label: localized.partialMatch, shortLabel: localized.partial }
  if (score >= 30) return { ...MATCH_META.weak, label: localized.weakMatch, shortLabel: localized.weak }
  return { ...MATCH_META.fail, label: localized.failMatch, shortLabel: localized.fail }
}

const overlapRatio = (required, actual) => {
  if (!required.length || !actual.length) return 0

  const hits = required.filter((token) => actual.includes(token)).length
  return hits / required.length
}

const formatLanguage = (language) => {
  const name = String(language?.name || '').trim()
  const level = String(language?.level || '').trim()

  if (!name) return ''
  return level ? `${name} ${level}` : name
}

const formatList = (values) => values.filter(Boolean).join(', ')

const getTitleExperienceScore = (candidate, job) => {
  const titleTokens = tokenize(job?.job_title || job?.title)
  const descriptionTokens = tokenize(job?.job_description || job?.description).slice(0, 12)
  const candidateRoleTokens = tokenize(candidate?.candidate_current_role || candidate?.current_role)
  const candidateProfileTokens = tokenize(
    candidate?.candidate_current_role || candidate?.current_role,
    candidate?.candidate_summary || candidate?.summary,
    candidate?.candidate_skills || candidate?.skills,
    ...(Array.isArray(candidate?.candidate_sectors) ? candidate.candidate_sectors.map((sector) => sector?.name || sector) : []),
  )

  if (!candidateProfileTokens.length) {
    return {
      score: 18,
      details: [text('candidateProfileWeak')],
    }
  }

  const titleRatio = overlapRatio(titleTokens, candidateProfileTokens)
  const roleRatio = overlapRatio(titleTokens, candidateRoleTokens.length ? candidateRoleTokens : candidateProfileTokens)
  const descriptionRatio = overlapRatio(descriptionTokens, candidateProfileTokens)
  const roleScore = 24 + (titleRatio * 34) + (roleRatio * 24) + (descriptionRatio * 18)
  const matchedRoleTokens = titleTokens.filter((token) => candidateProfileTokens.includes(token)).slice(0, 4)
  const matchedDescriptionTokens = descriptionTokens
    .filter((token) => candidateProfileTokens.includes(token) && !matchedRoleTokens.includes(token))
    .slice(0, 4)
  const details = []

  if (matchedRoleTokens.length) {
    details.push(text('roleMatch', { value: formatList(matchedRoleTokens) }))
  } else {
    details.push(text('roleWeak'))
  }

  if (matchedDescriptionTokens.length) {
    details.push(text('descriptionMatch', { value: formatList(matchedDescriptionTokens) }))
  }

  if (candidate?.candidate_current_role || candidate?.current_role) {
    details.push(text('currentRole', { value: candidate.candidate_current_role || candidate.current_role }))
  }

  return {
    score: clamp(Math.round(roleScore)),
    details,
  }
}

const getLanguageScore = (candidate, job) => {
  const required = normalizeLanguages(job?.languages ?? job?.languages_json)
  const actual = normalizeLanguages(
    candidate?.candidate_languages ??
    candidate?.languages ??
    candidate?.languages_json,
  )

  if (!required.length) {
    return { score: 100, details: [text('noLanguageRequirements')] }
  }

  if (!actual.length) {
    return {
      score: 18,
      details: [
        text('requiredLanguages', { value: formatList(required.map(formatLanguage)) }),
        text('candidateLanguagesMissing'),
      ],
    }
  }

  const matched = []
  const missing = []

  required.forEach((needed) => {
    const candidateLanguage = actual.find((item) => item.name.toLowerCase() === needed.name.toLowerCase())
    if (!candidateLanguage) {
      missing.push(formatLanguage(needed))
      return
    }

    if (levelRank(candidateLanguage.level) >= levelRank(needed.level)) {
      matched.push(text('matchedArrow', { required: formatLanguage(needed), actual: formatLanguage(candidateLanguage) }))
    } else {
      missing.push(text('requiredVsCandidate', {
        name: needed.name,
        required: needed.level,
        actual: candidateLanguage.level || '?',
      }))
    }
  })

  const ratio = matched.length / required.length
  const score = clamp(Math.round((ratio * 78) + 22))
  const details = [text('requiredLanguages', { value: formatList(required.map(formatLanguage)) })]

  if (matched.length) details.push(text('languageMatched', { value: formatList(matched) }))
  if (missing.length) details.push(text('languageMissing', { value: formatList(missing) }))

  return { score, details }
}

const getLicenseScore = (candidate, job) => {
  const required = normalizeLicenses(job?.licenses ?? job?.licenses_json)
  const actual = normalizeLicenses(
    candidate?.candidate_licenses ??
    candidate?.licenses ??
    candidate?.licenses_json,
  )

  if (!required.length) {
    return { score: 100, details: [text('noLicenseRequirements')] }
  }

  if (!actual.length) {
    return {
      score: 20,
      details: [
        text('requiredLicenses', { value: formatList(required) }),
        text('candidateLicensesMissing'),
      ],
    }
  }

  const matched = required.filter((item) => actual.some((license) => license.toLowerCase() === item.toLowerCase()))
  const missing = required.filter((item) => !matched.includes(item))
  const ratio = matched.length / required.length
  const score = clamp(Math.round((ratio * 75) + 25))
  const details = [text('requiredLicenses', { value: formatList(required) })]

  if (matched.length) details.push(text('licenseMatched', { value: formatList(matched) }))
  if (missing.length) details.push(text('licenseMissing', { value: formatList(missing) }))

  return { score, details }
}

const getReadinessScore = (candidate) => {
  const details = []
  let score = 24

  const workPermit = candidate?.candidate_work_permit || candidate?.work_permit || candidate?.permit
  if (workPermit) {
    score += 22
    details.push(text('workPermit', { value: workPermit }))
  } else {
    details.push(text('noWorkPermit'))
  }

  const availability = candidate?.candidate_availability || candidate?.availability
  if (availability) {
    score += 18
    details.push(text('availability', { value: availability }))
  }

  if (candidate?.resume_url || candidate?.cv_url || candidate?.resume) {
    score += 18
    details.push(text('resumeAttached'))
  } else {
    details.push(text('resumeMissing'))
  }

  if (candidate?.phone || candidate?.email) {
    score += 18
    details.push(text('contactsFilled'))
  } else {
    details.push(text('contactsMissing'))
  }

  return { score: clamp(score), details }
}

export const analyzeCandidateMatch = (candidate, job) => {
  const experience = getTitleExperienceScore(candidate, job)
  const language = getLanguageScore(candidate, job)
  const license = getLicenseScore(candidate, job)
  const readiness = getReadinessScore(candidate)

  const score = clamp(Math.round(
    (experience.score * 0.4) +
    (language.score * 0.25) +
    (license.score * 0.2) +
    (readiness.score * 0.15),
  ))

  const meta = getMatchMeta(score)

  return {
    score,
    meta,
    breakdown: [
      { key: 'experience', label: copy().experience, score: experience.score, details: experience.details, meta: getMatchMeta(experience.score) },
      { key: 'language', label: copy().language, score: language.score, details: language.details, meta: getMatchMeta(language.score) },
      { key: 'license', label: copy().license, score: license.score, details: license.details, meta: getMatchMeta(license.score) },
      { key: 'readiness', label: copy().readiness, score: readiness.score, details: readiness.details, meta: getMatchMeta(readiness.score) },
    ],
  }
}

export const getMatchMetaByKey = (key) => MATCH_META[key] || MATCH_META.partial
