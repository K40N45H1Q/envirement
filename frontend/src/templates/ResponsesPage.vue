<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { deleteResponse, getResponses } from '@/api/jobs'

const responses = ref([])
const status = ref('')
const isLoading = ref(false)

const formatDate = (value) => {
  if (!value) return 'Дата не указана'
  return new Date(value).toLocaleDateString('ru-RU')
}

const loadResponses = async () => {
  isLoading.value = true
  status.value = ''

  try {
    const data = await getResponses()
    responses.value = Array.isArray(data) ? data : []
  } catch {
    status.value = 'Войдите как работодатель, чтобы увидеть отклики.'
  } finally {
    isLoading.value = false
  }
}

const remove = async (id) => {
  try {
    await deleteResponse(id)
    responses.value = responses.value.filter((item) => item.id !== id)
  } catch {
    status.value = 'Не удалось удалить отклик.'
  }
}

onMounted(loadResponses)
</script>

<template>
  <AppLayout>
    <main class="page">
      <section class="head">
        <p class="eyebrow">Отклики работодателя</p>
        <h1>Кандидаты</h1>
        <p>Здесь собраны отклики на ваши вакансии с быстрым переходом в диалог с кандидатом.</p>
      </section>

      <p v-if="status" class="notice">{{ status }}</p>
      <p v-if="isLoading" class="notice">Загрузка...</p>

      <section class="list">
        <article v-for="item in responses" :key="item.id" class="response-card">
          <div class="avatar">{{ (item.name || 'C')[0] }}{{ (item.surname || 'V')[0] }}</div>

          <div class="main">
            <h2>{{ item.name }} {{ item.surname }}</h2>
            <p>{{ item.job_title }} · {{ item.job_company }}</p>
            <span>{{ item.phone }} · {{ item.email }} · Подан {{ formatDate(item.created_at) }}</span>
            <p v-if="item.message" class="message">{{ item.message }}</p>
          </div>

          <div class="side">
            <strong>{{ item.job_location }}</strong>
            <span>{{ item.job_salary || 'Зарплата не указана' }}</span>
            <RouterLink :to="`/messages?application=${item.id}`">Написать</RouterLink>
            <button type="button" @click="remove(item.id)">Удалить</button>
          </div>
        </article>

        <p v-if="!isLoading && !responses.length" class="notice">
          Откликов пока нет.
        </p>
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
.response-card,
.notice {
  border-radius: 0.75rem;
  background: #fff;
  box-shadow: 0 0.5rem 2rem rgba(30, 35, 38, 0.06);
}

.head,
.notice {
  padding: 1.5rem;
}

.eyebrow {
  margin: 0 0 0.5rem;
  color: #19785a;
  font-weight: 700;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
}

.list {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
}

.response-card {
  display: grid;
  grid-template-columns: 4rem minmax(0, 1fr) auto;
  gap: 1rem;
  padding: 1.25rem;
  align-items: center;
}

.avatar {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #19785a;
  color: #fff;
  font-weight: 800;
}

.main {
  min-width: 0;
}

h2,
p {
  margin: 0;
}

.main p,
.main span {
  color: rgba(30, 35, 38, 0.62);
}

.message {
  margin-top: 0.5rem;
}

.side {
  display: grid;
  gap: 0.35rem;
  text-align: center;
}

.side strong {
  color: #19785a;
  font-size: 1.2rem;
}

.side a {
  color: #19785a;
  font-weight: 700;
  text-decoration: none;
}

.side button {
  border: none;
  background: transparent;
  color: #d32f2f;
  cursor: pointer;
}

@media (max-width: 48rem) {
  .response-card {
    grid-template-columns: 1fr;
  }

  .side {
    text-align: left;
  }
}
</style>
