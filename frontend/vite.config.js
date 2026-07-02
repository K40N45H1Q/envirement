import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const createBackendProxy = () => ({
  target: 'http://127.0.0.1:8000',
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
      '/create_account': createBackendProxy(),
      '/login': createBackendProxy(),
      '/get_me': createBackendProxy(),
      '/api': createBackendProxy(),
      '/uploads': createBackendProxy(),
    },
  }
})
