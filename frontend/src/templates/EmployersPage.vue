<script setup>
import { RouterLink } from 'vue-router'
import { useI18n } from '@/i18n'
import AppLayout from '@/components/AppLayout.vue'
import ServicePricingCard from '@/components/ServicePricingCard.vue'

const { t } = useI18n()
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="hero-panel">
        <div>
          <p class="eyebrow">{{ t('employersPage.eyebrow') }}</p>
          <h1>{{ t('employersPage.title') }}</h1>
          <p>{{ t('employersPage.description') }}</p>
          <div class="actions">
            <RouterLink to="/dashboard?section=jobs" class="btn-primary">{{ t('employersPage.postJob') }}</RouterLink>
            <RouterLink to="/responses" class="btn-secondary">{{ t('employersPage.viewResponses') }}</RouterLink>
          </div>
        </div>

        <div class="stats">
          <div><strong>50 000+</strong><span>{{ t('employersPage.statsCandidates') }}</span></div>
          <div><strong>15 000+</strong><span>{{ t('employersPage.statsResponses') }}</span></div>
          <div><strong>99%</strong><span>{{ t('employersPage.statsTransparency') }}</span></div>
        </div>
      </section>

      <section class="steps">
        <article>
          <i class="fas fa-briefcase"></i>
          <h2>{{ t('employersPage.stepCreateTitle') }}</h2>
          <p>{{ t('employersPage.stepCreateText') }}</p>
        </article>
        <article>
          <i class="fas fa-users"></i>
          <h2>{{ t('employersPage.stepResponsesTitle') }}</h2>
          <p>{{ t('employersPage.stepResponsesText') }}</p>
        </article>
        <article>
          <i class="fas fa-chart-line"></i>
          <h2>{{ t('employersPage.stepCompareTitle') }}</h2>
          <p>{{ t('employersPage.stepCompareText') }}</p>
        </article>
      </section>

      <section class="pricing-section">
        <ServicePricingCard />
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.page { max-width: 100rem; margin: 0 auto; padding: 2rem 1rem 4rem; }
.hero-panel { display: grid; grid-template-columns: minmax(0, 1fr) 24rem; gap: 2rem; align-items: center; padding: 2.5rem; border-radius: 0.75rem; background: #fff; box-shadow: 0 0.5rem 2rem rgba(30, 35, 38, 0.06); }
.eyebrow { margin: 0 0 0.5rem; color: var(--brand-strong); font-weight: 700; text-transform: uppercase; }
h1 { max-width: 42rem; margin: 0; color: #1e2326; font-size: clamp(2rem, 4vw, 3.2rem); }
p { color: rgba(30, 35, 38, 0.66); line-height: 1.6; }
.actions { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1.5rem; }
.stats { display: grid; gap: 1rem; }
.stats div, .steps article { padding: 1.25rem; border-radius: 0.75rem; background: #f8fafc; }
.stats strong { display: block; color: var(--brand-strong); font-size: 2rem; }
.steps { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; margin-top: 1rem; }
.steps i { color: var(--brand-strong); font-size: 1.5rem; }
.steps h2 { margin-bottom: 0.4rem; }
.pricing-section { margin-top: 1rem; }
@media (max-width: 56rem) { .hero-panel, .steps { grid-template-columns: 1fr; } }
</style>
