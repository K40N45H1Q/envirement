import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const BACKEND_TARGET = 'http://127.0.0.1:8000'

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

export default defineConfig({
  plugins: [
    vue(),
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
      '/api': createBackendProxy(),
      '/uploads': createBackendProxy(),
    },
  }
})
