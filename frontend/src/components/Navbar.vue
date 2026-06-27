<template>
  <header class="navbar">
    <RouterLink to="/" class="logo-link" @click="closeMenu">
      <Logo />
    </RouterLink>

    <nav class="desktop-nav">
      <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link">
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="actions">
      <BaseDropdown
        v-model="currentLanguage"
        class="language-switcher"
        aria-label="Выбор языка"
        icon-class="fas fa-globe"
        :options="languageOptions"
        size="sm"
        align="right"
        :show-selected-hint="false"
        @change="changeLanguage"
      />

      <template v-if="user">
        <div class="user-menu-wrapper">
          <button type="button" class="user-email" @click="isUserMenuOpen = !isUserMenuOpen">
            <span class="user-email__meta">{{ accountTypeLabel }}</span>
            <span>{{ user.email }}</span>
          </button>

          <div v-if="isUserMenuOpen" class="user-dropdown">
            <RouterLink class="dropdown-item" to="/profile" @click="isUserMenuOpen = false">
              Профиль
            </RouterLink>
            <RouterLink class="dropdown-item" :to="dashboardRoute" @click="isUserMenuOpen = false">
              Кабинет
            </RouterLink>
            <button class="dropdown-item dropdown-item--danger" type="button" @click="logout">
              Выйти
            </button>
          </div>
        </div>
      </template>

      <template v-else>
        <button type="button" class="btn-secondary" @click="$emit('open-login')">
          Войти
        </button>
        <button type="button" class="btn-primary" @click="$emit('open-register')">
          Регистрация
        </button>
      </template>
    </div>

    <button class="burger-menu" type="button" :aria-expanded="isMenuOpen" @click="toggleMenu">
      <i :class="isMenuOpen ? 'fas fa-xmark' : 'fas fa-bars'"></i>
    </button>

    <transition name="menu-fade">
      <div v-if="isMenuOpen" class="mobile-menu-overlay" @click="closeMenu">
        <aside class="mobile-menu" @click.stop>
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="mobile-nav-link"
            @click="closeMenu"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </RouterLink>

          <div class="mobile-auth-buttons">
            <label class="mobile-language-switcher">
              <span>Язык</span>
              <BaseDropdown
                v-model="currentLanguage"
                aria-label="Выбор языка"
                :options="languageOptions"
                full-width
                align="right"
                :show-selected-hint="false"
                @change="changeLanguage"
              />
            </label>

            <template v-if="user">
              <span class="mobile-user-email">{{ user.email }}</span>
              <RouterLink
                v-for="item in mobileAccountLinks"
                :key="item.to"
                :to="item.to"
                :class="item.primary ? 'btn-primary' : 'btn-secondary'"
                @click="closeMenu"
              >
                {{ item.label }}
              </RouterLink>
              <button type="button" class="btn-secondary" @click="logout">Выйти</button>
            </template>

            <template v-else>
              <button type="button" class="btn-secondary" @click="openLoginFromMenu">
                Войти
              </button>
              <button type="button" class="btn-primary" @click="openRegisterFromMenu">
                Регистрация
              </button>
            </template>
          </div>
        </aside>
      </div>
    </transition>
  </header>
</template>

<script>
import { useAuth } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import BaseDropdown from './BaseDropdown.vue'
import Logo from './Logo.vue'

const ACCOUNT_LABELS = {
  candidate: 'Кандидат',
  user: 'Кандидат',
  employer: 'Работодатель',
  admin: 'Администратор',
}

function normalizeAccountType(accountType) {
  if (accountType === 'user') return 'candidate'
  return accountType || ''
}

function routeForAccount(accountType) {
  const normalizedType = normalizeAccountType(accountType)

  if (normalizedType === 'candidate') {
    return '/dashboard'
  }

  if (normalizedType === 'employer') {
    return '/employer-dashboard'
  }

  if (normalizedType === 'admin') {
    return '/admin'
  }

  return '/'
}

