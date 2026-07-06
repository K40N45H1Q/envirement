import { normalizeLanguages, normalizeLicenses } from './jobRequirements'
import { useUiStore } from '@/stores/ui'
import { inferJobCategory } from '@/utils/jobCategories'

const CEFR_RANK = {
  A1: 1,
  A2: 1,
  B1: 2,
  B2: 3,
  C1: 4,
  C2: 4,
}

const EDUCATION_RANK = {
  primary: 0,
  secondary: 1,
  vocational: 2,
  bachelor: 3,
  master: 4,
  phd: 5,
}

const EXPERIENCE_YEARS = {
  'no_experience': 0,
  'no experience': 0,
  'without experience': 0,
  'без опыта': 0,
  '1_year': 1,
  '2_years': 2,
  '3_years': 3,
  '4_years': 4,
  '5_years': 5,
  '7_years': 7,
  '10_years': 10,
  '1+ year': 1,
  '1+ years': 1,
  '1+ год': 1,
  '2+ years': 2,
  '2+ года': 2,
  '3+ years': 3,
  '3+ года': 3,
  '4+ years': 4,
  '4+ года': 4,
  '5+ years': 5,
  '5+ лет': 5,
  '7+ years': 7,
  '7+ лет': 7,
  '10+ years': 10,
  '10+ лет': 10,
}

const PROFILE_WEIGHTS = {
  physical: { experience: 56, tags: 33, language: 11 },
  transport: { experience: 44, tags: 33, language: 23 },
  service: { experience: 33, language: 44, tags: 23 },
  office: { experience: 37, language: 26, tags: 26, education: 11 },
  expert: { experience: 32, tags: 32, education: 21, language: 15 },
}

const CATEGORY_PROFILE = {
  'administrative-work': 'office',
  banking: 'office',
  'public-administration': 'office',
  'marketing-advertising-pr': 'office',
  'hr-training': 'office',
  management: 'office',
  finance: 'office',
  'healthcare-social-work': 'expert',
  'information-technology': 'expert',
  'media-creative-translation': 'expert',
  'education-science': 'expert',
  'electronics-telecommunications': 'expert',
  'energy-natural-resources': 'expert',
  'transport-logistics': 'transport',
  service: 'service',
  security: 'service',
  food: 'service',
  sales: 'service',
  'tourism-hospitality': 'service',
  'industry-production': 'physical',
  'agriculture-forestry': 'physical',
  'construction-real-estate': 'physical',
  'mechanics-technology': 'physical',
}

const MATCH_META = {
  strong: {
    key: 'strong',
    textColor: '#19785a',
    badgeBackground: '#e6f0ec',
    accentBackground: 'rgba(25, 120, 90, 0.12)',
  },
  good: {
    key: 'good',
    textColor: '#3b82f6',
    badgeBackground: '#e8f0fe',
    accentBackground: 'rgba(59, 130, 246, 0.12)',
  },
  partial: {
    key: 'partial',
    textColor: '#d68a12',
    badgeBackground: '#fef3e2',
    accentBackground: 'rgba(214, 138, 18, 0.14)',
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
  'and', 'the', 'for', 'with', 'your', 'that', 'this', 'from', 'you', 'will', 'our', 'are', 'job', 'role', 'work',
  'candidate', 'company', 'team', 'position', 'required', 'requirements', 'experience', 'skill', 'skills', 'years',
  'лет', 'год', 'года', 'работа', 'работы', 'опыт', 'опыта', 'компания', 'кандидат', 'позиция', 'требования',
  'обязанности', 'условия', 'должность', 'специалист', 'вакансия', 'vacancy', 'full', 'time', 'part', 'remote',
])

const LICENSE_PATTERN = /\b(AM|A1|A2|A|B|BE|C1|C1E|C|CE|D1|D1E|D|DE|ADR|VCA|Forklift|Code 95)\b/gi
const TAG_PHRASES = [
  'mig/mag',
  'tig',
  'mag',
  'mig',
  'arc',
  'plc',
  'sap',
  'sql',
  'java',
  'javascript',
  'typescript',
  'python',
  'react',
  'vue',
  'angular',
  'node',
  'docker',
  'kubernetes',
  'devops',
  'backend',
  'frontend',
  'fullstack',
  'warehouse',
  'forklift',
  'adr',
  'ce',
  'refrigerator',
  'refrigerated',
  'cashier',
  'sales',
  'retail',
  'accounting',
  'bookkeeping',
  'welding',
  'electrician',
  'plumber',
  'mechanic',
  'maintenance',
  'cleaning',
  'housekeeping',
  'nurse',
  'caregiver',
  'teacher',
  'translator',
  'photography',
  'video',
]

