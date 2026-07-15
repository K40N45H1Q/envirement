export const toText = (value) => (value == null ? '' : String(value))

export const toArray = (value) => {
  if (Array.isArray(value)) return value
  if (typeof value !== 'string' || !value.trim()) return []

  try {
    const parsed = JSON.parse(value)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export const splitTextList = (value) => toText(value)
  .split(/[,;\n]+/)
  .map((item) => item.trim())
  .filter(Boolean)

export const limitText = (value, maxLength = 520, { preserveLineBreaks = false } = {}) => {
  const cleanText = preserveLineBreaks
    ? toText(value).replace(/[^\S\r\n]+/g, ' ').replace(/\r\n?/g, '\n').trim()
    : toText(value).replace(/\s+/g, ' ').trim()
  if (cleanText.length <= maxLength) return cleanText

  const clipped = cleanText.slice(0, maxLength).replace(/[^\S\r\n]+\S*$/, '').trim()
  return `${clipped}…`
}

export const createEmptyWorkExperience = () => ({
  occupation_id: '',
  position: '',
  job_category: '',
  company_name: '',
  start_date: '',
  end_date: '',
  current: false,
  country: 'Latvia',
  description: '',
})

export const createEmptyEducation = () => ({
  level: '',
  institution: '',
  speciality: '',
  second_speciality: '',
  country: 'Latvia',
  start_date: '',
  end_date: '',
  current: false,
  unfinished: false,
  additional_information: '',
})

export const createEmptyResumeData = () => ({
  cv_language: 'lv',
  birth_date: '',
  birth_month: '',
  birth_day: '',
  birth_year: '',
  hide_birth_date: false,
  gender: '',
  hide_gender: false,
  communication_language: 'lv',
  citizenship: '',
  no_driving_license: false,
  driving_licenses: [],
  additional_emails: [],
  additional_phones: [],
  no_work_experience: false,
  work_experiences: [createEmptyWorkExperience()],
  educations: [createEmptyEducation()],
})

export const createEmptyProfile = () => ({
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  summary: '',
  current_role: '',
  desired_occupation_id: '',
  desired_occupation_label: '',
  skills: '',
  skill_ids: [],
  sectors: [],
  languages: [],
  licenses: [],
  mobility: '',
  work_permit: '',
  availability: '',
  salary_expectation: '',
  preferred_employment_type: '',
  education_level: '',
  remote_ready: false,
  resume_name: '',
  resume_url: '',
  avatar_url: '',
  resume_data: createEmptyResumeData(),
})

export const parseBirthDate = (value) => {
  const text = toText(value).trim()
  if (!text) return null

  if (/^\d{4}-\d{2}-\d{2}$/.test(text)) {
    const [year, month, day] = text.split('-').map(Number)
    const parsed = new Date(year, month - 1, day)
    if (
      parsed.getFullYear() !== year
      || parsed.getMonth() !== month - 1
      || parsed.getDate() !== day
    ) return null
    return parsed
  }

  if (/^\d{2}\.\d{2}\.\d{4}$/.test(text)) {
    const [day, month, year] = text.split('.').map(Number)
    const parsed = new Date(year, month - 1, day)
    if (
      parsed.getFullYear() !== year
      || parsed.getMonth() !== month - 1
      || parsed.getDate() !== day
    ) return null
    return parsed
  }

  return null
}

export const isValidDateValue = (value) => Boolean(parseBirthDate(value))

export const formatDateTypingValue = (value) => {
  const digits = toText(value).replace(/\D+/g, '').slice(0, 8)
  if (!digits) return ''
  if (digits.length <= 2) return digits
  if (digits.length <= 4) return `${digits.slice(0, 2)}.${digits.slice(2)}`
  return `${digits.slice(0, 2)}.${digits.slice(2, 4)}.${digits.slice(4)}`
}

export const formatDateInput = (value) => {
  const parsed = parseBirthDate(value)
  if (!parsed) return toText(value)

  const day = String(parsed.getDate()).padStart(2, '0')
  const month = String(parsed.getMonth() + 1).padStart(2, '0')
  const year = String(parsed.getFullYear())
  return `${day}.${month}.${year}`
}

export const normalizeDateInput = (value) => {
  const text = formatDateTypingValue(value)
  if (!text) return ''

  if (/^\d{2}\.\d{2}\.\d{4}$/.test(text)) {
    const [day, month, year] = text.split('.').map(Number)
    return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  }

  return text
}

export const formatDateValue = (value, locale) => {
  const parsed = parseBirthDate(value)
  if (!parsed) return toText(value)
  return new Intl.DateTimeFormat(locale).format(parsed)
}

export const isValidEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(toText(value).trim())

export const getPhoneDigits = (value) => toText(value).replace(/\D+/g, '')

export const isValidPhone = (value) => getPhoneDigits(value).length >= 7
