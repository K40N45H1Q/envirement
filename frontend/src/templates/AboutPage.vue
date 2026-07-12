<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { translate, useI18n } from '@/i18n'

const { language } = useI18n()
const copy = computed(() => translate('aboutPage', {}, language.value))
</script>

<template>
  <AppLayout>
    <main class="about-page">
      <section class="hero-shell">
        <div class="hero-copy">
          <p class="eyebrow">{{ copy.eyebrow }}</p>
          <h1 class="hero-title">
            <span>{{ copy.titleLead }}</span>
            <em>{{ copy.titleAccent }}</em>
          </h1>
          <p class="hero-subtitle">{{ copy.subtitle }}</p>

          <div class="hero-actions">
            <RouterLink to="/jobs" class="btn-primary">{{ copy.primaryCta }}</RouterLink>
            <RouterLink to="/employers" class="btn-secondary">{{ copy.secondaryCta }}</RouterLink>
          </div>

          <div class="hero-pills">
            <span v-for="pill in copy.pills" :key="pill" class="hero-pill">{{ pill }}</span>
          </div>
        </div>

        <aside class="hero-aside">
          <div class="signal-card signal-card--main">
            <span class="signal-kicker">CVHOLD</span>
            <strong>Match Score</strong>
            <p>{{ copy.signalLead }}</p>
          </div>

          <div class="signal-grid">
            <article v-for="note in copy.manifestoNotes" :key="note" class="signal-card">
              <i class="fas fa-check"></i>
              <span>{{ note }}</span>
            </article>
          </div>
        </aside>
      </section>

      <section class="manifesto-shell">
        <div class="section-head">
          <p class="eyebrow">{{ copy.manifestoEyebrow }}</p>
          <h2>{{ copy.manifestoTitle }}</h2>
        </div>

        <div class="manifesto-layout">
          <div class="manifesto-body">
            <p v-for="paragraph in copy.manifestoBody" :key="paragraph">{{ paragraph }}</p>
          </div>

          <div class="manifesto-panel">
            <div class="manifesto-panel__line"></div>
            <p>{{ copy.manifestoPanel }}</p>
          </div>
        </div>
      </section>

      <section class="principles-shell">
        <div class="section-head">
          <p class="eyebrow">{{ copy.principlesEyebrow }}</p>
          <h2>{{ copy.principlesTitle }}</h2>
        </div>

        <div class="principles-grid">
          <article v-for="item in copy.principles" :key="item.mark" class="principle-card">
            <span class="principle-mark">{{ item.mark }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.body }}</p>
          </article>
        </div>
      </section>

      <section class="candidate-shell">
        <div class="section-head section-head--light">
          <p class="eyebrow">{{ copy.candidateEyebrow }}</p>
          <h2>{{ copy.candidateTitle }}</h2>
          <p class="section-subtitle">{{ copy.candidateSubtitle }}</p>
        </div>

        <div class="candidate-grid">
          <article v-for="item in copy.candidatePoints" :key="item.title" class="candidate-card">
            <div class="candidate-card__icon">
              <i class="fas fa-arrow-right"></i>
            </div>
            <div class="candidate-card__body">
              <h3>{{ item.title }}</h3>
              <p>{{ item.body }}</p>
            </div>
          </article>
        </div>
      </section>

      <section class="contact-shell">
        <div class="section-head">
          <p class="eyebrow">{{ copy.contactEyebrow }}</p>
          <h2>{{ copy.contactTitle }}</h2>
          <p class="section-subtitle">{{ copy.contactSubtitle }}</p>
        </div>

        <div class="contact-grid">
          <a
            v-for="item in copy.contacts"
            :key="item.label"
            :href="item.href"
            class="contact-card"
            target="_blank"
            rel="noreferrer"
          >
            <span class="contact-card__label">{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </a>
        </div>
      </section>
    </main>
  </AppLayout>
</template>

<style scoped>
.about-page {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 1.5rem var(--shell-gutter) 4rem;
  display: grid;
  gap: 1.25rem;
}

.hero-shell,
.manifesto-shell,
.principles-shell,
.candidate-shell,
.founder-shell,
.contact-shell {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 2rem;
  box-shadow: var(--shadow-soft);
  overflow: hidden;
}

.hero-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(20rem, 24rem);
  gap: 1.25rem;
  padding: 1.75rem;
  align-items: start;
  background:
    radial-gradient(circle at top right, rgba(20, 184, 87, 0.14), transparent 22%),
    radial-gradient(circle at bottom left, rgba(37, 167, 108, 0.08), transparent 24%),
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 94%, white), var(--surface-primary));
}

