<template>
  <Teleport to="body">
    <Transition name="modal-fade" appear>
      <div class="register-modal" role="dialog" aria-modal="true" aria-labelledby="register-title">
        <form class="register-card" novalidate @submit.prevent="submit">
          <button type="button" class="modal-close" aria-label="Закрыть окно регистрации" @click="close">
            <i class="fa-solid fa-xmark"></i>
          </button>

          <h1 id="register-title" class="title">Создание аккаунта</h1>

          <Transition name="expand">
            <div v-if="apiError" class="api-error-msg">
              <i class="fa-solid fa-circle-exclamation"></i>
              <span>{{ apiError }}</span>
            </div>
          </Transition>

          <div class="field">
            <div class="account-type">
              <button
                type="button"
                class="account-option"
                :class="{ 'account-option--active': accountType === 'user' }"
                @click="accountType = 'user'"
              >
                <strong>Кандидат</strong>
                <span>Создать профиль и откликаться на вакансии</span>
              </button>
              <button
                type="button"
                class="account-option"
                :class="{ 'account-option--active': accountType === 'employer' }"
                @click="accountType = 'employer'"
              >
                <strong>Работодатель</strong>
                <span>Публиковать вакансии и управлять откликами</span>
              </button>
            </div>
          </div>

          <div class="field">
            <input
              v-model="email"
              type="email"
              placeholder="Email"
              class="input"
              :class="{ error: isEmailTouched && !isEmailValid }"
              autocomplete="email"
              @blur="isEmailTouched = true"
              @input="apiError = ''"
            />
            <span v-if="isEmailTouched && !isEmailValid" class="error-msg">
              Введите корректный email
            </span>
          </div>

          <div class="field">
            <div class="password-wrapper">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Пароль"
                class="input"
                :class="{ error: isPasswordTouched && !isPasswordValid }"
                autocomplete="new-password"
                @blur="isPasswordTouched = true"
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

            <Transition name="expand">
              <div v-show="showRequirements" class="requirements">
                <div class="req-item" :class="{ valid: checks.length }">
                  <i class="fa-solid" :class="checks.length ? 'fa-check' : 'fa-xmark'"></i>
                  <span>Минимум 8 символов</span>
                </div>
                <div class="req-item" :class="{ valid: checks.uppercase }">
                  <i class="fa-solid" :class="checks.uppercase ? 'fa-check' : 'fa-xmark'"></i>
                  <span>Одна заглавная буква</span>
                </div>
                <div class="req-item" :class="{ valid: checks.lowercase }">
                  <i class="fa-solid" :class="checks.lowercase ? 'fa-check' : 'fa-xmark'"></i>
                  <span>Одна строчная буква</span>
                </div>
                <div class="req-item" :class="{ valid: checks.number }">
                  <i class="fa-solid" :class="checks.number ? 'fa-check' : 'fa-xmark'"></i>
                  <span>Одна цифра</span>
                </div>
                <div class="req-item" :class="{ valid: checks.special }">
                  <i class="fa-solid" :class="checks.special ? 'fa-check' : 'fa-xmark'"></i>
                  <span>Один спецсимвол (!@#$%^&*)</span>
                </div>
              </div>
            </Transition>
          </div>

          <div class="field">
            <div class="password-wrapper">
              <input
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="Подтвердите пароль"
                class="input"
                :class="{ error: isConfirmTouched && !doPasswordsMatch }"
                autocomplete="new-password"
                @blur="isConfirmTouched = true"
                @input="apiError = ''"
              />
              <button
                type="button"
                class="toggle"
                aria-label="Показать пароль"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <i :class="showConfirmPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'"></i>
              </button>
            </div>
            <span v-if="isConfirmTouched && !doPasswordsMatch" class="error-msg">
              Пароли не совпадают
            </span>
          </div>

          <button type="submit" class="submit-btn btn-primary" :disabled="!isFormValid || isSubmitting">
            <span v-if="isSubmitting" class="spinner"></span>
            <span v-else>Зарегистрироваться</span>
          </button>

          <button type="button" class="link" @click="openLogin">
            Уже есть аккаунт? <span class="link-accent">Войти</span>
          </button>
        </form>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { createAccount } from '@/api/auth'

const emit = defineEmits(['close', 'open-login'])

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const accountType = ref('user')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isSubmitting = ref(false)
const apiError = ref('')
const isEmailTouched = ref(false)
const isPasswordTouched = ref(false)
const isConfirmTouched = ref(false)

const showRequirements = computed(() => isPasswordTouched.value || password.value.length > 0)

const isEmailValid = computed(() => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email.value)
})

const checks = computed(() => ({
  length: password.value.length >= 8,
  uppercase: /[A-Z]/.test(password.value),
  lowercase: /[a-z]/.test(password.value),
  number: /\d/.test(password.value),
  special: /[^A-Za-z0-9]/.test(password.value),
}))

