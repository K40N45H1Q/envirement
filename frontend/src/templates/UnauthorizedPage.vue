<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useI18n } from '@/i18n'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()
const { language, t } = useI18n()

const signInTarget = computed(() => ({
  path: `/${language.value}/signin`,
  query: {
    auth: 'login',
    ...(typeof route.query.redirect === 'string' ? { redirect: route.query.redirect } : {}),
  },
}))

const homeTarget = computed(() => `/${language.value}`)
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="card">
        <p class="eyebrow">{{ t('unauthorizedPage.eyebrow') }}</p>
        <h1>{{ t('unauthorizedPage.title') }}</h1>
        <p class="lead">{{ t('unauthorizedPage.text') }}</p>

        <div class="actions">
          <RouterLink :to="signInTarget" class="btn-primary">{{ t('unauthorizedPage.signIn') }}</RouterLink>
          <RouterLink :to="homeTarget" class="btn-secondary">{{ t('unauthorizedPage.home') }}</RouterLink>
        </div>

        <p class="hint">{{ t('unauthorizedPage.hint') }}</p>
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.page {
  min-height: calc(100vh - 6rem);
  display: grid;
  place-items: center;
  padding: 2rem 1rem 4rem;
}

.card {
  width: min(100%, 42rem);
  padding: 2rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.5rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.eyebrow {
  margin: 0 0 0.5rem;
  color: #b91c1c;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
  color: var(--text-primary);
}

.lead,
.hint {
  color: var(--text-muted);
}

.lead {
  margin-top: 0.85rem;
  font-size: 1rem;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.hint {
  margin-top: 1rem;
  font-size: 0.92rem;
}

@media (max-width: 40rem) {
  .card {
    padding: 1.5rem;
  }

  .actions {
    display: grid;
  }

  .actions :deep(a) {
    width: 100%;
  }
}
</style>
