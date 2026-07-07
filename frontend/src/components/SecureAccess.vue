<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { useBetaAccess } from '@/stores/betaAccess'
import { getLocaleFromPath, withLocale } from '@/router/locale'

const router = useRouter()
const route = useRoute()
const uiStore = useUiStore()
const betaAccess = useBetaAccess()
const canvasRef = ref(null)
const errorMessage = ref('')
const form = reactive({ accessToken: '' })

const TEXT = 'Enter your beta testing access token'
const INVALID = 'Invalid access token.'
const BANNED = 'Ваш IP адрес был забанен.'
const GREEN = '#1da86b'
const RED = '#ff0000'

const hexToRgb = (hex) => {
  const value = Number.parseInt(hex.replace('#', ''), 16)
  return { r: (value >> 16) & 255, g: (value >> 8) & 255, b: value & 255 }
}

const color = computed(() => hexToRgb(errorMessage.value ? RED : GREEN))
const hintText = computed(() => errorMessage.value || TEXT)

const CONFIG = {
  particles: { density: 0.06, minCount: 15, maxCount: 400, speed: 10, minSize: 1.5, maxSize: 5.5, minAlpha: 0.7, maxAlpha: 1, mouseRepelForce: 0.6 },
  connections: { distance: 200, lineWidth: 1, maxOpacity: 0.3 },
  mouse: { radius: 150 },
}

let animationFrameId = null
let particles = []
let ctx = null

const mouse = { x: 0, y: 0, active: false }

const attemptsText = (attempts) => `${attempts} attempt${attempts === 1 ? '' : 's'} remaining.`
const invalidText = (attempts) => typeof attempts === 'number' && attempts > 0 ? `${INVALID} ${attemptsText(attempts)}` : INVALID

const getParticleCount = () => {
  const canvas = canvasRef.value
  if (!canvas) return CONFIG.particles.minCount
  return Math.max(CONFIG.particles.minCount, Math.min(CONFIG.particles.maxCount, Math.floor((canvas.width * canvas.height / 1000) * CONFIG.particles.density)))
}

class Particle {
  constructor(canvas) {
    this.canvas = canvas
    this.x = Math.random() * canvas.width
    this.y = Math.random() * canvas.height
    this.size = Math.random() * (CONFIG.particles.maxSize - CONFIG.particles.minSize) + CONFIG.particles.minSize
    this.alpha = Math.random() * (CONFIG.particles.maxAlpha - CONFIG.particles.minAlpha) + CONFIG.particles.minAlpha
    this.baseSpeedX = Math.random() - 0.5
    this.baseSpeedY = Math.random() - 0.5
  }

  update() {
    const speed = CONFIG.particles.speed * 0.1
    this.x += this.baseSpeedX * speed
    this.y += this.baseSpeedY * speed

    if (this.x < 0) this.x = this.canvas.width
    if (this.x > this.canvas.width) this.x = 0
    if (this.y < 0) this.y = this.canvas.height
    if (this.y > this.canvas.height) this.y = 0
    if (!mouse.active) return

    const dx = mouse.x - this.x
    const dy = mouse.y - this.y
    const distance = Math.sqrt(dx * dx + dy * dy)

    if (distance > 0 && distance < CONFIG.mouse.radius) {
      const force = (CONFIG.mouse.radius - distance) / CONFIG.mouse.radius
      this.x -= (dx / distance) * force * CONFIG.particles.mouseRepelForce
      this.y -= (dy / distance) * force * CONFIG.particles.mouseRepelForce
    }
  }

