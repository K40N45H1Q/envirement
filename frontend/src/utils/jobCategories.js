export const categoryConfigs = [
  { id: 'all', labelKey: 'jobsStore.allCategories', icon: 'fas fa-border-all' },
  { id: 'construction', labelKey: 'categories.construction', icon: 'fas fa-hard-hat' },
  { id: 'production', labelKey: 'categories.production', icon: 'fas fa-industry' },
  { id: 'logistics', labelKey: 'categories.logistics', icon: 'fas fa-truck-fast' },
  { id: 'it', labelKey: 'categories.it', icon: 'fas fa-laptop-code' },
  { id: 'health', labelKey: 'categories.health', icon: 'fas fa-heart-pulse' },
  { id: 'hospitality', labelKey: 'categories.hospitality', icon: 'fas fa-bell-concierge' },
]

export const localizeCategoryConfigs = (translate) => categoryConfigs.map((category) => ({
  ...category,
  label: translate(category.labelKey),
}))

export const inferJobCategory = (job = {}) => {
  const explicitCategory = String(job.category || job.job_category || '').trim().toLowerCase()
  if (categoryConfigs.some((category) => category.id === explicitCategory && explicitCategory !== 'all')) {
    return explicitCategory
  }

  const haystack = `${job.title || ''} ${job.description || ''} ${job.company || ''}`.toLowerCase()

  if (/(свар|weld|welder|welding|монтаж|стро|construction|electric|элект|technician|repair|metal)/.test(haystack)) return 'construction'
  if (/(manufactur|производ|factory|industrial|assembly|operator)/.test(haystack)) return 'production'
  if (/(driver|логист|transport|truck|warehouse|fleet|\bce\b|courier|delivery)/.test(haystack)) return 'logistics'
  if (/(\bdeveloper\b|\bsoftware\b|\bdata\b|\btech\b|\bfrontend\b|\bbackend\b|\bfullstack\b|\bdevops\b|\bqa\b|\bit support\b)/.test(haystack)) return 'it'
  if (/(medical|doctor|nurse|мед|clinic|caregiver|healthcare)/.test(haystack)) return 'health'
  if (/(hotel|hostel|chef|cook|restaurant|guest|hospitality|waiter)/.test(haystack)) return 'hospitality'
  return 'construction'
}
