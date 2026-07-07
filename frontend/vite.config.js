import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const BACKEND_TARGET = 'http://127.0.0.1:8000'

const normalizeIp = (value) => {
  const source = String(value || '').trim().toLowerCase()
  if (!source) return ''

  let ip = source.includes(',') ? source.split(',', 1)[0].trim() : source

  if (ip.startsWith('::ffff:')) {
    ip = ip.slice(7)
  }

  if (ip === '::1') {
    return '127.0.0.1'
  }

  return ip
}

const isPublicIp = (value) => {
  const ip = normalizeIp(value)
  if (!ip) return false

  if (ip.includes(':')) {
    const normalized = ip.toLowerCase()
    return !(
      normalized === '::1'
      || normalized === '::'
      || normalized.startsWith('fc')
      || normalized.startsWith('fd')
      || normalized.startsWith('fe8')
      || normalized.startsWith('fe9')
      || normalized.startsWith('fea')
      || normalized.startsWith('feb')
    )
  }

  const parts = ip.split('.').map(Number)
  if (parts.length !== 4 || parts.some((part) => Number.isNaN(part) || part < 0 || part > 255)) {
    return false
  }

  return !(
    parts[0] === 10
    || parts[0] === 127
    || (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31)
    || (parts[0] === 192 && parts[1] === 168)
    || (parts[0] === 169 && parts[1] === 254)
    || parts[0] === 0
  )
}

const getForwardedPublicIp = (req) => {
  const candidates = [
    req.headers['cf-connecting-ip'],
    req.headers['true-client-ip'],
    req.headers['fly-client-ip'],
    req.headers['x-client-ip'],
    req.headers['x-forwarded-for'],
    req.headers['x-real-ip'],
  ]

  for (const candidate of candidates) {
    if (!candidate) continue
    for (const rawIp of String(candidate).split(',')) {
      const ip = normalizeIp(rawIp)
      if (isPublicIp(ip)) {
        return ip
      }
    }
  }

  return ''
}

const createBackendProxy = () => ({
  target: BACKEND_TARGET,
  changeOrigin: true,
  configure(proxy) {
    proxy.on('error', (error) => {
      if (error?.code === 'ECONNREFUSED') return
      console.error(error)
    })
  },
})

const betaBlacklistGuard = () => ({
  name: 'beta-blacklist-guard',
  configureServer(server) {
    server.middlewares.use(async (req, res, next) => {
      try {
        const forwardedFor = getForwardedPublicIp(req)

        const response = await fetch(`${BACKEND_TARGET}/api/beta-auth/status`, {
          headers: forwardedFor
            ? {
              'x-forwarded-for': forwardedFor,
              'x-real-ip': forwardedFor,
            }
            : {},
        })

        if (response.status === 404) {
          req.socket?.destroy()
          res.socket?.destroy()
          return
        }
      } catch {
        req.socket?.destroy()
        res.socket?.destroy()
        return
      }

      next()
    })
  },
})

export default defineConfig({
  plugins: [
    vue(),
    betaBlacklistGuard(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true,
    allowedHosts: ['.trycloudflare.com'],
    proxy: {
      '/create_account': createBackendProxy(),
      '/request_registration_code': createBackendProxy(),
      '/verify_registration_code': createBackendProxy(),
      '/request_password_reset_code': createBackendProxy(),
      '/confirm_password_reset': createBackendProxy(),
      '/login': createBackendProxy(),
      '/get_me': createBackendProxy(),
      '/api': createBackendProxy(),
      '/uploads': createBackendProxy(),
    },
  }
})