.hero-copy {
  max-width: 48rem;
}

.hero-copy,
.hero-aside,
.manifesto-layout,
.founder-shell {
  min-width: 0;
}

.eyebrow,
.signal-kicker,
.principle-mark,
.contact-card__label {
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.eyebrow,
.signal-kicker,
.principle-mark {
  color: var(--brand-strong);
}

.hero-title,
h2,
h3 {
  margin: 0;
  color: var(--text-primary);
}

.hero-title {
  display: grid;
  gap: 0.3rem;
  font-size: clamp(2.5rem, 4.8vw, 4.6rem);
  line-height: 0.94;
  letter-spacing: -0.06em;
}

.hero-title em {
  font-style: normal;
  color: var(--brand-strong);
}

.hero-subtitle,
.section-subtitle,
.manifesto-body p,
.manifesto-panel p,
.principle-card p,
.candidate-card p,
.founder-copy p,
.signal-card p {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.72;
}

.hero-subtitle {
  margin-top: 1rem;
  max-width: 38rem;
  font-size: 1.02rem;
}

.hero-actions,
.hero-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.875rem;
}

.hero-actions {
  margin-top: 1.5rem;
}

.hero-pills {
  margin-top: 1.2rem;
}

.hero-pill {
  padding: 0.55rem 0.9rem;
  border-radius: 999px;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-strong) 20%, white);
  background: color-mix(in srgb, var(--brand-soft) 40%, white);
  color: var(--brand-strong);
  font-size: 0.82rem;
  font-weight: 700;
}

.hero-aside {
  display: grid;
  gap: 0.9rem;
  align-content: start;
}

.signal-card,
.principle-card,
.candidate-card,
.contact-card,
.founder-badge,
.manifesto-panel {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.35rem;
}

.signal-card {
  padding: 1.15rem;
  background: color-mix(in srgb, var(--surface-secondary) 94%, white);
}

.signal-card--main {
  display: grid;
  gap: 0.35rem;
  padding: 1.1rem 1.15rem;
  background:
    linear-gradient(135deg, rgba(25, 120, 90, 0.08), rgba(255, 255, 255, 0.96)),
    var(--surface-secondary);
}

.signal-card strong {
  font-size: 1.35rem;
  color: var(--text-primary);
}

.signal-grid {
  display: grid;
  gap: 0.9rem;
}

.signal-grid .signal-card {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.8rem;
  align-items: start;
}

.signal-grid i {
  width: 2rem;
  height: 2rem;
  border-radius: 0.8rem;
  display: grid;
  place-items: center;
  background: color-mix(in srgb, var(--brand-soft) 38%, white);
  color: var(--brand-strong);
}

.manifesto-shell,
.principles-shell,
.founder-shell,
.contact-shell {
  padding: 1.65rem;
  background:
    radial-gradient(circle at top right, rgba(20, 184, 87, 0.08), transparent 20%),
    linear-gradient(180deg, color-mix(in srgb, var(--surface-primary) 92%, white), white);
}

