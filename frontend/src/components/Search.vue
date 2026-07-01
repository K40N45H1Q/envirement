<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/i18n'
import BaseDropdown from '@/components/BaseDropdown.vue'
import { useJobsStore } from '@/stores/jobs'

const route = useRoute()
const router = useRouter()
const jobsStore = useJobsStore()
const { t } = useI18n()

const query = ref('')
const location = ref('')
const category = ref('all')

const categoryOptions = computed(() => jobsStore.categoryConfigs.map((item) => ({
  value: item.id,
  label: item.label,
  iconClass: item.icon,
})))

const syncFromRoute = () => {
  query.value = typeof route.query.q === 'string' ? route.query.q : ''
  location.value = typeof route.query.loc === 'string' ? route.query.loc : ''
  category.value = typeof route.query.category === 'string' ? route.query.category : 'all'
}

const submit = () => {
  const nextQuery = {}
  if (query.value.trim()) nextQuery.q = query.value.trim()
  if (location.value.trim()) nextQuery.loc = location.value.trim()
  if (category.value !== 'all') nextQuery.category = category.value
  router.push({ path: '/jobs', query: nextQuery })
}

onMounted(syncFromRoute)
watch(() => route.query, syncFromRoute)
</script>

<template>
  <section class="search-frame">
    <div class="search-shell surface-card">
      <form class="search-grid" @submit.prevent="submit">
        <label>
          <span>{{ t('search.lookingFor') }}</span>
          <div class="input-wrap">
            <input v-model="query" type="text" :placeholder="t('search.lookingPlaceholder')" />
            <i class="fas fa-magnifying-glass"></i>
          </div>
        </label>

        <label>
          <span>{{ t('search.where') }}</span>
          <div class="input-wrap">
            <input v-model="location" type="text" :placeholder="t('search.wherePlaceholder')" />
            <i class="fas fa-location-dot"></i>
          </div>
        </label>

        <label>
          <span>{{ t('search.category') }}</span>
          <BaseDropdown
            v-model="category"
            :aria-label="t('search.category')"
            class="search-dropdown"
            :options="categoryOptions"
            full-width
            :show-selected-hint="false"
          />
        </label>

        <button type="submit" class="btn-primary search-button">
          {{ t('search.submit') }}
        </button>
      </form>
    </div>
  </section>
</template>

<style scoped>
.search-frame {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 0 var(--shell-gutter);
}

.search-shell {
  padding: 1.15rem;
  border-radius: 1.5rem;
}

.search-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr) minmax(0, 1fr) auto;
  gap: 0.85rem;
  align-items: end;
}

label {
  display: grid;
  gap: 0.45rem;
  color: var(--text-primary);
  font-weight: 700;
}

.input-wrap {
  position: relative;
}

.input-wrap input {
  width: 100%;
  min-height: 3.3rem;
  padding: 0.9rem 2.8rem 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font: inherit;
}

.input-wrap i {
  position: absolute;
  top: 50%;
  right: 1rem;
  transform: translateY(-50%);
  color: var(--brand-strong);
  pointer-events: none;
}

.search-dropdown {
  width: 100%;
}

.search-button {
  min-width: 11.5rem;
}

@media (max-width: 56rem) {
  .search-grid {
    grid-template-columns: 1fr;
  }
}
</style>
