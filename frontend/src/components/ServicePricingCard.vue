<script setup>
import { computed, ref, watch } from 'vue'
import { getPricingPlans } from '@/api/pricing'
import { useI18n } from '@/i18n'
import ServiceCard from '@/components/ServiceCard.vue'
import '@fortawesome/fontawesome-free/css/all.css'

const billingPeriod = ref('monthly')
const pricingResponse = ref(null)
const pricingError = ref(false)
const { language, t } = useI18n()

const staticPlans = computed(() => ({
  basic: {
    name: 'Basic',
    period: t('pricing.basicPeriod'),
    description: t('pricing.basicDescription'),
    features: [t('pricing.basicFeature1'), t('pricing.basicFeature2'), t('pricing.basicFeature3')],
  },
  standard: {
    name: 'Standard',
    period: t('pricing.standardPeriod'),
    description: t('pricing.standardDescription'),
    features: [t('pricing.standardFeature1'), t('pricing.standardFeature2'), t('pricing.standardFeature3')],
  },
  pro: {
    name: 'Pro',
    period: t('pricing.proPeriod'),
    description: t('pricing.proDescription'),
    features: [t('pricing.proFeature1'), t('pricing.proFeature2'), t('pricing.proFeature3')],
  },
}))

const fallbackPrices = {
  monthly: {
    basic: 99,
    standard: 149,
    pro: 229,
  },
  yearly: {
    basic: 84.15,
    standard: 126.65,
    pro: 194.65,
  },
}

const formatPrice = (value) => {
  const locale = language.value === 'en' ? 'en-US' : 'ru-RU'
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: Number.isInteger(value) ? 0 : 2,
    maximumFractionDigits: 2,
  }).format(value)
}

const loadPricingPlans = async () => {
  pricingError.value = false

  try {
    pricingResponse.value = await getPricingPlans(billingPeriod.value)
  } catch {
    pricingError.value = true
    pricingResponse.value = null
  }
}

watch(billingPeriod, () => {
  loadPricingPlans()
}, { immediate: true })

const plans = computed(() => {
  const remotePlans = Array.isArray(pricingResponse.value?.plans) ? pricingResponse.value.plans : []
  const remoteById = new Map(remotePlans.map((plan) => [plan.id, plan]))
  const currentFallbackPrices = fallbackPrices[billingPeriod.value] || fallbackPrices.monthly

  return ['basic', 'standard', 'pro'].map((id) => {
    const staticPlan = staticPlans.value[id]
    const remotePlan = remoteById.get(id)
    const numericPrice = Number(remotePlan?.price ?? currentFallbackPrices[id] ?? 0)

    return {
      id,
      name: remotePlan?.name || staticPlan.name,
      price: formatPrice(numericPrice),
      currency: remotePlan?.currency || 'EUR',
      period: staticPlan.period,
      description: staticPlan.description,
      features: staticPlan.features,
    }
  })
})
</script>

<template>
  <ServiceCard id="pricing" header-class="service-pricing-card__header">
    <template #header>
      <div class="pricing-header">
        <div>
          <p class="section-eyebrow section-eyebrow--muted">{{ t('pricing.eyebrow') }}</p>
          <h2>{{ t('pricing.title') }}</h2>
          <p class="section-subtitle">{{ t('pricing.subtitle') }}</p>
        </div>

        <div class="billing-toggle">
          <button class="toggle-btn" :class="{ active: billingPeriod === 'monthly' }" @click="billingPeriod = 'monthly'">
            {{ t('pricing.monthly') }}
          </button>
          <button class="toggle-btn" :class="{ active: billingPeriod === 'yearly' }" @click="billingPeriod = 'yearly'">
            {{ t('pricing.yearly') }}
            <span class="discount">-15%</span>
          </button>
        </div>
      </div>
    </template>

    <p v-if="pricingError" class="pricing-note">
      {{ language === 'en' ? 'Prices are shown from the local fallback.' : 'Цены показаны из локального резервного набора.' }}
    </p>

    <div class="pricing-grid">
      <article v-for="plan in plans" :key="plan.id" class="plan-card">
        <div class="plan-top">
          <strong class="plan-name">{{ plan.name }}</strong>
          <div class="plan-price">
            <span class="price">{{ plan.price }}</span>
            <span class="currency">{{ plan.currency }}</span>
          </div>
          <p class="plan-period">{{ plan.period }}</p>
        </div>

        <p class="plan-description">{{ plan.description }}</p>

        <ul class="plan-features">
          <li v-for="feature in plan.features" :key="feature">
            <i class="fas fa-check"></i>
            <span>{{ feature }}</span>
          </li>
        </ul>

        <button class="btn-primary plan-button">{{ t('pricing.start') }}</button>
      </article>
    </div>
  </ServiceCard>
</template>

<style scoped>
:deep(.service-pricing-card__header) {
  width: 100%;
  max-width: none;
}

h2,
p {
  margin: 0;
}

.section-subtitle,
.plan-description,
.plan-period,
.pricing-note {
  color: var(--text-muted);
  line-height: 1.65;
}

.pricing-header {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 1.75rem;
  width: 100%;
}

.pricing-header > div:first-child {
  max-width: 26rem;
}

.billing-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
  margin-left: auto;
  margin-top: 0.6rem;
  padding: 0.35rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 999rem;
  background: rgba(255, 255, 255, 0.9);
}

.toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 2.8rem;
  padding: 0.7rem 1.15rem;
  border: none;
  border-radius: 999rem;
  background: transparent;
  color: var(--text-muted);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.toggle-btn.active {
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
}

.discount {
  color: var(--brand-strong);
  font-size: 0.82rem;
  font-weight: 800;
}

.toggle-btn.active .discount {
  color: #d9ffe9;
}

.pricing-note {
  margin-bottom: 1rem;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.plan-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 100%;
  padding: 1.5rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.25rem;
  background: rgba(255, 255, 255, 0.82);
}

.plan-top {
  display: grid;
  gap: 0.35rem;
}

.plan-name {
  color: var(--text-primary);
  font-size: 0.85rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.plan-price {
  display: flex;
  align-items: flex-end;
  gap: 0.25rem;
}

.price {
  font-size: clamp(2.2rem, 4vw, 3rem);
  line-height: 0.95;
  font-weight: 900;
  color: var(--text-primary);
}

.currency {
  margin-bottom: 0.35rem;
  color: var(--text-primary);
  font-weight: 700;
}

.plan-description {
  flex: 1;
}

.plan-features {
  list-style: none;
  display: grid;
  gap: 0.8rem;
  padding: 0;
  margin: 0;
}

.plan-features li {
  display: flex;
  gap: 0.7rem;
  align-items: flex-start;
  color: var(--text-primary);
  line-height: 1.45;
}

.plan-features i {
  color: var(--brand-strong);
  margin-top: 0.2rem;
}

.plan-button {
  width: 100%;
  margin-top: auto;
}

@media (max-width: 78rem) {
  .pricing-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 56rem) {
  .pricing-header {
    display: grid;
    align-items: start;
  }

  .pricing-header > div:first-child {
    max-width: 42rem;
  }

  .billing-toggle {
    margin-left: 0;
    margin-top: 0;
  }
}

@media (max-width: 42rem) {
  .billing-toggle {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr 1fr;
    border-radius: 1rem;
  }

  .toggle-btn {
    justify-content: center;
  }
}
</style>
