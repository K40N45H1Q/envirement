<template>
  <header class="navbar">
    <RouterLink to="/" class="logo-link" @click="closeMenu">
      <Logo />
    </RouterLink>

    <nav class="desktop-nav">
      <RouterLink
        v-for="item in navItems"
        :key="item.label"
        :to="item.to"
        class="nav-link"
        :class="{ 'nav-link--active': isNavItemActive(item), 'nav-link--hash': item.hash }"
        @click="handleNavClick(item, $event)"
      >
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="actions">
      <BaseDropdown
        v-model="currentLanguage"
        class="language-switcher"
        :aria-label="t('common.language')"
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
              {{ t('navbar.profile') }}
            </RouterLink>
            <RouterLink class="dropdown-item" :to="dashboardRoute" @click="isUserMenuOpen = false">
              {{ t('navbar.dashboard') }}
            </RouterLink>
            <button class="dropdown-item dropdown-item--danger" type="button" @click="logout">
              {{ t('common.logout') }}
            </button>
          </div>
        </div>
      </template>

      <template v-else>
        <button type="button" class="btn-secondary" @click="$emit('open-login')">
          {{ t('common.login') }}
        </button>
        <button type="button" class="btn-primary" @click="$emit('open-register')">
          {{ t('common.register') }}
        </button>
      </template>
    </div>

    <button class="burger-menu" type="button" :aria-expanded="isMenuOpen" @click="toggleMenu">
      <i :class="isMenuOpen ? 'fas fa-xmark' : 'fas fa-bars'"></i>
    </button>

    <transition name="menu-fade">
      <div v-if="isMenuOpen" class="mobile-menu-overlay" @click="closeMenu">
        <aside class="mobile-menu" @click.stop>
          <div class="mobile-menu-links">
            <RouterLink
              v-for="item in navItems"
              :key="item.label"
              :to="item.to"
              class="mobile-nav-link"
              :class="{ 'mobile-nav-link--active': isNavItemActive(item), 'mobile-nav-link--hash': item.hash }"
              @click="handleMobileNavClick(item, $event)"
            >
              <i :class="item.icon"></i>
              <span>{{ item.label }}</span>
            </RouterLink>

            <RouterLink
              v-for="item in mobileSecondaryLinks"
              :key="item.to"
              :to="item.to"
              class="mobile-nav-link mobile-nav-link--secondary"
              @click="closeMenu"
            >
              <span>{{ item.label }}</span>
            </RouterLink>
          </div>

          <div class="mobile-auth-buttons">
            <label class="mobile-language-switcher">
              <span>{{ t('common.language') }}</span>
              <BaseDropdown
                v-model="currentLanguage"
                :aria-label="t('common.language')"
                :options="languageOptions"
                full-width
                align="right"
                :show-selected-hint="false"
                @change="changeLanguage"
              />
            </label>

            <template v-if="user">
              <span class="mobile-user-email">{{ user.email }}</span>
              <RouterLink v-if="mobilePrimaryLink" class="btn-primary" :to="mobilePrimaryLink.to" @click="closeMenu">
                {{ mobilePrimaryLink.label }}
              </RouterLink>
              <button type="button" class="btn-secondary" @click="logout">{{ t('common.logout') }}</button>
            </template>

            <template v-else>
              <button type="button" class="btn-secondary" @click="openLoginFromMenu">
                {{ t('common.login') }}
              </button>
              <button type="button" class="btn-primary" @click="openRegisterFromMenu">
                {{ t('common.register') }}
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
import { useI18n } from '@/i18n'
import { localizeFullPath } from '@/router/locale'
import BaseDropdown from './BaseDropdown.vue'
import Logo from './Logo.vue'

function normalizeAccountType(accountType) {
  if (accountType === 'user') return 'candidate'
  return accountType || ''
}

