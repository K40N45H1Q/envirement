<script setup>
import { RouterLink } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="hero-panel">
        <div>
          <p class="eyebrow">Работодателям</p>
          <h1>Найдите лучших сотрудников быстрее</h1>
          <p>Публикуйте вакансии, собирайте отклики и смотрите кандидатов в одном кабинете.</p>
          <div class="actions">
            <RouterLink to="/employer-dashboard" class="btn-primary">Разместить вакансию</RouterLink>
            <RouterLink to="/responses" class="btn-secondary">Смотреть отклики</RouterLink>
          </div>
        </div>

        <div class="stats">
          <div><strong>50 000+</strong><span>кандидатов</span></div>
          <div><strong>15 000+</strong><span>откликов</span></div>
          <div><strong>99%</strong><span>прозрачности</span></div>
        </div>
      </section>

      <section class="steps">
        <article>
          <i class="fas fa-briefcase"></i>
          <h2>Создайте вакансию</h2>
          <p>Заполните роль, зарплату, локацию и требования.</p>
        </article>
        <article>
          <i class="fas fa-users"></i>
          <h2>Получайте отклики</h2>
          <p>Все заявки попадают в кабинет работодателя.</p>
        </article>
        <article>
          <i class="fas fa-chart-line"></i>
          <h2>Сравнивайте кандидатов</h2>
          <p>Match Score помогает быстрее принимать решения.</p>
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

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 24rem;
  gap: 2rem;
  align-items: center;
  padding: 2.5rem;
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
  max-width: 42rem;
  margin: 0;
  color: #1e2326;
  font-size: clamp(2rem, 4vw, 3.2rem);
}

p {
  color: rgba(30, 35, 38, 0.66);
  line-height: 1.6;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1.5rem;
}

.stats {
  display: grid;
  gap: 1rem;
}

.stats div,
.steps article {
  padding: 1.25rem;
  border-radius: 0.75rem;
  background: #f8fafc;
}

.stats strong {
  display: block;
  color: #19785a;
  font-size: 2rem;
}

.steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.steps i {
  color: #19785a;
  font-size: 1.5rem;
}

.steps h2 {
  margin-bottom: 0.4rem;
}

@media (max-width: 56rem) {
  .hero-panel,
  .steps {
    grid-template-columns: 1fr;
  }
}
</style>
