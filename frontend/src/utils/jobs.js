const colors = ['#19785a', '#1e2326', '#2563eb', '#9333ea', '#0f766e', '#b45309']

export const demoJobs = [
  {
    id: 'demo-electrician',
    title: 'Электрик',
    company: 'Build Solutions GmbH',
    location: 'Берлин, Германия',
    salary: '2 200 - 2 800 €',
    description: 'Монтаж и обслуживание промышленных электрических систем на строительных объектах.',
    logo: '',
  },
  {
    id: 'demo-welder',
    title: 'Сварщик MIG/MAG',
    company: 'Nord Metal',
    location: 'Тампере, Финляндия',
    salary: '2 600 - 3 100 €',
    description: 'Работа с металлоконструкциями, чтение чертежей, стабильные смены.',
    logo: '',
  },
  {
    id: 'demo-driver',
    title: 'Водитель CE',
    company: 'Euro Logistics',
    location: 'Прага, Чехия',
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

export const normalizeJob = (job, index = 0) => ({
  id: job.id ?? job.slug ?? index,
  title: job.title || 'Вакансия',
  company: job.company || 'Компания',
  location: job.location || 'Локация не указана',
  salary: job.salary || 'По договоренности',
  description: job.description || '',
  logo: job.logo || '',
  has_housing: Boolean(job.has_housing),
  has_transport: Boolean(job.has_transport),
  status: job.status || 'approved',
  created_at: job.created_at || '',
  initials: initialsFor(job.company || job.title),
  color: colors[index % colors.length],
})

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
