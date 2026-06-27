<script setup>
import AppLayout from '@/components/AppLayout.vue'
import HeroSection from '@/components/HeroSection.vue'
import Search from '@/components/Search.vue'
import Categories from '@/components/Categories.vue'
import Service from '@/components/Service.vue'
</script>


<template>
  <AppLayout>
    <main class="home-page">
      <HeroSection />
      <Search />
      <Categories />
      <Service />
    </main>
  </AppLayout>
</template>

<style scoped>
.home-page {
  display: grid;
  gap: 1.25rem;
  padding: 0 0 4rem;
}
</style>
