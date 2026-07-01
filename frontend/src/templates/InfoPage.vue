<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from '@/i18n'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()
const { language } = useI18n()

const isEnglish = computed(() => language.value === 'en')
const cardDescription = computed(() => (
  isEnglish.value
    ? 'This section is designed as a full part of the platform and follows the same CVHOLD interface style.'
    : 'Раздел оформлен как полноценная часть платформы и поддерживает единый стиль интерфейса CVHOLD.'
))

const pages = computed(() => (
  isEnglish.value
    ? {
      blog: {
        eyebrow: 'Blog',
        title: 'Useful materials about working in Europe',
        text: 'Vacancy roundups, resume tips, and interview preparation guides.',
        cards: ['How to prepare for work abroad', 'Which documents a candidate needs', 'How to improve your Match Score'],
      },
      about: {
        eyebrow: 'About the platform',
        title: 'CVHOLD is a platform for the European labour market',
        text: 'We connect candidates and employers through transparent applications, clear profiles, and convenient dashboards.',
        cards: ['50,000+ candidates', '15,000+ applications', '99% transparency'],
      },
      contacts: {
        eyebrow: 'Contacts',
        title: 'Get in touch with us',
        text: 'The CVHOLD team answers questions from both candidates and employers.',
        cards: ['support@cvhold.example', '+371 00 000 000', 'Riga, Latvia'],
      },
      faq: {
        eyebrow: 'FAQ',
        title: 'Frequently asked questions',
        text: 'Answers to common questions about registration, vacancies, applications, and dashboards.',
        cards: ['How do I create an account?', 'How do I apply?', 'How do I post a vacancy?'],
      },
      terms: {
        eyebrow: 'Terms',
        title: 'Platform terms of use',
        text: 'Core terms for candidates, employers, and data processing.',
        cards: ['User agreement', 'Privacy policy', 'Vacancy publishing rules'],
      },
    }
    : {
      blog: {
        eyebrow: 'Блог',
        title: 'Полезные материалы о работе в Европе',
        text: 'Подборки вакансий, советы по резюме и подготовке к интервью.',
        cards: ['Как подготовиться к работе за границей', 'Какие документы нужны кандидату', 'Как повысить Match Score'],
      },
      about: {
        eyebrow: 'О платформе',
        title: 'CVHOLD — платформа для рынка труда Европы',
        text: 'Мы соединяем кандидатов и работодателей через прозрачные отклики, профили и удобные кабинеты.',
        cards: ['50 000+ кандидатов', '15 000+ откликов', '99% прозрачности'],
      },
      contacts: {
        eyebrow: 'Контакты',
        title: 'Свяжитесь с нами',
        text: 'Команда CVHOLD отвечает на вопросы кандидатов и работодателей.',
        cards: ['support@cvhold.example', '+371 00 000 000', 'Riga, Latvia'],
      },
      faq: {
        eyebrow: 'FAQ',
        title: 'Часто задаваемые вопросы',
        text: 'Ответы на основные вопросы о регистрации, вакансиях, откликах и кабинетах.',
        cards: ['Как создать аккаунт?', 'Как откликнуться?', 'Как разместить вакансию?'],
      },
      terms: {
        eyebrow: 'Условия',
        title: 'Правила использования платформы',
        text: 'Основные положения для кандидатов, работодателей и обработки данных.',
        cards: ['Пользовательское соглашение', 'Политика конфиденциальности', 'Правила публикации вакансий'],
      },
    }
))

const page = computed(() => pages.value[route.meta.page] || pages.value.about)
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
