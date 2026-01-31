import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/HAI2026-Interactive-Slides/',
  build: {
    outDir: '../docs',
    emptyOutDir: true,
  }
})