const getLanguage = () => {
  try {
    return useUiStore().language
  } catch {
    return 'ru'
  }
}

const copy = () => {
  if (getLanguage() === 'en') {
    return {
      strongMatch: 'Excellent match',
      goodMatch: 'Good match',
      partialMatch: 'Potential match',
      weakMatch: 'Weak match',
      failMatch: 'Blocked by requirements',
      strong: 'Excellent',
      good: 'Good',
      partial: 'Potential',
      weak: 'Weak',
      fail: 'Blocked',
      green: 'Green light',
      amber: 'Amber light',
      red: 'Red light',
      profilePhysical: 'Physical work profile',
      profileTransport: 'Transport profile',
      profileService: 'Service profile',
      profileOffice: 'Office profile',
      profileExpert: 'Expert profile',
      experience: 'Experience',
      language: 'Languages',
      tags: 'Skills and signals',
      education: 'Education',
      prefilters: 'Prefilters',
      gates: 'Hard requirements',
      prefilterSalary: 'Expected salary is above the vacancy ceiling.',
      prefilterEmployment: 'Employment type does not match the vacancy.',
      gateLicense: 'Missing required license: {value}.',
      gateLanguage: 'Language below required level: {value}.',
      gateTag: 'Missing mandatory skill or keyword: {value}.',
      gateWorkAuth: 'No work authorization for {value}.',
      gateEducation: 'Education level is below the minimum.',
      gateCertified: 'Required proof or certificate is missing.',
      gateEmployment: 'Employment type does not match.',
      gateUnknown: 'One of the mandatory requirements is not met.',
      noRelevantExperience: 'No confirmed experience found in this job category.',
      matchedExperience: 'Experience in matching category: {value} years.',
      requiredExperience: 'Vacancy baseline: {value}+ years.',
      languageMissing: 'Candidate language data is missing.',
      noLanguageRequirements: 'The vacancy has no language requirements.',
      requiredLanguages: 'Required: {value}.',
      languageAverage: 'Average language coverage: {value}%.',
      noTagRequirements: 'No extra skill tags were detected for this vacancy.',
      matchedTags: 'Matched tags: {value}.',
      missingTags: 'Not matched: {value}.',
      noEducationRequirements: 'No education requirement is defined for this vacancy.',
      educationMatched: 'Education matches the vacancy level.',
      educationGap: 'Education is close but one step below the target.',
      educationLow: 'Education level is below the expected baseline.',
      pass: 'Passed',
      blocked: 'Blocked',
      scoreLabel: 'Match score',
    }
  }

  return {
    strongMatch: 'Идеальное совпадение',
    goodMatch: 'Хорошее совпадение',
    partialMatch: 'Потенциальное совпадение',
    weakMatch: 'Слабое совпадение',
    failMatch: 'Блокируется требованиями',
    strong: 'Идеально',
    good: 'Хорошо',
    partial: 'Потенциал',
    weak: 'Слабо',
    fail: 'Блок',
    green: 'Зелёный свет',
    amber: 'Жёлтый свет',
    red: 'Красный свет',
    profilePhysical: 'Профиль физического труда',
    profileTransport: 'Профиль транспорта',
    profileService: 'Профиль сервиса',
    profileOffice: 'Профиль офиса',
    profileExpert: 'Профиль экспертной роли',
    experience: 'Опыт',
    language: 'Языки',
    tags: 'Навыки и сигналы',
    education: 'Образование',
    prefilters: 'Предфильтры',
    gates: 'Жёсткие требования',
    prefilterSalary: 'Ожидаемая зарплата выше потолка вакансии.',
    prefilterEmployment: 'Тип занятости не совпадает с вакансией.',
    gateLicense: 'Не хватает обязательной лицензии: {value}.',
    gateLanguage: 'Язык ниже требуемого уровня: {value}.',
    gateTag: 'Не найден обязательный навык или тег: {value}.',
    gateWorkAuth: 'Нет разрешения на работу для {value}.',
    gateEducation: 'Уровень образования ниже минимального.',
    gateCertified: 'Не найден обязательный сертификат или подтверждение.',
    gateEmployment: 'Тип занятости не совпадает.',
    gateUnknown: 'Одно из обязательных требований не выполнено.',
    noRelevantExperience: 'Не найден подтверждённый опыт в нужной категории.',
    matchedExperience: 'Опыт в совпадающей категории: {value} лет.',
    requiredExperience: 'Базовое требование вакансии: от {value} лет.',
    languageMissing: 'У кандидата не заполнены языки.',
    noLanguageRequirements: 'У вакансии нет языковых требований.',
    requiredLanguages: 'Требуются: {value}.',
    languageAverage: 'Среднее покрытие по языкам: {value}%.',
    noTagRequirements: 'У вакансии не найдены дополнительные теги навыков.',
    matchedTags: 'Совпавшие теги: {value}.',
    missingTags: 'Не совпало: {value}.',
    noEducationRequirements: 'Для вакансии не задано требование по образованию.',
    educationMatched: 'Образование соответствует вакансии.',
    educationGap: 'Образование близко, но на один уровень ниже.',
    educationLow: 'Образование заметно ниже ожидаемого уровня.',
    pass: 'Пройдено',
    blocked: 'Блок',
    scoreLabel: 'Match score',
  }
}

