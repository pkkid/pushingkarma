import {defineConfig} from 'vite'
import {fileURLToPath, URL} from 'node:url'
import {PrimeVueResolver} from 'unplugin-vue-components/resolvers'
import Components from 'unplugin-vue-components/vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    Components({resolvers: [PrimeVueResolver()]})
  ],
  build: {
    assetsDir: 'static',
    outDir: 'pk/_dist',
    chunkSizeWarningLimit: 1000,  // KB
  },
  resolve: {
    alias: {'@': fileURLToPath(new URL('./vue', import.meta.url))}
  }
})
