<template>
  <div class='codeeditor' :theme='theme' :class='{readOnly, showLineNums, scrollable}'>
    <div class='codewrap hljs'>
      <div ref='codearea' class='codearea'>
        <div v-if='showLineNums' class='linenumbar'></div>
        <div v-if='showLineNums' ref='lineNums' class='linenums'>
          <div v-for='num in numLines' :key='num'>{{num}}</div>
        </div>
        <textarea ref='textarea' spellcheck='false' :readOnly='readOnly' :autofocus='autoFocus'
          :value='content' @input='updateContent($event.target.value)' @scroll='onScroll'
          @keydown.tab.prevent.stop='onTab'></textarea>
        <pre><code ref='code' :class='codeClass'></code></pre>
      </div>
    </div>
  </div>
</template>

<script setup>
  // Code Editor
  // Even simpler implementation of Simple-Code-Editor
  // https://github.com/justcaliturner/simple-code-editor
  // https://github.com/highlightjs/highlight.js
  import {computed, nextTick, onMounted, onUnmounted, ref, watch, watchEffect, onUpdated} from 'vue'
  import hljs from 'highlight.js'

  const emit = defineEmits(['update:modelValue'])
  const props = defineProps({
    autoFocus: {type:Boolean, default:false},       // Autofocus on the editor
    language: {type:String, default:'javascript'},  // Language of the editor
    modelValue: {type:String},                      // v-model; varied value
    padding: {type:String, default:'20px'},         // Padding around the editor
    readOnly: {type:Boolean, default:false},        // Enable editable or not
    showLineNums: {type:Boolean, default:false},    // Show line numbers
    tabSpaces: {type:Number, default:2},            // Number of spaces for tab
    theme: {type:String, default:'dracula'},        // Highlight.js theme to apply
    value: {type:String, default:'Hello World!'},   // Static value if not using v-model
  })

  var lineNumsObserver = null                       // ResizeObserver for lineNums
  var textareaObserver = null                       // ResizeObserver for textarea
  const backgroundColor = ref('transparent')        // Background color of current theme
  const code = ref(null)                            // Reference to code element
  const codearea = ref(null)                        // Reference to codearea div
  const lineNums = ref(null)                        // Reference to linenums div
  const lineNumsWidth = ref('0px')                  // Width of lineNums div
  const scrollbarHeight = ref('0px')                // Height of textarea scrollbar
  const scrollbarWidth = ref('0px')                 // Width of textarea scrollbar
  const scrollLeft = ref('0px')                     // Amount scrolled right
  const scrollTop = ref('0px')                      // Amount scrolled down
  const textarea = ref(null)                        // Reference to textarea
  const content = ref(null)
  
  const codeClass = computed(function() { return `language-${props.language}` })
  const numLines = computed(function() { return content.value?.split('\n').length || 0 })
  const scrollable = computed(function() { return props.height == 'auto' ? false : true })

  watchEffect(function() { content.value = props.modelValue || props.value })
  watchEffect(() => props.theme, function() { updateCssVarables() })

  // On Mounted
  // Watch textarea and lineNum resizing
  onMounted(function() {
    textareaObserver = new ResizeObserver(updateCssVarables)
    textareaObserver.observe(textarea.value)
    if (props.showLineNums) {
      lineNumsObserver = new ResizeObserver(updateCssVarables)
      lineNumsObserver.observe(lineNums.value)
    }
  })

  // On Unmounted
  // Disconnect ResizeObservers
  onUnmounted(function() {
    if (textareaObserver) { textareaObserver.disconnect() }
    if (lineNumsObserver) { lineNumsObserver.disconnect() }
  })

  // Watch Code Value
  // Calls highlight.js
  watchEffect(function() {
    if (code.value == null) { return }
    code.value.textContent = content.value
    delete code.value.dataset.highlighted
    hljs.highlightElement(code.value)
    code.value.classList.remove('hljs')
  })

  // On Scroll
  // Updates saved scolling state
  const onScroll = function(event) {
    scrollTop.value = `${-event.target.scrollTop}px`
    scrollLeft.value = `${-event.target.scrollLeft}px`
  }

  // On Tab
  // Inserts tab or spaces
  const onTab = async function() {
    const tab = ' '.repeat(props.tabSpaces)
    var pos = textarea.value.selectionStart
    var newval = textarea.value.value
    newval = newval.substring(0, pos) + tab + newval.substring(pos)
    updateContent(newval)
    await nextTick()
    textarea.value.setSelectionRange(pos+tab.length, pos+tab.length)
  }

  // Update CSS Variables
  // Variables passed to css for dynamic styling
  const updateCssVarables = function() {
    lineNumsWidth.value = `${lineNums.value.offsetWidth}px`
    scrollbarWidth.value = `${textarea.value.offsetWidth - textarea.value.clientWidth}px`
    scrollbarHeight.value = `${textarea.value.offsetHeight - textarea.value.clientHeight}px`
    backgroundColor.value = window.getComputedStyle(codearea.value).backgroundColor
  }

  // Update Content
  // Emits the update or simply updates content.value
  const updateContent = function(newval) {
    if (props.modelValue) { emit('update:modelValue', newval) }
    else { content.value = newval }
  }
