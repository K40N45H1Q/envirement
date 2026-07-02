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

defineEmits(['select-section'])
</script>

<template>
  <main class="dashboard-shell">
    <aside class="dashboard-sidebar">
      <div class="dashboard-sidebar__top">
        <p class="dashboard-sidebar__eyebrow">{{ t('dashboardShell.sectionsTitle') }}</p>
      </div>
      <component
        :is="section.to ? RouterLink : 'button'"
        v-for="section in sections"
        :key="section.id"
        :to="section.to"
        :type="section.to ? undefined : 'button'"
        class="dashboard-sidebar__item"
        :class="{ 'dashboard-sidebar__item--active': activeSection === section.id }"
        @click="!section.to && $emit('select-section', section.id)"
      >
        <i :class="section.icon"></i>
        <span>{{ section.label }}</span>
      </component>
    </aside>

    <section class="dashboard-content">
      <section class="dashboard-head">
        <div class="dashboard-head__copy">
          <p v-if="eyebrow" class="dashboard-eyebrow">{{ eyebrow }}</p>
          <h1>{{ title }}</h1>
          <p v-if="description" class="dashboard-description">{{ description }}</p>
        </div>

        <div v-if="$slots.actions" class="dashboard-head__actions">
          <slot name="actions" />
        </div>
      </section>

      <section v-if="stats.length" class="dashboard-stats">
        <article v-for="item in stats" :key="item.label">
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
  margin: 0 auto;
  padding: 2rem var(--shell-gutter) 4rem;
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
  display: grid;
  align-content: start;
  gap: 0.45rem;
  padding: 1rem;
  position: sticky;
  top: 5.5rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 251, 248, 0.98)),
    var(--surface-primary);
}

.dashboard-sidebar__top {
  padding: 0.25rem 0.2rem 0.7rem;
}

.dashboard-sidebar__eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.dashboard-sidebar__item {
  display: flex;
  gap: 0.65rem;
  align-items: center;
  min-height: 3rem;
  padding: 0.75rem 0.9rem;
  border: 0.0625rem solid transparent;
  border-radius: 0.875rem;
  background: transparent;
  color: var(--text-primary);
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.dashboard-sidebar__item i {
  width: 1.1rem;
  text-align: center;
  color: color-mix(in srgb, var(--text-muted) 78%, transparent);
  transition: color 0.2s ease;
}

.dashboard-sidebar__item:hover,
.dashboard-sidebar__item:focus-visible {
  background: color-mix(in srgb, var(--brand-soft) 60%, transparent);
  color: var(--brand-strong);
}

.dashboard-sidebar__item:hover i,
.dashboard-sidebar__item:focus-visible i {
  color: var(--brand-strong);
}

.dashboard-sidebar__item--active {
  background: linear-gradient(180deg, color-mix(in srgb, var(--brand-base) 22%, transparent), color-mix(in srgb, var(--brand-strong) 14%, transparent));
  border: 0.0625rem solid var(--border-strong);
  color: var(--text-primary);
  box-shadow: 0 0.75rem 1.5rem rgba(21, 149, 93, 0.08);
}

.dashboard-sidebar__item--active i {
  color: var(--brand-strong);
}

.dashboard-content {
  display: grid;
  gap: 1.5rem;
}

.dashboard-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.7rem;
  background:
    radial-gradient(circle at top right, rgba(26, 177, 111, 0.16), transparent 30%),
    radial-gradient(circle at left bottom, rgba(15, 118, 110, 0.06), transparent 26%),
    var(--surface-primary);
}

.dashboard-head__copy {
  display: grid;
  gap: 0.55rem;
}

.dashboard-eyebrow {
  margin: 0;
  color: var(--brand-strong);
  font-weight: 700;
  text-transform: uppercase;
}

.dashboard-description {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.6;
  max-width: 48rem;
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 3.4vw, 2.85rem);
  line-height: 1.02;
  color: var(--text-primary);
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.dashboard-stats article {
  position: relative;
  overflow: hidden;
  padding: 1.35rem 1.4rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 251, 248, 0.98)),
    var(--surface-primary);
}

.dashboard-stats article::before {
  content: '';
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 0.2rem;
  background: linear-gradient(90deg, rgba(16, 185, 129, 0.95), rgba(16, 185, 129, 0));
}

.dashboard-stats strong {
  display: block;
  color: var(--brand-strong);
  font-size: 2rem;
  line-height: 1;
  margin-bottom: 0.4rem;
}

.dashboard-stats span {
  color: var(--text-muted);
}

@media (max-width: 72rem) {
  .dashboard-shell {
    grid-template-columns: 1fr;
  }

  .dashboard-sidebar {
    display: none;
  }
}

@media (max-width: 48rem) {
  .dashboard-head,
  .dashboard-stats {
    grid-template-columns: 1fr;
  }

  .dashboard-head {
    display: grid;
  }

  .dashboard-stats {
    grid-template-columns: 1fr;
  }
}
</style>
