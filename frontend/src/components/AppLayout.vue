<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/i18n'
import Navbar from '@/components/Navbar.vue'
import LoginModal from '@/components/LoginModal.vue'
import RegisterModal from '@/components/RegisterModal.vue'
import SiteFooter from '@/components/SiteFooter.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const activeModal = ref(null)
const isAuthModalOpen = computed(() => activeModal.value !== null)
const registrationNotice = ref(null)
let registrationNoticeTimer = null

const openLoginModal = () => {
  activeModal.value = 'login'
}

const openRegisterModal = () => {
  activeModal.value = 'register'
}

const closeAuthModal = () => {
  activeModal.value = null

  if (route.query.auth) {
    const { auth, ...query } = route.query
    router.replace({ path: route.path, query, hash: route.hash })
  }
}

const clearRegistrationNotice = () => {
  if (registrationNoticeTimer) {
    window.clearTimeout(registrationNoticeTimer)
    registrationNoticeTimer = null
  }
  registrationNotice.value = null
}

const showRegistrationNotice = (type, message) => {
  clearRegistrationNotice()
  registrationNotice.value = { type, message }
  registrationNoticeTimer = window.setTimeout(() => {
    registrationNotice.value = null
    registrationNoticeTimer = null
  }, 5000)
}

const handleRegistered = (payload) => {
  const isEmployer = payload?.accountType === 'employer'
  showRegistrationNotice(
    'success',
    isEmployer ? t('register.successEmployer') : t('register.successCandidate'),
  )
  closeAuthModal()

  if (!isEmployer) {
    openLoginModal()
  }
}

const handleRegisterError = (payload) => {
  showRegistrationNotice('error', payload?.message || t('register.createAccountFailed'))
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
  clearRegistrationNotice()
})
</script>

<template>
  <Transition name="notice-fade">
    <div
      v-if="registrationNotice"
      class="registration-notice"
      :class="registrationNotice.type === 'success' ? 'registration-notice--success' : 'registration-notice--error'"
      role="status"
      aria-live="polite"
    >
      <i :class="registrationNotice.type === 'success' ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-exclamation'"></i>
      <span>{{ registrationNotice.message }}</span>
      <button type="button" class="registration-notice__close" @click="clearRegistrationNotice">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  </Transition>

  <div class="app-layout" :class="{ 'app-layout--blurred': isAuthModalOpen }">
    <Navbar @open-login="openLoginModal" @open-register="openRegisterModal" />
    <div class="app-layout__content">
      <slot />
    </div>
    <SiteFooter />
  </div>

  <LoginModal
    v-if="activeModal === 'login'"
    @close="closeAuthModal"
    @open-register="openRegisterModal"
  />
  <RegisterModal
    v-if="activeModal === 'register'"
    :visible="true"
    @close="closeAuthModal"
    @open-login="openLoginModal"
    @registered="handleRegistered"
    @register-error="handleRegisterError"
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

.registration-notice {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 2200;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: min(30rem, calc(100vw - 2rem));
  padding: 0.95rem 1rem;
  border-radius: 1rem;
  box-shadow: var(--shadow-strong);
  border: 0.0625rem solid var(--border-subtle);
  background: var(--surface-primary);
}

.registration-notice--success {
  border-color: rgba(21, 149, 93, 0.22);
  background: color-mix(in srgb, var(--brand-soft) 38%, white);
  color: var(--brand-strong);
}

.registration-notice--error {
  border-color: rgba(220, 38, 38, 0.2);
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.registration-notice span {
  flex: 1;
  line-height: 1.45;
  font-weight: 600;
}

.registration-notice__close {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  padding: 0.25rem;
}

.notice-fade-enter-active,
.notice-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.notice-fade-enter-from,
.notice-fade-leave-to {
  opacity: 0;
  transform: translateY(-0.4rem);
}
</style>
