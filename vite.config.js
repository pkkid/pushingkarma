import {defineConfig} from 'vite'
import {fileURLToPath, URL} from 'node:url'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  build: {
    assetsDir: 'static',
    outDir: '_dist',
    chunkSizeWarningLimit: 1000,  // KB
  },
  resolve: {
    alias: {'@': fileURLToPath(new URL('./vue', import.meta.url))}
  }
})
