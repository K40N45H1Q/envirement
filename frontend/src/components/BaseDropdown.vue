<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from '@/i18n'

const { t } = useI18n()

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean],
    default: '',
  },
  options: {
    type: Array,
    default: () => [],
  },
  placeholder: {
    type: String,
    default: '',
  },
  ariaLabel: {
    type: String,
    default: '',
  },
  iconClass: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  fullWidth: {
    type: Boolean,
    default: false,
  },
  size: {
    type: String,
    default: 'md',
  },
  variant: {
    type: String,
    default: 'surface',
  },
  align: {
    type: String,
    default: 'left',
  },
  showSelectedHint: {
    type: Boolean,
    default: true,
  },
  overlay: {
    type: Boolean,
    default: false,
  },
  menuClass: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'change', 'open', 'close'])

const root = ref(null)
const menu = ref(null)
const isOpen = ref(false)
const highlightedIndex = ref(-1)
const menuStyle = ref({})

const normalizedOptions = computed(() => props.options.map((option) => {
  if (typeof option === 'object' && option !== null) {
    return {
      label: option.label ?? String(option.value ?? ''),
      value: option.value,
      hint: option.hint ?? '',
      iconClass: option.iconClass ?? '',
    }
  }

  return {
    label: String(option),
    value: option,
    hint: '',
    iconClass: '',
  }
}))

const selectedOption = computed(() => (
  normalizedOptions.value.find((option) => option.value === props.modelValue) || null
))

const resolvedPlaceholder = computed(() => props.placeholder || t('common.choose'))
const resolvedAriaLabel = computed(() => props.ariaLabel || t('common.selectionList'))
const buttonLabel = computed(() => selectedOption.value?.label || resolvedPlaceholder.value)
const leadIconClass = computed(() => selectedOption.value?.iconClass || props.iconClass)

const close = () => {
  if (!isOpen.value) return
  isOpen.value = false
  highlightedIndex.value = normalizedOptions.value.findIndex((option) => option.value === props.modelValue)
  emit('close')
}

const open = () => {
  if (props.disabled || isOpen.value) return
  isOpen.value = true
  highlightedIndex.value = Math.max(
    normalizedOptions.value.findIndex((option) => option.value === props.modelValue),
    0,
  )
  emit('open')
}

const updateMenuPosition = () => {
  if (!props.overlay || !isOpen.value || !root.value) return

  const rect = root.value.getBoundingClientRect()
  const width = rect.width
  const top = rect.bottom + 8
  const left = props.align === 'right' ? rect.right - width : rect.left

  menuStyle.value = {
    position: 'fixed',
    top: `${top}px`,
    left: `${Math.max(8, left)}px`,
    width: `${width}px`,
    minWidth: `${width}px`,
    maxWidth: `${width}px`,
    zIndex: 4000,
  }
}

const toggle = () => {
  if (isOpen.value) {
    close()
    return
  }

  open()
}

const selectOption = (option) => {
  emit('update:modelValue', option.value)
  emit('change', option)
  close()
}

const moveHighlight = (direction) => {
  if (!normalizedOptions.value.length) return

  if (!isOpen.value) {
    open()
    return
  }

  const nextIndex = highlightedIndex.value + direction
  if (nextIndex < 0) {
    highlightedIndex.value = normalizedOptions.value.length - 1
    return
  }

  if (nextIndex >= normalizedOptions.value.length) {
    highlightedIndex.value = 0
    return
  }

  highlightedIndex.value = nextIndex
}

const onKeydown = (event) => {
  if (props.disabled) return

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    moveHighlight(1)
    return
  }

  if (event.key === 'ArrowUp') {
    event.preventDefault()
    moveHighlight(-1)
    return
  }

  if (event.key === 'Escape') {
    event.preventDefault()
    close()
    return
  }

  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()

    if (!isOpen.value) {
      open()
      return
    }

    const option = normalizedOptions.value[highlightedIndex.value]
    if (option) {
      selectOption(option)
    }
  }
}

const handleOutsideClick = (event) => {
  if (!root.value?.contains(event.target) && !menu.value?.contains(event.target)) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  window.addEventListener('resize', updateMenuPosition)
  window.addEventListener('scroll', updateMenuPosition, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
  window.removeEventListener('resize', updateMenuPosition)
  window.removeEventListener('scroll', updateMenuPosition, true)
})

watch(isOpen, async (value) => {
  if (!value) return
  await nextTick()
  updateMenuPosition()
})
</script>

