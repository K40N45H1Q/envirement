<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from '@/i18n'

import industrialBanner from '@/assets/banners/jobs-banner-industrial.png'
import logisticsBanner from '@/assets/banners/jobs-banner-logistics.png'
import healthcareBanner from '@/assets/banners/jobs-banner-healthcare.png'

const { language } = useI18n()

const isEnglish = computed(() => language.value === 'en')
const copy = computed(() => (
  isEnglish.value
    ? {
      slides: [
        {
          id: 'industrial',
          image: industrialBanner,
          eyebrow: 'Industry and construction',
          title: 'Strong vacancies for people who get things done',
          text: 'Verified employers, clear terms, and a faster way to apply.',
        },
        {
          id: 'logistics',
          image: logisticsBanner,
          eyebrow: 'Logistics and warehouses',
          title: 'Jobs where speed and reliability matter',
          text: 'Filter opportunities by country, salary, and employment format.',
        },
        {
          id: 'healthcare',
          image: healthcareBanner,
          eyebrow: 'Healthcare and care',
          title: 'European jobs with a human-first approach',
          text: 'From clinics to private centres: everything in one search without extra noise.',
        },
      ],
      dotsLabel: 'Job banners',
      showBanner: 'Show banner {index}',
    }
    : {
      slides: [
        {
          id: 'industrial',
          image: industrialBanner,
          eyebrow: 'Производство и стройка',
          title: 'Сильные вакансии для людей дела',
          text: 'Проверенные работодатели, понятные условия и быстрый отклик.',
        },
        {
          id: 'logistics',
          image: logisticsBanner,
          eyebrow: 'Логистика и склады',
          title: 'Работа, где ценят скорость и надежность',
          text: 'Подбирайте предложения по странам, зарплате и формату занятости.',
        },
        {
          id: 'healthcare',
          image: healthcareBanner,
          eyebrow: 'Медицина и care',
          title: 'Европейские вакансии с человеческим подходом',
          text: 'От клиник до частных центров: все в одном поиске без лишнего шума.',
        },
      ],
      dotsLabel: 'Баннеры вакансий',
      showBanner: 'Показать баннер {index}',
    }
))

const slides = computed(() => copy.value.slides)
const activeIndex = ref(0)
let autoplayTimer = null

const activeSlide = computed(() => slides.value[activeIndex.value] ?? slides.value[0])
const interpolate = (template, params = {}) => String(template).replace(/\{(\w+)\}/g, (_, key) => String(params[key] ?? ''))

const showSlide = (index) => {
  activeIndex.value = index
}

const startAutoplay = () => {
  stopAutoplay()
  autoplayTimer = window.setInterval(() => {
    activeIndex.value = (activeIndex.value + 1) % slides.value.length
  }, 5000)
}

const stopAutoplay = () => {
  if (autoplayTimer) {
    window.clearInterval(autoplayTimer)
    autoplayTimer = null
  }
}

const selectSlide = (index) => {
  showSlide(index)
  startAutoplay()
}

onMounted(() => {
  startAutoplay()
})

onBeforeUnmount(() => {
  stopAutoplay()
})
</script>

<template>
  <div class="hero-banner" @mouseenter="stopAutoplay" @mouseleave="startAutoplay">
    <transition name="hero-banner-fade" mode="out-in">
      <article :key="activeSlide.id" class="hero-banner__slide">
        <img :src="activeSlide.image" :alt="activeSlide.title" class="hero-banner__image" />
        <div class="hero-banner__overlay"></div>
        <div class="hero-banner__content">
          <span class="hero-banner__eyebrow">{{ activeSlide.eyebrow }}</span>
          <h3>{{ activeSlide.title }}</h3>
          <p>{{ activeSlide.text }}</p>
        </div>
      </article>
    </transition>

    <div class="hero-banner__dots" :aria-label="copy.dotsLabel">
      <button
        v-for="(slide, index) in slides"
        :key="slide.id"
        type="button"
        class="hero-banner__dot"
        :class="{ 'hero-banner__dot--active': index === activeIndex }"
        :aria-label="interpolate(copy.showBanner, { index: index + 1 })"
        @click="selectSlide(index)"
      ></button>
    </div>
  </div>
