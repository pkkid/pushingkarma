import {defineConfig} from 'vite'
import {fileURLToPath, URL} from 'node:url'
import vue from '@vitejs/plugin-vue'

// Vite Configuration
// https://vitejs.dev/config/
export default defineConfig({
  build: {
    assetsDir: 'static',
    outDir: '_dist',
    chunkSizeWarningLimit: 1000,  // KB
  },
  plugins: [vue()],
  publicDir: 'public',
  resolve: {
    alias: {'@': fileURLToPath(new URL('./vue', import.meta.url))}
  },
})