<template>
  <div
    ref="root"
    class="dropdown"
    :class="[
      `dropdown--${size}`,
      `dropdown--${variant}`,
      `dropdown--${align}`,
      {
        'dropdown--open': isOpen,
        'dropdown--full': fullWidth,
        'dropdown--disabled': disabled,
      },
    ]"
  >
    <button
      type="button"
      class="dropdown__trigger"
      :aria-expanded="isOpen"
      :aria-label="resolvedAriaLabel"
      :disabled="disabled"
      @click="toggle"
      @keydown="onKeydown"
    >
      <span v-if="leadIconClass" class="dropdown__lead">
        <i :class="leadIconClass"></i>
      </span>

      <span class="dropdown__content">
        <span class="dropdown__label">{{ buttonLabel }}</span>
        <span v-if="showSelectedHint && selectedOption?.hint" class="dropdown__hint">{{ selectedOption.hint }}</span>
      </span>

      <span class="dropdown__chevron">
        <i class="fas fa-chevron-down"></i>
      </span>
    </button>

    <Teleport to="body" :disabled="!overlay">
      <transition name="dropdown-fade">
        <div
          v-if="isOpen"
          ref="menu"
          class="dropdown__menu"
          :class="menuClass"
          :style="overlay ? menuStyle : undefined"
          role="listbox"
          @mouseleave="highlightedIndex = -1"
        >
          <button
            v-for="(option, index) in normalizedOptions"
            :key="`${option.value}-${index}`"
            type="button"
            class="dropdown__option"
            :class="{
              'dropdown__option--selected': option.value === modelValue,
              'dropdown__option--highlighted': index === highlightedIndex,
            }"
            @click="selectOption(option)"
            @mouseenter="highlightedIndex = index"
          >
            <span v-if="option.iconClass" class="dropdown__option-icon">
              <i :class="option.iconClass"></i>
            </span>

            <span class="dropdown__option-copy">
              <span class="dropdown__option-label">{{ option.label }}</span>
              <span v-if="option.hint" class="dropdown__option-hint">{{ option.hint }}</span>
            </span>

            <span v-if="option.value === modelValue" class="dropdown__option-check">
              <i class="fas fa-check"></i>
            </span>
          </button>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<style scoped>
.dropdown {
  position: relative;
  min-width: 0;
}

.dropdown--full {
  width: 100%;
}

.dropdown__trigger {
  box-sizing: border-box;
  width: 100%;
  min-height: 3.3rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.74rem 0.95rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(247, 251, 248, 0.95)),
    var(--surface-secondary);
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.dropdown__trigger:hover,
.dropdown--open .dropdown__trigger {
  border-color: color-mix(in srgb, var(--brand-base) 28%, var(--border-subtle));
  box-shadow: 0 0.625rem 1.4rem rgba(16, 24, 40, 0.08);
}

.dropdown__trigger:focus-visible {
  outline: none;
  border-color: var(--brand-strong);
  box-shadow: 0 0 0 0.1875rem rgba(20, 184, 87, 0.14);
}

.dropdown--disabled .dropdown__trigger {
  opacity: 0.65;
  cursor: not-allowed;
  box-shadow: none;
}

.dropdown__lead,
.dropdown__chevron,
.dropdown__option-icon,
.dropdown__option-check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}

.dropdown__lead,
.dropdown__chevron {
  color: var(--brand-strong);
}

.dropdown__content,
.dropdown__option-copy {
  min-width: 0;
  display: grid;
}

.dropdown__content {
  flex: 1;
}

.dropdown__label,
.dropdown__option-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
}

.dropdown__hint,
.dropdown__option-hint {
  color: var(--text-muted);
  font-size: 0.82rem;
  line-height: 1.35;
}

.dropdown__chevron {
  transition: transform 0.2s ease;
}

.dropdown--open .dropdown__chevron {
  transform: rotate(180deg);
}

.dropdown__menu {
  box-sizing: border-box;
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  z-index: 30;
  min-width: 100%;
  max-height: 18rem;
  overflow-y: auto;
  padding: 0.5rem;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 16%, var(--border-subtle));
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.97);
  box-shadow: 0 1rem 2rem rgba(16, 24, 40, 0.12);
  backdrop-filter: blur(1rem);
}

.dropdown--right .dropdown__menu {
  right: 0;
  left: auto;
}

.dropdown__option {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.8rem 0.85rem;
  border: none;
  border-radius: 0.8rem;
  background: transparent;
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease;
}

.dropdown__option:hover,
.dropdown__option--highlighted {
  background: color-mix(in srgb, var(--brand-soft) 58%, white);
}

.dropdown__option--selected {
  background: color-mix(in srgb, var(--brand-soft) 72%, white);
}

.dropdown__option-icon,
.dropdown__option-check {
  color: var(--brand-strong);
}

.dropdown--sm .dropdown__trigger {
  min-height: 3rem;
  padding: 0.62rem 0.9rem;
  border-radius: 999rem;
}

.dropdown--ghost .dropdown__trigger {
  border-color: transparent;
  background: transparent;
  box-shadow: none;
}

.dropdown--ghost.dropdown--open .dropdown__trigger,
.dropdown--ghost .dropdown__trigger:hover {
  background: color-mix(in srgb, var(--brand-soft) 48%, white);
  border-color: color-mix(in srgb, var(--brand-base) 18%, transparent);
}

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-0.25rem);
}
</style>
