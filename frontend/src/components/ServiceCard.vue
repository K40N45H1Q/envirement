<script setup>
defineProps({
  eyebrow: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    default: '',
  },
  subtitle: {
    type: String,
    default: '',
  },
  headerClass: {
    type: String,
    default: '',
  },
  contentClass: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <section class="service-card">
    <div v-if="eyebrow || title || subtitle || $slots.header" class="service-card__header" :class="headerClass">
      <slot name="header">
        <p v-if="eyebrow" class="section-eyebrow section-eyebrow--muted">{{ eyebrow }}</p>
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="subtitle" class="service-card__subtitle">{{ subtitle }}</p>
      </slot>
    </div>

    <div class="service-card__content" :class="contentClass">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.service-card {
  display: grid;
  gap: 1.4rem;
  padding: 1.5rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.5rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 249, 0.98));
  box-shadow: var(--shadow-soft);
}

.service-card__header {
  display: grid;
  gap: 0.7rem;
  max-width: 44rem;
}

.section-eyebrow--muted {
  color: color-mix(in srgb, var(--text-muted) 78%, transparent);
  letter-spacing: 0.1em;
}

.service-card__content {
  display: grid;
  gap: 1rem;
}

h2,
p {
  margin: 0;
}

h2 {
  font-size: clamp(1.8rem, 3vw, 2.35rem);
  line-height: 1.1;
  color: var(--text-primary);
}

.service-card__subtitle {
  color: var(--text-muted);
  line-height: 1.65;
}
</style>