.candidate-shell {
  padding: 1.65rem;
  background:
    radial-gradient(circle at top left, rgba(255, 255, 255, 0.12), transparent 24%),
    linear-gradient(135deg, #172722, #19785a 70%, #25a76c);
}

.section-head {
  display: grid;
  gap: 0.7rem;
  margin-bottom: 1.4rem;
}

.section-head--light h2,
.section-head--light .section-subtitle {
  color: white;
}

h2 {
  font-size: clamp(1.85rem, 3.5vw, 2.9rem);
  line-height: 0.98;
  letter-spacing: -0.05em;
}

.section-subtitle {
  max-width: 44rem;
}

.manifesto-layout,
.founder-shell {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(18rem, 0.8fr);
  gap: 1.2rem;
}

.manifesto-body {
  display: grid;
  gap: 0.95rem;
}

.manifesto-panel {
  padding: 1.25rem;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--surface-secondary) 94%, white), color-mix(in srgb, var(--brand-soft) 22%, white));
  display: grid;
  align-content: center;
  gap: 0.9rem;
}

.manifesto-panel__line {
  width: 4rem;
  height: 0.25rem;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--brand-strong), #6bd1a0);
}

.principles-grid,
.candidate-grid,
.contact-grid {
  display: grid;
  gap: 1rem;
}

.principles-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.principle-card {
  min-height: 14rem;
  padding: 1.35rem;
  background: color-mix(in srgb, var(--surface-secondary) 94%, white);
  display: grid;
  align-content: start;
  gap: 0.9rem;
}

.principle-mark {
  display: inline-flex;
  width: fit-content;
  padding: 0.35rem 0.55rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--brand-soft) 36%, white);
}

.principle-card h3,
.candidate-card h3 {
  font-size: 1.2rem;
  line-height: 1.2;
}

.candidate-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.candidate-card {
  padding: 1.05rem;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.14);
}

.candidate-card__icon {
  width: 2.45rem;
  height: 2.45rem;
  border-radius: 0.9rem;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.14);
  color: #d7ffec;
}

.candidate-card__body {
  display: grid;
  gap: 0.4rem;
}

.candidate-card h3,
.candidate-card p {
  margin: 0;
}

.candidate-card h3 {
  color: white;
}

.candidate-card p {
  color: rgba(255, 255, 255, 0.72);
}

.founder-badge {
  padding: 1.35rem;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--surface-secondary) 94%, white), color-mix(in srgb, var(--brand-soft) 20%, white));
  display: grid;
  justify-items: start;
  align-content: start;
  gap: 0.9rem;
}

.founder-avatar {
  width: 5.5rem;
  height: 5.5rem;
  border-radius: 1.4rem;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #19785a, #114f39);
  color: white;
  font-size: 2rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  box-shadow: 0 1rem 2rem rgba(25, 120, 90, 0.18);
}

.founder-role {
  color: var(--text-muted);
  font-weight: 700;
}

.founder-copy {
  display: grid;
  gap: 0.9rem;
}

.contact-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.contact-card {
  padding: 1.15rem;
  background: color-mix(in srgb, var(--surface-secondary) 94%, white);
  text-decoration: none;
  display: grid;
  gap: 0.35rem;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.contact-card strong {
  color: var(--text-primary);
  word-break: break-word;
}

.contact-card__label {
  color: var(--brand-strong);
}

.contact-card:hover {
  transform: translateY(-0.125rem);
  border-color: color-mix(in srgb, var(--brand-strong) 34%, white);
  box-shadow: 0 1rem 2rem rgba(21, 32, 27, 0.08);
}

@media (max-width: 72rem) {
  .hero-shell,
  .manifesto-layout,
  .founder-shell,
  .principles-grid,
  .candidate-grid,
  .contact-grid {
    grid-template-columns: 1fr;
  }

  .hero-copy,
  .hero-subtitle {
    max-width: none;
  }
}

@media (max-width: 48rem) {
  .about-page {
    padding-top: 1rem;
    padding-bottom: 3rem;
    gap: 1rem;
  }

  .hero-shell,
  .manifesto-shell,
  .principles-shell,
  .candidate-shell,
  .founder-shell,
  .contact-shell {
    padding: 1.25rem;
    border-radius: 1.5rem;
  }

  .hero-actions {
    display: grid;
    grid-template-columns: 1fr;
  }

  .hero-actions :deep(a) {
    width: 100%;
  }
}
</style>
