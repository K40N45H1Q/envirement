<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { translate, useI18n } from '@/i18n'

const route = useRoute()
const { language } = useI18n()

const page = computed(() => {
  const pages = translate('infoPage', {}, language.value)
  return pages[route.meta.page] || pages.about
})

const cardDescription = computed(() => translate('infoPageCardDescription', {}, language.value))
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="head">
        <p class="eyebrow">{{ page.eyebrow }}</p>
        <h1>{{ page.title }}</h1>
        <p>{{ page.text }}</p>
      </section>

      <section class="cards">
        <article v-for="card in page.cards" :key="card">
          <i class="fas fa-check-circle"></i>
          <h2>{{ card }}</h2>
          <p>{{ cardDescription }}</p>
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

.head,
.cards article {
  border-radius: 0.75rem;
  background: #fff;
  box-shadow: 0 0.5rem 2rem rgba(30, 35, 38, 0.06);
}

.head {
  padding: 2rem;
}

.eyebrow {
  color: #19785a;
  font-weight: 700;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
}

.head p,
.cards p {
  color: rgba(30, 35, 38, 0.66);
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.cards article {
  padding: 1.25rem;
}

.cards i {
  color: #19785a;
  font-size: 1.5rem;
}

@media (max-width: 56rem) {
  .cards {
    grid-template-columns: 1fr;
  }
}
</style>
