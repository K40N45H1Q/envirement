<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  ariaLabel: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const countries = [
  { iso: 'lv', dial: '+371' },
  { iso: 'lt', dial: '+370' },
  { iso: 'ee', dial: '+372' },
  { iso: 'pl', dial: '+48' },
  { iso: 'de', dial: '+49' },
  { iso: 'fi', dial: '+358' },
  { iso: 'se', dial: '+46' },
  { iso: 'no', dial: '+47' },
  { iso: 'dk', dial: '+45' },
  { iso: 'nl', dial: '+31' },
  { iso: 'be', dial: '+32' },
  { iso: 'fr', dial: '+33' },
  { iso: 'gb', dial: '+44' },
  { iso: 'ie', dial: '+353' },
  { iso: 'es', dial: '+34' },
  { iso: 'pt', dial: '+351' },
  { iso: 'it', dial: '+39' },
  { iso: 'at', dial: '+43' },
  { iso: 'ch', dial: '+41' },
  { iso: 'cz', dial: '+420' },
  { iso: 'sk', dial: '+421' },
  { iso: 'ua', dial: '+380' },
  { iso: 'ro', dial: '+40' },
  { iso: 'bg', dial: '+359' },
  { iso: 'hu', dial: '+36' },
  { iso: 'hr', dial: '+385' },
  { iso: 'si', dial: '+386' },
  { iso: 'gr', dial: '+30' },
  { iso: 'cy', dial: '+357' },
  { iso: 'mt', dial: '+356' },
  { iso: 'lu', dial: '+352' },
  { iso: 'us', dial: '+1' },
]

const root = ref(null)
const isOpen = ref(false)
const selectedIso = ref('lv')
const nationalNumber = ref('')

const selectedCountry = computed(() => (
  countries.find((country) => country.iso === selectedIso.value) || countries[0]
))

const findCountryByPhone = (value) => {
  const compact = String(value || '').replace(/[\s()-]/g, '')
  if (!compact.startsWith('+')) return null

  return [...countries]
    .sort((left, right) => right.dial.length - left.dial.length)
    .find((country) => compact.startsWith(country.dial)) || null
}

const syncFromModel = (value) => {
  const raw = String(value || '').trim()
  const country = findCountryByPhone(raw)

  if (country) {
    selectedIso.value = country.iso
    const dialIndex = raw.replace(/^[\s(]*/, '').indexOf(country.dial)
    nationalNumber.value = raw
      .slice(Math.max(0, dialIndex) + country.dial.length)
      .replace(/^\s+/, '')
    return
  }

  nationalNumber.value = raw
}

const emitPhone = () => {
  const localNumber = nationalNumber.value.trim()
  emit('update:modelValue', localNumber ? `${selectedCountry.value.dial} ${localNumber}` : '')
}

const handleInput = (event) => {
  const value = event.target.value
  const pastedCountry = findCountryByPhone(value)

  if (pastedCountry) {
    selectedIso.value = pastedCountry.iso
    nationalNumber.value = value
      .replace(/^[\s(]*/, '')
      .slice(pastedCountry.dial.length)
      .replace(/^\s+/, '')
  } else {
    nationalNumber.value = value
  }

  emitPhone()
}

const selectCountry = (country) => {
  selectedIso.value = country.iso
  isOpen.value = false
  emitPhone()
}

const handleOutsideClick = (event) => {
  if (!root.value?.contains(event.target)) isOpen.value = false
}

watch(() => props.modelValue, syncFromModel, { immediate: true })

onMounted(() => document.addEventListener('click', handleOutsideClick))
onBeforeUnmount(() => document.removeEventListener('click', handleOutsideClick))
</script>

<template>
  <div ref="root" class="phone-input" :class="{ 'phone-input--open': isOpen }">
    <button
      type="button"
      class="phone-input__country"
      :aria-expanded="isOpen"
      :aria-label="ariaLabel"
      @click="isOpen = !isOpen"
    >
      <span class="phone-input__flag fi" :class="`fi-${selectedCountry.iso}`"></span>
      <span class="phone-input__dial">{{ selectedCountry.dial }}</span>
      <i class="fas fa-chevron-down phone-input__chevron"></i>
    </button>

    <input
      :value="nationalNumber"
      type="tel"
      inputmode="tel"
      autocomplete="tel"
      class="phone-input__field"
      :placeholder="placeholder"
      :aria-label="ariaLabel"
      :required="required"
      @input="handleInput"
    />

    <div v-if="isOpen" class="phone-input__menu">
      <button
        v-for="country in countries"
        :key="country.iso"
        type="button"
        class="phone-input__option"
        :class="{ 'phone-input__option--selected': country.iso === selectedIso }"
        @click="selectCountry(country)"
      >
        <span class="phone-input__flag fi" :class="`fi-${country.iso}`"></span>
        <span>{{ country.iso.toUpperCase() }}</span>
        <strong>{{ country.dial }}</strong>
      </button>
    </div>
  </div>
</template>

<style scoped>
.phone-input {
  position: relative;
  width: 100%;
  min-height: 3.2rem;
  display: flex;
  align-items: stretch;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background: var(--surface-secondary, #fff);
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.phone-input:focus-within,
.phone-input--open {
  border-color: var(--brand-strong);
  box-shadow: 0 0 0 0.1875rem rgba(20, 184, 87, 0.12);
}

.phone-input__country {
  min-width: 7.2rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.7rem 0.75rem;
  border: none;
  border-right: 0.0625rem solid var(--border-subtle);
  border-radius: 0.9rem 0 0 0.9rem;
  background: color-mix(in srgb, var(--brand-soft) 28%, white);
  color: var(--text-primary);
  font: inherit;
  cursor: pointer;
}

.phone-input__flag {
  width: 1.3rem;
  flex: 0 0 1.3rem;
  border-radius: 0.18rem;
  box-shadow: 0 0 0 0.0625rem rgba(15, 23, 42, 0.12);
}

.phone-input__dial {
  font: inherit;
  font-weight: 700;
}

.phone-input__chevron {
  color: var(--brand-strong);
  font-size: 0.66rem;
  transition: transform 0.2s ease;
}

.phone-input--open .phone-input__chevron {
  transform: rotate(180deg);
}

.phone-input__field {
  min-width: 0;
  flex: 1;
  padding: 0.8rem 0.9rem;
  border: none;
  border-radius: 0 0.9rem 0.9rem 0;
  outline: none;
  background: transparent;
  color: var(--text-primary);
  font: inherit;
}

.phone-input__menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  z-index: 50;
  width: min(18rem, 100%);
  max-height: 16rem;
  display: grid;
  gap: 0.15rem;
  overflow-y: auto;
  padding: 0.45rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 1rem 2rem rgba(15, 23, 42, 0.14);
}

.phone-input__option {
  width: 100%;
  display: grid;
  grid-template-columns: 1.3rem 1fr auto;
  align-items: center;
  gap: 0.65rem;
  padding: 0.62rem 0.7rem;
  border: none;
  border-radius: 0.7rem;
  background: transparent;
  color: var(--text-primary);
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.phone-input__option:hover,
.phone-input__option--selected {
  background: color-mix(in srgb, var(--brand-soft) 62%, white);
}

.phone-input__option strong {
  color: var(--brand-strong);
}

@media (max-width: 24rem) {
  .phone-input__country {
    min-width: 6.6rem;
    padding-inline: 0.6rem;
  }
}
</style>
