<script setup>
import { RouterLink } from 'vue-router'
import { useI18n } from '@/i18n'

const { t } = useI18n()

defineProps({
  sections: {
    type: Array,
    default: () => [],
  },
  activeSection: {
    type: String,
    default: '',
  },
  eyebrow: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    default: '',
  },
  description: {
    type: String,
    default: '',
  },
  stats: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['select-section', 'stat-click'])
</script>

<template>
  <main class="dashboard-shell">
    <aside class="dashboard-sidebar">
      <div class="dashboard-sidebar__top">
        <p class="dashboard-sidebar__eyebrow">
          {{ t('dashboardShell.sectionsTitle') }}
        </p>
      </div>

      <component
        :is="section.to && !section.disabled ? RouterLink : 'button'"
        v-for="section in sections"
        :key="section.id"
        :to="section.disabled ? undefined : section.to"
        :type="section.to && !section.disabled ? undefined : 'button'"
        :disabled="section.disabled || undefined"
        :aria-disabled="section.disabled ? 'true' : undefined"
        class="dashboard-sidebar__item"
        :class="{
          'dashboard-sidebar__item--active': activeSection === section.id,
          'dashboard-sidebar__item--disabled': section.disabled,
          'dashboard-sidebar__item--danger': section.danger,
          'dashboard-sidebar__item--divider': section.divider,
        }"
        @click="!section.disabled && !section.to && $emit('select-section', section.id)"
      >
        <i :class="section.icon"></i>
        <span>{{ section.label }}</span>
      </component>
    </aside>

    <section class="dashboard-content">
      <section class="dashboard-head">
        <div class="dashboard-head__copy">
          <p v-if="eyebrow" class="dashboard-eyebrow">
            {{ eyebrow }}
          </p>

          <h1>{{ title }}</h1>
        </div>

        <div v-if="$slots.actions" class="dashboard-head__actions">
          <slot name="actions" />
        </div>
      </section>

      <section
        v-if="stats.length"
        class="dashboard-stats"
        :class="`dashboard-stats--${Math.min(stats.length, 4)}`"
      >
        <article
          v-for="item in stats"
          :key="item.label"
          :class="{
            'dashboard-stats__item--clickable': item.section,
          }"
          @click="item.section && $emit('stat-click', item.section)"
        >
          <strong>{{ item.value }}</strong>
          <span>{{ item.label }}</span>
        </article>
      </section>

      <slot />
    </section>
  </main>
</template>

<style scoped>
.dashboard-shell {
  width: min(100%, var(--shell-max-width));
  margin-inline: auto;
  padding: 1.5rem var(--shell-gutter) 4rem;
  display: grid;
  grid-template-columns: 15rem minmax(0, 1fr);
  gap: 1.25rem;
}

.dashboard-sidebar,
.dashboard-head,
.dashboard-stats article {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.dashboard-sidebar {
  position: sticky;
  top: 5.5rem;
  display: grid;
  align-content: start;
  gap: 0.45rem;
  padding: 1rem;
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.98),
      rgba(247, 251, 248, 0.98)
    ),
    var(--surface-primary);
}

.dashboard-sidebar__top {
  padding: 0.25rem 0.2rem 0.7rem;
}

.dashboard-sidebar__eyebrow,
.dashboard-eyebrow {
  margin: 0;
}

.dashboard-sidebar__eyebrow {
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.dashboard-sidebar__item {
  min-width: 0;
  min-height: 3rem;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 0.9rem;
  border: 0.0625rem solid transparent;
  border-radius: 0.875rem;
  background: transparent;
  color: var(--text-primary);
  font: inherit;
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition:
    background 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    transform 0.2s ease;
}

.dashboard-sidebar__item i {
  width: 1.1rem;
  flex: 0 0 1.1rem;
  color: color-mix(in srgb, var(--text-muted) 78%, transparent);
  text-align: center;
  transition: color 0.2s ease;
}

.dashboard-sidebar__item span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dashboard-sidebar__item:hover,
.dashboard-sidebar__item:focus-visible {
  background: color-mix(in srgb, var(--brand-soft) 60%, transparent);
  color: var(--brand-strong);
  transform: translateX(0.12rem);
}

.dashboard-sidebar__item:hover i,
.dashboard-sidebar__item:focus-visible i,
.dashboard-sidebar__item--active i {
  color: var(--brand-strong);
}

.dashboard-sidebar__item:focus-visible {
  outline: 0.1875rem solid
    color-mix(in srgb, var(--brand-base) 22%, transparent);
  outline-offset: 0.125rem;
}

.dashboard-sidebar__item--active {
  border-color: var(--border-strong);
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--brand-base) 22%, transparent),
    color-mix(in srgb, var(--brand-strong) 14%, transparent)
  );
  color: var(--text-primary);
  box-shadow: 0 0.75rem 1.5rem rgba(21, 149, 93, 0.08);
}