export default {
  emits: ['open-login', 'open-register'],
  components: {
    BaseDropdown,
    Logo,
  },

  setup() {
    const { state, logout: logoutAuth } = useAuth()
    const uiStore = useUiStore()
    return {
      authState: state,
      logoutAuth,
      uiStore,
    }
  },

  data() {
    return {
      isUserMenuOpen: false,
      isMenuOpen: false,
      languageOptions: [
        { value: 'ru', label: 'RU', hint: 'Русский' },
        { value: 'en', label: 'EN', hint: 'English' },
        { value: 'lv', label: 'LV', hint: 'Latviešu' },
      ],
      navItems: [
        { label: 'Вакансии', to: '/jobs', icon: 'fas fa-briefcase' },
        { label: 'Работодателям', to: '/employers', icon: 'fas fa-users' },
        { label: 'Резюме', to: '/resume-builder', icon: 'fas fa-file-lines' },
        { label: 'О платформе', to: '/about', icon: 'fas fa-circle-info' },
        { label: 'Цены', to: '/pricing', icon: 'fas fa-tags' },
      ],
    }
  },

  computed: {
    user() {
      return this.authState.user
    },

    normalizedAccountType() {
      return normalizeAccountType(this.user?.account_type)
    },

    currentLanguage: {
      get() {
        return this.uiStore.language
      },
      set(value) {
        this.uiStore.setLanguage(value)
      },
    },

    dashboardRoute() {
      return routeForAccount(this.user?.account_type)
    },

    accountTypeLabel() {
      return ACCOUNT_LABELS[this.user?.account_type] || ACCOUNT_LABELS[this.normalizedAccountType] || 'Account'
    },

    mobileAccountLinks() {
      if (!this.user) return []

      if (this.normalizedAccountType === 'candidate') {
        return [
          { label: 'Профиль', to: '/profile', primary: true },
          { label: 'Дашборд', to: '/dashboard' },
          { label: 'Резюме', to: '/resume-builder' },
          { label: 'Сообщения', to: '/messages' },
          { label: 'Вакансии', to: '/jobs' },
        ]
      }

      if (this.normalizedAccountType === 'admin') {
        return [
          { label: 'Админ-панель', to: '/admin', primary: true },
          { label: 'Кабинет работодателя', to: '/employer-dashboard' },
          { label: 'Вакансии', to: '/admin?section=jobs' },
          { label: 'Профиль', to: '/profile' },
        ]
      }

      return [
        { label: 'Кабинет', to: '/employer-dashboard', primary: true },
        { label: 'Мои вакансии', to: '/employer-dashboard?section=jobs' },
        { label: 'Отклики', to: '/employer-dashboard?section=responses' },
        { label: 'Сообщения', to: '/employer-dashboard?section=messages' },
        { label: 'Тарифы', to: '/employer-dashboard?section=pricing' },
        { label: 'Профиль', to: '/profile' },
      ]
    },
  },

  methods: {
    changeLanguage() {
      this.uiStore.setLanguage(this.currentLanguage)
    },

    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen
      document.body.style.overflow = this.isMenuOpen ? 'hidden' : ''
    },

    closeMenu() {
      this.isMenuOpen = false
      document.body.style.overflow = ''
    },

    openLoginFromMenu() {
      this.closeMenu()
      this.$emit('open-login')
    },

    openRegisterFromMenu() {
      this.closeMenu()
      this.$emit('open-register')
    },

    logout() {
      this.closeMenu()
      this.logoutAuth()
      this.isUserMenuOpen = false
    },

    handleResize() {
      if (window.innerWidth > 944 && this.isMenuOpen) {
        this.closeMenu()
      }
    },
  },

  mounted() {
    window.addEventListener('resize', this.handleResize)
    this.uiStore.initialize()
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    document.body.style.overflow = ''
  },
}
</script>

<style scoped>
.navbar {
  display: flex;
  max-width: var(--shell-max-width);
  align-items: center;
  padding: 1rem var(--shell-gutter);
  justify-content: space-between;
  gap: 0.85rem;
  font-size: 0.86rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
  position: sticky;
  top: 0;
  z-index: 1000;
  background: color-mix(in srgb, var(--surface-primary) 90%, transparent);
  backdrop-filter: blur(1rem);
  user-select: none;
  margin: 0 auto;
  width: 100%;
}

