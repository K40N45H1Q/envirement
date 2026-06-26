<template>
  <section class="hero">
    <div class="hero-content">
      <div class="badge">НАШЕ ПРЕИМУЩЕСТВО</div>
      <h1>
        Умный подбор.<br />
        Прозрачные отклики.<br />
        <span class="accent">Точный результат.</span>
      </h1>
      <p class="hero-description">
        Каждый кандидат получает Score по вашим требованиям.<br />
        Вы видите только тех, кто действительно подходит.
      </p>
      <div class="hero-buttons">
        <RouterLink to="/jobs" class="btn-primary">
          <i class="fas fa-magnifying-glass"></i>
          Найти сотрудника
        </RouterLink>
        <RouterLink to="/employer-dashboard" class="btn-secondary">
          Разместить вакансию
          <i class="fas fa-plus"></i>
        </RouterLink>
      </div>
      <div class="features">
        <div class="feature">
          <div class="feature-icon">
            <i class="fas fa-chart-bar"></i>
          </div>
          <div class="feature-text">
            <h4>Match Score</h4>
            <p>по каждому отклику</p>
          </div>
        </div>
        <div class="feature">
          <div class="feature-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="feature-text">
            <h4>Сравнение</h4>
            <p>кандидатов side-by-side</p>
          </div>
        </div>
        <div class="feature">
          <div class="feature-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="feature-text">
            <h4>Аналитика</h4>
            <p>по всем этапам подбора</p>
          </div>
        </div>
      </div>
    </div>

    <Match />
  </section>
</template>

<style scoped>
.hero {
  --s: clamp(0.75rem, 1.7vw, 0.875rem);

  padding: calc(var(--s) * 3.75) 0;
  display: grid;
  grid-template-columns: 1fr 40%;
  gap: calc(var(--s) * 3.75);
  align-items: start;
  max-width: 100rem;
  margin: 0 auto;
  padding-left: 10px;
  padding-right: 10px;
}

.badge {
  display: inline-block;
  padding: calc(var(--s) * 0.375) calc(var(--s) * 1);
  color: #19785a;
  border: 0.15rem solid rgba(25, 120, 90, 0.7);
  border-radius: calc(var(--s) * 1.25);
  font-size: calc(var(--s) * 1);
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: calc(var(--s) * 1.5);
}

h1 {
  font-size: clamp(1.75rem, 5vw, 3rem);
  line-height: 1.1;
  margin: 0 0 calc(var(--s) * 1.25);
  font-weight: 700;
  color: #1e2326;
}

.accent {
  color: #19785a;
}

.hero-description {
  font-size: var(--s);
  color: #666;
  margin: 0 0 calc(var(--s) * 2);
  line-height: 1.6;
}

.hero-buttons {
  display: grid;
  grid-template-columns: auto auto;
  gap: calc(var(--s) * 1.5);
  margin-bottom: calc(var(--s) * 2.5);
}

.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: calc(var(--s) * 2.5);
  align-items: start;
}

.feature {
  display: grid;
  grid-template-columns: calc(var(--s) * 3) 1fr;
  gap: calc(var(--s) * 0.5);
  min-width: 0;
  align-items: start;
}

.feature-icon {
  width: calc(var(--s) * 3);
  height: calc(var(--s) * 3);
  min-width: calc(var(--s) * 3);
  background: #e6f0ec;
  border-radius: calc(var(--s) * 0.5);
  display: grid;
  place-items: center;
  color: #19785a;
  font-size: calc(var(--s) * 1.125);
}

.feature-text h4 {
  font-size: calc(var(--s) * 1);
  margin: 0 0 calc(var(--s) * 0.25);
  color: #1e2326;
  word-wrap: break-word;
  overflow-wrap: break-word;
  line-height: 1.3;
}

.feature-text p {
  font-size: calc(var(--s) * 0.9);
  color: #999;
  margin: 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
  line-height: 1.3;
}

.btn-primary,
.btn-secondary {
  height: 3.5rem;
  font-size: clamp(0.8125rem, 1.5vw, 1rem);
}

@media (max-width: 62rem) {
  .hero {
    grid-template-columns: 1fr;
  }
  .hero-buttons {
    grid-template-columns: 1fr;
  }
  .features {
    place-items: start center;
  }

  .feature {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: calc(var(--s) * 0.75);
  }

  .feature-icon {
    width: calc(var(--s) * 3.5);
    height: calc(var(--s) * 3.5);
    min-width: unset;
    font-size: calc(var(--s) * 1.5);
  }

  .feature-text {
    text-align: center;
  }
}
</style>

<script setup>
import { RouterLink } from 'vue-router';
import Match from './Match.vue';
</script>
