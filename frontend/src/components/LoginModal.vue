<template>
  <Teleport to="body">
    <Transition name="modal-fade" appear>
      <div class="login-modal" role="dialog" aria-modal="true" aria-labelledby="login-title">
        <form class="login-card" @submit.prevent="submit">
          <button type="button" class="modal-close" aria-label="Закрыть окно входа" @click="close">
            <i class="fa-solid fa-xmark"></i>
          </button>

          <h1 id="login-title" class="title">Вход в аккаунт</h1>

          <Transition name="expand">
            <div v-if="apiError" class="api-error-msg">
              <i class="fa-solid fa-circle-exclamation"></i>
              <span>{{ apiError }}</span>
            </div>
          </Transition>

          <input
            v-model="email"
            type="email"
            placeholder="Email"
            class="input"
            :class="{ error: apiError }"
            @input="apiError = ''"
          />

          <div class="password">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Пароль"
              class="input"
              :class="{ error: apiError }"
              @input="apiError = ''"
            />

            <button
              type="button"
              class="toggle"
              aria-label="Показать пароль"
              @click="showPassword = !showPassword"
            >
              <i :class="showPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'"></i>
            </button>
          </div>

          <button type="submit" class="submit-btn btn-primary" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner"></span>
            <span v-else>Войти</span>
          </button>

          <button type="button" class="link" @click="openRegister">
            Нет аккаунта? <span class="link-accent">Зарегистрироваться</span>
          </button>
        </form>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMe, login } from '@/api/auth'
import { useAuth } from '@/stores/auth'
import { defaultRouteForAccount } from '@/utils/auth'

const emit = defineEmits(['close', 'open-register'])
const route = useRoute()
const router = useRouter()
const { setUser } = useAuth()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const isSubmitting = ref(false)
const apiError = ref('')

const close = () => {
  emit('close')
}

const openRegister = () => {
  emit('open-register')
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    close()
  }
}

const submit = async () => {
  if (!email.value || !password.value) {
    apiError.value = 'Заполните все поля'
    return
  }

  isSubmitting.value = true
  apiError.value = ''

  try {
    await login({
      email: email.value.trim(),
      password: password.value,
    })

    const user = await getMe()
    setUser(user)
    const redirectTo = typeof route.query.redirect === 'string'
      ? route.query.redirect
      : defaultRouteForAccount(user.account_type)
    close()
    router.push(redirectTo)
  } catch (error) {
    const errorMessages = {
      invalid_credentials: 'Неверный Email или пароль',
      missing_fields: 'Заполните все обязательные поля',
      no_token_received: 'Ошибка сервера: токен не получен',
      network_error: 'Нет связи с сервером. Проверьте подключение и повторите попытку.',
      unknown_error: 'Произошла непредвиденная ошибка',
    }

    apiError.value = errorMessages[error.key || error.message] || `Ошибка: ${error.message}`
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

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
  margin-top: 0.25rem;
  cursor: pointer;
  transition: color 0.2s ease;
  font-family: inherit;
}

.link:hover {
  color: #1e2326;
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

.api-error-msg i {
  color: #ff4d4f;
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
