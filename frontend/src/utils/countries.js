export const countryMeta = [
  {
    key: 'germany',
    label: 'Германия',
    canonicalLabel: 'Germany',
    flagCode: 'de',
    aliases: ['germany', 'deutschland', 'германия'],
    cities: ['Berlin', 'Hamburg', 'Munich', 'Frankfurt', 'Leipzig', 'Stuttgart'],
  },
  {
    key: 'finland',
    label: 'Финляндия',
    canonicalLabel: 'Finland',
    flagCode: 'fi',
    aliases: ['finland', 'suomi', 'финляндия'],
    cities: ['Helsinki', 'Tampere', 'Turku', 'Oulu', 'Vantaa'],
  },
  {
    key: 'czechia',
    label: 'Чехия',
    canonicalLabel: 'Czechia',
    flagCode: 'cz',
    aliases: ['czechia', 'czech republic', 'cesko', 'česko', 'чехия'],
    cities: ['Prague', 'Brno', 'Ostrava', 'Pilsen'],
  },
  {
    key: 'netherlands',
    label: 'Нидерланды',
    canonicalLabel: 'Netherlands',
    flagCode: 'nl',
    aliases: ['netherlands', 'nederland', 'holland', 'нидерланды'],
    cities: ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven'],
  },
  {
    key: 'poland',
    label: 'Польша',
    canonicalLabel: 'Poland',
    flagCode: 'pl',
    aliases: ['poland', 'polska', 'польша'],
    cities: ['Warsaw', 'Krakow', 'Wroclaw', 'Gdansk', 'Poznan'],
  },
  {
    key: 'belgium',
    label: 'Бельгия',
    canonicalLabel: 'Belgium',
    flagCode: 'be',
    aliases: ['belgium', 'belgie', 'belgique', 'бельгия'],
    cities: ['Brussels', 'Antwerp', 'Ghent', 'Liege'],
  },
  {
    key: 'france',
    label: 'Франция',
    canonicalLabel: 'France',
    flagCode: 'fr',
    aliases: ['france', 'francia', 'frankrijk', 'франция'],
    cities: ['Paris', 'Lyon', 'Marseille', 'Lille', 'Toulouse'],
  },
  {
    key: 'latvia',
    label: 'Латвия',
    canonicalLabel: 'Latvia',
    flagCode: 'lv',
    aliases: ['latvia', 'latvija', 'латвия'],
    cities: ['Riga', 'Liepaja', 'Daugavpils', 'Jelgava', 'Ventspils'],
  },
  {
    key: 'estonia',
    label: 'Эстония',
    canonicalLabel: 'Estonia',
    flagCode: 'ee',
    aliases: ['estonia', 'eesti', 'эстония'],
    cities: ['Tallinn', 'Tartu', 'Narva', 'Parnu'],
  },
]

export const citiesByCountry = Object.fromEntries(
  countryMeta.map((country) => [country.key, country.cities]),
)

export const salaryCurrencyOptions = [
  { value: '€', label: '€' },
  { value: '$', label: '$' },
  { value: 'zł', label: 'zł' },
  { value: 'Kč', label: 'Kč' },
]

const normalizeText = (value = '') => String(value || '')
  .normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLowerCase()
  .replace(/[^a-zа-яё0-9]+/gi, ' ')
  .trim()

const looksLikeMojibake = (value = '') => /[ÐÑ]/.test(String(value || ''))

const countryAliases = Object.fromEntries(
  countryMeta.flatMap((country) => country.aliases.map((alias) => [normalizeText(alias), country.key])),
)

export const countryDropdownOptions = countryMeta.map((country) => ({
  value: country.key,
  label: country.label,
  iconClass: `fi fi-${country.flagCode}`,
}))

export const countryByKey = Object.fromEntries(countryMeta.map((country) => [country.key, country]))

export const inferCountryFromLabel = (value = '') => {
  const normalized = normalizeText(value)
  return countryAliases[normalized] || ''
}

export const inferCountryFromLocation = (location = '') => {
  const normalizedLocation = normalizeText(location)
  if (!normalizedLocation) return ''

  const matchedCountry = countryMeta.find((country) => (
    country.aliases.some((alias) => normalizedLocation.includes(normalizeText(alias)))
      || country.cities.some((city) => normalizedLocation.includes(normalizeText(city)))
  ))

  return matchedCountry?.key || ''
}

const normalizeCountryKey = (value = '') => normalizeText(value).replace(/\s+/g, '')

export const resolveCountryMeta = (job = {}) => {
  const rawCountryKey = normalizeCountryKey(job.country_key || job.countryKey)
  const rawFlagCode = String(job.country_flag_code || job.countryFlagCode || '').trim().toLowerCase()
  const detectedCountryKey = rawCountryKey
    || inferCountryFromLabel(job.country_label)
    || inferCountryFromLabel(job.countryLabel)
    || inferCountryFromLocation(job.location)
  const country = countryByKey[detectedCountryKey] || null
  const safeLabel = [job.countryLabel, job.country_label]
    .map((value) => String(value || '').trim())
    .find((value) => value && !looksLikeMojibake(value) && normalizeText(value) !== 'europe')

  return {
    countryKey: country?.key || detectedCountryKey || '',
    countryLabel: country?.label || safeLabel || '',
    countryFlagCode: country?.flagCode || rawFlagCode || '',
  }
}

export const formatJobLocation = (job = {}) => {
  const { countryLabel } = resolveCountryMeta(job)
  const location = String(job.location || '').trim()

  if (countryLabel && location) return `${countryLabel}, ${location}`
  return countryLabel || location || 'Локация не указана'
}