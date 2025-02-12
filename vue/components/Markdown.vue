<template>
  <div class='markdown-content'>
    <div v-html='outhtml' />
  </div>
</template>

<script setup>
  import {computed, ref, watchEffect} from 'vue'
  import markdownIt from 'markdown-it'
  import markdownHighlightJs from '@/utils/markdown/markdown-hljs'
  import markdownToc, {markdownHeadings} from '@/utils/markdown/markdown-toc'

  // Init MarkdownIt
  // create the markdown-it object
  const md = new markdownIt()
    .use(markdownHighlightJs)
    .use(markdownToc)

  const emit = defineEmits(['headings'])            // Emit when new headings calculated
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
  const outhtml = computed(function() {
    var result = md.render(props.source)
    emit('headings', markdownHeadings)
    return result
  })

  // Options 
  // Pass through markdown-it options
  const options = computed(function() {
    return {
      html: props.html,
      xhtmlOut: props.xhtmlOut,
      breaks: props.breaks,
      linkify: props.linkify,
      typographer: props.typographer,
      langPrefix: props.langPrefix,
      quotes: props.quotes,
    }
  })

  // Watch Options
  // updates markdown-it options
  watchEffect(function() {
    md.set(options.value)
  })
</script>