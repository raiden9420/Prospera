import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5000,
    allowedHosts: ['localhost'],
    proxy: {
      '/api/ask-ai': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/api/quick-insights': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/api/visualize': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/api': {
        target: 'http://localhost:8081',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 5000,
  },
})
