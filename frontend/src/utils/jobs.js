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

export const demoJobs = [
  {
    id: 'demo-electrician',
    title: 'Электрик',
    company: 'Build Solutions GmbH',
    location: 'Берлин, Германия',
    country_key: 'germany',
    country_label: 'Германия',
    country_flag_code: 'de',
    salary: '2 200 - 2 800 €',
    description: 'Монтаж и обслуживание промышленных электрических систем на строительных объектах.',
    logo: '',
  },
  {
    id: 'demo-welder',
    title: 'Сварщик MIG/MAG',
    company: 'Nord Metal',
    location: 'Тампере, Финляндия',
    country_key: 'finland',
    country_label: 'Финляндия',
    country_flag_code: 'fi',
    salary: '2 600 - 3 100 €',
    description: 'Работа с металлоконструкциями, чтение чертежей, стабильные смены.',
    logo: '',
  },
  {
    id: 'demo-driver',
    title: 'Водитель CE',
    company: 'Euro Logistics',
    location: 'Прага, Чехия',
    country_key: 'czechia',
    country_label: 'Чехия',
    country_flag_code: 'cz',
    salary: '2 000 - 2 500 €',
    description: 'Международные перевозки, современный автопарк, помощь с документами.',
    logo: '',
  },
]

export const initialsFor = (value = '') => {
  const words = value.trim().split(/\s+/).filter(Boolean)
  return (words.length ? words : ['CV'])
    .slice(0, 2)
    .map(word => word[0])
    .join('')
    .toUpperCase()
}

export const normalizeJob = (job, index = 0) => {
  const country = resolveCountryMeta(job)

  return {
    id: job.id ?? job.slug ?? index,
    title: job.title || 'Вакансия',
    company: job.company || 'Компания',
    location: job.location || 'Локация не указана',
    displayLocation: formatJobLocation(job),
    employment_type: job.employment_type || job.employmentType || '',
    countryKey: country.countryKey,
    countryLabel: country.countryLabel || 'Европа',
    countryFlagCode: country.countryFlagCode || 'eu',
    salary: job.salary || 'По договоренности',
    description: job.description || '',
    logo: job.logo || '',
    languages_json: job.languages_json || '',
    licenses_json: job.licenses_json || '',
    languages: parseJsonArray(job.languages ?? job.languages_json),
    licenses: parseJsonArray(job.licenses ?? job.licenses_json),
    has_housing: Boolean(job.has_housing),
    has_transport: Boolean(job.has_transport),
    status: job.status || 'approved',
    created_at: job.created_at || '',
    initials: initialsFor(job.company || job.title),
    color: colors[index % colors.length],
  }
}

export const filterJobs = (jobs, query = {}) => {
  const q = (query.q || '').toString().toLowerCase()
  const loc = (query.loc || '').toString().toLowerCase()
  const cat = (query.cat || '').toString().toLowerCase()

  return jobs.filter(job => {
    const haystack = `${job.title} ${job.company} ${job.description}`.toLowerCase()
    const place = job.location.toLowerCase()
    return (!q || haystack.includes(q))
      && (!loc || place.includes(loc))
      && (!cat || haystack.includes(cat))
  })
}
