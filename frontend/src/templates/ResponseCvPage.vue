<script setup>
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import Profile from '@/components/Profile.vue'

const route = useRoute()
</script>

<template>
  <AppLayout>
    <Profile :application-id="route.params.id" />
  </AppLayout>
</template>
