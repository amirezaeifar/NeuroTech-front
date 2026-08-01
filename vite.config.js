import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // Honour an externally assigned port (e.g. tooling that sets PORT) so the
  // dev server binds where the launcher expects it.
  server: process.env.PORT ? { port: Number(process.env.PORT), strictPort: true } : {},
})
