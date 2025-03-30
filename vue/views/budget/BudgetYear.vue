<template>
  <LayoutPaper width='1200px'>
    <template #content>
      <CodeEditor theme='gruvbox-light-hard' language='javascript' padding='12px'
        style='height:400px; width:500px;' v-model='code'/>
    </template>
  </LayoutPaper>
</template>

<script setup>
  import {ref, watch} from 'vue'
  import {CodeEditor, LayoutPaper} from '@/components'

  const code = ref(`// Main Vue Setup
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

// Mount the App after waiting for all component promises to be met.
import './assets/styles.css'
app.mount('#app')`)

  watch(code, function() {
    console.log(code.value)
  })

</script>

<style>
</style>
