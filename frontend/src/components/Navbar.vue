<template>
  <header class="navbar">
    <RouterLink to="/" class="logo-link" @click="closeMenu">
      <Logo />
    </RouterLink>

    <nav class="desktop-nav">
      <template v-for="item in navItems" :key="item.label">
        <div
          v-if="item.menu === 'jobs'"
          class="jobs-menu"
        >
          <button
            type="button"
            class="nav-link nav-link--button"
            :class="{ 'nav-link--active': isNavItemActive(item) || isJobsMenuOpen }"
            :aria-expanded="isJobsMenuOpen"
            :aria-label="t('navbar.jobsMenuOpen')"
            @click="toggleJobsMenu"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
            <i class="fas fa-chevron-down jobs-menu__chevron" :class="{ 'jobs-menu__chevron--open': isJobsMenuOpen }"></i>
          </button>

          <transition name="menu-fade">
            <div v-if="isJobsMenuOpen" class="jobs-menu__dropdown">
              <div
                v-for="section in jobsMenuSections"
                :key="section.title"
                class="jobs-menu__section"
              >
                <p class="jobs-menu__title">{{ section.title }}</p>
                <RouterLink
                  v-for="entry in section.items"
                  :key="entry.label"
                  :to="entry.to"
                  class="jobs-menu__link"
                  @click="closeAllMenus"
                >
                  {{ entry.label }}
                </RouterLink>
              </div>
            </div>
          </transition>
        </div>

        <RouterLink
          v-else
          :to="item.to"
          class="nav-link"
          :class="{ 'nav-link--active': isNavItemActive(item), 'nav-link--hash': item.hash }"
          @click="handleNavClick(item, $event)"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </RouterLink>
      </template>
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
            <RouterLink class="dropdown-item" :to="dashboardRoute" @click="isUserMenuOpen = false">
              {{ t('navbar.dashboard') }}
            </RouterLink>
            <RouterLink
              v-if="normalizedAccountType === 'admin'"
              class="dropdown-item"
              to="/profile"
              @click="isUserMenuOpen = false"
            >
              {{ t('navbar.profile') }}
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
      <div v-if="isMenuOpen" class="mobile-menu-overlay">
        <aside class="mobile-menu" @click.stop>
          <div class="mobile-user-card">
            <div class="mobile-user-card__avatar">
              <img v-if="mobileUserAvatar" :src="mobileUserAvatar" :alt="mobileUserTitle" />
              <span v-else>{{ mobileUserInitials }}</span>
            </div>

            <div class="mobile-user-card__meta">
              <span class="mobile-user-card__role">{{ mobileUserRole }}</span>
              <strong>{{ mobileUserTitle }}</strong>
            </div>
          </div>

          <div class="mobile-menu-links">
            <template v-for="item in navItems" :key="item.label">
              <div v-if="item.menu === 'jobs'" class="mobile-jobs-menu">
                <button
                  type="button"
                  class="mobile-nav-link mobile-nav-link--button"
                  :class="{ 'mobile-nav-link--active': isNavItemActive(item) || isMobileJobsMenuOpen }"
                  @click="isMobileJobsMenuOpen = !isMobileJobsMenuOpen"
                >
                  <span class="mobile-nav-link__main">
                    <i :class="item.icon"></i>
                    <span>{{ item.label }}</span>
                  </span>
                  <i class="fas fa-chevron-down mobile-jobs-menu__chevron" :class="{ 'mobile-jobs-menu__chevron--open': isMobileJobsMenuOpen }"></i>
                </button>

                <div v-if="isMobileJobsMenuOpen" class="mobile-jobs-menu__dropdown">
                  <div
                    v-for="section in jobsMenuSections"
                    :key="section.title"
                    class="mobile-jobs-menu__section"
                  >
                    <p class="mobile-jobs-menu__title">{{ section.title }}</p>
                    <RouterLink
                      v-for="entry in section.items"
                      :key="entry.label"
                      :to="entry.to"
                      class="mobile-jobs-menu__link"
                      @click="closeMenu"
                    >
                      {{ entry.label }}
                    </RouterLink>
                  </div>
                </div>
              </div>

              <RouterLink
                v-else
                :to="item.to"
                class="mobile-nav-link"
                :class="{ 'mobile-nav-link--active': isNavItemActive(item), 'mobile-nav-link--hash': item.hash }"
                @click="handleMobileNavClick(item, $event)"
              >
                <i :class="item.icon"></i>
                <span>{{ item.label }}</span>
              </RouterLink>
            </template>

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
  if (normalizedType === 'employer') return '/dashboard?section=jobs'
  if (normalizedType === 'admin') return '/dashboard?section=jobs'

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
      isJobsMenuOpen: false,
      isMobileJobsMenuOpen: false,
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
      const items = [
        { label: this.t('navbar.jobs'), to: '/', icon: 'fas fa-briefcase', menu: 'jobs' },
        { label: this.t('navbar.employers'), to: '/employers', icon: 'fas fa-users' },
        { label: this.t('navbar.resume'), to: '/resume-builder', icon: 'fas fa-file-lines' },
        { label: this.t('navbar.about'), to: '/about', icon: 'fas fa-circle-info' },
        { label: this.t('navbar.pricing'), to: '/pricing', icon: 'fas fa-tags' },
      ]

      if (this.user) {
        items.push({
          label: this.t('navbar.dashboard'),
          to: this.dashboardRoute,
          icon: 'fas fa-table-columns',
        })
      }

      return items
    },

    jobsMenuSections() {
      return [
        {
          title: this.t('navbar.jobsMenuBrowse'),
          items: [
            { label: this.t('navbar.jobsMenuAll'), to: { path: '/jobs', hash: '#jobs-results' } },
            { label: this.t('navbar.jobsMenuCategories'), to: '/jobs/categories' },
            { label: this.t('navbar.jobsMenuLocation'), to: '/jobs/latvia-cities' },
            { label: this.t('navbar.jobsMenuAbroad'), to: { path: '/jobs', query: { abroad: '1' }, hash: '#jobs-results' } },
            { label: this.t('navbar.jobsMenuHousing'), to: { path: '/jobs', query: { housing: '1' }, hash: '#jobs-results' } },
            { label: this.t('navbar.jobsMenuTransport'), to: { path: '/jobs', query: { transport: '1' }, hash: '#jobs-results' } },
          ],
        },
        {
          title: this.t('navbar.jobsMenuTools'),
          items: [
            { label: this.t('navbar.jobsMenuSaved'), to: { path: '/jobs', query: { tab: 'favorites', bookmarked: '1' }, hash: '#jobs-results' } },
            { label: this.t('navbar.jobsMenuSalary'), to: { path: '/jobs', query: { sort: 'salary' }, hash: '#jobs-results' } },
            { label: this.t('navbar.jobsMenuCountries'), to: '/jobs/countries' },
          ],
        },
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
        return [
          { label: this.t('navbar.profile'), to: '/profile', primary: true, icon: 'fas fa-user' },
          { label: this.t('navbar.dashboard'), to: '/dashboard', icon: 'fas fa-table-columns' },
        ]
      }

      if (this.normalizedAccountType === 'admin') {
        return [
          { label: this.t('navbar.dashboard'), to: '/dashboard?section=jobs', primary: true, icon: 'fas fa-table-columns' },
          { label: this.t('navbar.responses'), to: '/dashboard?section=responses', icon: 'fas fa-inbox' },
          { label: this.t('navbar.messages'), to: '/dashboard?section=messages', icon: 'fas fa-message' },
          { label: this.t('navbar.plans'), to: '/dashboard?section=pricing', icon: 'fas fa-credit-card' },
          { label: this.t('navbar.adminPanel'), to: '/admin', icon: 'fas fa-shield-halved' },
          { label: this.t('navbar.profile'), to: '/profile', icon: 'fas fa-user' },
        ]
      }

      return [
        { label: this.t('navbar.dashboard'), to: '/dashboard?section=jobs', primary: true, icon: 'fas fa-table-columns' },
        { label: this.t('navbar.myJobs'), to: '/dashboard?section=jobs', icon: 'fas fa-briefcase' },
        { label: this.t('navbar.responses'), to: '/dashboard?section=responses', icon: 'fas fa-inbox' },
        { label: this.t('navbar.messages'), to: '/dashboard?section=messages', icon: 'fas fa-message' },
        { label: this.t('navbar.plans'), to: '/dashboard?section=pricing', icon: 'fas fa-credit-card' },
      ]
    },

    mobilePrimaryLink() {
      return this.mobileAccountLinks.find((item) => item.to === '/profile') || null
    },

    mobileUserAvatar() {
      return this.user?.avatar_url || this.user?.company_logo_url || ''
    },

    mobileGuestLabel() {
      return this.currentLanguage === 'en' ? 'Guest' : 'Гость'
    },

    mobileUserRole() {
      return this.user ? this.accountTypeLabel : this.mobileGuestLabel
    },

    mobileUserTitle() {
      return this.user?.email || this.mobileGuestLabel
    },

    mobileUserInitials() {
      const source = this.user?.full_name || this.user?.company_name || this.user?.email || this.mobileGuestLabel
      return source
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0])
        .join('')
        .toUpperCase()
    },
  },

  methods: {
    isNavItemActive(item) {
      if (item.menu === 'jobs') {
        return this.$route.path === '/' || this.$route.path === '/jobs'
      }

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
      if (!item.hash || this.$route.path !== (item.hashBasePath || '/')) return

      event.preventDefault()

      if (this.$route.hash !== item.hash) {
        this.$router.push({ path: item.hashBasePath || '/', hash: item.hash })
        return
      }

      this.scrollToHash(item.hash)
    },

    handleMobileNavClick(item, event) {
      this.closeMenu()
      this.handleNavClick(item, event)
    },

    toggleJobsMenu() {
      this.isJobsMenuOpen = !this.isJobsMenuOpen
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
      this.isMobileJobsMenuOpen = false
      document.body.style.overflow = ''
    },

    closeAllMenus() {
      this.isJobsMenuOpen = false
      this.isUserMenuOpen = false
      this.closeMenu()
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
      this.isJobsMenuOpen = false
      this.$router.replace(localizeFullPath('/', this.currentLanguage))
    },

    handleResize() {
      if (window.innerWidth > 944 && this.isMenuOpen) {
        this.closeMenu()
      }
    },

    closeDesktopMenusOnOutsideClick(event) {
      const target = event.target

      if (!target.closest('.jobs-menu')) {
        this.isJobsMenuOpen = false
      }

      if (!target.closest('.user-menu-wrapper')) {
        this.isUserMenuOpen = false
      }
    },
  },

  mounted() {
    window.addEventListener('resize', this.handleResize)
    document.addEventListener('click', this.closeDesktopMenusOnOutsideClick)
    this.uiStore.initialize()
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    document.removeEventListener('click', this.closeDesktopMenusOnOutsideClick)
    document.body.style.overflow = ''
  },

  watch: {
    $route() {
      this.isJobsMenuOpen = false
      this.isUserMenuOpen = false
      this.isMobileJobsMenuOpen = false
    },
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
  gap: 1.5rem;
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

.nav-link--button {
  border: none;
  background: transparent;
  font: inherit;
  cursor: pointer;
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

.jobs-menu {
  position: relative;
}

.jobs-menu__chevron {
  font-size: 0.76rem;
  transition: transform 0.2s ease;
}

.jobs-menu__chevron--open {
  transform: rotate(180deg);
}

.jobs-menu__dropdown {
  position: absolute;
  top: calc(100% + 0.9rem);
  left: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(12rem, 1fr));
  gap: 1.1rem;
  min-width: 32rem;
  padding: 1.2rem 1.35rem;
  border-radius: 1.35rem;
  border: 0.0625rem solid var(--border-subtle);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 251, 248, 0.98));
  box-shadow: 0 1.6rem 3rem rgba(15, 23, 42, 0.12);
}

