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
          <p class="section-eyebrow section-eyebrow--muted">
            {{ t('service.eyebrow') }}
          </p>
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
        <p class="section-eyebrow section-eyebrow--muted">
          {{ t('pricing.eyebrow') }}
        </p>
        <h2 id="pricing-cta-title">{{ t('pricing.title') }}</h2>
        <p class="pricing-cta__subtitle">{{ t('pricing.ctaSubtitle') }}</p>
        <RouterLink class="btn-primary pricing-cta__button" to="/pricing">
          {{ t('pricing.viewPlans') }}
        </RouterLink>
      </section>
    </div>
  </section>
</template>

<style scoped>
.service-shell {
  width: min(100%, var(--shell-max-width));
  margin-inline: auto;
  padding-inline: var(--shell-gutter);
}

.service-stack {
  display: grid;
  gap: clamp(1rem, 2vw, 1.25rem);
}

.service-card,
.pricing-cta {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: clamp(1rem, 2vw, 1.5rem);
  box-shadow: var(--shadow-soft);
  background:
    radial-gradient(circle at top left, rgba(26, 177, 111, 0.12), transparent 26%),
    radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.06), transparent 20%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 249, 0.98));
}

.service-card {
  display: grid;
  gap: clamp(1.25rem, 3vw, 2rem);
  padding: clamp(1.25rem, 4vw, 3rem) clamp(1.25rem, 6vw, 5.5rem);
}

.pricing-cta {
  display: grid;
  justify-items: center;
  gap: clamp(0.7rem, 1.8vw, 0.85rem);
  padding: clamp(2rem, 7vw, 5.5rem) clamp(1.25rem, 5vw, 4rem);
  text-align: center;
}

.pricing-cta__subtitle {
  max-width: 36rem;
  color: var(--text-muted);
  line-height: 1.65;
}

.pricing-cta__button {
  margin-top: 0.65rem;
  min-width: min(100%, 12rem);
  justify-content: center;
}

.section-head {
  display: grid;
  gap: 0.45rem;
  padding-bottom: clamp(1rem, 2.4vw, 1.8rem);
  border-bottom: 0.125rem solid color-mix(in srgb, var(--text-primary) 74%, transparent);
}

.section-head h2 {
  text-wrap: nowrap;
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
  max-width: 16ch;
  color: var(--text-primary);
  font-size: clamp(1.7rem, 5vw, 2.65rem);
  line-height: 1.08;
  text-transform: uppercase;
}

.pricing-cta h2 {
  max-width: 18ch;
}

h3 {
  color: var(--text-primary);
  font-size: clamp(1rem, 1.4vw, 1.05rem);
  line-height: 1.3;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr));
  gap: 0;
}

.step-card {
  display: grid;
  align-content: start;
  gap: 0.85rem;
  min-height: clamp(10rem, 18vw, 12rem);
  padding: clamp(1.25rem, 2.5vw, 1.75rem);
  border-inline-start: 0.0625rem solid color-mix(in srgb, var(--text-primary) 12%, transparent);
}

.step-card:first-child {
  border-inline-start: 0;
  padding-inline-start: 0;
}

.step-number {
  display: block;
  margin-bottom: 0.5rem;
  color: color-mix(in srgb, var(--brand-strong) 70%, #c99a4a);
  font-size: 0.78rem;
  font-weight: 800;
}

.step-card p {
  max-width: 21rem;
  color: var(--text-muted);
  line-height: 1.65;
}

@media (max-width: 56rem) {
  .step-card:nth-child(odd) {
    border-inline-start: 0;
    padding-inline-start: 0;
  }
}

@media (max-width: 36rem) {
  .service-shell {
    padding-inline: max(1rem, var(--shell-gutter));
  }

  .service-card {
    padding: 1.25rem;
  }

  .steps-grid {
    grid-template-columns: 1fr;
  }

  .section-head h2 {
    display: none;
  }

  .step-card {
    min-height: auto;
    padding: 1.25rem 0;
    border-inline-start: 0;
    border-top: 0.0625rem solid color-mix(in srgb, var(--text-primary) 12%, transparent);
  }

  .step-card:first-child {
    border-top: 0;
    padding-top: 0.25rem;
  }

  .step-card:last-child {
    padding-bottom: 0;
  }

  .pricing-cta__button {
    width: 100%;
  }
}
</style>