function routeForAccount(accountType) {
  const normalizedType = normalizeAccountType(accountType)

  if (normalizedType === 'candidate') return '/dashboard'
  if (normalizedType === 'employer') return '/employer-dashboard'
  if (normalizedType === 'admin') return '/admin'

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
    const { t } = useI18n()

    return {
      authState: state,
      logoutAuth,
      uiStore,
      t,
    }
  },

  data() {
    return {
      isUserMenuOpen: false,
      isMenuOpen: false,
      languageOptions: [
        { value: 'ru', label: 'RU', hint: 'Русский' },
        { value: 'en', label: 'EN', hint: 'English' },
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

    navItems() {
      return [
        { label: this.t('navbar.jobs'), to: '/jobs', icon: 'fas fa-briefcase' },
        { label: this.t('navbar.employers'), to: '/', icon: 'fas fa-users' },
        { label: this.t('navbar.resume'), to: '/resume-builder', icon: 'fas fa-file-lines' },
        { label: this.t('navbar.about'), to: '/about', icon: 'fas fa-circle-info' },
        { label: this.t('navbar.pricing'), to: '/#pricing', icon: 'fas fa-tags', hash: '#pricing' },
      ]
    },

    dashboardRoute() {
      return routeForAccount(this.user?.account_type)
    },

    accountTypeLabel() {
      if (this.normalizedAccountType === 'candidate') return this.t('navbar.accountCandidate')
      if (this.normalizedAccountType === 'employer') return this.t('navbar.accountEmployer')
      if (this.normalizedAccountType === 'admin') return this.t('navbar.accountAdmin')
      return 'Account'
    },

    mobileAccountLinks() {
      if (!this.user) return []

      if (this.normalizedAccountType === 'candidate') {
        return [{ label: this.t('navbar.profile'), to: '/profile', primary: true }]
      }

      if (this.normalizedAccountType === 'admin') {
        return [
          { label: this.t('navbar.adminPanel'), to: '/admin', primary: true },
          { label: this.t('navbar.employerDashboard'), to: '/employer-dashboard' },
          { label: this.t('navbar.jobs'), to: '/admin?section=jobs' },
          { label: this.t('navbar.profile'), to: '/profile' },
        ]
      }

      return [
        { label: this.t('navbar.dashboard'), to: '/employer-dashboard', primary: true },
        { label: this.t('navbar.myJobs'), to: '/employer-dashboard?section=jobs' },
        { label: this.t('navbar.responses'), to: '/employer-dashboard?section=responses' },
        { label: this.t('navbar.messages'), to: '/employer-dashboard?section=messages' },
        { label: this.t('navbar.plans'), to: '/employer-dashboard?section=pricing' },
        { label: this.t('navbar.profile'), to: '/profile' },
      ]
    },

    mobilePrimaryLink() {
      return this.mobileAccountLinks.find((item) => item.to === '/profile') || null
    },

    mobileSecondaryLinks() {
      return this.mobileAccountLinks.filter((item) => item.to !== '/profile')
    },
  },

  methods: {
    isNavItemActive(item) {
      if (item.hash) return false
      return this.$route.path === item.to
    },

    scrollToHash(hash, duration = 1100) {
      const target = document.querySelector(hash)
      if (!target) return

      const navbar = document.querySelector('.navbar')
      const offset = navbar ? navbar.offsetHeight + 20 : 96
      const startY = window.scrollY
      const targetTop = target.getBoundingClientRect().top + window.scrollY - offset
      const distance = targetTop - startY
      const startTime = performance.now()

      const easeInOutCubic = (progress) => {
        return progress < 0.5
          ? 4 * progress * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 3) / 2
      }

      const step = (currentTime) => {
        const elapsed = currentTime - startTime
        const progress = Math.min(elapsed / duration, 1)
        const easedProgress = easeInOutCubic(progress)

        window.scrollTo({
          top: startY + distance * easedProgress,
          behavior: 'auto',
        })

        if (progress < 1) {
          window.requestAnimationFrame(step)
        }
      }

      window.requestAnimationFrame(step)
    },

    handleNavClick(item, event) {
      if (!item.hash || this.$route.path !== '/') return

      event.preventDefault()

      if (this.$route.hash !== item.hash) {
        this.$router.push({ path: '/', hash: item.hash })
        return
      }

      this.scrollToHash(item.hash)
    },

    handleMobileNavClick(item, event) {
      this.closeMenu()
      this.handleNavClick(item, event)
    },

    changeLanguage() {
      this.uiStore.setLanguage(this.currentLanguage)
      const nextPath = localizeFullPath(this.$route.fullPath, this.currentLanguage)
      if (nextPath !== this.$route.fullPath) {
        this.$router.replace(nextPath)
      }
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
      this.$router.replace(localizeFullPath('/', this.currentLanguage))
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
.nav-link.router-link-active,
.nav-link--active {
  color: var(--brand-strong);
}

.nav-link:hover::after,
.nav-link.router-link-active::after,
.nav-link--active::after {
  transform: scaleX(1);
}

.nav-link--hash.router-link-active {
  color: var(--text-primary);
}

.nav-link--hash.router-link-active::after {
  transform: scaleX(0);
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
  background: rgba(247, 250, 248, 0.32);
  z-index: 1000;
  backdrop-filter: none;
}

.mobile-menu {
  position: fixed;
  top: 0;
  right: 0;
  width: 75vw;
  max-width: 22rem;
  height: 100vh;
  background: color-mix(in srgb, var(--surface-primary) 96%, white);
  box-shadow: -1rem 0 2rem rgba(17, 24, 39, 0.08);
  padding: 5rem 1.5rem 2rem;
  overflow-y: auto;
  animation: slideIn 0.3s ease-out;
}

.mobile-menu-links {
  display: grid;
  gap: 0.35rem;
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

.mobile-nav-link.router-link-active,
.mobile-nav-link--active {
  color: var(--brand-strong);
  background: var(--brand-soft);
}

.mobile-nav-link--hash.router-link-active {
  color: var(--text-primary);
  background: transparent;
}

.mobile-nav-link--secondary {
  padding-left: 2.75rem;
  border: 0.0625rem solid var(--border-subtle);
  background: var(--surface-primary);
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
