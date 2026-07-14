﻿<template>
  <header class="navbar">
    <RouterLink to="/" class="logo-link logo-link--header" @click="closeMenu">
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

        <button
          v-else-if="item.action === 'login'"
          type="button"
          class="nav-link nav-link--button"
          @click="$emit('open-login')"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </button>

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

    <button
      class="burger-menu"
      :class="{ 'burger-menu--open': isMenuOpen }"
      type="button"
      :aria-expanded="isMenuOpen"
      @click="toggleMenu"
    >
      <i :class="isMenuOpen ? 'fas fa-xmark' : 'fas fa-bars'"></i>
    </button>

    <transition name="menu-fade">
      <div v-if="isMenuOpen" class="mobile-menu-overlay" @click="closeMenu">
        <aside class="mobile-menu" @click.stop>
          <div class="mobile-menu-header">
            <RouterLink to="/" class="logo-link logo-link--mobile-menu" @click="closeMenu">
              <Logo />
            </RouterLink>

            <BaseDropdown
              v-model="currentLanguage"
              class="mobile-menu-language"
              :aria-label="t('common.language')"
              :options="languageOptions"
              size="sm"
              align="right"
              :show-selected-hint="false"
              @change="changeLanguage"
            />
          </div>

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
            <template v-for="item in mobileNavItems" :key="item.label">
              <button
                v-if="item.action === 'login'"
                type="button"
                class="mobile-nav-link nav-link--button"
                @click="openLoginFromMenu"
              >
                <i :class="item.icon"></i>
                <span>{{ item.label }}</span>
              </button>

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
      isJobsMenuOpen: false,
      languageOptions: [
        { value: 'lv', label: 'LV', hint: 'Latviešu' },
        { value: 'en', label: 'EN', hint: 'English' },
        { value: 'ru', label: 'RU', hint: 'Русский' },
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
      ]

      if (!this.user || this.normalizedAccountType === 'candidate') {
        items.push({
          label: this.t('navbar.resume'),
          ...(this.user ? { to: '/createcv' } : { action: 'login' }),
          icon: 'fas fa-file-lines',
        })
      }

      items.push(
        { label: this.t('navbar.about'), to: '/about', icon: 'fas fa-circle-info' },
        { label: this.t('navbar.pricing'), to: '/pricing', icon: 'fas fa-tags' },
      )

      if (this.user) {
        items.push({
          label: this.t('navbar.dashboard'),
          to: this.dashboardRoute,
          icon: 'fas fa-table-columns',
        })
      }

      return items
    },

    mobileNavItems() {
      return this.navItems.map((item) => {
        if (item.menu !== 'jobs') return item

        return {
          ...item,
          to: '/jobs',
        }
      })
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
      if (this.normalizedAccountType === 'candidate') {
        return String(this.user?.full_name || '').trim() || this.t('navbar.accountCandidate')
      }
      if (this.normalizedAccountType === 'employer') {
        return String(this.user?.company_registration_number || '').trim() || this.t('navbar.accountEmployer')
      }
      if (this.normalizedAccountType === 'admin') return this.t('navbar.accountAdmin')
      return this.t('common.account')
    },

    mobilePrimaryLink() {
      return this.mobileNavItems.find((item) => item.to === this.dashboardRoute) || null
    },

    mobileUserAvatar() {
      return this.user?.avatar_url || this.user?.company_logo_url || ''
    },

    mobileGuestLabel() {
      return this.t('navbar.guest')
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
    },
  },
}
</script>

<style scoped src="../styles/components/navbar.css"></style>
