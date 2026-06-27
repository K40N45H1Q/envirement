<template>
  <Teleport to="body">
    <Transition name="modal-fade" appear>
      <div
        v-if="visible"
        class="register-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="register-title"
        @click.self="close"
      >
        <form class="register-card" novalidate @submit.prevent="handleSubmit">
          <button type="button" class="modal-close" aria-label="Закрыть окно регистрации" @click="close">
            <i class="fa-solid fa-xmark"></i>
          </button>

          <h1 id="register-title" class="title">
            {{ selectedAccountType === 'employer' ? 'Создать аккаунт компании' : 'Создание аккаунта' }}
          </h1>
          <p class="subtitle">
            {{
              isEmployerCompanyStep
                ? 'Шаг 2 из 2. Заполните данные компании в том же окне.'
                : 'Создайте аккаунт и продолжите работу в едином интерфейсе платформы.'
            }}
          </p>

          <Transition name="expand">
            <div v-if="error" class="api-error-msg">
              <i class="fa-solid fa-circle-exclamation"></i>
              <span>{{ error }}</span>
            </div>
          </Transition>

          <div v-if="selectedAccountType === 'employer'" class="steps">
            <div class="step" :class="{ 'step--active': currentStep === 1, 'step--done': currentStep > 1 }">
              <span>1</span>
              <strong>Аккаунт</strong>
            </div>
            <div class="steps-line"></div>
            <div class="step" :class="{ 'step--active': currentStep === 2 }">
              <span>2</span>
              <strong>Компания</strong>
            </div>
          </div>

          <div v-if="!isEmployerCompanyStep" class="field">
            <div class="account-type">
              <button
                type="button"
                class="account-option"
                :class="{ 'account-option--active': selectedAccountType === 'candidate' }"
                @click="selectAccountType('candidate')"
              >
                <strong>Кандидат</strong>
                <span>Создать профиль и откликаться на вакансии</span>
              </button>
              <button
                type="button"
                class="account-option"
                :class="{ 'account-option--active': selectedAccountType === 'employer' }"
                @click="selectAccountType('employer')"
              >
                <strong>Работодатель</strong>
                <span>Публиковать вакансии и управлять откликами</span>
              </button>
            </div>
          </div>

          <template v-if="!isEmployerCompanyStep">
            <div class="field">
              <input
                v-model.trim="email"
                type="email"
                placeholder="Email"
                class="input"
                autocomplete="email"
                @input="error = ''"
              />
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
                  @input="error = ''"
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
                  @input="error = ''"
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

            <label class="policy">
              <input v-model="acceptedPolicy" type="checkbox" />
              <span>Я принимаю политику конфиденциальности и согласен на обработку данных.</span>
            </label>

            <button type="submit" class="submit-btn btn-primary" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              <span v-else>{{ selectedAccountType === 'employer' ? 'Продолжить' : 'Зарегистрироваться' }}</span>
            </button>
          </template>

          <template v-else>
            <div class="field">
              <input
                v-model.trim="companyName"
                type="text"
                placeholder="Название компании"
                class="input"
                autocomplete="organization"
                @input="error = ''"
              />
            </div>

            <div class="field field-grid">
              <BaseDropdown
                v-model="companyCountry"
                aria-label="Страна компании"
                :options="countryDropdownOptions"
                placeholder="Страна"
                full-width
                :show-selected-hint="false"
              />

              <BaseDropdown
                v-model="companyIndustry"
                aria-label="Отрасль компании"
                :options="industryDropdownOptions"
                placeholder="Отрасль"
                full-width
                :show-selected-hint="false"
              />
            </div>

            <div class="field">
              <input
                v-model.trim="companyRegistrationNumber"
                type="text"
                placeholder="Регистрационный номер"
                class="input"
                autocomplete="off"
                @input="error = ''"
              />
            </div>

            <div class="hint-card">
              После регистрации вы сможете заполнить карточку работодателя и сразу опубликовать первую вакансию.
            </div>

            <div class="actions">
              <button type="button" class="btn-secondary secondary-action" :disabled="loading" @click="currentStep = 1">
                Назад
              </button>
              <button type="submit" class="submit-btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner"></span>
                <span v-else>Создать компанию</span>
              </button>
            </div>
          </template>

          <button v-if="!isEmployerCompanyStep" type="button" class="link" @click="emit('open-login')">
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
import BaseDropdown from '@/components/BaseDropdown.vue'

defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close', 'registered', 'open-login'])

const selectedAccountType = ref('candidate')
const currentStep = ref(1)
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const acceptedPolicy = ref(false)
const companyName = ref('')
const companyCountry = ref('')
const companyIndustry = ref('')
const companyRegistrationNumber = ref('')
const isPasswordTouched = ref(false)
const isConfirmTouched = ref(false)
const error = ref('')
const loading = ref(false)

const countryOptions = ['Латвия', 'Литва', 'Эстония', 'Германия', 'Польша', 'Нидерланды']
const industryOptions = ['Энергетика', 'Строительство', 'Производство', 'Логистика', 'Металлообработка']
const countryDropdownOptions = countryOptions.map((option) => ({ value: option, label: option }))
const industryDropdownOptions = industryOptions.map((option) => ({ value: option, label: option }))

const isEmployerCompanyStep = computed(() => selectedAccountType.value === 'employer' && currentStep.value === 2)
const showRequirements = computed(() => isPasswordTouched.value || password.value.length > 0)
const checks = computed(() => ({
  length: password.value.length >= 8,
  uppercase: /[A-Z]/.test(password.value),
  lowercase: /[a-z]/.test(password.value),
  number: /\d/.test(password.value),
  special: /[^A-Za-z0-9]/.test(password.value),
}))
const isPasswordValid = computed(() => {
  const value = checks.value
  return value.length && value.uppercase && value.lowercase && value.number && value.special
})
const doPasswordsMatch = computed(() => password.value === confirmPassword.value && confirmPassword.value !== '')

function resetForm() {
  email.value = ''
  password.value = ''
  confirmPassword.value = ''
  showPassword.value = false
  showConfirmPassword.value = false
  acceptedPolicy.value = false
  companyName.value = ''
  companyCountry.value = ''
  companyIndustry.value = ''
  companyRegistrationNumber.value = ''
  isPasswordTouched.value = false
  isConfirmTouched.value = false
  currentStep.value = 1
  error.value = ''
  loading.value = false
}

function close() {
  resetForm()
  emit('close')
}

function selectAccountType(type) {
  selectedAccountType.value = type
  currentStep.value = 1
  error.value = ''
}

function validateAccountStep() {
  if (!email.value || !password.value || !confirmPassword.value) {
    error.value = 'Заполните email и пароль.'
    return false
  }

  if (!isPasswordValid.value) {
    error.value = 'Пароль не соответствует требованиям.'
    return false
  }

  if (!doPasswordsMatch.value) {
    error.value = 'Пароли не совпадают.'
    return false
  }

  if (!acceptedPolicy.value) {
    error.value = 'Подтвердите согласие с политикой конфиденциальности.'
    return false
  }

  return true
}

function validateCompanyStep() {
  if (!companyName.value || !companyCountry.value || !companyIndustry.value) {
    error.value = 'Заполните название компании, страну и отрасль.'
    return false
  }

  return true
}

