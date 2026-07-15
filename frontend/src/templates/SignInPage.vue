<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from '@/i18n'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()
const { t } = useI18n()

const destinationLabel = computed(() => {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''

  if (redirect.startsWith('/dashboard?section=jobs') || redirect.startsWith('/dashboard')) return t('signInPage.destinations.dashboard')
  if (redirect.startsWith('/responses')) return t('signInPage.destinations.responses')
  if (redirect.startsWith('/messages')) return t('signInPage.destinations.messages')
  if (redirect.startsWith('/profile')) return t('signInPage.destinations.profile')
  return t('signInPage.destinations.dashboard')
})
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="hero">
        <div class="copy">
          <p class="eyebrow">{{ t('signInPage.eyebrow') }}</p>
          <h1>{{ t('signInPage.title', { destination: destinationLabel }) }}</h1>
          <p>{{ t('signInPage.description') }}</p>
        </div>

        <div class="panel">
          <strong>{{ t('signInPage.panelTitle') }}</strong>
          <ul>
            <li>{{ t('signInPage.featureProfile') }}</li>
            <li>{{ t('signInPage.featureEmployer') }}</li>
            <li>{{ t('signInPage.featureMessages') }}</li>
          </ul>
        </div>
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 100rem;
  margin: 0 auto;
  padding: 2rem 1rem 4rem;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(18rem, 24rem);
  gap: 1rem;
  align-items: stretch;
}

.copy,
.panel {
  padding: 2rem;
  border-radius: 0.75rem;
  background: #fff;
  box-shadow: 0 0.5rem 2rem rgba(30, 35, 38, 0.06);
}

.eyebrow {
  margin: 0 0 0.5rem;
  color: #19785a;
  font-weight: 700;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: #1e2326;
  font-size: clamp(2rem, 4vw, 3.25rem);
}

p {
  margin: 1rem 0 0;
  color: rgba(30, 35, 38, 0.68);
  line-height: 1.65;
}

.panel {
  display: grid;
  gap: 1rem;
  align-content: center;
}

.panel strong {
  color: #1e2326;
  font-size: 1.05rem;
}

ul {
  margin: 0;
  padding-left: 1.2rem;
  color: rgba(30, 35, 38, 0.7);
  line-height: 1.7;
}

@media (max-width: 56rem) {
  .hero {
    grid-template-columns: 1fr;
  }
}
</style>
