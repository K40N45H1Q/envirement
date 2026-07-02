<script setup>
import { computed } from 'vue'
import CandidateDashboardPage from '@/templates/CandidateDashboardPage.vue'
import EmployerDashboardPage from '@/templates/EmployerDashboardPage.vue'
import { useAuth } from '@/stores/auth'

const { state } = useAuth()

const normalizedAccountType = computed(() => {
  if (state.user?.account_type === 'user') return 'candidate'
  return state.user?.account_type || ''
})

const dashboardComponent = computed(() => (
  ['employer', 'admin'].includes(normalizedAccountType.value)
    ? EmployerDashboardPage
    : CandidateDashboardPage
))
</script>

<template>
  <component :is="dashboardComponent" />
</template>
