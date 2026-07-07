<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
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
const attemptsMessage = ref('')

const form = reactive({
  accessToken: '',
})

const CONFIG = {
  colors: {
    particle: { r: 0, g: 230, b: 118 },
    line: { r: 0, g: 230, b: 118 },
  },
  particles: {
    density: 0.06,
    minCount: 15,
    maxCount: 400,
    speed: 10,
    minSize: 1.5,
    maxSize: 5.5,
    minAlpha: 0.7,
    maxAlpha: 1,
    mouseRepelForce: 0.6,
  },
  connections: {
    distance: 200,
    lineWidth: 1,
    maxOpacity: 0.3,
  },
  mouse: {
    radius: 150,
  },
}

let animationFrameId = null
let particles = []
let ctx = null

const mouse = { x: undefined, y: undefined, active: false }

const getParticleCount = () => {
  const canvas = canvasRef.value
  if (!canvas) return CONFIG.particles.minCount

  const area = (canvas.width * canvas.height) / 1000
  const count = Math.floor(area * CONFIG.particles.density)
  return Math.max(CONFIG.particles.minCount, Math.min(CONFIG.particles.maxCount, count))
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
    ctx.fillStyle = `rgba(${CONFIG.colors.particle.r}, ${CONFIG.colors.particle.g}, ${CONFIG.colors.particle.b}, ${this.alpha})`
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
        ctx.strokeStyle = `rgba(${CONFIG.colors.line.r}, ${CONFIG.colors.line.g}, ${CONFIG.colors.line.b}, ${opacity * CONFIG.connections.maxOpacity})`
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
  if (!canvas) return

  particles = Array.from({ length: getParticleCount() }, () => new Particle(canvas))
}

const handleResize = () => {
  const canvas = canvasRef.value
  if (!canvas) return

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  initParticles()
}

const handleMouseMove = (event) => {
  mouse.x = event.clientX
  mouse.y = event.clientY
  mouse.active = true
}

const handleMouseOut = () => {
  mouse.active = false
}

const handleTouchMove = (event) => {
  if (!event.touches.length) return
  mouse.x = event.touches[0].clientX
  mouse.y = event.touches[0].clientY
  mouse.active = true
}

const handleTouchEnd = () => {
  mouse.active = false
}

const reloadCurrentPage = () => {
  if (typeof window === 'undefined') return
  window.location.replace(window.location.href)
}

const submit = async () => {
  errorMessage.value = ''
  attemptsMessage.value = ''

  try {
    const authorized = await betaAccess.login(form)
    if (!authorized) {
      errorMessage.value = 'Invalid access token.'
      return
    }

    const locale = getLocaleFromPath(route.path) || uiStore.language || 'ru'
    const target = typeof route.query.redirect === 'string'
      ? route.query.redirect
      : withLocale('/', locale)

    await router.replace(target)
  } catch (error) {
    const remainingAttempts = error?.payload?.detail?.remaining_attempts
    const isBlocked = error?.payload?.detail?.blocked === true

    if (
      error?.status === 500
      || error?.status === 404
      || error?.status === 0
      || isBlocked
      || (typeof remainingAttempts === 'number' && remainingAttempts <= 0)
    ) {
      reloadCurrentPage()
      return
    }

    errorMessage.value = 'Invalid access token.'

    if (typeof remainingAttempts === 'number' && remainingAttempts > 0) {
      attemptsMessage.value = `${remainingAttempts} attempt${remainingAttempts === 1 ? '' : 's'} remaining before IP block.`
    }
  }
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return

  ctx = canvas.getContext('2d')
  handleResize()

  window.addEventListener('resize', handleResize)
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseout', handleMouseOut)
  window.addEventListener('touchmove', handleTouchMove)
  window.addEventListener('touchend', handleTouchEnd)

  animate()
})

onBeforeUnmount(() => {
  if (animationFrameId) {
    window.cancelAnimationFrame(animationFrameId)
  }

  window.removeEventListener('resize', handleResize)
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseout', handleMouseOut)
  window.removeEventListener('touchmove', handleTouchMove)
  window.removeEventListener('touchend', handleTouchEnd)

  particles = []
  ctx = null
})
</script>

<template>
  <main class="secure-access">
    <div class="particle-container">
      <canvas ref="canvasRef"></canvas>
    </div>

    <form class="secure-access__form" @submit.prevent="submit">
      <p class="secure-access__hint">Enter your beta testing access key</p>
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
      <p v-if="errorMessage" class="secure-access__error">{{ errorMessage }}</p>
      <p v-if="attemptsMessage" class="secure-access__warning">{{ attemptsMessage }}</p>
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
}

.secure-access__hint {
  color: #fff;
  text-align: center;
  font-size: 0.95rem;
  line-height: 1.5;
}

.secure-access__form input,
.secure-access__form button {
  width: 100%;
  min-height: 3.35rem;
  padding: 0.95rem 1rem;
  border: 0.0625rem solid rgba(255, 255, 255, 0.18);
  background: rgba(5, 5, 5, 0.88);
  color: #fff;
  font: inherit;
}

.secure-access__form input::placeholder {
  color: #8f8f8f;
}

.secure-access__form input:focus-visible,
.secure-access__form button:focus-visible {
  outline: none;
  border-color: #fff;
}

.secure-access__form button {
  cursor: pointer;
  font-weight: 700;
  background: #fff;
  color: #000;
}

.secure-access__form button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.secure-access__error {
  color: #ff6b6b;
  font-size: 0.92rem;
  text-align: center;
}

.secure-access__warning {
  color: #ffd166;
  font-size: 0.92rem;
  text-align: center;
}
</style>
