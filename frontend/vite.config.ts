import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
 
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api/auth': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api\/auth/, ''),
      },
      '/api/products': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api\/products/, ''),
      },
      '/api/inventory': {
        target: 'http://127.0.0.1:8003',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api\/inventory/, ''),
      },
      '/api/orders': {
        target: 'http://127.0.0.1:8004',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api\/orders/, ''),
      },
      '/api/payment': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api\/payment/, ''),
      },
    },
  },
})