.dashboard-sidebar__item--disabled,
.dashboard-sidebar__item--disabled:hover,
.dashboard-sidebar__item--disabled:focus-visible {
  border-color: transparent;
  background: color-mix(in srgb, var(--surface-muted) 78%, transparent);
  color: var(--text-muted);
  box-shadow: none;
  cursor: not-allowed;
  opacity: 0.52;
  transform: none;
}

.dashboard-sidebar__item--disabled i,
.dashboard-sidebar__item--disabled:hover i,
.dashboard-sidebar__item--disabled:focus-visible i {
  color: var(--text-muted);
}

.dashboard-sidebar__item--divider {
  margin-top: 0.55rem;
}

.dashboard-sidebar__item--danger {
  border-color: color-mix(in srgb, var(--danger, #dc2626) 22%, transparent);
  background: color-mix(in srgb, var(--danger, #dc2626) 7%, transparent);
  color: var(--danger, #dc2626);
  font-weight: 700;
}

.dashboard-sidebar__item--danger i,
.dashboard-sidebar__item--danger:hover i,
.dashboard-sidebar__item--danger:focus-visible i {
  color: currentColor;
}

.dashboard-sidebar__item--danger:hover,
.dashboard-sidebar__item--danger:focus-visible {
  border-color: color-mix(in srgb, var(--danger, #dc2626) 45%, transparent);
  background: color-mix(in srgb, var(--danger, #dc2626) 12%, transparent);
  color: var(--danger, #dc2626);
}

.dashboard-content,
.dashboard-head__copy {
  min-width: 0;
  display: grid;
}

.dashboard-content {
  gap: 1.5rem;
  container-type: inline-size;
}

.dashboard-head {
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: clamp(1.15rem, 2vw, 1.55rem);
  background:
    radial-gradient(
      circle at top right,
      rgba(26, 177, 111, 0.12),
      transparent 28%
    ),
    radial-gradient(
      circle at left bottom,
      rgba(15, 118, 110, 0.05),
      transparent 24%
    ),
    var(--surface-primary);
}

.dashboard-head__copy {
  gap: 0.55rem;
}

.dashboard-head__actions {
  flex: 0 0 auto;
}

.dashboard-eyebrow {
  color: var(--brand-strong);
  font-weight: 700;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(1.75rem, 2.6vw, 2.35rem);
  line-height: 1.06;
  overflow-wrap: anywhere;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.dashboard-stats--3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.dashboard-stats article {
  position: relative;
  min-width: 0;
  min-height: 6.4rem;
  display: grid;
  align-content: center;
  overflow: hidden;
  padding: 1.15rem 1.25rem;
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.98),
      rgba(246, 251, 248, 0.98)
    ),
    var(--surface-primary);
}

.dashboard-stats article::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 0.2rem;
  background: linear-gradient(
    90deg,
    rgba(16, 185, 129, 0.95),
    rgba(16, 185, 129, 0)
  );
}

.dashboard-stats strong {
  display: block;
  margin-bottom: 0.4rem;
  color: var(--brand-strong);
  font-size: clamp(1.55rem, 3vw, 1.9rem);
  line-height: 1;
  overflow-wrap: anywhere;
}

.dashboard-stats span {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.dashboard-stats__item--clickable {
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.dashboard-stats__item--clickable:hover {
  transform: translateY(-0.2rem);
  box-shadow: 0 0.75rem 1.5rem rgba(16, 185, 129, 0.15);
}

.dashboard-stats__item--clickable:active {
  transform: none;
}

@media (max-width: 72rem) {
  .dashboard-shell {
    grid-template-columns: 1fr;
  }

  .dashboard-sidebar {
    display: none;
  }

  .dashboard-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 48rem) {
  .dashboard-shell {
    padding-top: 1rem;
    padding-bottom: 2.5rem;
  }

  .dashboard-content {
    gap: 1rem;
  }

  .dashboard-head {
    display: grid;
    gap: 1rem;
    border-radius: 0.9rem;
  }

  .dashboard-head__actions,
  .dashboard-head__actions :deep(button),
  .dashboard-head__actions :deep(a) {
    width: 100%;
  }

  .dashboard-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
  }

  .dashboard-stats article {
    min-height: 5.8rem;
    padding: 1rem;
    border-radius: 0.9rem;
  }

  .dashboard-stats strong {
    font-size: clamp(1.4rem, 7vw, 1.75rem);
  }

  .dashboard-stats span {
    font-size: 0.82rem;
  }
}

@media (max-width: 28rem) {
  .dashboard-shell {
    padding-inline: max(0.75rem, var(--shell-gutter));
  }

  .dashboard-stats {
    gap: 0.55rem;
  }

  .dashboard-stats article {
    min-height: 5.35rem;
    padding: 0.85rem 0.75rem;
  }

  .dashboard-stats strong {
    font-size: 1.35rem;
  }

  .dashboard-stats span {
    font-size: 0.76rem;
    line-height: 1.25;
  }
}

@media (max-width: 22rem) {
  .dashboard-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (hover: none) {
  .dashboard-sidebar__item:hover,
  .dashboard-stats__item--clickable:hover {
    transform: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .dashboard-sidebar__item,
  .dashboard-stats__item--clickable {
    transition: none;
  }
}
</style>
