<template>
  <Teleport to="body">
    <Transition name="modal-fade" appear>
      <div class="login-modal" role="dialog" aria-modal="true" aria-labelledby="login-title">
        <form class="login-card" @submit.prevent="submit">
          <button type="button" class="modal-close" :aria-label="t('common.closeLogin')" @click="close">
            <i class="fa-solid fa-xmark"></i>
          </button>

          <h1 id="login-title" class="title">{{ isResetMode ? t('login.forgotTitle') : t('login.title') }}</h1>

          <Transition name="expand">
            <div v-if="feedbackMessage" class="api-error-msg" :class="{ 'api-error-msg--success': feedbackType === 'success' }">
              <i :class="feedbackType === 'success' ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-exclamation'"></i>
              <span>{{ feedbackMessage }}</span>
            </div>
          </Transition>

          <p v-if="isResetMode" class="hint">{{ t('login.forgotHint') }}</p>

          <input
            v-model.trim="email"
            type="email"
            placeholder="Email"
            class="input"
            :class="{ error: feedbackType === 'error' && feedbackMessage }"
            @input="clearFeedback"
          />

          <template v-if="!isResetMode">
            <div class="password">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="t('login.password')"
                class="input"
                :class="{ error: feedbackType === 'error' && feedbackMessage }"
                @input="clearFeedback"
              />

              <button
                type="button"
                class="toggle"
                :aria-label="t('common.showPassword')"
                @click="showPassword = !showPassword"
              >
                <i :class="showPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'"></i>
              </button>
            </div>
          </template>

          <template v-else-if="resetRequested">
            <input
              v-model.trim="resetCode"
              type="text"
              inputmode="numeric"
              maxlength="6"
              :placeholder="t('login.resetCode')"
              class="input input-center"
              :class="{ error: feedbackType === 'error' && feedbackMessage }"
              @input="clearFeedback"
            />

            <div class="password">
              <input
                v-model="newPassword"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="t('login.newPassword')"
                class="input"
                :class="{ error: (feedbackType === 'error' && feedbackMessage) || (isResetPasswordTouched && !isPasswordStrong(newPassword)) }"
                @blur="isResetPasswordTouched = true"
                @input="clearFeedback"
              />

              <button
                type="button"
                class="toggle"
                :aria-label="t('common.showPassword')"
                @click="showPassword = !showPassword"
              >
                <i :class="showPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'"></i>
              </button>
            </div>

            <Transition name="expand">
              <div v-show="showResetRequirements" class="requirements">
                <div class="req-item" :class="{ valid: resetChecks.length }">
                  <i class="fa-solid" :class="resetChecks.length ? 'fa-check' : 'fa-xmark'"></i>
                  <span>{{ t('register.reqLength') }}</span>
                </div>
                <div class="req-item" :class="{ valid: resetChecks.uppercase }">
                  <i class="fa-solid" :class="resetChecks.uppercase ? 'fa-check' : 'fa-xmark'"></i>
                  <span>{{ t('register.reqUppercase') }}</span>
                </div>
                <div class="req-item" :class="{ valid: resetChecks.lowercase }">
                  <i class="fa-solid" :class="resetChecks.lowercase ? 'fa-check' : 'fa-xmark'"></i>
                  <span>{{ t('register.reqLowercase') }}</span>
                </div>
                <div class="req-item" :class="{ valid: resetChecks.number }">
                  <i class="fa-solid" :class="resetChecks.number ? 'fa-check' : 'fa-xmark'"></i>
                  <span>{{ t('register.reqNumber') }}</span>
                </div>
                <div class="req-item" :class="{ valid: resetChecks.special }">
                  <i class="fa-solid" :class="resetChecks.special ? 'fa-check' : 'fa-xmark'"></i>
                  <span>{{ t('register.reqSpecial') }}</span>
                </div>
              </div>
            </Transition>

            <div class="password">
              <input
                v-model="confirmNewPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                :placeholder="t('login.confirmNewPassword')"
                class="input"
                :class="{ error: (feedbackType === 'error' && feedbackMessage) || (isResetConfirmTouched && newPassword !== confirmNewPassword && confirmNewPassword) }"
                @blur="isResetConfirmTouched = true"
                @input="clearFeedback"
              />

              <button
                type="button"
                class="toggle"
                :aria-label="t('common.showPassword')"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <i :class="showConfirmPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'"></i>
              </button>
            </div>
          </template>

          <button type="submit" class="submit-btn btn-primary" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner"></span>
            <span v-else>{{ submitLabel }}</span>
          </button>

          <template v-if="isResetMode">
            <button v-if="resetRequested" type="button" class="link" :disabled="isSubmitting" @click="requestResetCode">
              {{ t('login.resendResetCode') }}
            </button>
            <button type="button" class="link" @click="switchToLogin">
              {{ t('login.backToLogin') }}
            </button>
          </template>

          <template v-else>
            <button type="button" class="link" @click="switchToReset">
              <span class="link-accent">{{ t('login.forgotPassword') }}</span>
            </button>
            <button type="button" class="link" @click="openRegister">
              {{ t('login.noAccount') }} <span class="link-accent">{{ t('login.registerNow') }}</span>
            </button>
          </template>
        </form>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/i18n'
