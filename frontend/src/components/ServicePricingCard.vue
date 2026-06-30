<script setup>
import { ref } from 'vue'
import ServiceCard from '@/components/ServiceCard.vue'
import '@fortawesome/fontawesome-free/css/all.css'

const billingPeriod = ref('monthly')

const plans = [
  {
    name: 'Basic',
    price: '99',
    period: '1 вакансия · 30 дней',
    description: 'Для тех, кто нанимает редко. Полный Match Score и все инструменты фильтрации.',
    features: ['Match Score по каждому отклику', 'Breakdown по параметрам', 'Кнопка «Пригласить»'],
  },
  {
    name: 'Standard',
    price: '149',
    period: '3 вакансии · 30 дней каждая',
    description: 'Для регулярного найма. Сравнение кандидатов и история откликов по компании.',
    features: ['Всё из Basic', 'Сравнение кандидатов бок о бок', 'История откликов по компании'],
  },
  {
    name: 'Pro',
    price: '229',
    period: 'Безлимит вакансий · 30 дней',
    description: 'Для компаний с постоянным потоком найма. Все функции без ограничений.',
    features: ['Всё из Standard', 'Безлимит активных вакансий', 'Приоритетная поддержка'],
  },
]
</script>

<template>
  <ServiceCard id="pricing" header-class="service-pricing-card__header">
    <template #header>
      <div class="pricing-header">
        <div>
          <p class="section-eyebrow section-eyebrow--muted">Цены</p>
          <h2>Прозрачное ценообразование</h2>
          <p class="section-subtitle">
            Одна вакансия — 30 дней. Никакого автопродления. Напоминаем за 3 дня до окончания.
          </p>
        </div>

        <div class="billing-toggle">
          <button class="toggle-btn" :class="{ active: billingPeriod === 'monthly' }" @click="billingPeriod = 'monthly'">
            Ежемесячно
          </button>
          <button class="toggle-btn" :class="{ active: billingPeriod === 'yearly' }" @click="billingPeriod = 'yearly'">
            Ежегодно
            <span class="discount">-15%</span>
          </button>
        </div>
      </div>
    </template>

    <div class="pricing-grid">
      <article v-for="plan in plans" :key="plan.name" class="plan-card">
        <div class="plan-top">
          <strong class="plan-name">{{ plan.name }}</strong>
          <div class="plan-price">
            <span class="price">{{ plan.price }}</span>
            <span class="currency">EUR</span>
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

        <button class="btn-primary plan-button">Начать</button>
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
.plan-period {
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
