<template>
  <div class='markdown-content'>
    <div v-html='outhtml' />
  </div>
</template>

<script setup>
  import {computed, ref, watchEffect} from 'vue'
  import markdownIt from 'markdown-it'
  import markdownhljs from 'markdown-it-highlightjs'

  // Init MarkdownIt
  // create the markdown-it object
  const md = new markdownIt()
    .use(markdownhljs)

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
  const outhtml = computed(function() { return md.render(props.source) })  // Output html

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