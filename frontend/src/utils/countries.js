import { useUiStore } from '@/stores/ui'

const makeCity = (value, ru, aliases = []) => ({
  value,
  ru,
  aliases: [value, ru, ...aliases],
})

export const countryMeta = [
  {
    key: 'germany',
    label: 'Германия',
    canonicalLabel: 'Germany',
    flagCode: 'de',
    aliases: ['germany', 'deutschland', 'германия'],
    cities: [
      makeCity('Berlin', 'Берлин'),
      makeCity('Hamburg', 'Гамбург'),
      makeCity('Munich', 'Мюнхен', ['Muenchen']),
      makeCity('Cologne', 'Кёльн', ['Koln', 'Koeln']),
      makeCity('Frankfurt', 'Франкфурт-на-Майне'),
      makeCity('Stuttgart', 'Штутгарт'),
      makeCity('Dusseldorf', 'Дюссельдорф', ['Duesseldorf']),
      makeCity('Leipzig', 'Лейпциг'),
      makeCity('Dortmund', 'Дортмунд'),
      makeCity('Bremen', 'Бремен'),
      makeCity('Hanover', 'Ганновер', ['Hannover']),
      makeCity('Nuremberg', 'Нюрнберг', ['Nuernberg']),
    ],
  },
  {
    key: 'finland',
    label: 'Финляндия',
    canonicalLabel: 'Finland',
    flagCode: 'fi',
    aliases: ['finland', 'suomi', 'финляндия'],
    cities: [
      makeCity('Helsinki', 'Хельсинки'),
      makeCity('Espoo', 'Эспоо'),
      makeCity('Tampere', 'Тампере'),
      makeCity('Vantaa', 'Вантаа'),
      makeCity('Turku', 'Турку'),
      makeCity('Oulu', 'Оулу'),
      makeCity('Lahti', 'Лахти'),
      makeCity('Kuopio', 'Куопио'),
      makeCity('Jyvaskyla', 'Ювяскюля', ['Jyvaeskyla']),
      makeCity('Pori', 'Пори'),
      makeCity('Vaasa', 'Вааса'),
      makeCity('Joensuu', 'Йоэнсуу'),
    ],
  },
  {
    key: 'czechia',
    label: 'Чехия',
    canonicalLabel: 'Czechia',
    flagCode: 'cz',
    aliases: ['czechia', 'czech republic', 'cesko', 'česko', 'чехия'],
    cities: [
      makeCity('Prague', 'Прага', ['Praha']),
      makeCity('Brno', 'Брно'),
      makeCity('Ostrava', 'Острава'),
      makeCity('Pilsen', 'Пльзень', ['Plzen']),
      makeCity('Liberec', 'Либерец'),
      makeCity('Olomouc', 'Оломоуц'),
      makeCity('Ceske Budejovice', 'Ческе-Будеёвице', ['České Budějovice']),
      makeCity('Hradec Kralove', 'Градец-Кралове', ['Hradec Králové']),
      makeCity('Pardubice', 'Пардубице'),
      makeCity('Zlin', 'Злин'),
      makeCity('Jihlava', 'Йиглава'),
      makeCity('Karlovy Vary', 'Карловы Вары'),
    ],
  },
  {
    key: 'netherlands',
    label: 'Нидерланды',
    canonicalLabel: 'Netherlands',
    flagCode: 'nl',
    aliases: ['netherlands', 'nederland', 'holland', 'нидерланды'],
    cities: [
      makeCity('Amsterdam', 'Амстердам'),
      makeCity('Rotterdam', 'Роттердам'),
      makeCity('The Hague', 'Гаага', ['Den Haag']),
      makeCity('Utrecht', 'Утрехт'),
      makeCity('Eindhoven', 'Эйндховен'),
      makeCity('Tilburg', 'Тилбург'),
      makeCity('Groningen', 'Гронинген'),
      makeCity('Almere', 'Алмере'),
      makeCity('Breda', 'Бреда'),
      makeCity('Nijmegen', 'Неймеген'),
      makeCity('Enschede', 'Энсхеде'),
      makeCity('Haarlem', 'Харлем'),
    ],
  },
  {
    key: 'poland',
    label: 'Польша',
    canonicalLabel: 'Poland',
    flagCode: 'pl',
    aliases: ['poland', 'polska', 'польша'],
    cities: [
      makeCity('Warsaw', 'Варшава'),
      makeCity('Krakow', 'Краков', ['Cracow']),
      makeCity('Lodz', 'Лодзь', ['Łódź']),
      makeCity('Wroclaw', 'Вроцлав', ['Wrocław']),
      makeCity('Poznan', 'Познань', ['Poznań']),
      makeCity('Gdansk', 'Гданьск', ['Gdańsk']),
      makeCity('Szczecin', 'Щецин'),
      makeCity('Bydgoszcz', 'Быдгощ'),
      makeCity('Lublin', 'Люблин'),
      makeCity('Katowice', 'Катовице'),
      makeCity('Bialystok', 'Белосток', ['Białystok']),
      makeCity('Gdynia', 'Гдыня'),
    ],
  },
  {
    key: 'belgium',
    label: 'Бельгия',
    canonicalLabel: 'Belgium',
    flagCode: 'be',
    aliases: ['belgium', 'belgie', 'belgique', 'бельгия'],
    cities: [
      makeCity('Brussels', 'Брюссель'),
      makeCity('Antwerp', 'Антверпен'),
      makeCity('Ghent', 'Гент'),
      makeCity('Liege', 'Льеж', ['Liège']),
      makeCity('Bruges', 'Брюгге', ['Brugge']),
      makeCity('Charleroi', 'Шарлеруа'),
      makeCity('Namur', 'Намюр'),
      makeCity('Leuven', 'Лёвен'),
      makeCity('Mons', 'Монс'),
      makeCity('Aalst', 'Алст'),
      makeCity('Mechelen', 'Мехелен'),
      makeCity('Kortrijk', 'Кортрейк'),
    ],
  },
  {
    key: 'france',
    label: 'Франция',
    canonicalLabel: 'France',
    flagCode: 'fr',
    aliases: ['france', 'francia', 'frankrijk', 'франция'],
    cities: [
      makeCity('Paris', 'Париж'),
      makeCity('Marseille', 'Марсель'),
      makeCity('Lyon', 'Лион'),
      makeCity('Toulouse', 'Тулуза'),
      makeCity('Nice', 'Ницца'),
      makeCity('Nantes', 'Нант'),
      makeCity('Strasbourg', 'Страсбург'),
      makeCity('Montpellier', 'Монпелье'),
      makeCity('Bordeaux', 'Бордо'),
      makeCity('Lille', 'Лилль'),
      makeCity('Rennes', 'Ренн'),
      makeCity('Grenoble', 'Гренобль'),
    ],
  },
  {
    key: 'latvia',
    label: 'Латвия',
    canonicalLabel: 'Latvia',
    flagCode: 'lv',
    aliases: ['latvia', 'latvija', 'латвия'],
    cities: [
      makeCity('Riga', 'Рига'),
      makeCity('Daugavpils', 'Даугавпилс'),
      makeCity('Liepaja', 'Лиепая', ['Liepāja']),
      makeCity('Jelgava', 'Елгава'),
      makeCity('Jurmala', 'Юрмала', ['Jūrmala']),
      makeCity('Ventspils', 'Вентспилс'),
      makeCity('Rezekne', 'Резекне', ['Rēzekne']),
      makeCity('Valmiera', 'Валмиера'),
      makeCity('Ogre', 'Огре'),
      makeCity('Cesis', 'Цесис', ['Cēsis']),
      makeCity('Tukums', 'Тукумс'),
      makeCity('Salaspils', 'Саласпилс'),
    ],
  },
  {
    key: 'estonia',
    label: 'Эстония',
    canonicalLabel: 'Estonia',
    flagCode: 'ee',
    aliases: ['estonia', 'eesti', 'эстония'],
    cities: [
      makeCity('Tallinn', 'Таллин'),
      makeCity('Tartu', 'Тарту'),
      makeCity('Narva', 'Нарва'),
      makeCity('Parnu', 'Пярну', ['Pärnu']),
      makeCity('Kohtla-Jarve', 'Кохтла-Ярве', ['Kohtla-Järve']),
      makeCity('Viljandi', 'Вильянди'),
      makeCity('Rakvere', 'Раквере'),
      makeCity('Maardu', 'Маарду'),
      makeCity('Kuressaare', 'Курессааре'),
      makeCity('Sillamae', 'Силламяэ', ['Sillamäe']),
      makeCity('Haapsalu', 'Хаапсалу'),
      makeCity('Paide', 'Пайде'),
    ],
  },
]

