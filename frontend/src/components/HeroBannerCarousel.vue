<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import industrialBanner from '@/assets/banners/jobs-banner-industrial.png'
import logisticsBanner from '@/assets/banners/jobs-banner-logistics.png'
import healthcareBanner from '@/assets/banners/jobs-banner-healthcare.png'

const slides = [
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
]

const activeIndex = ref(0)
let autoplayTimer = null

const activeSlide = computed(() => slides[activeIndex.value] ?? slides[0])

const showSlide = (index) => {
  activeIndex.value = index
}

const startAutoplay = () => {
  stopAutoplay()
  autoplayTimer = window.setInterval(() => {
    activeIndex.value = (activeIndex.value + 1) % slides.length
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

    <div class="hero-banner__dots" aria-label="Баннеры вакансий">
      <button
        v-for="(slide, index) in slides"
        :key="slide.id"
        type="button"
        class="hero-banner__dot"
        :class="{ 'hero-banner__dot--active': index === activeIndex }"
        :aria-label="`Показать баннер ${index + 1}`"
        @click="selectSlide(index)"
      ></button>
    </div>
  </div>
</template>

<style scoped>
.hero-banner {
  flex: 1 1 auto;
  width: 100%;
  position: relative;
  min-height: 15rem;
  height: 100%;
  overflow: hidden;
  border-radius: 1.25rem;
  background:
    radial-gradient(circle at top left, rgba(34, 197, 94, 0.22), transparent 45%),
    linear-gradient(180deg, rgba(9, 18, 16, 0.02), rgba(9, 18, 16, 0.16));
  box-shadow: inset 0 0 0 0.25rem rgba(31, 201, 127, 0.28);
}

.hero-banner__slide {
  position: relative;
  min-height: 15rem;
  height: 100%;
}

.hero-banner__image,
.hero-banner__overlay,
.hero-banner__content {
  position: absolute;
  inset: 0;
}

.hero-banner__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-banner__overlay {
  background:
    linear-gradient(90deg, rgba(9, 18, 16, 0.02) 0%, rgba(9, 18, 16, 0.08) 36%, rgba(9, 18, 16, 0.46) 100%),
    linear-gradient(180deg, rgba(9, 18, 16, 0) 0%, rgba(9, 18, 16, 0.18) 100%);
}

.hero-banner__content {
  left: auto;
  width: min(62%, 14rem);
  padding: 0;
  margin: auto 1.15rem 1.15rem auto;
  align-self: end;
  inset: auto 1.15rem 1.15rem auto;
}

.hero-banner__eyebrow {
  display: inline-flex;
  align-items: center;
  min-height: 1.85rem;
  padding: 0.1rem 0.8rem 0;
  border-radius: 999px;
  background: rgba(224, 245, 234, 0.72);
  color: var(--brand-strong);
  font-size: 0.68rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  box-shadow: 0 0.5rem 1rem rgba(9, 18, 16, 0.12);
}

.hero-banner__content h3 {
  margin: 0.5rem 0 0;
  font-size: 1.22rem;
  line-height: 1.12;
  color: white;
  text-wrap: balance;
  text-shadow: 0 0.35rem 1rem rgba(9, 18, 16, 0.42);
}

.hero-banner__content p {
  margin: 0.45rem 0 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.88rem;
  line-height: 1.38;
  text-shadow: 0 0.25rem 0.8rem rgba(9, 18, 16, 0.38);
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
    min-height: 17rem;
  }

  .hero-banner__content {
    width: calc(100% - 2.3rem);
    inset: auto 1.15rem 1.15rem 1.15rem;
  }
}
</style>
