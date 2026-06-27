<script setup>
import { RouterLink } from 'vue-router'
import Match from './Match.vue'
</script>

<template>
  <section class="hero-shell">
    <div class="hero surface-card">
      <div class="hero-copy">
        <p class="hero-eyebrow">Наше преимущество</p>
        <h1>
          Умный подбор.
          <br />
          Прозрачные отклики.
          <br />
          <span>Точный результат.</span>
        </h1>
        <p class="hero-description">
          Каждый кандидат получает Score по вашим требованиям.
          Вы видите только тех, кто действительно подходит.
        </p>

        <div class="hero-actions">
          <RouterLink to="/jobs" class="btn-primary">
            <i class="fas fa-magnifying-glass"></i>
            Найти сотрудника
          </RouterLink>
          <RouterLink to="/employer-dashboard" class="btn-secondary">
            Разместить вакансию
            <i class="fas fa-plus"></i>
          </RouterLink>
        </div>

        <div class="hero-features">
          <article class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-chart-bar"></i>
            </div>
            <div>
              <h3>Match Score</h3>
              <p>По каждому отклику</p>
            </div>
          </article>

          <article class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-users"></i>
            </div>
            <div>
              <h3>Сравнение</h3>
              <p>Кандидатов side-by-side</p>
            </div>
          </article>

          <article class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <div>
              <h3>Аналитика</h3>
              <p>По всем этапам подбора</p>
            </div>
          </article>
        </div>
      </div>

      <div class="hero-score">
        <Match />
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-shell {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 1.25rem var(--shell-gutter) 0;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(18rem, 31rem);
  gap: 1.75rem;
  align-items: start;
  padding: 1.75rem;
  border-radius: 1.6rem;
  border: 0.0625rem solid var(--border-subtle);
  background:
    radial-gradient(circle at top left, rgba(26, 177, 111, 0.12), transparent 26%),
    radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.06), transparent 20%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 249, 0.98));
  box-shadow: var(--shadow-soft);
}

.hero-copy {
  display: grid;
  gap: 1.3rem;
  align-content: start;
}

.hero-eyebrow {
  margin: 0;
  color: var(--brand-strong);
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: clamp(2.2rem, 4.8vw, 4rem);
  line-height: 0.98;
  color: var(--text-primary);
}

h1 span {
  color: var(--brand-strong);
}

.hero-description {
  max-width: 40rem;
  margin: 0;
  color: var(--text-muted);
  font-size: 1rem;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  gap: 0.9rem;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  min-height: 3.4rem;
  min-width: 13rem;
  padding-inline: 1.35rem;
  border-radius: 1rem;
}

.hero-features {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.85rem;
}

.feature-card {
  display: grid;
  grid-template-columns: 3rem 1fr;
  gap: 0.8rem;
  align-items: start;
  padding: 1rem;
  border-radius: 1.1rem;
  border: 0.0625rem solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.76);
}

.feature-icon {
  width: 3rem;
  height: 3rem;
  display: grid;
  place-items: center;
  border-radius: 0.9rem;
  color: var(--brand-strong);
  background: color-mix(in srgb, var(--brand-soft) 76%, transparent);
}

.feature-card h3 {
  margin: 0 0 0.25rem;
  font-size: 0.98rem;
  color: var(--text-primary);
}

.feature-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.84rem;
  line-height: 1.45;
}

.hero-score {
  min-width: 0;
}

@media (max-width: 74rem) {
  .hero {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 56rem) {
  .hero-features {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 40rem) {
  .hero {
    padding: 1.25rem;
  }

  .hero-actions {
    display: grid;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