import { confirmPasswordReset, getMe, login, requestPasswordResetCode } from '@/api/auth'
import { useAuth } from '@/stores/auth'
import { defaultRouteForAccount } from '@/utils/auth'

const emit = defineEmits(['close', 'open-register'])
const props = defineProps({
  notice: {
    type: Object,
    default: null,
  },
})

const route = useRoute()
const router = useRouter()
const { setUser } = useAuth()
const { language, t } = useI18n()

const email = ref('')
const password = ref('')
const resetCode = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isResetPasswordTouched = ref(false)
const isResetConfirmTouched = ref(false)
const isSubmitting = ref(false)
const feedbackMessage = ref('')
const feedbackType = ref('error')
const mode = ref('login')
const resetRequested = ref(false)

const isResetMode = computed(() => mode.value === 'reset')
const submitLabel = computed(() => {
  if (!isResetMode.value) return t('common.login')
  return resetRequested.value ? t('login.resetPassword') : t('login.requestResetCode')
})
const resetChecks = computed(() => ({
  length: newPassword.value.length >= 8,
  uppercase: /[A-Z]/.test(newPassword.value),
  lowercase: /[a-z]/.test(newPassword.value),
  number: /\d/.test(newPassword.value),
  special: /[^A-Za-z0-9]/.test(newPassword.value),
}))
const showResetRequirements = computed(() => isResetPasswordTouched.value || newPassword.value.length > 0)

const close = () => emit('close')
const openRegister = () => emit('open-register')

const clearFeedback = () => {
  feedbackMessage.value = ''
  feedbackType.value = 'error'
}

const setFeedback = (message, type = 'error') => {
  feedbackMessage.value = message
  feedbackType.value = type
}

const resetResetState = () => {
  resetCode.value = ''
  newPassword.value = ''
  confirmNewPassword.value = ''
  showPassword.value = false
  showConfirmPassword.value = false
  isResetPasswordTouched.value = false
  isResetConfirmTouched.value = false
  resetRequested.value = false
}

const switchToReset = () => {
  mode.value = 'reset'
  password.value = ''
  clearFeedback()
}

const switchToLogin = () => {
  mode.value = 'login'
  password.value = ''
  resetResetState()
  clearFeedback()
}

const applyNotice = (notice) => {
  if (isResetMode.value || !notice?.message) {
    if (!isResetMode.value) clearFeedback()
    return
  }

  setFeedback(notice.message, notice.type === 'success' ? 'success' : 'error')
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') close()
}

