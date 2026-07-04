<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import LoginModal from '@/components/LoginModal.vue'
import RegisterModal from '@/components/RegisterModal.vue'
import SiteFooter from '@/components/SiteFooter.vue'

const route = useRoute()
const router = useRouter()
const activeModal = ref(null)
const authModalNotice = ref(null)
const isAuthModalOpen = computed(() => activeModal.value !== null)

const openLoginModal = (notice = null) => {
  authModalNotice.value = notice
  activeModal.value = 'login'
}

const openRegisterModal = (notice = null) => {
  authModalNotice.value = notice
  activeModal.value = 'register'
}

const closeAuthModal = () => {
  activeModal.value = null
  authModalNotice.value = null

  if (route.query.auth) {
    const { auth, ...query } = route.query
    router.replace({ path: route.path, query, hash: route.hash })
  }
}

const handleRegistered = (payload) => {
  closeAuthModal()
  openLoginModal({
    type: 'success',
    message: payload?.successMessage || '',
  })
}

watch(() => route.query.auth, (auth) => {
  if (auth === 'login') openLoginModal()
  if (auth === 'register') openRegisterModal()
}, { immediate: true })

watch(isAuthModalOpen, (isOpen) => {
  document.body.style.overflow = isOpen ? 'hidden' : ''
})

onBeforeUnmount(() => {
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="app-layout" :class="{ 'app-layout--blurred': isAuthModalOpen }">
    <Navbar @open-login="openLoginModal" @open-register="openRegisterModal" />
    <div class="app-layout__content">
      <slot />
    </div>
    <SiteFooter />
  </div>

  <LoginModal
    v-if="activeModal === 'login'"
    :notice="activeModal === 'login' ? authModalNotice : null"
    @close="closeAuthModal"
    @open-register="() => openRegisterModal()"
  />
  <RegisterModal
    v-if="activeModal === 'register'"
    :visible="true"
    :notice="activeModal === 'register' ? authModalNotice : null"
    @close="closeAuthModal"
    @open-login="() => openLoginModal()"
    @registered="handleRegistered"
  />
</template>

<style scoped>
.app-layout {
  min-height: 100%;
  display: flex;
  overflow: clip;
  flex-direction: column;
  background: transparent;
  transition: filter 0.2s ease, transform 0.2s ease;
}

.app-layout__content {
  flex: 1 0 auto;
}

.app-layout--blurred {
  filter: blur(0.25rem);
  transform: scale(0.995);
  pointer-events: none;
  user-select: none;
}

</style>
