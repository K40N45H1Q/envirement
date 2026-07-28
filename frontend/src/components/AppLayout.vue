<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import LoginModal from '@/components/LoginModal.vue'
import RegisterModal from '@/components/RegisterModal.vue'
import SiteFooter from '@/components/SiteFooter.vue'
import { completeEmailLinkAuth, getRegistrationOptions } from '@/api/auth'
import { useI18n } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { defaultRouteForAccount } from '@/utils/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuth()
const { t } = useI18n()
const activeModal = ref(null)
const authModalNotice = ref(null)
const recoveryPasswordMode = ref(false)
const betaRegistrationRequired = ref(false)
const registrationOptionsLoaded = ref(false)
const isAuthModalOpen = computed(() => activeModal.value !== null)
const registrationDisabled = computed(() => !registrationOptionsLoaded.value || betaRegistrationRequired.value)

const openLoginModal = (notice = null) => {
  authModalNotice.value = notice
  recoveryPasswordMode.value = notice?.mode === 'recovery-password'
  activeModal.value = 'login'
}

const openRegisterModal = (notice = null) => {
  if (registrationDisabled.value) {
    openLoginModal(notice)
    return
  }
  authModalNotice.value = notice
  recoveryPasswordMode.value = false
  activeModal.value = 'register'
}

const closeAuthModal = () => {
  activeModal.value = null
  authModalNotice.value = null
  recoveryPasswordMode.value = false

  if (route.query.auth) {
    const { auth, ...query } = route.query
    router.replace({ path: route.path, query, hash: route.hash })
  }
}

const handleRegistered = (payload) => {
  auth.setUser(payload?.user || null)
  closeAuthModal()
}

const parseSupabaseAuthHash = (hash) => {
  const params = new URLSearchParams((hash || '').replace(/^#/, ''))
  const accessToken = params.get('access_token')
  const refreshToken = params.get('refresh_token')

  if (!accessToken || !refreshToken) return null

  return {
    accessToken,
    refreshToken,
    expiresIn: params.get('expires_in'),
    type: params.get('type') || '',
  }
}

const handleSupabaseAuthHash = async () => {
  const payload = parseSupabaseAuthHash(route.hash)
  if (!payload) return

  await router.replace({ path: route.path, query: route.query, hash: '' })

  try {
    const result = await completeEmailLinkAuth(payload)
    auth.setUser(result.user)

    if (payload.type === 'recovery') {
      openLoginModal({
        type: 'success',
        mode: 'recovery-password',
        message: t('login.recoveryPasswordHint'),
      })
      return
    }

    closeAuthModal()
    router.push(defaultRouteForAccount(result.user?.account_type))
  } catch (error) {
    openLoginModal({
      type: 'error',
      message: t('login.authLinkFailed'),
    })
  }
}

watch(() => route.query.auth, (auth) => {
  if (auth === 'login') openLoginModal()
  if (auth === 'register') openRegisterModal()
}, { immediate: true })

watch(isAuthModalOpen, (isOpen) => {
  document.body.style.overflow = isOpen ? 'hidden' : ''
})

watch(() => route.hash, () => {
  handleSupabaseAuthHash()
})

onMounted(() => {
  getRegistrationOptions()
    .then((options) => {
      betaRegistrationRequired.value = Boolean(options?.beta_access_required)
    })
    .catch(() => {
      betaRegistrationRequired.value = false
    })
    .finally(() => {
      registrationOptionsLoaded.value = true
    })
  handleSupabaseAuthHash()
})

onBeforeUnmount(() => {
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="app-layout" :class="{ 'app-layout--blurred': isAuthModalOpen }">
    <Navbar
      :registration-disabled="registrationDisabled"
      @open-login="openLoginModal"
      @open-register="openRegisterModal"
    />
    <div class="app-layout__content">
      <slot />
    </div>
    <SiteFooter />
  </div>

  <LoginModal
    v-if="activeModal === 'login'"
    :notice="activeModal === 'login' ? authModalNotice : null"
    :recovery-password-mode="recoveryPasswordMode"
    :registration-disabled="registrationDisabled"
    @close="closeAuthModal"
    @open-register="() => openRegisterModal()"
  />
  <RegisterModal
    v-if="activeModal === 'register'"
    :visible="true"
    :notice="activeModal === 'register' ? authModalNotice : null"
    :beta-access-required="betaRegistrationRequired"
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
