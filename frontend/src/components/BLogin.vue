<script setup>
import { computed, onMounted, onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { useBetaAccess } from '@/stores/betaAccess'
import { getLocaleFromPath, withLocale } from '@/router/locale'
const TEXT_CONSTANTS = {
  hintDefault: 'Provide your personal access token',
  invalidToken: 'Please contact your administrator',
  bannedIp: ':('
}
const GRID_CONSTANTS = {
  densityFactor: 0.01,
  minParticles: 50,
  maxParticles: 50,
  speedMultiplier: 1,
  maxConnectionDistance: 300,
  lineWidth: 0.5
}
const PARTICLE_CONSTANTS = {
  radius: 3,
  minVelocity: -0.5,
  maxVelocity: 0.5
}
const COLOR_CONSTANTS = {
  ok: '#1da86b',
  error: '#f00'
}
const FORM_DEFAULTS = {
  accessToken: ''
}
const FIXED_CANVAS_WIDTH = 1920
const FIXED_CANVAS_HEIGHT = 1080
const router = useRouter()
const route = useRoute()
const uiStore = useUiStore()
const betaAccessStore = useBetaAccess()
const canvasElement = ref(null)
const errorMessage = ref('')
const formState = reactive({ ...FORM_DEFAULTS })
let canvasContext = null
let animationFrameId = null
let particleList = []
const currentColor = computed(() => (errorMessage.value ? COLOR_CONSTANTS.error : COLOR_CONSTANTS.ok))
const currentHintText = computed(() => errorMessage.value || TEXT_CONSTANTS.hintDefault)

const randomBetween = (min, max) => Math.random() * (max - min) + min

const calculateParticleCount = () => {
  const calculated = Math.floor(((FIXED_CANVAS_WIDTH * FIXED_CANVAS_HEIGHT) / 1000) * GRID_CONSTANTS.densityFactor)
  return Math.max(GRID_CONSTANTS.minParticles, Math.min(GRID_CONSTANTS.maxParticles, calculated))
}
class Particle {
  constructor() {
    this.x = randomBetween(0, FIXED_CANVAS_WIDTH)
    this.y = randomBetween(0, FIXED_CANVAS_HEIGHT)
    this.radius = PARTICLE_CONSTANTS.radius
    this.velocityX = randomBetween(PARTICLE_CONSTANTS.minVelocity, PARTICLE_CONSTANTS.maxVelocity)
    this.velocityY = randomBetween(PARTICLE_CONSTANTS.minVelocity, PARTICLE_CONSTANTS.maxVelocity)
  }
  update() {
    this.x += this.velocityX * GRID_CONSTANTS.speedMultiplier
    this.y += this.velocityY * GRID_CONSTANTS.speedMultiplier
    if (this.x < 0) this.x = FIXED_CANVAS_WIDTH
    if (this.x > FIXED_CANVAS_WIDTH) this.x = 0
    if (this.y < 0) this.y = FIXED_CANVAS_HEIGHT
    if (this.y > FIXED_CANVAS_HEIGHT) this.y = 0
  }
  draw() {
    canvasContext.beginPath()
    canvasContext.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
    canvasContext.fillStyle = currentColor.value
    canvasContext.fill()
  }
}
const drawConnections = () => {
  canvasContext.strokeStyle = currentColor.value
  canvasContext.lineWidth = GRID_CONSTANTS.lineWidth
  particleList.forEach((particleA, i) => {
    particleList.slice(i + 1).forEach((particleB) => {
      const distance = Math.hypot(particleA.x - particleB.x, particleA.y - particleB.y)
      if (distance < GRID_CONSTANTS.maxConnectionDistance) {
        canvasContext.beginPath()
        canvasContext.moveTo(particleA.x, particleA.y)
        canvasContext.lineTo(particleB.x, particleB.y)
        canvasContext.stroke()
      }
    })
  })
}
const initializeCanvas = () => {
  const canvas = canvasElement.value
  if (!canvas) return
  canvas.width = FIXED_CANVAS_WIDTH
  canvas.height = FIXED_CANVAS_HEIGHT
  particleList = Array.from({ length: calculateParticleCount() }, () => new Particle())
}
const animate = () => {
  const canvas = canvasElement.value
  if (!canvas || !canvasContext) return
  canvasContext.clearRect(0, 0, FIXED_CANVAS_WIDTH, FIXED_CANVAS_HEIGHT)
  particleList.forEach((particle) => {
    particle.update()
    particle.draw()
  })
  drawConnections()
  animationFrameId = requestAnimationFrame(animate)
}
const submitForm = async () => {
  try {
    const isSuccess = await betaAccessStore.login(formState)
    if (!isSuccess) {
      errorMessage.value = TEXT_CONSTANTS.invalidToken
      return
    }
    const locale = getLocaleFromPath(route.path) || uiStore.language || 'lv'
    const redirect = typeof route.query.redirect === 'string' 
      ? route.query.redirect 
      : withLocale('/', locale)
    await router.replace(redirect)
  } catch (error) {
    const detail = error?.payload?.detail
    const remainingAttempts = detail?.remaining_attempts
    
    const isBanned = detail?.blocked || 
                     error?.status === 403 || 
                     error?.status === 429 || 
                     remainingAttempts <= 0
    if (isBanned) {
      errorMessage.value = TEXT_CONSTANTS.bannedIp
    } else if (remainingAttempts > 0) {
      errorMessage.value = `${TEXT_CONSTANTS.invalidToken} ${remainingAttempts} attempts left.`
    } else {
      errorMessage.value = TEXT_CONSTANTS.invalidToken
    }
  }
}
onMounted(() => {
  const canvas = canvasElement.value
  if (!canvas) return

  canvasContext = canvas.getContext('2d')
  initializeCanvas()
  animate()
})
onBeforeUnmount(() => {
  cancelAnimationFrame(animationFrameId)
  particleList = []
  canvasContext = null
})
</script>
<template>
  <main class="wrap" :class="{ bad: errorMessage }">
    <canvas ref="canvasElement" />
    <form class="form" @submit.prevent="submitForm">
      <p>{{ currentHintText }}</p>
      <input
        v-model.trim="formState.accessToken"
        type="password"
        placeholder="Access token"
      />
      <button :disabled="betaAccessStore.isLoading">Sign In</button>
    </form>
  </main>
</template>
<style scoped>
.wrap {
  position: relative;
  min-height: 100vh;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #000;
  padding: 1.5rem;
  --c: #1da86b;
}
.wrap.bad {
  --c: #f00;
}
canvas {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: auto;
  height: auto;
  z-index: 0;
}
.form {
  z-index: 1;
  width: min(100%, 22rem);
  display: grid;
  gap: 1rem;
}
.form p {
  margin: 0;
  color: var(--c);
  text-align: center;
  font-size: 1.05rem;
}
input {
  outline: none !important;
}
.form input,
.form button {
  padding: 1rem 1.1rem;
  min-height: 3.35rem;
  color: var(--c) !important;
  background: #000 !important;
  border: 0.075rem solid var(--c) !important;
  border-radius: 0.9rem;
  font-size: 1rem;
  text-align: center;
  caret-color: transparent;
}
.form input::placeholder {
  color: #777;
}
.form button {
  cursor: pointer;
  font-weight: 700;
  transition: 0.15s;
}
.form button:hover {
  background: var(--c) !important;
  color: #000 !important;
}
.form button:disabled {
  cursor: wait;
}
</style>