export const salaryCurrencyOptions = [
  { value: 'EUR', label: 'EUR' },
  { value: 'USD', label: 'USD' },
  { value: 'PLN', label: 'PLN' },
  { value: 'CZK', label: 'CZK' },
]

const getLanguage = () => {
  try {
    return useUiStore().language === 'en' ? 'en' : 'ru'
  } catch {
    return 'ru'
  }
}

export const normalizeText = (value = '') => String(value || '')
  .normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLowerCase()
  .replace(/[^\p{L}\p{N}]+/gu, ' ')
  .trim()

const looksLikeMojibake = (value = '') => /[ÃÐÑ]/.test(String(value || ''))
const normalizeCountryKey = (value = '') => normalizeText(value).replace(/\s+/g, '')

const countryAliases = Object.fromEntries(
  countryMeta.flatMap((country) => country.aliases.map((alias) => [normalizeText(alias), country.key])),
)

const cityLookup = countryMeta.flatMap((country) => country.cities.map((city) => ({
  ...city,
  countryKey: country.key,
})))

export const countryDropdownOptions = countryMeta.map((country) => ({
  value: country.key,
  label: country.label,
  iconClass: `fi fi-${country.flagCode}`,
}))

export const countryByKey = Object.fromEntries(countryMeta.map((country) => [country.key, country]))