const isPasswordStrong = (value) => (
  value.length >= 8
  && /[A-Z]/.test(value)
  && /[a-z]/.test(value)
  && /\d/.test(value)
  && /[^A-Za-z0-9]/.test(value)
)

const requestResetCode = async () => {
  if (!email.value) {
    setFeedback(t('login.missingResetEmail'))
    return
  }

  isSubmitting.value = true
  clearFeedback()

  try {
    await requestPasswordResetCode({ email: email.value.trim() })
    resetRequested.value = true
    setFeedback(t('login.resetCodeSent'), 'success')
  } catch (error) {
    const errorMessages = {
      missing_reset_email: t('login.missingResetEmail'),
      smtp_not_configured: t('login.resetEmailDeliveryFailed'),
      smtp_delivery_failed: t('login.resetEmailDeliveryFailed'),
      network_error: t('login.networkError'),
      unknown_error: t('login.unknownError'),
    }
    setFeedback(errorMessages[error.key || error.message] || t('login.genericError', { message: error.message }))
  } finally {
    isSubmitting.value = false
  }
}

const submitLogin = async () => {
  if (!email.value || !password.value) {
    setFeedback(t('login.fillFields'))
    return
  }

  await login({
    email: email.value.trim(),
    password: password.value,
  })

  const user = await getMe()
  setUser(user)
  setFeedback(language.value === 'en' ? 'Signed in successfully.' : 'Вход выполнен успешно.', 'success')
  const redirectTo = typeof route.query.redirect === 'string'
    ? route.query.redirect
    : defaultRouteForAccount(user.account_type)
  window.setTimeout(() => {
    close()
    router.push(redirectTo)
  }, 250)
}

const submitReset = async () => {
  if (!resetRequested.value) {
    await requestResetCode()
    return
  }

  if (!email.value || !resetCode.value || !newPassword.value || !confirmNewPassword.value) {
    setFeedback(t('login.missingResetFields'))
    return
  }

  isResetPasswordTouched.value = true
  isResetConfirmTouched.value = true

  if (!isPasswordStrong(newPassword.value)) {
    setFeedback(t('login.weakPassword'))
    return
  }

  if (newPassword.value !== confirmNewPassword.value) {
    setFeedback(t('login.passwordMismatch'))
    return
  }

  isSubmitting.value = true
  clearFeedback()

  try {
    await confirmPasswordReset({
      email: email.value.trim(),
      code: resetCode.value.trim(),
      newPassword: newPassword.value,
    })
    setFeedback(t('login.resetSuccess'), 'success')
    password.value = ''
    resetResetState()
    mode.value = 'login'
  } catch (error) {
    const errorMessages = {
      missing_reset_fields: t('login.missingResetFields'),
      weak_password: t('login.weakPassword'),
      invalid_password_reset_code: t('login.invalidResetCode'),
      password_reset_code_expired: t('login.resetCodeExpired'),
      password_reset_session_not_found: t('login.resetSessionNotFound'),
      network_error: t('login.networkError'),
      unknown_error: t('login.unknownError'),
    }
    setFeedback(errorMessages[error.key || error.message] || t('login.genericError', { message: error.message }))
  } finally {
    isSubmitting.value = false
  }
}

