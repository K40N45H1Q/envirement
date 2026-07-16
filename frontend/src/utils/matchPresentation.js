const WEIGHTS = {
  experience: 30,
  languages: 20,
  availability: 20,
  credentials: 20,
  skills: 10,
}

const COPY = {
  ru: {
    excellent: 'Отличное совпадение', good: 'Хорошее совпадение', partial: 'Частичное совпадение', weak: 'Слабое совпадение',
    experience: 'Опыт', languages: 'Языки', availability: 'Доступность', credentials: 'Права и лицензии', skills: 'Навыки', stability_penalty: 'Стабильность',
    required_missing: 'Обязательное требование', stability: 'Частая смена работы', exceeds_requirement: 'Выше требования', serverMatch: 'Серверный расчёт',
  },
  en: {
    excellent: 'Excellent match', good: 'Good match', partial: 'Partial match', weak: 'Weak match',
    experience: 'Experience', languages: 'Languages', availability: 'Availability', credentials: 'Licences and certificates', skills: 'Skills', stability_penalty: 'Stability',
    required_missing: 'Mandatory requirement', stability: 'Frequent job changes', exceeds_requirement: 'Exceeds requirement', serverMatch: 'Server-calculated match',
  },
  lv: {
    excellent: 'Izcila atbilstība', good: 'Laba atbilstība', partial: 'Daļēja atbilstība', weak: 'Vāja atbilstība',
    experience: 'Pieredze', languages: 'Valodas', availability: 'Pieejamība', credentials: 'Tiesības un licences', skills: 'Prasmes', stability_penalty: 'Stabilitāte',
    required_missing: 'Obligāta prasība', stability: 'Bieža darba maiņa', exceeds_requirement: 'Pārsniedz prasību', serverMatch: 'Servera aprēķins',
  },
}

const META = {
  strong: { key: 'strong', textColor: '#19785a', badgeBackground: '#e6f0ec' },
  good: { key: 'good', textColor: 'rgba(22, 155, 97, 0.92)', badgeBackground: 'rgba(29, 168, 107, 0.12)' },
  partial: { key: 'partial', textColor: '#d68a12', badgeBackground: '#fef3e2' },
  weak: { key: 'weak', textColor: '#6b7280', badgeBackground: '#f3f4f6' },
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
  const score = Number(raw?.score || 0)
  const styleKey = styleKeyForScore(score)
  const flags = Array.isArray(raw?.flags) ? raw.flags : []
  const redFlags = flags.filter((flag) => flag.type === 'required_missing')
  const hasStabilityFlag = flags.some((flag) => flag.type === 'stability')
  const breakdown = Object.entries(raw?.breakdown || {}).map(([key, detail]) => {
    const points = Number(detail?.points || 0)
    const max = WEIGHTS[key] || 0
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
    label: raw?.label || 'weak',
    algorithmVersion: raw?.algorithm_version || '',
    profile: copy.serverMatch,
    trafficLight: redFlags.length ? 'red' : hasStabilityFlag ? 'yellow' : score >= 70 ? 'green' : score >= 50 ? 'yellow' : 'red',
    failedGates: redFlags.map((flag) => `${copy.required_missing}: ${flag.value}`),
    flags: flags.map((flag) => ({ ...flag, label: copy[flag.type] || flag.type })),
    meta: { ...META[styleKey], label: copy[raw?.label] || copy.weak },
    breakdown,
  }
}
