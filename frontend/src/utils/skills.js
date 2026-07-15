import skillsCatalog from '@/data/skillsCatalog'

const normalize = (value = '') => String(value).toLocaleLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').trim()
const localeFor = (locale) => ['ru', 'en', 'lv'].includes(locale) ? locale : 'ru'

export const getSkillOptions = (locale = 'ru') => {
  const resolved = localeFor(locale)
  return skillsCatalog.map((skill) => ({
    id: skill.id,
    value: skill.id,
    label: skill[resolved] || skill.en,
    category: skill.category,
    sector: skill.sector,
    searchLabel: normalize(`${skill.ru} ${skill.en} ${skill.lv}`),
  }))
}

export const findSkillSuggestions = (query = '', locale = 'ru', selected = [], limit = 8) => {
  const search = normalize(query)
  const excluded = new Set(selected.map((item) => String(item?.id || item)))
  if (!search) return []
  return getSkillOptions(locale)
    .filter((skill) => !excluded.has(skill.id) && skill.searchLabel.includes(search))
    .sort((left, right) => Number(!normalize(left.label).startsWith(search)) - Number(!normalize(right.label).startsWith(search)))
    .slice(0, limit)
}

export const localizeSkill = (value, locale = 'ru') => {
  const id = String(value?.id || value || '')
  return getSkillOptions(locale).find((skill) => skill.id === id)?.label || String(value?.label || value || '')
}
