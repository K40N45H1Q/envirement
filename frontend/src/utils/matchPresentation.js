import { resolveOccupation } from '@/utils/occupations'

const COPY = {
  ru: {
    excellent: 'Отличное совпадение', good: 'Хорошее совпадение', partial: 'Частичное совпадение', weak: 'Слабое совпадение',
    excluded: 'Вне профессиональной области', outside_occupation: 'Профессия не совпадает',
    experience: 'Опыт', languages: 'Языки', availability: 'Доступность', credentials: 'Права и лицензии', skills: 'Навыки', stability_penalty: 'Стабильность',
    required_missing: 'Обязательное требование', stability: 'Частая смена работы', exceeds_requirement: 'Выше требования', serverMatch: 'Серверный расчёт',
  },
  en: {
    excellent: 'Excellent match', good: 'Good match', partial: 'Partial match', weak: 'Weak match',
    excluded: 'Outside professional area', outside_occupation: 'Occupation does not match',
    experience: 'Experience', languages: 'Languages', availability: 'Availability', credentials: 'Licences and certificates', skills: 'Skills', stability_penalty: 'Stability',
    required_missing: 'Mandatory requirement', stability: 'Frequent job changes', exceeds_requirement: 'Exceeds requirement', serverMatch: 'Server-calculated match',
  },
  lv: {
    excellent: 'Izcila atbilstība', good: 'Laba atbilstība', partial: 'Daļēja atbilstība', weak: 'Vāja atbilstība',
    excluded: 'Ārpus profesionālās jomas', outside_occupation: 'Profesija neatbilst',
    experience: 'Pieredze', languages: 'Valodas', availability: 'Pieejamība', credentials: 'Tiesības un licences', skills: 'Prasmes', stability_penalty: 'Stabilitāte',
    required_missing: 'Obligāta prasība', stability: 'Bieža darba maiņa', exceeds_requirement: 'Pārsniedz prasību', serverMatch: 'Servera aprēķins',
  },
}

const META = {
  strong: { key: 'strong', textColor: '#19785a', badgeBackground: '#e6f0ec' },
  good: { key: 'good', textColor: '#19785a', badgeBackground: '#e6f0ec' },
  partial: { key: 'partial', textColor: '#d68a12', badgeBackground: '#fef3e2' },
  weak: { key: 'weak', textColor: '#dc2626', badgeBackground: '#fee2e2' },
  fail: { key: 'fail', textColor: '#dc2626', badgeBackground: '#fee2e2' },
}

const styleKeyForScore = (score) => (
  score >= 90 ? 'strong' : score >= 70 ? 'good' : score >= 50 ? 'partial' : 'weak'
)

const detailLines = (key, detail, copy) => {
  if (key === 'experience') return [`${detail.actual_months || 0} / ${detail.required_months || 0} мес.`]
  if (key === 'availability') return detail.required_from ? [`${detail.candidate_from || '—'} → ${detail.required_from}`] : []
  if (key === 'stability_penalty') return detail.average_tenure_months ? [`${copy.stability}: ${detail.average_tenure_months} мес.`] : []
  if ('required' in detail) return [`${detail.matched || 0} / ${detail.required || 0}`]
  return []
}

export const presentMatchAnalysis = (raw = {}, locale = 'ru') => {
  const copy = COPY[locale] || COPY.ru
  const excluded = Boolean(raw?.excluded)
  const score = excluded ? null : Number(raw?.score || 0)
  const styleKey = excluded ? 'fail' : styleKeyForScore(score)
  const flags = Array.isArray(raw?.flags) ? raw.flags : []
  const redFlags = flags.filter((flag) => flag.type === 'required_missing')
  const exclusionFlags = flags.filter((flag) => flag.type === 'outside_occupation')
  const localizedOccupation = (value) => resolveOccupation(value, '', locale)?.label || value
  const hasStabilityFlag = flags.some((flag) => flag.type === 'stability')
  const breakdown = Object.entries(raw?.breakdown || {}).map(([key, detail]) => {
    const points = Number(detail?.points || 0)
    const max = Number(detail?.max_points || 0)
    const partScore = key === 'stability_penalty' ? Math.max(0, 100 + points * 10) : max ? Math.round(points / max * 100) : 100
    const partStyle = styleKeyForScore(partScore)
    return {
      key,
      label: copy[key] || key,
      score: key === 'stability_penalty' ? points : `${points}/${max}`,
      details: detailLines(key, detail || {}, copy),
      meta: META[partStyle],
    }
  })

  return {
    score,
    excluded,
    label: raw?.label || 'weak',
    algorithmVersion: raw?.algorithm_version || '',
    profile: copy.serverMatch,
    trafficLight: excluded || redFlags.length ? 'red' : hasStabilityFlag ? 'yellow' : score >= 70 ? 'green' : score >= 50 ? 'yellow' : 'red',
    failedGates: [
      ...exclusionFlags.map((flag) => `${copy.outside_occupation}: ${localizedOccupation(flag.value)}`),
      ...redFlags.map((flag) => `${copy.required_missing}: ${flag.value}`),
    ],
    flags: flags.map((flag) => ({ ...flag, label: copy[flag.type] || flag.type })),
    meta: { ...META[styleKey], label: copy[raw?.label] || copy.weak },
    breakdown,
  }
}