.logo-link {
  display: flex;
  flex-shrink: 0;
  text-decoration: none;
}

.logo-link :deep(svg) {
  width: 10.5rem;
  height: auto;
}

.desktop-nav {
  flex: 1;
  gap: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-link,
.language-switcher {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-primary);
  position: relative;
  text-decoration: none;
  transition: color 0.2s ease;
  white-space: nowrap;
}

.nav-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -0.25rem;
  width: 100%;
  height: 0.125rem;
  background-color: var(--brand-strong);
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform 0.3s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--brand-strong);
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  transform: scaleX(1);
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.language-switcher {
  min-width: 6.5rem;
}

.language-switcher:deep(.dropdown__trigger) {
  min-height: 2.75rem;
  padding-inline: 0.85rem 0.8rem;
  border-radius: 999rem;
  border-color: color-mix(in srgb, var(--brand-base) 16%, var(--border-subtle));
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(241, 249, 245, 0.98));
  box-shadow: 0 0.55rem 1.25rem rgba(16, 24, 40, 0.06);
}

.language-switcher:deep(.dropdown__content) {
  gap: 0.05rem;
}

.language-switcher:deep(.dropdown__label) {
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.language-switcher:deep(.dropdown__menu) {
  min-width: 8.5rem;
}

.user-email,
.mobile-user-email {
  max-width: 14rem;
  overflow: hidden;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-email {
  display: grid;
  justify-items: end;
  gap: 0.22rem;
  border: none;
  background: transparent;
  line-height: 1.2;
}

.user-email__meta {
  color: var(--brand-strong);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.burger-menu {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  font-size: 1.6rem;
  color: var(--text-primary);
  z-index: 1001;
}

.mobile-menu-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  backdrop-filter: blur(0.25rem);
}

.mobile-menu {
  position: fixed;
  top: 0;
  right: 0;
  width: 75vw;
  max-width: 22rem;
  height: 100vh;
  background: var(--surface-secondary);
  box-shadow: -0.25rem 0 0.625rem rgba(0, 0, 0, 0.2);
  padding: 5rem 1.5rem 2rem;
  overflow-y: auto;
  animation: slideIn 0.3s ease-out;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  color: var(--text-primary);
  text-decoration: none;
  border-radius: 0.5rem;
}

.mobile-nav-link.router-link-active {
  color: var(--brand-strong);
  background: var(--brand-soft);
}

.mobile-auth-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 1rem;
  margin-top: 1rem;
  border-top: 0.0625rem solid var(--border-subtle);
}

.mobile-language-switcher {
  display: grid;
  gap: 0.75rem;
  border-radius: 1rem;
  padding: 0.9rem 1rem;
  border: 0.0625rem solid var(--border-subtle);
  background: var(--surface-primary);
}

.mobile-auth-buttons .btn-primary,
.mobile-auth-buttons .btn-secondary {
  width: 100%;
  justify-content: center;
}

.user-menu-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.user-dropdown {
  position: absolute;
  top: 120%;
  right: 0;
  background: var(--surface-secondary);
  border-radius: 0.5rem;
  box-shadow: var(--shadow-strong);
  min-width: 10rem;
  z-index: 2000;
  overflow: hidden;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: var(--text-primary);
  text-align: left;
  text-decoration: none;
  cursor: pointer;
}

.dropdown-item:hover {
  background: color-mix(in srgb, var(--brand-soft) 60%, transparent);
}

.dropdown-item--danger {
  color: #d32f2f;
}

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: opacity 0.3s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

@media (max-width: 82rem) {
  .desktop-nav {
    gap: 0.75rem;
  }
}

@media (max-width: 74rem) {
  .desktop-nav,
  .actions {
    display: none;
  }

  .burger-menu {
    display: block;
  }
}

@media (max-width: 30rem) {
  .navbar {
    padding: 0.8rem 1rem;
  }

  .logo-link :deep(svg) {
    width: 9.5rem;
  }

  .mobile-menu {
    width: 85vw;
  }
}
</style>