</template>

<style scoped>
.hero-banner {
  width: 100%;
  position: relative;
  height: clamp(15rem, 28vw, 18.5rem);
  overflow: hidden;
  border-radius: 1.25rem;
  background: #111;
  box-shadow: inset 0 0 0 0.25rem rgba(31, 201, 127, 0.28);
}

.hero-banner__slide {
  position: relative;
  height: 100%;
  overflow: hidden;
}

.hero-banner__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-banner__overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      90deg,
      rgba(9, 18, 16, 0.02) 0%,
      rgba(9, 18, 16, 0.12) 34%,
      rgba(9, 18, 16, 0.58) 72%,
      rgba(9, 18, 16, 0.76) 100%
    ),
    linear-gradient(
      180deg,
      rgba(9, 18, 16, 0.02) 0%,
      rgba(9, 18, 16, 0.18) 100%
    );
}

.hero-banner__content {
  position: relative;
  z-index: 1;
  width: min(48%, 18rem);
  height: 100%;
  margin-left: auto;
  padding: 2.15rem 1.35rem 1.65rem 0.75rem;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  gap: 0.55rem;
  text-align: right;
}

.hero-banner__eyebrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  align-self: flex-end;
  max-width: 13.5rem;
  min-height: 1.75rem;
  padding: 0.35rem 0.85rem 0.3rem;
  border-radius: 999px;
  background: rgba(224, 245, 234, 0.86);
  color: var(--brand-strong);
  font-size: 0.62rem;
  font-weight: 900;
  line-height: 1.15;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  box-shadow: 0 0.5rem 1rem rgba(9, 18, 16, 0.16);
}

.hero-banner__content h3 {
  max-width: 16rem;
  margin: 0;
  color: white;
  font-size: clamp(1.12rem, 2.2vw, 1.42rem);
  font-weight: 900;
  line-height: 1.12;
  text-wrap: balance;
  text-shadow: 0 0.35rem 1rem rgba(9, 18, 16, 0.52);
}

.hero-banner__content p {
  max-width: 15.5rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.38;
  text-shadow: 0 0.25rem 0.8rem rgba(9, 18, 16, 0.45);
}

.hero-banner__dots {
  position: absolute;
  left: 1rem;
  bottom: 1rem;
  z-index: 2;
  display: inline-flex;
  gap: 0.45rem;
  padding: 0.45rem 0.55rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(0.85rem);
  box-shadow: 0 0.75rem 1.5rem rgba(9, 18, 16, 0.14);
}

.hero-banner__dot {
  width: 0.62rem;
  height: 0.62rem;
  border: none;
  border-radius: 50%;
  background: rgba(22, 163, 74, 0.25);
  cursor: pointer;
  transition: transform 0.25s ease, background 0.25s ease;
}

.hero-banner__dot:hover,
.hero-banner__dot--active {
  background: var(--brand-strong);
  transform: scale(1.15);
}

.hero-banner-fade-enter-active,
.hero-banner-fade-leave-active {
  transition: opacity 0.45s ease;
}

.hero-banner-fade-enter-from,
.hero-banner-fade-leave-to {
  opacity: 0;
}

@media (max-width: 640px) {
  .hero-banner {
    height: 17rem;
  }

  .hero-banner__slide {
    height: 100%;
  }

  .hero-banner__overlay {
    background:
      linear-gradient(
        180deg,
        rgba(9, 18, 16, 0.05) 0%,
        rgba(9, 18, 16, 0.28) 42%,
        rgba(9, 18, 16, 0.82) 100%
      );
  }

  .hero-banner__content {
    width: 100%;
    height: 100%;
    margin-left: 0;
    padding: 1.25rem 1.15rem 3.2rem;
    align-items: center;
    justify-content: center;
    text-align: center;
  }

  .hero-banner__eyebrow {
    align-self: center;
    max-width: max-content;
  }
  
  .hero-banner__content h3,
  .hero-banner__content p {
    max-width: 20rem;
  }

  .hero-banner__dots {
    left: 50%;
    transform: translateX(-50%);
  }
}
</style>