async function handleSubmit() {
  error.value = ''

  if (!isEmployerCompanyStep.value) {
    isPasswordTouched.value = true
    isConfirmTouched.value = true

    if (!validateAccountStep()) return

    if (selectedAccountType.value === 'employer') {
      currentStep.value = 2
      return
    }
  } else if (!validateCompanyStep()) {
    return
  }

  loading.value = true

  try {
    const payload = await createAccount({
      email: email.value.trim(),
      password: password.value,
      accountType: selectedAccountType.value,
      companyName: selectedAccountType.value === 'employer' ? companyName.value : '',
      companyCountry: selectedAccountType.value === 'employer' ? companyCountry.value : '',
      companyIndustry: selectedAccountType.value === 'employer' ? companyIndustry.value : '',
      companyRegistrationNumber: selectedAccountType.value === 'employer' ? companyRegistrationNumber.value : '',
    })

    emit('registered', payload)

    if (selectedAccountType.value === 'candidate') {
      emit('open-login')
    } else {
      close()
    }
  } catch (requestError) {
    error.value = requestError?.message || 'Не удалось создать аккаунт.'
  } finally {
    loading.value = false
  }
}

function handleKeydown(event) {
  if (event.key === 'Escape') {
    close()
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
  margin: 0;
  padding-right: 2rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.subtitle {
  margin: -0.375rem 0 0;
  color: var(--text-muted);
  font-size: 0.875rem;
  line-height: 1.5;
}

.steps {
  display: grid;
  grid-template-columns: auto minmax(6rem, 1fr) auto;
  align-items: center;
  gap: 0.25rem;
}

.steps-line {
  width: 100%;
  height: 0.125rem;
  margin: 0 0.125rem;
  background: linear-gradient(90deg, rgba(25, 120, 90, 0.72), rgba(25, 120, 90, 0.32));
  border-radius: 999px;
}

.step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: color-mix(in srgb, var(--text-muted) 78%, transparent);
  font-size: 0.8125rem;
}

.step span {
  width: 1.875rem;
  height: 1.875rem;
  border-radius: 50%;
  border: 0.0625rem solid color-mix(in srgb, var(--brand-base) 22%, var(--border-subtle));
  display: grid;
  place-items: center;
  background: var(--surface-secondary);
  font-weight: 700;
}

.step--active,
.step--done {
  color: var(--brand-strong);
}

.step--active span,
.step--done span {
  background: var(--brand-strong);
  border-color: var(--brand-strong);
  color: #fff;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.account-type {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.account-option {
  display: grid;
  gap: 0.35rem;
  width: 100%;
  min-height: 5.25rem;
  align-content: start;
  padding: 0.95rem;
  text-align: left;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.75rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.account-option strong,
.account-option span {
  display: block;
}

.account-option span {
  color: var(--text-muted);
  font-size: 0.8125rem;
  line-height: 1.4;
}

.account-option--active {
  border-color: color-mix(in srgb, var(--brand-base) 28%, var(--border-subtle));
  background: color-mix(in srgb, var(--brand-soft) 66%, white);
  box-shadow: 0 0 0 0.1875rem color-mix(in srgb, var(--brand-soft) 68%, transparent);
}

.input {
  width: 100%;
  padding: 0.75rem 0.875rem;
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.5rem;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
  min-height: 2.875rem;
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
  color: var(--brand-strong);
}

.requirements {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  padding: 0.75rem;
  background: color-mix(in srgb, var(--brand-soft) 36%, white);
  border: 0.0625rem solid var(--border-subtle);
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
  color: var(--brand-strong);
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

.policy {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.policy input {
  margin-top: 0.125rem;
}

.hint-card {
  padding: 0.875rem 1rem;
  background: color-mix(in srgb, var(--brand-soft) 34%, white);
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.5rem;
  color: var(--text-muted);
  font-size: 0.8125rem;
  line-height: 1.5;
}

.actions {
  display: grid;
  grid-template-columns: 7rem 1fr;
  gap: 0.75rem;
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
}

.submit-btn:disabled,
.secondary-action:disabled {
  background: #e2e8f0;
  color: rgba(30, 35, 38, 0.4);
  cursor: not-allowed;
}

.secondary-action {
  min-height: 2.875rem;
}

.link {
  display: block;
  width: 100%;
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
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 10rem;
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

  .account-type,
  .field-grid,
  .actions {
    grid-template-columns: 1fr;
  }
}
</style>