const submit = async () => {
  if (isSubmitting.value) return

  if (!isResetMode.value) {
    isSubmitting.value = true
    clearFeedback()

    try {
      await submitLogin()
    } catch (error) {
      const errorMessages = {
        invalid_credentials: t('login.invalidCredentials'),
        missing_fields: t('login.missingFields'),
        no_token_received: t('login.noToken'),
        network_error: t('login.networkError'),
        unknown_error: t('login.unknownError'),
      }
      setFeedback(errorMessages[error.key || error.message] || t('login.genericError', { message: error.message }))
    } finally {
      isSubmitting.value = false
    }
    return
  }

  await submitReset()
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

watch(() => props.notice, (notice) => {
  applyNotice(notice)
}, { immediate: true, deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.login-modal {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(30, 35, 38, 0.38);
  backdrop-filter: blur(0.45rem);
}

.login-card {
  position: relative;
  width: min(100%, 25rem);
  padding: 2rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-secondary);
  box-shadow: var(--shadow-strong);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 2.25rem;
  height: 2.25rem;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: rgba(30, 35, 38, 0.55);
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: color-mix(in srgb, var(--brand-soft) 45%, white);
  color: var(--text-primary);
}

.title {
  margin: 0 1.5rem 0.5rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
}

.hint {
  margin: -0.25rem 0 0;
  color: var(--text-muted);
  font-size: 0.875rem;
  line-height: 1.55;
  text-align: center;
}

.input {
  width: 100%;
  padding: 0.75rem 0.875rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.875rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
}

.input::placeholder {
  color: color-mix(in srgb, var(--text-muted) 75%, transparent);
}

.input:focus {
  border-color: var(--brand-strong);
  box-shadow: 0 0 0 0.1875rem rgba(29, 168, 107, 0.12);
}

.input.error {
  border-color: #ff4d4f;
  background: rgba(255, 77, 79, 0.02);
}

.input-center {
  text-align: center;
  letter-spacing: 0.2em;
  font-weight: 700;
}

.requirements {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  padding: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 36%, white);
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.5rem;
  margin-top: -0.25rem;
}

.req-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: rgba(30, 35, 38, 0.5);
  transition: color 0.2s ease;
}

.req-item.valid {
  color: var(--brand-strong);
}

.req-item i {
  width: 0.875rem;
  font-size: 0.625rem;
  text-align: center;
}

.password {
  position: relative;
  display: grid;
}

.password .input {
  padding-right: 2.75rem;
}

.toggle {
  position: absolute;
  right: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0.375rem;
  color: rgba(30, 35, 38, 0.5);
  display: grid;
  place-items: center;
  transition: color 0.2s ease;
}

.toggle:hover {
  color: var(--brand-strong);
}

.submit-btn {
  width: 100%;
  min-height: 2.875rem;
  margin-top: 0.5rem;
}

.submit-btn:disabled {
  background: #e2e8f0;
  color: rgba(30, 35, 38, 0.4);
  cursor: not-allowed;
}

.link {
  border: none;
  background: transparent;
  text-align: center;
  font-size: 0.8125rem;
  color: rgba(30, 35, 38, 0.6);
  text-decoration: none;
  margin-top: 0.15rem;
  cursor: pointer;
  transition: color 0.2s ease;
  font-family: inherit;
}

.link:hover {
  color: #1e2326;
}

.link:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.link-accent {
  color: var(--brand-strong);
  font-weight: 600;
}

.link:hover .link-accent {
  text-decoration: underline;
}

.api-error-msg {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(255, 77, 79, 0.08);
  border: 0.0625rem solid rgba(255, 77, 79, 0.2);
  border-radius: 0.5rem;
  color: #d32f2f;
  font-size: 0.8125rem;
  font-weight: 500;
}

.api-error-msg--success {
  background: rgba(22, 163, 74, 0.08);
  border: 0.0625rem solid rgba(22, 163, 74, 0.2);
  color: #15803d;
}

.api-error-msg i {
  color: #ff4d4f;
}

.api-error-msg--success i {
  color: #16a34a;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .login-card,
.modal-fade-leave-active .login-card {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-fade-enter-from .login-card,
.modal-fade-leave-to .login-card {
  opacity: 0;
  transform: translateY(0.75rem) scale(0.98);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-0.625rem);
}

.spinner {
  width: 1rem;
  height: 1rem;
  border: 0.125rem solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 30rem) {
  .login-modal {
    align-items: flex-start;
    padding: 4.5rem 1rem 1rem;
  }

  .login-card {
    padding: 1.5rem;
  }
}
</style>
