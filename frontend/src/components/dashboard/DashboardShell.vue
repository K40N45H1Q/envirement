<script setup>
import { RouterLink } from 'vue-router'

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
  grid-template-columns: 16rem minmax(0, 1fr);
  gap: 1.5rem;
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
}

.dashboard-sidebar__item {
  display: flex;
  gap: 0.65rem;
  align-items: center;
  min-height: 3rem;
  padding: 0.75rem 0.9rem;
  border: none;
  border-radius: 0.875rem;
  background: transparent;
  color: var(--text-primary);
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.dashboard-sidebar__item:hover,
.dashboard-sidebar__item:focus-visible,
.dashboard-sidebar__item--active,
.dashboard-sidebar__item.router-link-active {
  background: linear-gradient(180deg, color-mix(in srgb, var(--brand-base) 22%, transparent), color-mix(in srgb, var(--brand-strong) 14%, transparent));
  border: 0.0625rem solid var(--border-strong);
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
  padding: 1.75rem;
  background:
    radial-gradient(circle at top right, rgba(26, 177, 111, 0.14), transparent 28%),
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
  line-height: 1.65;
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
  color: var(--text-primary);
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1.5rem;
}

.dashboard-stats article {
  padding: 1.5rem;
}

.dashboard-stats strong {
  display: block;
  color: var(--brand-strong);
  font-size: 2.1rem;
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
    position: static;
    grid-auto-flow: column;
    grid-auto-columns: minmax(10.5rem, 1fr);
    overflow-x: auto;
    scrollbar-width: none;
  }

  .dashboard-sidebar::-webkit-scrollbar {
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
