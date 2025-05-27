<template>
  <div class='markdown-content' v-html='outhtml'/>
</template>

<script setup>
  import {ref, nextTick, onMounted, watch, watchEffect} from 'vue'
  import {createApp, h} from 'vue'
  import {markdownCode, codeComponents} from '@/components/Markdown'
  import {markdownProps, propComponents} from '@/components/Markdown'
  import {markdownToc, markdownHeadings} from '@/components/Markdown'
  import markdownIt from 'markdown-it'

  // Init MarkdownIt
  // create the markdown-it object
  const md = new markdownIt()
    .use(markdownProps)
    .use(markdownCode)
    .use(markdownToc)
  
  const props = defineProps({
    source: {type:String, required:true},           // Source markdown content
    html: {type:Boolean, default:true},             // Enable HTML tags in source
    xhtmlOut: {type:Boolean, default:true},         // Add '/' when closing single tags
    breaks: {type:Boolean, default:true},           // Convert \n in paragraphs into <br>
    langPrefix: {type:String, default:'language-'}, // CSS language class prefix for fenced blocks.
    linkify: {type:Boolean, default:true},          // Autoconvert URL-like text to links.
    typographer: {type:Boolean, default:false},     // Enable language-neutral replacement + quotes beautification
    quotes: {type:String, default:'“”‘’'},          // Quotes replacement pairs when typographer enabled
  })
  const emit = defineEmits(['headings'])            // Emit when new headings calculated
  const outhtml = ref(null)                         // Rendered HTML output

  // Watch Source
  // Update the markdown html when the source changes
  onMounted(function() { updateView() })
  watch(() => props.source, function() { updateView() })

  // Apply Vue Components
  // Inject components to the markdown html
  const applyVueComponents = async function() {
    await nextTick()
    const components = {...codeComponents, ...propComponents}
    document.querySelectorAll('.mdvuecomponent').forEach(function(elem) {
      const id = elem.dataset.id
      const cdata = components[id]
      if (!cdata) { return console.log(`Unknown component id: ${id}`) }
      const app = createApp({
        render: () => h(cdata.component, cdata.props)
      })
      app.mount(elem)
    })
  }

  // Update View
  // Update the markdown html when the source changes
  const updateView = function() {
    outhtml.value = md.render(props.source)
    applyVueComponents()
    emit('headings', markdownHeadings)
  }

  // Watch Options
  // updates markdown-it options
  watchEffect(function() {
    md.set({
      html: props.html,
      xhtmlOut: props.xhtmlOut,
      breaks: props.breaks,
      linkify: props.linkify,
      typographer: props.typographer,
      langPrefix: props.langPrefix,
      quotes: props.quotes,
    })
  })
</script>
