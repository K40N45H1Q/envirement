<script setup>
import { ref } from 'vue'
import '@fortawesome/fontawesome-free/css/all.css'

const billingPeriod = ref('monthly')

const steps = [
  {
    number: '1',
    title: 'Разместите вакансию',
    text: 'Укажите требования: категории, опыт, навыки, права, график, локация, зарплата и др.',
  },
  {
    number: '2',
    title: 'Получайте Score по каждому отклику',
    text: 'Каждый кандидат получает Match Score 0–100 по вашим критериям. Strong / Good / Partial / Weak — сразу видно, кто подходит.',
  },
  {
    number: '3',
    title: 'Нанимайте лучшего',
    text: 'Разбор по каждому параметру в карточке. Пригласите одним кликом — кандидат получит письмо с вашими контактами.',
  },
]

const reasons = [
  'Никаких «подходит/не подходит» вслепую',
  'Сравнение кандидатов по ключевым критериям',
  'Экономия времени рекрутера',
  'Более точные и быстрые наймы',
]

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
  <section class="service-shell">
    <div class="service-stack">
      <section class="service-card">
        <div class="section-head">
          <p class="section-eyebrow section-eyebrow--muted">Как это работает</p>
          <h2>Три шага до нужного кандидата</h2>
          <p class="section-subtitle">
            Структурированные профили с обеих сторон — вакансии и кандидат говорят на одном языке полей.
            Система сравнивает поле с полем.
          </p>
        </div>

        <div class="steps-grid">
          <article v-for="step in steps" :key="step.number" class="step-card">
            <div class="step-number">{{ step.number }}</div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.text }}</p>
          </article>

          <article class="step-card step-card--reasons">
            <h3>Почему это работает лучше</h3>
            <ul class="why-list">
              <li v-for="reason in reasons" :key="reason">
                <i class="fas fa-check"></i>
                <span>{{ reason }}</span>
              </li>
            </ul>
          </article>
        </div>
      </section>

      <section class="service-card">
        <div class="pricing-header">
          <div>
            <p class="section-eyebrow section-eyebrow--muted">Цены</p>
            <h2>Прозрачное ценообразование</h2>
            <p class="section-subtitle">
              Одна вакансия — 30 дней. Никакого автопродления.
              Напоминаем за 3 дня до окончания.
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
  gap: 1.4rem;
  padding: 1.5rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.5rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 249, 0.98));
  box-shadow: var(--shadow-soft);
}

.section-head {
  display: grid;
  gap: 0.7rem;
  max-width: 44rem;
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
  font-size: clamp(1.8rem, 3vw, 2.35rem);
  line-height: 1.1;
  color: var(--text-primary);
}

h3 {
  font-size: 1.05rem;
  line-height: 1.3;
  color: var(--text-primary);
}

.section-subtitle,
.step-card p,
.plan-description,
.plan-period {
  color: var(--text-muted);
  line-height: 1.65;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.step-card,
.plan-card {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  min-height: 100%;
  padding: 1.5rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.25rem;
  background: rgba(255, 255, 255, 0.82);
}

.step-card--reasons {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(239, 248, 243, 0.96));
}

.step-number {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 999rem;
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
  font-size: 0.82rem;
  font-weight: 800;
}

.why-list,
.plan-features {
  list-style: none;
  display: grid;
  gap: 0.8rem;
  padding: 0;
  margin: 0;
}

.why-list li,
.plan-features li {
  display: flex;
  gap: 0.7rem;
  align-items: flex-start;
  color: var(--text-primary);
  line-height: 1.45;
}

.why-list i,
.plan-features i {
  color: var(--brand-strong);
  margin-top: 0.2rem;
}

.pricing-header {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 1rem;
}

.pricing-header > div:first-child {
  max-width: 42rem;
}

.billing-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
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
  gap: 1rem;
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

.plan-button {
  width: 100%;
  margin-top: auto;
}

@media (max-width: 78rem) {
  .steps-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .pricing-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 56rem) {
  .pricing-header {
    display: grid;
    align-items: start;
  }
}

@media (max-width: 42rem) {
  .steps-grid {
    grid-template-columns: 1fr;
  }

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
