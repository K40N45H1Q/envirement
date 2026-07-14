import { translate } from '@/i18n'
import { getLocaleFromPath } from '@/router/locale'
import { formatJobLocation, resolveCountryMeta } from './countries'

const colors = ['#19785a', '#1e2326', '#2563eb', '#9333ea', '#0f766e', '#b45309']

const parseJsonArray = (value) => {
  if (Array.isArray(value)) return value
  if (typeof value !== 'string' || !value.trim()) return []

  try {
    const parsed = JSON.parse(value)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

const getLanguage = () => {
  if (typeof window === 'undefined') return 'ru'
  return getLocaleFromPath(window.location.pathname)
}

const t = (key) => translate(`jobsUtil.${key}`, {}, getLanguage())

export const initialsFor = (value = '') => {
  const words = value.trim().split(/\s+/).filter(Boolean)
  return (words.length ? words : ['CV'])
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase()
}

export const normalizeJob = (job, index = 0) => {
  const country = resolveCountryMeta(job)

  return {
    id: job.id ?? job.slug ?? index,
    user_id: job.user_id ?? job.userId ?? null,
    title: job.title || t('vacancy'),
    company: job.company || t('company'),
    location: job.location || t('locationMissing'),
    displayLocation: formatJobLocation(job),
    employment_type: job.employment_type || job.employmentType || '',
    experience_level: job.experience_level || job.job_experience_level || '',
    education_level: job.education_level || '',
    category: job.category || job.job_category || '',
    countryKey: country.countryKey,
    countryLabel: country.countryLabel || t('europe'),
    countryFlagCode: country.countryFlagCode || 'eu',
    salary: job.salary || t('salaryNegotiable'),
    description: job.description || '',
    logo: job.logo || '',
    banner_url: job.banner_url || job.job_banner_url || '',
    languages_json: job.languages_json || '',
    licenses_json: job.licenses_json || '',
    languages: parseJsonArray(job.languages ?? job.languages_json),
    licenses: parseJsonArray(job.licenses ?? job.licenses_json),
    has_housing: Boolean(job.has_housing),
    has_transport: Boolean(job.has_transport),
    status: job.status || 'approved',
    rejection_reason: job.rejection_reason || '',
    created_at: job.created_at || '',
    initials: initialsFor(job.company || job.title),
    color: colors[index % colors.length],
  }
}

export const filterJobs = (jobs, query = {}) => {
  const q = (query.q || '').toString().toLowerCase()
  const loc = (query.loc || '').toString().toLowerCase()
  const cat = (query.cat || '').toString().toLowerCase()

  return jobs.filter((job) => {
    const haystack = `${job.title} ${job.company} ${job.description}`.toLowerCase()
    const place = job.location.toLowerCase()
    return (!q || haystack.includes(q))
      && (!loc || place.includes(loc))
      && (!cat || haystack.includes(cat))
  })
}