const isPasswordValid = computed(() => {
  const c = checks.value
  return c.length && c.uppercase && c.lowercase && c.number && c.special
})

const doPasswordsMatch = computed(() => {
  return password.value === confirmPassword.value && confirmPassword.value !== ''
})

const isFormValid = computed(() => {
  return isEmailValid.value && isPasswordValid.value && doPasswordsMatch.value
})

const close = () => {
  emit('close')
}

const openLogin = () => {
  emit('open-login')
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    close()
  }
}

const submit = async () => {
  isEmailTouched.value = true
  isPasswordTouched.value = true
  isConfirmTouched.value = true

  if (!isFormValid.value) return

  isSubmitting.value = true
  apiError.value = ''

  try {
    await createAccount({
      email: email.value.trim(),
      password: password.value,
      accountType: accountType.value,
    })

    openLogin()
  } catch (error) {
    const errorMessages = {
      user_exists: 'Пользователь с таким Email уже существует',
      missing_fields: 'Заполните все обязательные поля',
      invalid_account_type: 'Недопустимый тип аккаунта',
      network_error: 'Нет связи с сервером. Проверьте, что backend запущен.',
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
.register-modal {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(30, 35, 38, 0.38);
  backdrop-filter: blur(0.45rem);
  overflow-y: auto;
}

.register-card {
  position: relative;
  width: min(100%, 31rem);
  max-height: calc(100vh - 3rem);
  overflow-y: auto;
  padding: 2rem;
  border: 0.0625rem solid #e2e8f0;
  border-radius: 0.5rem;
  background: #fff;
  box-shadow: 0 1.5rem 4rem rgba(0, 0, 0, 0.18);
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
  background: rgba(30, 35, 38, 0.06);
  color: #1e2326;
}

.title {
  margin: 0 1.5rem 0.5rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e2326;
  text-align: center;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.account-type {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.account-option {
  display: grid;
  gap: 0.35rem;
  padding: 0.95rem;
  text-align: left;
  border: 0.0625rem solid #e2e8f0;
  border-radius: 0.75rem;
  background: #fff;
  color: #1e2326;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.account-option span {
  color: rgba(30, 35, 38, 0.62);
  font-size: 0.8125rem;
  line-height: 1.4;
}

.account-option--active {
  border-color: rgba(25, 120, 90, 0.5);
  background: rgba(25, 120, 90, 0.06);
  box-shadow: 0 0 0 0.1875rem rgba(25, 120, 90, 0.08);
}

.input {
  width: 100%;
  padding: 0.75rem 0.875rem;
  border: 0.0625rem solid #e2e8f0;
  border-radius: 0.5rem;
  background: #fff;
  color: #1e2326;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
}

.input::placeholder {
  color: rgba(30, 35, 38, 0.4);
}

.input:focus {
  border-color: #19785a;
  box-shadow: 0 0 0 0.1875rem rgba(25, 120, 90, 0.1);
}

.input.error {
  border-color: #ff4d4f;
  background: rgba(255, 77, 79, 0.02);
  box-shadow: 0 0 0 0.1875rem rgba(255, 77, 79, 0.08);
}

.password-wrapper {
  position: relative;
  display: grid;
}

.password-wrapper .input {
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
  color: #19785a;
}

.requirements {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  padding: 0.75rem;
  background: #f8fafc;
  border: 0.0625rem solid #e2e8f0;
  border-radius: 0.5rem;
  margin-top: 0.25rem;
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
  color: #19785a;
}

.req-item i {
  width: 0.875rem;
  font-size: 0.625rem;
  text-align: center;
}

.error-msg {
  font-size: 0.75rem;
  color: #ff4d4f;
  padding-left: 0.25rem;
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

.submit-btn {
  width: 100%;
  min-height: 2.875rem;
  margin-top: 0.5rem;
  border: none;
  font-weight: 600;
  font-size: 0.9375rem;
  font-family: inherit;
}

.submit-btn:hover:not(:disabled) {
  background: #146a4f;
  transform: translateY(-0.0625rem);
  box-shadow: 0 0.25rem 0.75rem rgba(25, 120, 90, 0.2);
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
  color: #19785a;
  font-weight: 600;
}

.link:hover .link-accent {
  text-decoration: underline;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .register-card,
.modal-fade-leave-active .register-card {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-fade-enter-from .register-card,
.modal-fade-leave-to .register-card {
  opacity: 0;
  transform: translateY(0.75rem) scale(0.98);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 18.75rem;
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
  .register-modal {
    align-items: flex-start;
    padding: 4.5rem 1rem 1rem;
  }

  .register-card {
    max-height: none;
    padding: 1.5rem;
  }

  .account-type {
    grid-template-columns: 1fr;
  }
}
</style>
