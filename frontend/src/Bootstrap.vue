<template>
  <router-view />
</template>

<script setup>
import { onBeforeUnmount, onMounted } from 'vue'
import { useAuth } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import router from './router'
import { getLocaleFromPath, stripLocaleFromPath, withLocale } from './router/locale'

const auth = useAuth()
const uiStore = useUiStore()

const handleUnauthorized = () => {
  const currentRoute = router.currentRoute.value
  const logicalPath = stripLocaleFromPath(currentRoute.path)

  if (!currentRoute.meta.requiresAuth || logicalPath === '/unauthorized') {
    return
  }

  auth.logout()

  const locale = getLocaleFromPath(currentRoute.path) || uiStore.language || 'ru'
  router.replace({
    path: withLocale('/unauthorized', locale),
    query: {
      redirect: currentRoute.fullPath,
    },
  })
}

onMounted(() => {
  uiStore.initialize()
  auth.loadUser()
  window.addEventListener('app:unauthorized', handleUnauthorized)
})

onBeforeUnmount(() => {
  window.removeEventListener('app:unauthorized', handleUnauthorized)
})
</script>

<style>
@import url(
  'https://fonts.googleapis.com/css2?family=Google+Sans:ital,opsz,wght@0,17..18,400..700;1,17..18,400..700&display=swap');


* {
  margin: 0;
  padding: 0;
  font-style: normal;
  box-sizing: border-box;
}

html, body, #root {
  height: 100%;
}

body {
  overflow: auto;
  color: var(--text-primary);
  background: linear-gradient(
    180deg, rgba(244, 247, 244, 0.96), rgba(244, 247, 244, 0.98)
  );
}

a,
button,
input,
textarea,
select {
  font: inherit;
}

a {
  color: inherit;
}

.surface-card {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1rem;
  background: var(--surface-primary);
  box-shadow: var(--shadow-soft);
}

.surface-section {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.5rem;
  background: var(--surface-elevated);
  box-shadow: var(--shadow-soft);
}

.section-eyebrow {
  margin: 0 0 0.45rem;
  color: var(--brand-strong);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 2.75rem;
  padding: 0.75rem 1.1rem;
  border-radius: 0.875rem;
  text-decoration: none;
  line-height: 1.5;
  cursor: pointer;
  font-weight: 700;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.btn-primary {
  background: linear-gradient(180deg, #1ab16f 0%, #15955d 100%);
  color: #fff;
  border: 0.125rem solid transparent;
  box-shadow: 0 0.875rem 1.8rem rgba(21, 149, 93, 0.18);
}

.btn-secondary {
  border: 0.125rem solid var(--border-strong);
  color: var(--brand-strong);
  background: var(--surface-secondary);
}

.btn-primary:hover,
.btn-secondary:hover {
  transform: translateY(-0.0625rem);
}

.btn-primary:focus-visible,
.btn-secondary:focus-visible,
button:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
a:focus-visible {
  outline: 0.1875rem solid rgba(29, 168, 107, 0.22);
  outline-offset: 0.125rem;
}

input,
textarea,
select {
  color: var(--text-primary);
  background: var(--surface-secondary);
}

input::placeholder,
textarea::placeholder {
  color: color-mix(in srgb, var(--text-muted) 75%, transparent);
}
</style>
