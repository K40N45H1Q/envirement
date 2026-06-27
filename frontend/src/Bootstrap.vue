<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuth } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

const { loadUser } = useAuth()
const uiStore = useUiStore()

onMounted(() => {
  uiStore.initialize()
  loadUser()
})
</script>

<style>
@import url(
  'https://fonts.googleapis.com/css2?family=Google+Sans:ital,opsz,wght@0,17..18,400..700;1,17..18,400..700&display=swap');

:root {
  color-scheme: light;
  --shell-max-width: 100rem;
  --shell-gutter: clamp(1rem, 2vw, 1.5rem);
  --brand-strong: #169b61;
  --brand-base: #1da86b;
  --brand-soft: #e9f8ef;
  --surface-app: #f4f7f4;
  --surface-primary: rgba(255, 255, 255, 0.94);
  --surface-secondary: #ffffff;
  --surface-elevated: rgba(255, 255, 255, 0.88);
  --border-subtle: rgba(27, 42, 35, 0.1);
  --border-strong: rgba(22, 155, 97, 0.22);
  --text-primary: #15201b;
  --text-muted: rgba(21, 32, 27, 0.68);
  --shadow-soft: 0 1rem 2.5rem rgba(21, 32, 27, 0.08);
  --shadow-strong: 0 1.25rem 3rem rgba(18, 45, 31, 0.14);
}

* {
  margin: 0;
  padding: 0;
  font-style: normal;
  box-sizing: border-box;
  font-optical-sizing: auto;
  font-family: "Google Sans", sans-serif;
}

html, body, #root {
  height: 100%;
}

html {
  background:
    radial-gradient(circle at top left, rgba(29, 168, 107, 0.12), transparent 24%),
    radial-gradient(circle at top right, rgba(44, 197, 129, 0.08), transparent 20%),
    var(--surface-app);
}

body {
  color: var(--text-primary);
  background: transparent;
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
