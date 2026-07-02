<script setup>
import { computed } from 'vue'
import { useI18n } from '@/i18n'
import AppLayout from '@/components/AppLayout.vue'

const { t } = useI18n()

const plans = computed(() => [
  {
    name: 'Basic',
    price: '99 EUR',
    badge: '',
    features: [
      t('pricing.planFeatureJobs', { count: 1 }),
      t('pricing.planFeatureBasicCard'),
      t('pricing.planFeatureApplications'),
    ],
  },
  {
    name: 'Standard',
    price: '149 EUR',
    badge: t('pricing.popular'),
    features: [
      t('pricing.planFeatureJobs', { count: 5 }),
      t('pricing.planFeatureMatchScore'),
      t('pricing.planFeatureEmployerDashboard'),
    ],
  },
  {
    name: 'Pro',
    price: '229 EUR',
    badge: '',
    features: [
      t('pricing.planFeatureJobs', { count: 20 }),
      t('pricing.planFeaturePriorityListing'),
      t('pricing.planFeatureAnalytics'),
    ],
  },
])
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="head">
        <p class="eyebrow">{{ t('pricing.eyebrow') }}</p>
        <h1>{{ t('pricing.pricingPageTitle') }}</h1>
        <p>{{ t('pricing.pricingPageDescription') }}</p>
      </section>

      <section class="plans">
        <article v-for="plan in plans" :key="plan.name" class="plan" :class="{ featured: plan.badge }">
          <span v-if="plan.badge" class="badge">{{ plan.badge }}</span>
          <h2>{{ plan.name }}</h2>
          <strong>{{ plan.price }}</strong>
          <ul>
            <li v-for="feature in plan.features" :key="feature">
              <i class="fas fa-check"></i>{{ feature }}
            </li>
          </ul>
          <RouterLink to="/dashboard?section=pricing" class="btn-primary">{{ t('pricing.choose') }}</RouterLink>
        </article>
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

.head,
.plan {
  border-radius: 0.75rem;
  background: #fff;
  box-shadow: 0 0.5rem 2rem rgba(30, 35, 38, 0.06);
}

.head {
  padding: 2rem;
  text-align: center;
}

.eyebrow {
  color: #19785a;
  font-weight: 700;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
}

.plans {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.plan {
  position: relative;
  display: grid;
  gap: 1rem;
  padding: 1.5rem;
}

.featured {
  border: 0.125rem solid #19785a;
}

.badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  color: #19785a;
  font-weight: 700;
}

.plan strong {
  color: #19785a;
  font-size: 2.5rem;
}

ul {
  display: grid;
  gap: 0.7rem;
  padding: 0;
  margin: 0;
  list-style: none;
}

li {
  display: flex;
  gap: 0.5rem;
  color: rgba(30, 35, 38, 0.68);
}

li i {
  color: #19785a;
}

@media (max-width: 56rem) {
  .plans {
    grid-template-columns: 1fr;
  }
}
</style>
