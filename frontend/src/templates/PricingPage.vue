<script setup>
import AppLayout from '@/components/AppLayout.vue'
import ServicePricingCard from '@/components/ServicePricingCard.vue'
</script>

<template>
  <AppLayout>
    <main class="pricing-page">
      <ServicePricingCard />
    </main>
  </AppLayout>
</template>

<style scoped>
.pricing-page {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 1.25rem var(--shell-gutter) 4rem;
}

.pricing-page :deep(.service-card) {
  padding: 1.75rem;
  border-radius: 1.6rem;
  background:
    radial-gradient(circle at top left, rgba(26, 177, 111, 0.12), transparent 26%),
    radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.06), transparent 20%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 249, 0.98));
  box-shadow: var(--shadow-soft);
}

.pricing-page :deep(.pricing-header) {
  align-items: center;
  padding: 0.25rem 0 0.75rem;
}

.pricing-page :deep(.pricing-header h2) {
  font-size: clamp(2.2rem, 4.8vw, 4rem);
  line-height: 0.98;
}

.pricing-page :deep(.section-subtitle) {
  max-width: 40rem;
  font-size: 1rem;
}

.pricing-page :deep(.billing-toggle),
.pricing-page :deep(.plan-card) {
  background: rgba(255, 255, 255, 0.76);
}

.pricing-page :deep(.plan-card) {
  border-radius: 1.1rem;
}

.pricing-page :deep(.plan-card:nth-child(2)) {
  border-color: color-mix(in srgb, var(--brand-base) 28%, var(--border-subtle));
  background:
    radial-gradient(circle at top right, rgba(26, 177, 111, 0.1), transparent 34%),
    rgba(255, 255, 255, 0.84);
}

@media (max-width: 40rem) {
  .pricing-page :deep(.service-card) {
    padding: 1.25rem;
  }
}
</style>
