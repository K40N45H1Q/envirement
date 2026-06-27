<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const query = ref('')
const location = ref('')

const syncFromRoute = () => {
  query.value = route.query.q || ''
  location.value = route.query.loc || ''
}

const submit = () => {
  const nextQuery = {}
  if (query.value.trim()) nextQuery.q = query.value.trim()
  if (location.value.trim()) nextQuery.loc = location.value.trim()
  router.push({ path: '/jobs', query: nextQuery })
}

onMounted(syncFromRoute)
watch(() => route.query, syncFromRoute)
</script>

<template>
  <section class="search-section">
    <form class="search-card" @submit.prevent="submit">
      <label class="field">
        <span>Кого ищем?</span>
        <div class="input-wrap">
          <i class="fas fa-magnifying-glass"></i>
          <input v-model="query" type="text" placeholder="Должность, навык или компания" />
        </div>
      </label>

      <label class="field">
        <span>Где?</span>
        <div class="input-wrap">
          <i class="fas fa-location-dot"></i>
          <input v-model="location" type="text" placeholder="Страна, город или удаленно" />
        </div>
      </label>

      <button type="submit" class="search-button">
        <i class="fas fa-search"></i>
        <span>Найти</span>
      </button>
    </form>
  </section>
</template>

<style scoped>
.search-section {
  width: 100%;
  max-width: 100rem;
  margin: 0 auto;
}

.search-card {
  width: 100%;
  margin: 0 auto;
  padding: 1rem;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) auto;
  gap: 0.875rem;
  align-items: end;
  border: 0.0625rem solid rgba(25, 120, 90, 0.14);
  border-radius: 0.75rem;
  background: #fff;
  box-shadow: 0 1.25rem 3rem rgba(30, 35, 38, 0.08);
}

.field {
  min-width: 0;
  display: grid;
  gap: 0.5rem;
  color: #1e2326;
  font-weight: 700;
}

.input-wrap {
  min-height: 3rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 1rem;
  border: 0.0625rem solid #e2e8f0;
  border-radius: 0.5rem;
  color: #19785a;
  background: #f8fafc;
}

.input-wrap input {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: #1e2326;
  font: inherit;
}

.input-wrap input::placeholder {
  color: rgba(30, 35, 38, 0.45);
}

.search-button {
  min-height: 3rem;
  padding: 0 1.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
  border-radius: 0.5rem;
  background: #19785a;
  color: #fff;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

@media (max-width: 48rem) {
  .search-section {
    padding: 0 1rem 2rem;
  }

  .search-card {
    grid-template-columns: 1fr;
  }
}
</style>
