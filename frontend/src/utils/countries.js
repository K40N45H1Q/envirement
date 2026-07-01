export const countryMeta = [
  { key: 'germany', label: 'Германия', flagCode: 'de' },
  { key: 'finland', label: 'Финляндия', flagCode: 'fi' },
  { key: 'czechia', label: 'Чехия', flagCode: 'cz' },
  { key: 'netherlands', label: 'Нидерланды', flagCode: 'nl' },
  { key: 'poland', label: 'Польша', flagCode: 'pl' },
  { key: 'belgium', label: 'Бельгия', flagCode: 'be' },
  { key: 'france', label: 'Франция', flagCode: 'fr' },
  { key: 'latvia', label: 'Латвия', flagCode: 'lv' },
  { key: 'estonia', label: 'Эстония', flagCode: 'ee' },
]

export const countryDropdownOptions = countryMeta.map((country) => ({
  value: country.key,
  label: country.label,
  iconClass: `fi fi-${country.flagCode}`,
}))

export const countryByKey = Object.fromEntries(countryMeta.map((country) => [country.key, country]))

export const inferCountryFromLocation = (location = '') => {
  const value = String(location || '').toLowerCase()
  if (value.includes('герман') || value.includes('germany') || value.includes('berlin')) return 'germany'
  if (value.includes('finland') || value.includes('финля') || value.includes('tampere')) return 'finland'
  if (value.includes('czech') || value.includes('чех') || value.includes('prague') || value.includes('praha')) return 'czechia'
  if (value.includes('нидер') || value.includes('netherlands') || value.includes('rotterdam')) return 'netherlands'
  if (value.includes('польш') || value.includes('poland') || value.includes('warsaw')) return 'poland'
  if (value.includes('бельг') || value.includes('belgium') || value.includes('antwerp')) return 'belgium'
  if (value.includes('франц') || value.includes('france') || value.includes('paris')) return 'france'
  if (value.includes('латв') || value.includes('latvia') || value.includes('riga')) return 'latvia'
  if (value.includes('эстон') || value.includes('estonia') || value.includes('tallinn')) return 'estonia'
  return ''
}

export const resolveCountryMeta = (job = {}) => {
  const countryKey = String(job.country_key || job.countryKey || inferCountryFromLocation(job.location) || '').trim()
  const country = countryByKey[countryKey] || null

  return {
    countryKey: country?.key || countryKey,
    countryLabel: String(job.country_label || job.countryLabel || country?.label || '').trim(),
    countryFlagCode: String(job.country_flag_code || job.countryFlagCode || country?.flagCode || '').trim(),
  }
}

export const formatJobLocation = (job = {}) => {
  const country = String(job.country_label || job.countryLabel || '').trim()
  const location = String(job.location || '').trim()

  if (country && location) return `${country}, ${location}`
  return country || location || 'Локация не указана'
}
