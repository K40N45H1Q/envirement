<template>
  <footer class="site-footer">
    <div class="footer-shell">
      <div class="brand-block">
        <RouterLink to="/" class="brand-link" :aria-label="t('footer.homeLabel')">
          <Logo />
        </RouterLink>
        <p>{{ t('footer.home') }}</p>
      </div>

      <nav class="footer-grid" :aria-label="t('footer.navLabel')">
        <div class="footer-column">
          <h2>{{ t('footer.platform') }}</h2>
          <RouterLink to="/">{{ t('footer.jobs') }}</RouterLink>
          <button type="button" class="footer-link-button" @click="cvBuilder.open">{{ t('footer.resume') }}</button>
          <RouterLink to="/about">{{ t('footer.aboutUs') }}</RouterLink>
        </div>

        <div class="footer-column">
          <h2>{{ t('footer.forEmployers') }}</h2>
          <RouterLink to="/employers">{{ t('footer.solutions') }}</RouterLink>
          <RouterLink to="/pricing">{{ t('footer.pricing') }}</RouterLink>
          <RouterLink to="/dashboard">{{ t('footer.dashboard') }}</RouterLink>
        </div>

        <div class="footer-column">
          <h2>{{ t('footer.support') }}</h2>
          <RouterLink to="/faq">{{ t('footer.faq') }}</RouterLink>
          <RouterLink to="/contacts">{{ t('footer.contacts') }}</RouterLink>
          <RouterLink to="/terms">{{ t('footer.terms') }}</RouterLink>
        </div>
      </nav>
    </div>

    <div class="footer-meta">
      <span>&copy; {{ currentYear }} CVHOLD. {{ t('footer.rights') }}</span>
      <span>{{ t('footer.meta') }}</span>
    </div>
  </footer>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useI18n } from '@/i18n'
import Logo from '@/components/Logo.vue'
import { useCvBuilderStore } from '@/stores/cvBuilder'

const { t } = useI18n()
const cvBuilder = useCvBuilderStore()
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

.brand-link :deep(.logo) {
  width: clamp(9rem, 15vw, 12rem);
  height: auto;
}

.brand-link :deep(.logo) {
  color: var(--text-primary);
}

.brand-block p,
.footer-meta,
.footer-column a,
.footer-link-button {
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

.footer-column a,
.footer-link-button {
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-link-button {
  padding: 0;
  border: 0;
  background: transparent;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.footer-column a:hover,
.footer-column a:focus-visible,
.footer-link-button:hover,
.footer-link-button:focus-visible {
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
  .footer-column a,
  .footer-link-button {
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
  .footer-shell {
    gap: 1rem;
    padding-top: 1.15rem;
    padding-bottom: 1rem;
  }

  .brand-block {
    gap: 0;
  }

  .brand-link :deep(.logo) {
    width: 8.75rem;
  }

  .brand-block p {
    display: none;
  }

  .footer-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.65rem;
  }

  .footer-column {
    gap: 0.42rem;
    min-width: 0;
  }

  .footer-column h2 {
    margin-bottom: 0.1rem;
    font-size: 0.78rem;
    line-height: 1.25;
    overflow-wrap: anywhere;
  }

  .footer-column a,
  .footer-link-button {
    font-size: 0.76rem;
    line-height: 1.3;
    overflow-wrap: anywhere;
  }

  .footer-meta {
    display: block;
    padding-top: 0.75rem;
    padding-bottom: 0.9rem;
    font-size: 0.75rem;
    line-height: 1.4;
  }

  .footer-meta span:last-child {
    display: none;
  }
}
</style>