.jobs-menu__section {
  display: grid;
  gap: 0.05rem;
  align-content: start;
  align-self: start;
}

.jobs-menu__title {
  margin: 0 0 0.45rem;
  font-size: 0.9rem;
  font-weight: 900;
  color: var(--text-primary);
}

.jobs-menu__link {
  display: block;
  padding: 0.35rem 0;
  color: var(--text-primary);
  text-decoration: none;
  border-radius: 0.7rem;
  transition: color 0.2s ease, transform 0.2s ease;
}

.jobs-menu__link:hover,
.jobs-menu__link:focus-visible {
  color: var(--brand-strong);
  transform: translateX(0.15rem);
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

.user-email {
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
  background: transparent;
  height: 100vh;
  z-index: 1000;
}

.mobile-menu {
  position: fixed;
  top: 0;
  right: 0;
  width: 75vw;
  max-width: 22rem;
  height: 100vh;
  background: #fff;
  box-shadow: -1rem 0 2rem rgba(17, 24, 39, 0.08);
  padding: 5rem 1.5rem 2rem;
  overflow-y: auto;
  animation: slideIn 0.3s ease-out;
}

.mobile-user-card {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 0 0 1.1rem;
  margin-bottom: 0.95rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
}

.mobile-user-card__avatar {
  width: 3.35rem;
  height: 3.35rem;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 999rem;
  background: linear-gradient(135deg, color-mix(in srgb, var(--brand-soft) 70%, white), color-mix(in srgb, var(--brand-base) 20%, white));
  color: var(--brand-strong);
  font-size: 1rem;
  font-weight: 900;
  box-shadow: inset 0 0 0 0.0625rem color-mix(in srgb, var(--brand-base) 18%, var(--border-subtle));
}

.mobile-user-card__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mobile-user-card__meta {
  min-width: 0;
  display: grid;
  gap: 0.2rem;
}

.mobile-user-card__meta strong {
  color: var(--text-primary);
  font-size: 0.98rem;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mobile-user-card__role {
  color: var(--brand-strong);
  font-size: 0.72rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.08em;
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

.mobile-nav-link--button {
  width: 100%;
  justify-content: space-between;
  border: none;
  background: transparent;
  font: inherit;
  cursor: pointer;
}

.mobile-nav-link__main {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
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

.mobile-jobs-menu {
  display: grid;
  gap: 0.4rem;
}

.mobile-jobs-menu__chevron {
  font-size: 0.82rem;
  transition: transform 0.2s ease;
}

.mobile-jobs-menu__chevron--open {
  transform: rotate(180deg);
}

.mobile-jobs-menu__dropdown {
  display: grid;
  gap: 0.9rem;
  padding: 0.25rem 0.35rem 0.35rem 2.8rem;
}

.mobile-jobs-menu__section {
  display: grid;
  gap: 0.25rem;
}

.mobile-jobs-menu__title {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.mobile-jobs-menu__link {
  color: var(--text-primary);
  text-decoration: none;
  padding: 0.35rem 0;
}

.mobile-jobs-menu__link:hover,
.mobile-jobs-menu__link:focus-visible {
  color: var(--brand-strong);
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