  draw() {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(${color.value.r}, ${color.value.g}, ${color.value.b}, ${this.alpha})`
    ctx.fill()
  }
}

const connectParticles = () => {
  ctx.lineWidth = CONFIG.connections.lineWidth

  for (let i = 0; i < particles.length; i += 1) {
    for (let j = i + 1; j < particles.length; j += 1) {
      const dx = particles[i].x - particles[j].x
      const dy = particles[i].y - particles[j].y
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < CONFIG.connections.distance) {
        const opacity = 1 - distance / CONFIG.connections.distance
        ctx.strokeStyle = `rgba(${color.value.r}, ${color.value.g}, ${color.value.b}, ${opacity * CONFIG.connections.maxOpacity})`
        ctx.beginPath()
        ctx.moveTo(particles[i].x, particles[i].y)
        ctx.lineTo(particles[j].x, particles[j].y)
        ctx.stroke()
      }
    }
  }
}

const animate = () => {
  const canvas = canvasRef.value
  if (!canvas || !ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  particles.forEach((particle) => {
    particle.update()
    particle.draw()
  })
  connectParticles()
  animationFrameId = window.requestAnimationFrame(animate)
}

const initParticles = () => {
  const canvas = canvasRef.value
  if (canvas) particles = Array.from({ length: getParticleCount() }, () => new Particle(canvas))
}

const handleResize = () => {
  const canvas = canvasRef.value
  if (!canvas) return

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  initParticles()
}

const setMouse = (event) => {
  mouse.x = event.touches?.[0]?.clientX ?? event.clientX
  mouse.y = event.touches?.[0]?.clientY ?? event.clientY
  mouse.active = true
}

const clearMouse = () => {
  mouse.active = false
}

const submit = async () => {
  try {
    const authorized = await betaAccess.login(form)

    if (!authorized) {
      errorMessage.value = INVALID
      return
    }

    const locale = getLocaleFromPath(route.path) || uiStore.language || 'ru'
    await router.replace(typeof route.query.redirect === 'string' ? route.query.redirect : withLocale('/', locale))
  } catch (error) {
    const detail = error?.payload?.detail
    const attempts = detail?.remaining_attempts
    const banned = detail?.blocked === true || error?.status === 403 || error?.status === 429 || (typeof attempts === 'number' && attempts <= 0)

    errorMessage.value = banned ? BANNED : invalidText(attempts)
  }
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return

  ctx = canvas.getContext('2d')
  handleResize()

  window.addEventListener('resize', handleResize)
  window.addEventListener('mousemove', setMouse)
  window.addEventListener('touchmove', setMouse)
  window.addEventListener('mouseout', clearMouse)
  window.addEventListener('touchend', clearMouse)

  animate()
})

onBeforeUnmount(() => {
  if (animationFrameId) window.cancelAnimationFrame(animationFrameId)

  window.removeEventListener('resize', handleResize)
  window.removeEventListener('mousemove', setMouse)
  window.removeEventListener('touchmove', setMouse)
  window.removeEventListener('mouseout', clearMouse)
  window.removeEventListener('touchend', clearMouse)

  particles = []
  ctx = null
})
</script>

<template>
  <main class="secure-access">
    <div class="particle-container">
      <canvas ref="canvasRef"></canvas>
    </div>

    <form class="secure-access__form" :class="{ 'secure-access__form--error': errorMessage }" @submit.prevent="submit">
      <p class="secure-access__hint">
        {{ hintText }}
      </p>

      <input
        v-model.trim="form.accessToken"
        type="text"
        autocomplete="off"
        autocapitalize="off"
        spellcheck="false"
        placeholder="Access token"
        required
      >

      <button type="submit" :disabled="betaAccess.isLoading">
        Enter
      </button>
    </form>
  </main>
</template>

<style scoped>
.secure-access {
  position: relative;
  min-height: 100vh;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #000;
  padding: 1.5rem;
}

.particle-container {
  position: absolute;
  inset: 0;
  z-index: 0;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.secure-access__form {
  position: relative;
  z-index: 1;
  width: min(100%, 22rem);
  display: grid;
  gap: 0.9rem;
  --access-color: var(--brand-base);
}

.secure-access__form--error {
  --access-color: #ff0000;
}

.secure-access__hint {
  margin: 0;
  color: var(--access-color);
  text-align: center;
  line-height: 1.5;
  font-size: 1rem;
  font-weight: 400;
}

.secure-access__form button,
.secure-access__form input {
  padding: 0.95rem 1rem;
  min-height: 3.35rem !important;
  color: var(--access-color) !important;
  background-color: #000 !important;
  border-radius: 1rem !important;
  border: 0.0625rem solid var(--access-color) !important;
  text-align: center;
}

.secure-access__form button:hover {
  color: #000 !important;
  background-color: var(--access-color) !important;
}

.secure-access__form input::placeholder {
  color: #8f8f8f;
}

.secure-access__form input:focus-visible,
.secure-access__form button:focus-visible {
  outline: none;
  border-color: var(--access-color) !important;
}

.secure-access__form button {
  cursor: pointer;
  font-weight: 700;
}

.secure-access__form button:disabled {
  opacity: 0.7;
  cursor: wait;
}
</style>