</script>

<style>
  .codeeditor {
    /* Editor background color comes from the .hljs class. Since we wrapped all
    /* highlight.js themes in a [theme=<themename>] selector, the .hljs element
    /* must be inside the element defining the theme. Also, since the codearea
    /* contains overflow:hidden, this made the scrollbar drawings clipped and
    /* look bad when they were present with a border-radius. By applying the
    /* border-radius to .codewrap which doesn't contain overflow:hidden, things
    /* render correctly (but scrollbars may appear outside the border-radius). */
    font-family: Consolas, Monaco, monospace; 
    font-size: 13px;
    line-height: 1.2;
    position: relative;
    .codewrap.hljs {
      border-radius: 6px;
      padding: 0px;
    }
    .codearea {
      height: 100%;
      overflow: hidden;
      position: relative;
      text-align: left;
      width: 100%;
    }
    .linenums, textarea, code {
      font-family: inherit !important;
      font-size: inherit !important;
      line-height: inherit !important;
    }
    .linenums {
      box-sizing: border-box;
      min-width: 36px;
      padding-bottom: v-bind(padding);
      padding-left: 8px;
      padding-right: 8px;
      padding-top: v-bind(padding);
      position: absolute;
      text-align: right;
      top: v-bind(scrollTop); left: 0;
      & > div { opacity:0.2; }
    }
    .linenumbar {
      background-color: currentColor;
      content: ' ';
      display: block;
      height: 100%;
      left: calc(v-bind(lineNumsWidth) - 1px);
      opacity: 0.1;
      position: absolute;
      top: 0px;
      width: 1px;
    }
    textarea, textarea:focus {
      background: none;
      border-width: 0px;
      box-shadow: none;
      box-sizing: border-box;
      caret-color: rgb(127, 127, 127);
      color: transparent;
      height: 100%;
      margin-left: 0px;
      outline: none;
      overflow-y: hidden;
      padding: v-bind(padding) v-bind(padding) v-bind(padding);
      position: absolute;
      resize: none;
      top: 0; left: 0;
      white-space: pre;
      width: 100%;
      word-wrap: normal;
      z-index: 1;
    }
    pre {
      border-width: 0px;
      box-sizing: border-box;
      margin-left: 0px;
      margin: 0;
      overflow: hidden;
      padding-bottom: v-bind(scrollbarHeight);
      padding-left: 0px;
      padding-right: v-bind(scrollbarWidth);
      padding-top: 0px;
      position: relative;
      width: 100%;
    }
    code {
      border-radius: 0;
      box-sizing: border-box;
      display: block;
      left: v-bind(scrollLeft);
      margin: 0px;
      overflow-x: visible !important;
      padding: v-bind(padding) v-bind(padding) !important;
      position: relative;
      top: v-bind(scrollTop);
    }
    /* Show Line Numbers */
    &.showLineNums textarea,
    &.showLineNums pre {
      margin-left: v-bind(lineNumsWidth);
      width: calc(100% - v-bind(lineNumsWidth));
    }
    /* Scroll */
    &.scrollable .codearea { height:100%; }
    &.scrollable textarea { overflow:auto; }
    &.scrollable pre { width:100%; height:100%; overflow:hidden; }
  }
</style>
