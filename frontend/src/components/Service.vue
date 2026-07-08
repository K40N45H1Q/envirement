<script setup>
import { computed } from 'vue'
import { useI18n } from '@/i18n'

const { t } = useI18n()

const steps = computed(() => [
  { number: '01', title: t('service.step1Title'), text: t('service.step1Text') },
  { number: '02', title: t('service.step2Title'), text: t('service.step2Text') },
  { number: '03', title: t('service.step3Title'), text: t('service.step3Text') },
])
</script>

<template>
  <section class="service-shell">
    <div class="service-stack">
      <section class="service-card">
        <div class="section-head">
          <p class="section-eyebrow section-eyebrow--muted">{{ t('service.eyebrow') }}</p>
          <h2>{{ t('service.title') }}</h2>
        </div>

        <div class="steps-grid">
          <article v-for="step in steps" :key="step.number" class="step-card">
            <span class="step-number">{{ step.number }}</span>
            <h3>{{ step.title }}</h3>
            <p>{{ step.text }}</p>
          </article>
        </div>
      </section>

      <section class="pricing-cta" aria-labelledby="pricing-cta-title">
        <p class="section-eyebrow section-eyebrow--muted">{{ t('pricing.eyebrow') }}</p>
        <h2 id="pricing-cta-title">{{ t('pricing.title') }}</h2>
        <p class="pricing-cta__subtitle">{{ t('pricing.ctaSubtitle') }}</p>
        <RouterLink class="btn-primary pricing-cta__button" to="/pricing">{{ t('pricing.viewPlans') }}</RouterLink>
      </section>
    </div>
  </section>
</template>

<style scoped>
.service-shell {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 0 var(--shell-gutter);
}

.service-stack {
  display: grid;
  gap: 1.25rem;
}

.service-card {
  display: grid;
  gap: 15px;
  padding: 3rem clamp(1.5rem, 5vw, 5.5rem);
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.5rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 249, 0.98));
  box-shadow: var(--shadow-soft);
}

.pricing-cta {
  display: grid;
  justify-items: center;
  gap: 0.85rem;
  padding: clamp(3rem, 7vw, 5.5rem) clamp(1.25rem, 5vw, 4rem);
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.5rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 249, 0.98));
  box-shadow: var(--shadow-soft);
  text-align: center;
}

.pricing-cta__subtitle {
  max-width: 36rem;
  color: var(--text-muted);
  line-height: 1.65;
}

.pricing-cta__button {
  margin-top: 0.65rem;
  min-width: 12rem;
  justify-content: center;
}

.section-head {
  display: grid;
  gap: 0.45rem;
  width: 100%;
  padding-bottom: 1.8rem;
  border-bottom: 0.125rem solid color-mix(in srgb, var(--text-primary) 74%, transparent);
}

.section-eyebrow--muted {
  color: color-mix(in srgb, var(--text-muted) 78%, transparent);
  letter-spacing: 0.1em;
}

h2,
h3,
p {
  margin: 0;
}

h2 {
  font-size: clamp(1.9rem, 3vw, 2.65rem);
  line-height: 1.08;
  color: var(--text-primary);
  text-transform: uppercase;
}

h3 {
  font-size: 1.05rem;
  line-height: 1.3;
  color: var(--text-primary);
}

.step-card p {
  color: var(--text-muted);
  line-height: 1.65;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.step-card {
  display: flex;
  flex-direction: column;
  gap: 0;
  min-height: 12rem;
  padding: 1.75rem 2rem 0.25rem 0;
}

.step-card + .step-card {
  padding-left: 2rem;
  border-left: 0.0625rem solid color-mix(in srgb, var(--text-primary) 12%, transparent);
}

.step-number {
  display: block;
  margin-bottom: 1.35rem;
  color: color-mix(in srgb, var(--brand-strong) 70%, #c99a4a);
  font-size: 0.78rem;
  font-weight: 800;
}

.step-card h3 {
  margin-bottom: 0.85rem;
}

.step-card p {
  max-width: 21rem;
}

@media (max-width: 78rem) {
  .steps-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 42rem) {
  .steps-grid {
    grid-template-columns: 1fr;
  }

  .service-card {
    padding: 1.5rem;
  }

  .section-head {
    padding-bottom: 1rem;
  }

  .step-card {
    min-height: auto;
    padding: 1.25rem 0;
  }

  .step-card + .step-card {
    padding-left: 0;
    border-top: 0.0625rem solid color-mix(in srgb, var(--text-primary) 12%, transparent);
    border-left: 0;
  }
}
</style>
