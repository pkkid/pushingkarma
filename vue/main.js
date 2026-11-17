// Main Vue Setup
// @ts-nocheck
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)

// Setup Highlight.js
// highlightjs: https://highlightjs.org/
// https://github.com/highlightjs/vue-plugin
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import json from 'highlight.js/lib/languages/json'
import python from 'highlight.js/lib/languages/python'
import sql from 'highlight.js/lib/languages/sql'
import hljsVuePlugin from '@highlightjs/vue-plugin'

hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('json', json)
hljs.registerLanguage('python', python)
hljs.registerLanguage('sql', sql)
app.use(hljsVuePlugin)

// Fonts and Icons
// Bundled with the app (instead of loaded from Google Fonts and jsdelivr) so they
// get hashed file names and are cached by the browser forever.
import '@fontsource-variable/inter/opsz.css'
import '@fontsource-variable/inter/opsz-italic.css'
import '@fontsource-variable/merriweather/wght.css'
import '@fontsource-variable/merriweather/wght-italic.css'
import '@fontsource-variable/roboto-mono/wght.css'
import '@fontsource-variable/roboto-mono/wght-italic.css'
import '@mdi/font/css/materialdesignicons.min.css'

// Mount the App after waiting for all component promises to be met.
import './assets/main.css'
app.mount('#app')