const interpolate = (template, params = {}) => String(template).replace(/\{(\w+)\}/g, (_, key) => String(params[key] ?? ''))
const text = (key, params = {}) => interpolate(copy()[key], params)

const clamp = (value, min = 0, max = 100) => Math.max(min, Math.min(max, value))

const normalizeText = (value) => String(value || '')
  .toLowerCase()
  .replace(/ё/g, 'е')
  .replace(/[^a-zа-я0-9+#/ .-]+/gi, ' ')
  .replace(/\s+/g, ' ')
  .trim()

const tokenize = (...values) => [...new Set(values
  .flatMap((value) => normalizeText(value).split(/[\s,/|().-]+/))
  .map((token) => token.trim())
  .filter((token) => token.length >= 3 && !STOPWORDS.has(token)))]

const levelRank = (value) => CEFR_RANK[String(value || '').toUpperCase()] || 0

const parseSalaryRange = (salary = '') => {
  const values = String(salary || '').match(/\d[\d\s]*/g) || []
  const numbers = values
    .map((item) => Number(String(item).replace(/\s+/g, '')))
    .filter((item) => Number.isFinite(item) && item > 0)

  if (!numbers.length) return { min: null, max: null }
  if (numbers.length === 1) return { min: numbers[0], max: numbers[0] }
  return { min: Math.min(...numbers), max: Math.max(...numbers) }
}

const parseMinYears = (...values) => {
  const haystack = values.map((value) => String(value || '')).join(' ')
  const matches = [...haystack.matchAll(/(\d+)\s*\+?\s*(?:years?|yrs?|лет|года|год)/gi)]
  if (!matches.length) return null
  return Math.max(...matches.map((match) => Number(match[1]) || 0)) || null
}

const parseAvailabilityDate = (value) => {
  const normalized = String(value || '').trim()
  if (!normalized) return null
  if (/^\d{4}-\d{2}-\d{2}$/.test(normalized)) return normalized

  const today = new Date()
  const date = new Date(today)
  const lower = normalized.toLowerCase()

  if (lower === 'immediate' || lower === 'немедленно') return today.toISOString().slice(0, 10)
  if (lower.includes('1 week') || lower.includes('1 неделю')) {
    date.setDate(date.getDate() + 7)
    return date.toISOString().slice(0, 10)
  }
  if (lower.includes('2 week') || lower.includes('2 недели')) {
    date.setDate(date.getDate() + 14)
    return date.toISOString().slice(0, 10)
  }
  if (lower.includes('1 month') || lower.includes('1 месяц')) {
    date.setMonth(date.getMonth() + 1)
    return date.toISOString().slice(0, 10)
  }

  return null
}

const normalizeEmploymentType = (value) => {
  const normalized = normalizeText(value)
  if (!normalized) return ''
  if (normalized.includes('contract') || normalized.includes('контракт') || normalized.includes('project') || normalized.includes('проект')) return 'contract'
  if (normalized.includes('part') || normalized.includes('част')) return 'part_time'
  return 'full_time'
}

const normalizeEducationLevel = (value) => {
  const normalized = normalizeText(value)
  if (!normalized) return ''
  if (normalized === 'primary' || normalized.includes('начальн') || normalized.includes('primary')) return 'primary'
  if (normalized === 'secondary' || normalized.includes('средн') || normalized.includes('secondary')) return 'secondary'
  if (normalized === 'vocational' || normalized.includes('профес') || normalized.includes('vocational')) return 'vocational'
  if (normalized === 'bachelor' || normalized.includes('бакалав') || normalized.includes('bachelor')) return 'bachelor'
  if (normalized === 'master' || normalized.includes('магистр') || normalized.includes('master')) return 'master'
  if (normalized === 'phd' || normalized.includes('доктор') || normalized.includes('phd')) return 'phd'
  return normalized
}

const normalizePermit = (value) => {
  const normalized = normalizeText(value)
  if (!normalized) return []
  if (normalized.includes('eu')) return ['EU']
  if (normalized.includes('visa') || normalized.includes('виза')) return ['visa']
  return [normalized]
}

const formatPercent = (value) => Math.round(clamp(value * 100, 0, 100))

const formatLanguage = (language) => {
  const name = String(language?.name || '').trim()
  const level = String(language?.level || '').trim()
  return level ? `${name} ${level}` : name
}

const formatList = (values) => values.filter(Boolean).join(', ')

const getProfileKey = (category) => CATEGORY_PROFILE[category] || 'service'

const getProfileLabel = (profileKey) => {
  const mapping = {
    physical: text('profilePhysical'),
    transport: text('profileTransport'),
    service: text('profileService'),
    office: text('profileOffice'),
    expert: text('profileExpert'),
  }

  return mapping[profileKey] || mapping.service
}

const getMatchMeta = (score, failedGates = []) => {
  const localized = copy()

  if (failedGates.length || score <= 0) return { ...MATCH_META.fail, label: localized.failMatch, shortLabel: localized.fail }
  if (score >= 85) return { ...MATCH_META.strong, label: localized.strongMatch, shortLabel: localized.strong }
  if (score >= 75) return { ...MATCH_META.good, label: localized.goodMatch, shortLabel: localized.good }
  if (score >= 50) return { ...MATCH_META.partial, label: localized.partialMatch, shortLabel: localized.partial }
  return { ...MATCH_META.weak, label: localized.weakMatch, shortLabel: localized.weak }
}

const getTrafficLight = ({ score = 0, failedGates = [] }) => {
  if (failedGates.length || score < 50) return 'red'
  if (score >= 75) return 'green'
  return 'amber'
}

const levenshtein = (left = '', right = '') => {
  const a = normalizeText(left)
  const b = normalizeText(right)
  if (a === b) return 0
  if (!a.length) return b.length
  if (!b.length) return a.length

  const matrix = Array.from({ length: b.length + 1 }, (_, row) => [row])
  for (let column = 0; column <= a.length; column += 1) matrix[0][column] = column

  for (let row = 1; row <= b.length; row += 1) {
    for (let column = 1; column <= a.length; column += 1) {
      const cost = a[column - 1] === b[row - 1] ? 0 : 1
      matrix[row][column] = Math.min(
        matrix[row - 1][column] + 1,
        matrix[row][column - 1] + 1,
        matrix[row - 1][column - 1] + cost,
      )
    }
  }

  return matrix[b.length][a.length]
}

const similarity = (left, right) => {
  const a = normalizeText(left)
  const b = normalizeText(right)
  if (!a || !b) return 0
  if (a === b) return 1
  if (a.includes(b) || b.includes(a)) return 0.9
  return 1 - (levenshtein(a, b) / Math.max(a.length, b.length))
}

const matchesFuzzy = (candidateValue, requiredValue) => similarity(candidateValue, requiredValue) >= 0.8

const extractFreeTags = (...values) => {
  const haystack = values.map((value) => String(value || '')).join(' ')
  const normalized = normalizeText(haystack)
  const tags = new Set()

  TAG_PHRASES.forEach((phrase) => {
    if (normalized.includes(normalizeText(phrase))) tags.add(phrase)
  })

  ;(haystack.match(LICENSE_PATTERN) || []).forEach((license) => tags.add(String(license).toUpperCase()))
  tokenize(haystack).slice(0, 18).forEach((token) => tags.add(token))

  return [...tags]
}

const normalizeCandidate = (candidate = {}) => {
  const languages = normalizeLanguages(
    candidate.candidate_languages ??
    candidate.languages ??
    candidate.languages_json,
  )

  const licenses = normalizeLicenses(
    candidate.candidate_licenses ??
    candidate.licenses ??
    candidate.licenses_json,
  ).filter((item) => normalizeText(item) !== 'no license' && normalizeText(item) !== 'нет лицензий')

  const sectors = Array.isArray(candidate.candidate_sectors)
    ? candidate.candidate_sectors
    : Array.isArray(candidate.sectors)
      ? candidate.sectors
      : []
  const salaryRange = parseSalaryRange(
    candidate.candidate_salary_expectation ||
    candidate.salary_expectation ||
    candidate.salary ||
    '',
  )

  return {
    salary: salaryRange.max || salaryRange.min || null,
    employment_type: normalizeEmploymentType(
      candidate.candidate_preferred_employment_type ||
      candidate.preferred_employment_type ||
      candidate.employment_type ||
      '',
    ),
    work_auth: normalizePermit(candidate.candidate_work_permit || candidate.work_permit || ''),
    driving_licenses: licenses,
    education: normalizeEducationLevel(candidate.candidate_education_level || candidate.education_level || ''),
    languages: Object.fromEntries(languages.map((language) => [normalizeText(language.name), levelRank(language.level)])),
    tags: extractFreeTags(
      candidate.candidate_current_role,
      candidate.current_role,
      candidate.candidate_summary,
      candidate.summary,
      candidate.candidate_skills,
      candidate.skills,
      ...licenses,
      ...sectors.map((sector) => sector?.name || sector?.label || ''),
    ),
    experience: sectors.map((sector) => ({
      category: String(sector?.id || sector?.value || '').trim(),
      years: EXPERIENCE_YEARS[String(sector?.experience || '').trim()] || 0,
      tags: extractFreeTags(sector?.name, sector?.label),
      certified: Boolean(candidate.candidate_resume_url || candidate.resume_url),
    })),
  }
}

const normalizeVacancy = (job = {}) => {
  const category = String(job.job_category || job.category || inferJobCategory({
    title: job.job_title || job.title,
    description: job.job_description || job.description,
    company: job.job_company || job.company,
  })).trim()
  const languages = normalizeLanguages(job.job_languages ?? job.languages ?? job.languages_json)
  const licenses = normalizeLicenses(job.job_licenses ?? job.licenses ?? job.licenses_json)
  const salaryRange = parseSalaryRange(job.job_salary || job.salary || '')
  const explicitExperienceLevel = normalizeText(job.job_experience_level || job.experience_level || '')
  const parsedMinYears = parseMinYears(job.job_title, job.title, job.job_description, job.description)
  const minYears = Object.prototype.hasOwnProperty.call(EXPERIENCE_YEARS, explicitExperienceLevel)
    ? EXPERIENCE_YEARS[explicitExperienceLevel]
    : parsedMinYears
  const title = job.job_title || job.title || ''
  const description = job.job_description || job.description || ''
  const requirements = []
  const educationLevel = normalizeEducationLevel(job.job_education_level || job.education_level || '')

  licenses.forEach((license) => {
    requirements.push({ type: 'driving_license', value: license, gate: 'hard' })
  })

  languages.forEach((language) => {
    requirements.push({
      type: 'language',
      lang: normalizeText(language.name),
      level: levelRank(language.level),
      gate: 'soft',
    })
  })

  extractFreeTags(title, description)
    .filter((tag) => !licenses.some((license) => normalizeText(license) === normalizeText(tag)))
    .slice(0, 8)
    .forEach((tag) => {
      requirements.push({ type: 'tag', value: tag, gate: 'soft' })
    })

  if (educationLevel) {
    requirements.push({ type: 'education', value: educationLevel, gate: 'soft' })
  }

  return {
    category,
    employment_type: normalizeEmploymentType(job.job_employment_type || job.employment_type),
    salary_range: salaryRange,
    min_years: minYears,
    requirements,
  }
}

const meetsRequirement = (candidate, requirement) => {
  if (!requirement) return true

  switch (requirement.type) {
    case 'work_auth':
      return candidate.work_auth.some((item) => normalizeText(item) === normalizeText(requirement.value) || normalizeText(item) === 'eu')
    case 'driving_license':
      return candidate.driving_licenses.some((item) => normalizeText(item) === normalizeText(requirement.value))
    case 'language':
      return (candidate.languages[normalizeText(requirement.lang)] || 0) >= Number(requirement.level || 0)
    case 'tag':
      return candidate.tags.some((tag) => matchesFuzzy(tag, requirement.value))
    case 'certified':
      return candidate.experience.some((item) => item.certified)
    case 'education':
      return (EDUCATION_RANK[candidate.education] ?? -1) >= (EDUCATION_RANK[requirement.value] ?? -1)
    case 'employment_type':
      return candidate.employment_type && candidate.employment_type === requirement.value
    default:
      return false
  }
}

const describeRequirementFailure = (requirement) => {
  switch (requirement?.type) {
    case 'driving_license':
      return text('gateLicense', { value: requirement.value })
    case 'language':
      return text('gateLanguage', { value: `${requirement.lang} ${requirement.level}` })
    case 'tag':
      return text('gateTag', { value: requirement.value })
    case 'work_auth':
      return text('gateWorkAuth', { value: requirement.value })
    case 'education':
      return text('gateEducation')
    case 'certified':
      return text('gateCertified')
    case 'employment_type':
      return text('gateEmployment')
    default:
      return text('gateUnknown')
  }
}

const evaluatePrefilters = (candidate, vacancy) => {
  const failures = []

  if (candidate.salary && vacancy.salary_range.max && candidate.salary > vacancy.salary_range.max) {
    failures.push(text('prefilterSalary'))
  }
  if (candidate.employment_type && vacancy.employment_type && candidate.employment_type !== vacancy.employment_type) {
    failures.push(text('prefilterEmployment'))
  }
  return failures
}

const scoreExperience = (candidate, vacancy) => {
  const relevant = candidate.experience.filter((item) => item.category === vacancy.category)
  const totalYears = relevant.reduce((sum, item) => sum + Number(item.years || 0), 0)

  if (!vacancy.min_years) {
    return {
      result: relevant.length ? 1 : 0.25,
      details: relevant.length
        ? [text('matchedExperience', { value: totalYears })]
        : [text('noRelevantExperience')],
    }
  }

  let result = 0
  if (totalYears >= vacancy.min_years) result = 1
  else if (totalYears >= vacancy.min_years * 0.75) result = 0.75
  else if (totalYears >= vacancy.min_years * 0.5) result = 0.5
  else if (totalYears > 0) result = 0.25

  return {
    result,
    details: [
      text('requiredExperience', { value: vacancy.min_years }),
      relevant.length ? text('matchedExperience', { value: totalYears }) : text('noRelevantExperience'),
    ],
  }
}

const scoreLanguages = (candidate, vacancy) => {
  const requirements = vacancy.requirements.filter((item) => item.type === 'language' && item.gate === 'soft')
  if (!requirements.length) return { result: null, details: [text('noLanguageRequirements')] }

  const results = requirements.map((requirement) => {
    const actual = candidate.languages[normalizeText(requirement.lang)] || 0
    const diff = Number(requirement.level || 0) - actual
    if (diff <= 0) return 1
    if (diff === 1) return 0.5
    return 0.1
  })

  const average = results.reduce((sum, value) => sum + value, 0) / results.length

  return {
    result: average,
    details: [
      text('requiredLanguages', {
        value: formatList(requirements.map((item) => `${item.lang.toUpperCase()} ${item.level}`)),
      }),
      Object.keys(candidate.languages).length ? text('languageAverage', { value: formatPercent(average) }) : text('languageMissing'),
    ],
  }
}

const scoreTags = (candidate, vacancy) => {
  const requirements = vacancy.requirements.filter((item) => item.type === 'tag' && item.gate === 'soft')
  if (!requirements.length) return { result: null, details: [text('noTagRequirements')] }

  const matched = []
  const missing = []

  requirements.forEach((requirement) => {
    if (candidate.tags.some((tag) => matchesFuzzy(tag, requirement.value))) matched.push(requirement.value)
    else missing.push(requirement.value)
  })

  return {
    result: matched.length / requirements.length,
    details: [
      matched.length ? text('matchedTags', { value: formatList(matched) }) : text('missingTags', { value: formatList(missing) }),
      missing.length ? text('missingTags', { value: formatList(missing) }) : '',
    ].filter(Boolean),
  }
}

const scoreEducation = (candidate, vacancy) => {
  const requirement = vacancy.requirements.find((item) => item.type === 'education' && item.gate === 'soft')
  if (!requirement) return { result: null, details: [text('noEducationRequirements')] }

  const candidateRank = EDUCATION_RANK[candidate.education] ?? -1
  const requiredRank = EDUCATION_RANK[requirement.value] ?? -1
  if (candidateRank >= requiredRank) return { result: 1, details: [text('educationMatched')] }
  if (candidateRank === requiredRank - 1) return { result: 0.5, details: [text('educationGap')] }
  return { result: 0, details: [text('educationLow')] }
}

const buildBreakdownCard = (key, label, result, details, failed = false) => ({
  key,
  label,
  score: failed ? 0 : clamp(Math.round((result ?? 0) * 100)),
  details,
  meta: failed ? getMatchMeta(0, ['failed']) : getMatchMeta(clamp(Math.round((result ?? 0) * 100))),
})

export const analyzeCandidateMatch = (candidateRaw, vacancyRaw) => {
  const candidate = normalizeCandidate(candidateRaw)
  const vacancy = normalizeVacancy(vacancyRaw)
  const profileKey = getProfileKey(vacancy.category)
  const profileWeights = PROFILE_WEIGHTS[profileKey]
  const prefilterFailures = evaluatePrefilters(candidate, vacancy)
  const hardRequirements = vacancy.requirements.filter((item) => item.gate === 'hard')
  const failedGates = hardRequirements.filter((item) => !meetsRequirement(candidate, item)).map(describeRequirementFailure)

  const prefilterBreakdown = buildBreakdownCard(
    'prefilters',
    text('prefilters'),
    prefilterFailures.length ? 0 : 1,
    prefilterFailures.length ? prefilterFailures : [text('pass')],
    prefilterFailures.length > 0,
  )

  const hardGateBreakdown = buildBreakdownCard(
    'gates',
    text('gates'),
    failedGates.length ? 0 : 1,
    failedGates.length ? failedGates : [text('pass')],
    failedGates.length > 0,
  )

  if (prefilterFailures.length || failedGates.length) {
    const score = 0
    return {
      score,
      profile: getProfileLabel(profileKey),
      profileKey,
      trafficLight: getTrafficLight({ score, failedGates }),
      failedGates: [...prefilterFailures, ...failedGates],
      meta: getMatchMeta(score, [...prefilterFailures, ...failedGates]),
      breakdown: [prefilterBreakdown, hardGateBreakdown],
    }
  }

  const factorResults = {
    experience: scoreExperience(candidate, vacancy),
    language: scoreLanguages(candidate, vacancy),
    tags: scoreTags(candidate, vacancy),
    education: scoreEducation(candidate, vacancy),
  }

  const weightedEntries = Object.entries(profileWeights)
    .map(([key, weight]) => {
      const result = factorResults[key]?.result
      return result == null ? null : { key, weight, result }
    })
    .filter(Boolean)

  const weightedSum = weightedEntries.reduce((sum, entry) => sum + (entry.result * entry.weight), 0)
  const applicableWeight = weightedEntries.reduce((sum, entry) => sum + entry.weight, 0)
  const score = applicableWeight ? clamp(Math.round((weightedSum / applicableWeight) * 100)) : 0
  const meta = getMatchMeta(score)

  return {
    score,
    profile: getProfileLabel(profileKey),
    profileKey,
    trafficLight: getTrafficLight({ score, failedGates: [] }),
    failedGates: [],
    meta,
    breakdown: [
      prefilterBreakdown,
      hardGateBreakdown,
      buildBreakdownCard('experience', text('experience'), factorResults.experience.result, factorResults.experience.details),
      buildBreakdownCard('language', text('language'), factorResults.language.result, factorResults.language.details),
      buildBreakdownCard('tags', text('tags'), factorResults.tags.result, factorResults.tags.details),
      buildBreakdownCard('education', text('education'), factorResults.education.result, factorResults.education.details),
    ],
  }
}

export const getMatchMetaByKey = (key) => MATCH_META[key] || MATCH_META.partial
