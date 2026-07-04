const createCategory = (id, labelKey, icon, patterns = []) => ({
  id,
  labelKey,
  icon,
  patterns,
})

export const categoryConfigs = [
  createCategory('all', 'jobsStore.allCategories', 'fas fa-border-all'),
  createCategory('administrative-work', 'categories.administrativeWork', 'fas fa-clipboard-list', [
    /\b(admin|administrator|administrative|office manager|office assistant|secretary|receptionist|clerk)\b/i,
    /(админ|административ|офис|секретар|делопроизвод|оператор офиса)/i,
  ]),
  createCategory('banking', 'categories.banking', 'fas fa-building-columns', [
    /\b(bank|banking|teller|loan officer|credit specialist)\b/i,
    /(банк|банков|кредитн|кассир банка)/i,
  ]),
  createCategory('public-administration', 'categories.publicAdministration', 'fas fa-landmark', [
    /\b(government|municipal|public administration|civil service|state agency)\b/i,
    /(гос|муниципал|государственн|госслужб)/i,
  ]),
  createCategory('healthcare-social-work', 'categories.healthcareSocialWork', 'fas fa-heart-pulse', [
    /\b(doctor|nurse|medical|clinic|healthcare|caregiver|social worker|pharmacist)\b/i,
    /(мед|врач|медсестр|клиник|уход|социальн)/i,
  ]),
  createCategory('information-technology', 'categories.informationTechnology', 'fas fa-laptop-code', [
    /\b(developer|software|frontend|backend|fullstack|devops|qa|data engineer|it support|sysadmin|programmer)\b/i,
    /(разработчик|программист|айти|it|системн(?:ый|ого) администратор|тестировщик|данных)/i,
  ]),
  createCategory('marketing-advertising-pr', 'categories.marketingAdvertisingPr', 'fas fa-bullhorn', [
    /\b(marketing|advertising|brand manager|seo|smm|content manager|pr manager|copywriter)\b/i,
    /(маркетинг|реклам|бренд|копирайт|pr|пиар|smm|seo|контент)/i,
  ]),
  createCategory('media-creative-translation', 'categories.mediaCreativeTranslation', 'fas fa-photo-film', [
    /\b(designer|videographer|photographer|editor|translator|localization|media|creative)\b/i,
    /(дизайн|фото|видео|редактор|перевод|локализац|медиа|креатив)/i,
  ]),
  createCategory('mechanics-technology', 'categories.mechanicsTechnology', 'fas fa-gears', [
    /\b(mechanic|mechanical|technician|repair|maintenance|engineer|service engineer)\b/i,
    /(механик|техник|ремонт|обслуживан|инженер|наладчик)/i,
  ]),
  createCategory('education-science', 'categories.educationScience', 'fas fa-graduation-cap', [
    /\b(teacher|tutor|lecturer|professor|research|scientist|education)\b/i,
    /(учител|преподав|репетитор|исследов|наук|образован)/i,
  ]),
  createCategory('service', 'categories.service', 'fas fa-concierge-bell', [
    /\b(customer service|support specialist|call center|cleaner|housekeeping|assistant)\b/i,
    /(обслуживан|клиентск|поддержк|уборк|хаускипинг|помощник)/i,
  ]),
  createCategory('security', 'categories.security', 'fas fa-shield-halved', [
    /\b(security guard|security officer|law enforcement|police|safety inspector)\b/i,
    /(охран|безопасн|полиц|инспектор безопасности)/i,
  ]),
  createCategory('hr-training', 'categories.hrTraining', 'fas fa-users-gear', [
    /\b(hr|human resources|recruiter|talent acquisition|trainer|learning)\b/i,
    /(hr|рекрутер|подбор персонала|персонал|обучени|кадров)/i,
  ]),
  createCategory('food', 'categories.food', 'fas fa-utensils', [
    /\b(cook|chef|baker|barista|kitchen|food production)\b/i,
    /(повар|пекар|бариста|кухн|питан)/i,
  ]),
  createCategory('sales', 'categories.sales', 'fas fa-cart-shopping', [
    /\b(sales|sales manager|account manager|business development|cashier|seller)\b/i,
    /(продаж|продавец|кассир|аккаунт менеджер|менеджер по продажам)/i,
  ]),
  createCategory('industry-production', 'categories.industryProduction', 'fas fa-industry', [
    /\b(factory|industrial|manufacturing|production|assembly|machine operator|operator)\b/i,
    /(завод|промышлен|производств|сборк|оператор линии|станок)/i,
  ]),
  createCategory('agriculture-forestry', 'categories.agricultureForestry', 'fas fa-wheat-awn', [
    /\b(farm|agriculture|forestry|harvest|livestock)\b/i,
    /(ферм|сельск|урожай|лес|агро)/i,
  ]),
  createCategory('construction-real-estate', 'categories.constructionRealEstate', 'fas fa-helmet-safety', [
    /\b(construction|electrician|welder|plumber|carpenter|real estate|site manager|foreman)\b/i,
    /(строит|электрик|сварщик|свар|монтаж|сантех|плотник|недвижим|прораб)/i,
  ]),
  createCategory('transport-logistics', 'categories.transportLogistics', 'fas fa-truck-fast', [
    /\b(driver|truck|warehouse|logistics|courier|delivery|fleet|dispatcher)\b/i,
    /(водител|грузовик|склад|логист|курьер|доставк|диспетчер|ce\b)/i,
  ]),
  createCategory('tourism-hospitality', 'categories.tourismHospitality', 'fas fa-hotel', [
    /\b(hotel|hostel|tourism|travel consultant|guest relations|waiter|restaurant)\b/i,
    /(отел|гостиниц|туризм|ресторан|официант|хостес)/i,
  ]),
  createCategory('management', 'categories.management', 'fas fa-briefcase', [
    /\b(manager|management|team lead|operations manager|director|supervisor)\b/i,
    /(менеджер|управлен|руководител|директор|супервайзер)/i,
  ]),
  createCategory('finance', 'categories.finance', 'fas fa-coins', [
    /\b(finance|financial|accountant|auditor|controller|bookkeeper|payroll)\b/i,
    /(финанс|бухгалтер|аудитор|контрол[её]р|зарплат)/i,
  ]),
  createCategory('electronics-telecommunications', 'categories.electronicsTelecommunications', 'fas fa-microchip', [
    /\b(electronics|telecom|telecommunications|network engineer|fiber optic|embedded)\b/i,
    /(электрон|телеком|сети|оптоволокн|embedded)/i,
  ]),
  createCategory('energy-natural-resources', 'categories.energyNaturalResources', 'fas fa-bolt', [
    /\b(energy|power plant|oil|gas|mining|solar|wind|utilities)\b/i,
    /(энергет|электростанц|нефт|газ|добыч|солнеч|ветрян)/i,
  ]),
]

const categoryById = Object.fromEntries(categoryConfigs.map((category) => [category.id, category]))

export const localizeCategoryConfigs = (translate) => categoryConfigs.map((category) => ({
  ...category,
  label: translate(category.labelKey),
}))

export const inferJobCategory = (job = {}) => {
  const explicitCategory = String(job.category || job.job_category || '').trim().toLowerCase()
  if (categoryById[explicitCategory] && explicitCategory !== 'all') {
    return explicitCategory
  }

  const haystack = `${job.title || ''} ${job.description || ''} ${job.company || ''}`
  const matchedCategory = categoryConfigs
    .filter((category) => category.id !== 'all')
    .find((category) => category.patterns.some((pattern) => pattern.test(haystack)))

  return matchedCategory?.id || 'service'
}
