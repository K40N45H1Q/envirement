<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  suggestions: {
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
  disabled: {
    type: Boolean,
    default: false,
  },
  required: {
    type: Boolean,
    default: false,
  },
  iconClass: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'select', 'focus', 'blur'])

const root = ref(null)
const inputRef = ref(null)
const menuRef = ref(null)
const isOpen = ref(false)
const highlightedIndex = ref(-1)
const menuStyle = ref({})

const normalizedSuggestions = computed(() => props.suggestions.map((item) => (
  typeof item === 'string'
    ? { value: item, label: item }
    : {
      id: String(item?.id ?? item?.value ?? item?.label ?? ''),
      value: String(item?.value ?? item?.label ?? ''),
      label: String(item?.label ?? item?.value ?? ''),
    }
)))

const hasSuggestions = computed(() => normalizedSuggestions.value.length > 0)

const close = () => {
  isOpen.value = false
  highlightedIndex.value = -1
}

const updateMenuPosition = () => {
  if (!isOpen.value || !root.value) return

  const rect = root.value.getBoundingClientRect()
  const viewportPadding = 8
  const gap = 8
  const width = Math.min(rect.width, window.innerWidth - (viewportPadding * 2))
  const desiredHeight = Math.min(menuRef.value?.scrollHeight || 240, 240)
  const spaceBelow = window.innerHeight - rect.bottom - viewportPadding - gap
  const spaceAbove = rect.top - viewportPadding - gap
  const openAbove = spaceBelow < desiredHeight && spaceAbove > spaceBelow
  const availableHeight = Math.max(120, openAbove ? spaceAbove : spaceBelow)
  const top = openAbove
    ? Math.max(viewportPadding, rect.top - Math.min(desiredHeight, availableHeight) - gap)
    : rect.bottom + gap
  const left = Math.min(
    Math.max(viewportPadding, rect.left),
    window.innerWidth - width - viewportPadding,
  )

  menuStyle.value = {
    position: 'fixed',
    top: `${top}px`,
    left: `${left}px`,
    width: `${width}px`,
    minWidth: `${width}px`,
    maxWidth: `${width}px`,
    maxHeight: `${availableHeight}px`,
    zIndex: 4100,
  }
}

const open = async () => {
  if (props.disabled || !hasSuggestions.value) return
  isOpen.value = true
  highlightedIndex.value = 0
  await nextTick()
  updateMenuPosition()
}

const selectSuggestion = (option) => {
  emit('update:modelValue', option.value)
  emit('select', option)
  close()
}

const onInput = async (event) => {
  emit('update:modelValue', event.target.value)

  await nextTick()

  if (props.disabled || !event.target.value.trim() || !hasSuggestions.value) {
    close()
    return
  }

  await open()
}

const onFocus = async () => {
  emit('focus')

  if (!props.modelValue.trim() || !hasSuggestions.value) return
  await open()
}

const onBlur = () => {
  emit('blur')
  window.setTimeout(close, 120)
}

const moveHighlight = (direction) => {
  if (!hasSuggestions.value) return
  if (!isOpen.value) {
    void open()
    return
  }

  const nextIndex = highlightedIndex.value + direction
  if (nextIndex < 0) {
    highlightedIndex.value = normalizedSuggestions.value.length - 1
    return
  }

  if (nextIndex >= normalizedSuggestions.value.length) {
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

  if (event.key === 'Enter' && isOpen.value) {
    const option = normalizedSuggestions.value[highlightedIndex.value]
    if (!option) return
    event.preventDefault()
    selectSuggestion(option)
  }
}

const handleOutsideClick = (event) => {
  if (!root.value?.contains(event.target) && !menuRef.value?.contains(event.target)) {
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

watch(() => props.suggestions, () => {
  if (!props.modelValue.trim() || !hasSuggestions.value) {
    close()
    return
  }

  if (isOpen.value) {
    void nextTick().then(updateMenuPosition)
  }
})
</script>

<template>
  <div ref="root" class="autocomplete">
    <div class="autocomplete__input-wrap">
      <input
        ref="inputRef"
        :value="modelValue"
        type="text"
        :placeholder="placeholder"
        :aria-label="ariaLabel"
        :disabled="disabled"
        :required="required"
        autocomplete="off"
        @input="onInput"
        @focus="onFocus"
        @blur="onBlur"
        @keydown="onKeydown"
      />
      <i v-if="iconClass" :class="iconClass"></i>
    </div>

    <Teleport to="body">
      <div
        v-if="isOpen && hasSuggestions"
        ref="menuRef"
        class="autocomplete__menu"
        :style="menuStyle"
      >
        <button
          v-for="(option, index) in normalizedSuggestions"
          :key="`${option.value}-${index}`"
          type="button"
          class="autocomplete__option"
          :class="{ 'autocomplete__option--active': index === highlightedIndex }"
          @mousedown.prevent="selectSuggestion(option)"
          @mouseenter="highlightedIndex = index"
        >
          {{ option.label }}
        </button>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.autocomplete {
  width: 100%;
}

.autocomplete__input-wrap {
  position: relative;
}

.autocomplete__input-wrap input {
  width: 100%;
}

.autocomplete__input-wrap i,
.autocomplete__input-wrap :deep(svg.svg-inline--fa) {
  position: absolute;
  top: 50%;
  right: 1rem;
  transform: translateY(-50%);
  pointer-events: none;
  color: var(--brand-strong);
  width: 1rem;
  height: 1rem;
}

.autocomplete__input-wrap:has(i) input,
.autocomplete__input-wrap:has(svg) input {
  padding-right: 2.8rem;
}

.autocomplete__menu {
  overflow-y: auto;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 26%, #d6e6dc);
  border-radius: 1rem;
  background: #fff;
  box-shadow: 0 1.1rem 2.4rem rgba(16, 24, 20, 0.14);
  max-height: 15rem;
}

.autocomplete__option {
  width: 100%;
  display: flex;
  align-items: center;
  min-height: 2.65rem;
  padding: 0.62rem 0.85rem;
  border: 0;
  border-bottom: 0.0625rem solid #ecf3ee;
  background: transparent;
  color: var(--text-primary);
  font: inherit;
  font-weight: 700;
  font-size: 0.95rem;
  text-align: left;
  cursor: pointer;
}

.autocomplete__option:last-child {
  border-bottom: 0;
}

.autocomplete__option--active {
  background: color-mix(in srgb, var(--brand-base) 10%, #fff);
  color: var(--brand-strong);
}
</style>
