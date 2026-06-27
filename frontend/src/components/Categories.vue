<script setup>
import { RouterLink } from 'vue-router'

const cards = [
  { title: 'Строительство', jobs: '200 вакансий', category: 'construction', icon: 'fas fa-building' },
  { title: 'Производство', jobs: '200 вакансий', category: 'production', icon: 'fas fa-industry' },
  { title: 'Логистика', jobs: '200 вакансий', category: 'logistics', icon: 'fas fa-truck-fast' },
  { title: 'IT и технологии', jobs: '200 вакансий', category: 'it', icon: 'fas fa-desktop' },
  { title: 'Медицина', jobs: '200 вакансий', category: 'health', icon: 'fas fa-briefcase-medical' },
  { title: 'Гостиничный бизнес', jobs: '200 вакансий', category: 'hospitality', icon: 'fas fa-hotel' },
]
</script>

<template>
  <section class="categories-shell">
    <div class="categories-card">
      <div class="categories-head">
        <div>
          <p class="section-eyebrow">Категории</p>
          <h2>Популярные категории</h2>
        </div>
        <RouterLink :to="{ path: '/jobs' }" class="all-link">Все вакансии</RouterLink>
      </div>

      <div class="popular-grid">
        <RouterLink
          v-for="card in cards"
          :key="card.category"
          :to="{ path: '/jobs', query: { category: card.category } }"
          class="category-card"
        >
          <div class="card-icon-wrapper">
            <i :class="card.icon"></i>
          </div>
          <h3 class="card-title">{{ card.title }}</h3>
          <p class="card-vacancies">{{ card.jobs }}</p>
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.categories-shell {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 0 var(--shell-gutter);
}

.categories-card {
  display: grid;
  gap: 1.2rem;
  padding: 1.25rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.5rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 249, 0.98));
  box-shadow: var(--shadow-soft);
}

.categories-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
}

.section-eyebrow {
  margin: 0 0 0.35rem;
  color: var(--brand-strong);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h2,
.card-title,
.card-vacancies {
  margin: 0;
}

h2 {
  color: var(--text-primary);
  font-size: clamp(1.45rem, 2vw, 1.8rem);
}

.all-link {
  color: var(--brand-strong);
  font-weight: 800;
  text-decoration: none;
}

.popular-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.85rem;
}

.category-card {
  display: grid;
  gap: 0.7rem;
  justify-items: center;
  align-content: start;
  min-height: 11.5rem;
  padding: 1.25rem 0.9rem;
  border-radius: 1.2rem;
  border: 0.0625rem solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.82);
  text-align: center;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.category-card:hover {
  transform: translateY(-0.125rem);
  border-color: var(--border-strong);
  box-shadow: 0 1rem 2rem rgba(16, 24, 40, 0.08);
}

.card-icon-wrapper {
  width: 4rem;
  height: 4rem;
  display: grid;
  place-items: center;
  border-radius: 1rem;
  color: var(--brand-strong);
  background: linear-gradient(180deg, rgba(16, 185, 129, 0.16), rgba(255, 255, 255, 0.96));
  font-size: 1.5rem;
}

.card-title {
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 800;
  line-height: 1.25;
}

.card-vacancies {
  color: var(--text-muted);
  font-size: 0.86rem;
}

@media (max-width: 74rem) {
  .popular-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 40rem) {
  .categories-head {
    display: grid;
  }

  .popular-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .category-card {
    min-height: 10.5rem;
  }
}
</style>
