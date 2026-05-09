import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api/v1/intel/list': {
        target: 'http://localhost:8888',
        changeOrigin: true
      },
      '/api/search': {
        target: 'http://localhost:8888',
        changeOrigin: true
      },
      '/api/rag': {
        target: 'http://localhost:8888',
        changeOrigin: true
      },
      '/api/sa': {
        target: 'http://localhost:8888',
        changeOrigin: true
      },
      '/api/topics': {
        target: 'http://localhost:8888',
        changeOrigin: true
      }
    }
  }
})
