<script setup>
import { computed } from 'vue'
import CandidateDashboardPage from '@/templates/CandidateDashboardPage.vue'
import EmployerDashboardPage from '@/templates/EmployerDashboardPage.vue'
import AdminPanel from '@/components/apanel/AdminPanel.vue'
import { useAuth } from '@/stores/auth'

const { state } = useAuth()

const normalizedAccountType = computed(() => {
  if (state.user?.account_type === 'user') return 'candidate'
  return state.user?.account_type || ''
})

const dashboardComponent = computed(() => {
  if (normalizedAccountType.value === 'admin') return AdminPanel
  if (normalizedAccountType.value === 'employer') return EmployerDashboardPage
  return CandidateDashboardPage
})
</script>

<template>
  <component :is="dashboardComponent" />
</template>
