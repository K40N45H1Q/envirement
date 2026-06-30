<script setup>
import ServicePricingCard from '@/components/ServicePricingCard.vue'
import '@fortawesome/fontawesome-free/css/all.css'

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

      <ServicePricingCard />
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
.step-card p {
  color: var(--text-muted);
  line-height: 1.65;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.step-card {
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

.why-list {
  list-style: none;
  display: grid;
  gap: 0.8rem;
  padding: 0;
  margin: 0;
}

.why-list li {
  display: flex;
  gap: 0.7rem;
  align-items: flex-start;
  color: var(--text-primary);
  line-height: 1.45;
}

.why-list i {
  color: var(--brand-strong);
  margin-top: 0.2rem;
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
}
</style>