export const citiesByCountry = Object.fromEntries(
  countryMeta.map((country) => [country.key, country.cities.map((city) => city.value)]),
)

export const getLocalizedCountryLabel = (countryKey = '', fallback = '') => {
  const country = countryByKey[countryKey]
  if (!country) return fallback
  return getLanguage() === 'en' ? country.canonicalLabel : country.label
}

export const getCityOptions = (countryKey = '') => {
  const country = countryByKey[countryKey]
  if (!country) return []

  const isEnglish = getLanguage() === 'en'
  return country.cities.map((city) => ({
    value: city.value,
    label: isEnglish ? city.value : city.ru,
  }))
}

export const getLocalizedCityName = (value = '', countryKey = '') => {
  const normalizedValue = normalizeText(value)
  if (!normalizedValue) return ''

  const cities = countryKey
    ? (countryByKey[countryKey]?.cities || [])
    : cityLookup

  const city = cities.find((item) => item.aliases.some((alias) => normalizeText(alias) === normalizedValue))
    || cityLookup.find((item) => item.aliases.some((alias) => normalizeText(alias) === normalizedValue))

  if (!city) return String(value || '').trim()
  return getLanguage() === 'en' ? city.value : city.ru
}

export const getCountrySearchValues = (countryKey = '') => {
  const country = countryByKey[countryKey]
  if (!country) return []

  return [
    country.key,
    country.label,
    country.canonicalLabel,
    ...country.aliases,
  ].filter(Boolean)
}

export const getCitySearchValues = (value = '', countryKey = '') => {
  const normalizedValue = normalizeText(value)
  if (!normalizedValue) return []

  const cities = countryKey
    ? (countryByKey[countryKey]?.cities || [])
    : cityLookup

  const city = cities.find((item) => item.aliases.some((alias) => normalizeText(alias) === normalizedValue))
    || cityLookup.find((item) => item.aliases.some((alias) => normalizeText(alias) === normalizedValue))

  if (!city) return [String(value || '').trim()].filter(Boolean)

  return [city.value, city.ru, ...city.aliases].filter(Boolean)
}

export const getJobLocationSearchValues = (job = {}) => {
  const { countryKey, countryLabel } = resolveCountryMeta(job)
  const rawLocation = String(job.location || '').trim()
  const localizedLocation = getLocalizedCityName(rawLocation, countryKey)
  const countrySearchValues = getCountrySearchValues(countryKey)
  const citySearchValues = getCitySearchValues(rawLocation, countryKey)

  return [
    rawLocation,
    localizedLocation,
    countryLabel,
    formatJobLocation({
      ...job,
      country_key: countryKey,
      country_label: countryLabel,
    }),
    ...countrySearchValues,
    ...citySearchValues,
  ].filter(Boolean)
}

export const inferCountryFromLabel = (value = '') => {
  const normalized = normalizeText(value)
  return countryAliases[normalized] || ''
}

export const inferCountryFromLocation = (location = '') => {
  const normalizedLocation = normalizeText(location)
  if (!normalizedLocation) return ''

  const matchedCountry = countryMeta.find((country) => (
    country.aliases.some((alias) => normalizedLocation.includes(normalizeText(alias)))
      || country.cities.some((city) => city.aliases.some((alias) => normalizedLocation.includes(normalizeText(alias))))
  ))

  return matchedCountry?.key || ''
}

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
    countryLabel: getLocalizedCountryLabel(country?.key || detectedCountryKey || '', safeLabel || ''),
    countryFlagCode: country?.flagCode || rawFlagCode || '',
  }
}

export const formatJobLocation = (job = {}) => {
  const { countryKey, countryLabel } = resolveCountryMeta(job)
  const location = getLocalizedCityName(job.location, countryKey)

  if (countryLabel && location) return `${countryLabel}, ${location}`
  return countryLabel || location || 'Локация не указана'
}
