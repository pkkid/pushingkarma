// Main Vue Setup
// Icons: https://fonts.google.com/icons?icon.set=Material+Symbols
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
import hljsVuePlugin from "@highlightjs/vue-plugin"

hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('json', json)
hljs.registerLanguage('python', python)
hljs.registerLanguage('sql', sql)
app.use(hljsVuePlugin)

// Mount the App after waiting for all component promises to be met.
import './assets/styles.css'
import './assets/overrides.css'
app.mount('#app')
