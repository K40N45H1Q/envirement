<template>
  <footer class="site-footer">
    <div class="footer-shell">
      <div class="brand-block">
        <RouterLink to="/" class="brand-link" aria-label="CVHOLD home">
          <Logo />
        </RouterLink>
        <p>
          CVHOLD помогает работодателям и специалистам по всей Европе находить друг друга
          через понятные профили, прозрачные отклики и удобный рабочий процесс найма.
        </p>
      </div>

      <nav class="footer-grid" aria-label="Подвал сайта">
        <div class="footer-column">
          <h2>Платформа</h2>
          <RouterLink to="/jobs">Вакансии</RouterLink>
          <RouterLink to="/resume-builder">Резюме</RouterLink>
          <RouterLink to="/about">О нас</RouterLink>
        </div>

        <div class="footer-column">
          <h2>Работодателям</h2>
          <RouterLink to="/">Решения</RouterLink>
          <RouterLink to="/pricing">Тарифы</RouterLink>
          <RouterLink to="/employer-dashboard">Кабинет</RouterLink>
        </div>

        <div class="footer-column">
          <h2>Поддержка</h2>
          <RouterLink to="/faq">FAQ</RouterLink>
          <RouterLink to="/contacts">Контакты</RouterLink>
          <RouterLink to="/terms">Условия</RouterLink>
        </div>
      </nav>
    </div>

    <div class="footer-meta">
      <span>&copy; {{ currentYear }} CVHOLD. Все права защищены.</span>
      <span>Платформа для поиска работы и найма в Латвии, Литве, Эстонии и по всей Европе.</span>
    </div>
  </footer>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import Logo from '@/components/Logo.vue'
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.site-footer {
  margin-top: auto;
  border-top: 0.0625rem solid var(--border-subtle);
  background:
    radial-gradient(circle at top left, rgba(37, 167, 108, 0.16), transparent 30%),
    radial-gradient(circle at bottom right, rgba(20, 184, 87, 0.1), transparent 28%),
    var(--surface-primary);
}

.footer-shell,
.footer-meta {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding-left: var(--shell-gutter);
  padding-right: var(--shell-gutter);
}

.footer-shell {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 2rem;
  padding-top: 2rem;
  padding-bottom: 1.5rem;
}

.brand-block {
  display: grid;
  gap: 0.875rem;
}

.brand-link {
  display: inline-flex;
  width: fit-content;
}

.brand-link :deep(svg) {
  width: clamp(9rem, 15vw, 12rem);
  height: auto;
}

.brand-link :deep(.logo) {
  color: var(--text-primary);
}

.brand-block p,
.footer-meta,
.footer-column a {
  color: var(--text-muted);
}

.brand-block p {
  max-width: 32rem;
  line-height: 1.65;
}

.footer-column h2,
.brand-link,
.footer-meta span {
  text-shadow: 0 0.0625rem 0 rgba(0, 0, 0, 0.02);
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.footer-column {
  display: grid;
  gap: 0.65rem;
  align-content: start;
}

.footer-column h2 {
  margin: 0 0 0.2rem;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.footer-column a {
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-column a:hover,
.footer-column a:focus-visible {
  color: var(--brand-strong);
}

.footer-meta {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1rem;
  padding-bottom: 1.5rem;
  border-top: 0.0625rem solid var(--border-subtle);
  font-size: 0.875rem;
}

@media (prefers-reduced-motion: no-preference) {
  .brand-link,
  .footer-column a {
    transition: transform 0.2s ease, color 0.2s ease;
  }

  .brand-link:hover,
  .brand-link:focus-visible {
    transform: translateY(-0.0625rem);
  }
}

@media (max-width: 64rem) {
  .footer-shell {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 40rem) {
  .footer-grid,
  .footer-meta {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
