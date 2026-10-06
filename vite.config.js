import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backend = process.env.VITE_API_BASE_URL || env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api/v1'
  return {
    plugins: [vue()],
    server: {
      host: '127.0.0.1',
      port: Number(process.env.PORT || 5173),
      // Do not silently open a second copy on a different port.
      strictPort: true,
      // Cookies and API calls use the browser's own origin in development.
      // An explicitly chosen port (e.g. --port 5174) works the same way.
      proxy: {
        '/api': { target: new URL(backend, 'http://127.0.0.1:5000').origin, changeOrigin: true },
      },
    },
  }
})
