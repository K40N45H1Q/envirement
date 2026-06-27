<script setup>
import { onBeforeUnmount, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import MessagesPanel from '@/components/messages/MessagesPanel.vue'
import { useMessagingStore } from '@/stores/messaging'

const route = useRoute()
const router = useRouter()
const messaging = useMessagingStore()

const syncQuery = (applicationId) => {
  router.replace({
    path: '/messages',
    query: applicationId ? { application: String(applicationId) } : {},
  })
}

const loadConversations = async () => {
  await messaging.loadConversations(route.query.application)

  if (messaging.activeApplicationId) {
    syncQuery(messaging.activeApplicationId)
  }
}

watch(() => route.query.application, async (value) => {
  const applicationId = Number(value)
  if (!applicationId || applicationId === messaging.activeApplicationId) return

  const exists = messaging.conversations.some((item) => item.application_id === applicationId)
  if (exists) {
    await messaging.openConversation(applicationId)
  }
})

onMounted(async () => {
  await loadConversations()
  messaging.startRealtime()
})

onBeforeUnmount(() => {
  messaging.stopRealtime()
})
</script>

<template>
  <AppLayout>
    <main class="page">
      <MessagesPanel @open="syncQuery" />
    </main>
  </AppLayout>
</template>

<style scoped>
.page {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 2rem var(--shell-gutter) 4rem;
}
</style>
