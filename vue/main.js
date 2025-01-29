// Main Vue Setup
// Icons: https://fonts.google.com/icons?icon.set=Material+Symbols
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// Mount the App after waiting for all component promises to be met.
import './assets/styles.css'
import './assets/overrides.css'
app.mount('#app')
