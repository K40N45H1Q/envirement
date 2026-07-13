<script setup>
import { computed } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useI18n } from '@/i18n'

const { t } = useI18n()

const contactItems = computed(() => [
  {
    icon: 'fas fa-envelope',
    label: t('contactPage.emailLabel'),
    value: 'support@cvhold.com',
    action: t('contactPage.emailAction'),
  },
  {
    icon: 'fas fa-phone',
    label: t('contactPage.phoneLabel'),
    value: '+37125253030',
    action: t('contactPage.phoneAction'),
  },
  {
    icon: 'fas fa-location-dot',
    label: t('contactPage.locationLabel'),
    value: t('contactPage.locationValue'),
    href: null,
    action: t('contactPage.locationAction'),
  },
])
</script>

<template>
  <AppLayout>
    <main class="contacts-page">
      <section class="contacts-hero">
        <div class="contacts-hero__copy">
          <p class="contacts-eyebrow">{{ t('contactPage.eyebrow') }}</p>
          <h1>{{ t('contactPage.title') }}</h1>
          <p class="contacts-lead">{{ t('contactPage.description') }}</p>
        </div>

        <div class="contacts-hero__mark" aria-hidden="true">
          <i class="fas fa-headset"></i>
        </div>
      </section>

      <section class="contacts-grid" :aria-label="t('contactPage.contactsLabel')">
        <article v-for="item in contactItems" :key="item.label" class="contact-card">
          <div class="contact-card__icon">
            <i :class="item.icon"></i>
          </div>

          <div class="contact-card__content">
            <span>{{ item.label }}</span>
            <a v-if="item.href" :href="item.href">{{ item.value }}</a>
            <strong v-else>{{ item.value }}</strong>
            <small>{{ item.action }}</small>
          </div>
        </article>
      </section>

      <section class="support-note">
        <div class="support-note__icon">
          <i class="fas fa-circle-check"></i>
        </div>
        <div>
          <h2>{{ t('contactPage.noteTitle') }}</h2>
          <p>{{ t('contactPage.noteText') }}</p>
        </div>
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.contacts-page {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 1.5rem var(--shell-gutter) 4rem;
  display: grid;
  gap: 1.25rem;
}

.contacts-hero,
.contact-card,
.support-note {
  border: 0.0625rem solid var(--border-subtle);
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.contacts-hero {
  min-height: 17rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  padding: clamp(2rem, 5vw, 4rem);
  overflow: hidden;
  border-color: color-mix(in srgb, var(--brand-base) 24%, var(--border-subtle));
  border-radius: 1.5rem;
  background:
    radial-gradient(circle at 88% 15%, rgba(26, 177, 111, 0.2), transparent 28%),
    linear-gradient(135deg, #fff, color-mix(in srgb, var(--brand-soft) 38%, white));
}

.contacts-hero__copy {
  max-width: 46rem;
}

.contacts-eyebrow {
  margin: 0 0 0.75rem;
  color: var(--brand-strong);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  max-width: 15ch;
  color: var(--text-primary);
  font-size: clamp(2.2rem, 5vw, 4rem);
  line-height: 1.03;
}

.contacts-lead {
  max-width: 40rem;
  margin-top: 1rem;
  color: var(--text-muted);
  line-height: 1.7;
}

.contacts-hero__mark {
  width: clamp(7rem, 14vw, 10rem);
  height: clamp(7rem, 14vw, 10rem);
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 26%, transparent);
  border-radius: 50%;
  background: color-mix(in srgb, var(--brand-soft) 74%, white);
  color: var(--brand-strong);
  font-size: clamp(2.4rem, 5vw, 4rem);
}

.contacts-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.contact-card {
  min-width: 0;
  display: grid;
  grid-template-columns: 3.25rem minmax(0, 1fr);
  gap: 1rem;
  align-items: start;
  padding: 1.35rem;
  border-radius: 1.15rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.contact-card:hover {
  border-color: color-mix(in srgb, var(--brand-base) 35%, var(--border-subtle));
  background: color-mix(in srgb, var(--brand-soft) 24%, white);
  box-shadow: 0 0.9rem 1.8rem rgba(21, 149, 93, 0.1);
}

.contact-card__icon,
.support-note__icon {
  display: grid;
  place-items: center;
  color: var(--brand-strong);
  background: color-mix(in srgb, var(--brand-soft) 72%, white);
}

.contact-card__icon {
  width: 3.25rem;
  height: 3.25rem;
  border-radius: 1rem;
  font-size: 1.1rem;
}

.contact-card__content {
  min-width: 0;
  display: grid;
  gap: 0.35rem;
}

.contact-card__content > span {
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.contact-card a,
.contact-card strong {
  min-width: 0;
  color: var(--text-primary);
  font-size: clamp(1rem, 1.5vw, 1.15rem);
  font-weight: 800;
  overflow-wrap: anywhere;
  text-decoration: none;
}

.contact-card a:hover,
.contact-card a:focus-visible {
  color: var(--brand-strong);
}

.contact-card small {
  color: var(--text-muted);
  line-height: 1.45;
}

.support-note {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.35rem 1.5rem;
  border-color: color-mix(in srgb, var(--brand-base) 26%, var(--border-subtle));
  border-radius: 1.15rem;
  background: color-mix(in srgb, var(--brand-soft) 38%, white);
}

.support-note__icon {
  width: 2.75rem;
  height: 2.75rem;
  flex: 0 0 2.75rem;
  border-radius: 50%;
}

.support-note h2 {
  color: var(--text-primary);
  font-size: 1rem;
}

.support-note p {
  margin-top: 0.3rem;
  color: var(--text-muted);
  line-height: 1.55;
}

@media (max-width: 58rem) {
  .contacts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 40rem) {
  .contacts-page {
    padding-top: 1rem;
    padding-bottom: 2.5rem;
  }

  .contacts-hero {
    min-height: auto;
    padding: 1.5rem;
  }

  .contacts-hero__mark {
    display: none;
  }

  .contact-card {
    padding: 1rem;
  }

  .support-note {
    align-items: flex-start;
    padding: 1rem;
  }
}
</style>
