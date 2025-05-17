<!-- eslint-disable vue/use-v-on-exact -->
<template>
  <div class='codeeditor' ref='codeeditor' :theme='theme' :class='{readonly, showlinenums}'>
    <div class='codewrap hljs'>
      <div ref='codearea' class='codearea'>
        <div v-if='showlinenums' class='linenumsbar'></div>
        <div v-if='showlinenums' ref='linenums' class='linenums'>
          <div v-for='num in numlines' :key='num'>{{num}}</div>
        </div>
        <textarea v-if='!readonly' ref='textarea' spellcheck='false'
          :autofocus='autofocus' :value='currentvalue'
          @input='updateContent($event.target.value)'
          @scroll='onScroll'
          @keydown.tab.prevent.stop='onTab'
          @keydown.enter.prevent='onEnter'
          @keydown='onClosingBrace'
          @keydown.ctrl.s.exact.prevent='emit("save")'/>
        <pre><code ref='code' :class='langcls'></code></pre>
      </div>
    </div>
  </div>
</template>

<script setup>
  // Code Editor
  // Even simpler implementation of Simple-Code-Editor
  // https://github.com/justcaliturner/simple-code-editor
  // https://github.com/highlightjs/highlight.js
  import {computed, onMounted, onUnmounted, ref, watch, watchEffect} from 'vue'
  import {textedit} from '@/utils'
  import hljs from 'highlight.js'

  const props = defineProps({
    autofocus: {type:Boolean, default:false},             // Autofocus on the editor
    height: {type:String, default:'auto'},                // Height of the editor
    language: {type:String, default:'javascript'},        // Language of the editor
    maxheight: {type:String, default:'100%'},             // Max height of the editor
    modelValue: {type:String},                            // v-model; varied value
    readonly: {type:Boolean, default:false},              // Enable editable or not
    showlinenums: {type:Boolean, default:false},          // Show line numbers
    tabspaces: {type:Number, default:2},                  // Number of spaces for tab
    theme: {type:String, default:'gruvbox-light-hard'},   // Highlight.js theme to apply
    value: {type:String, default:'Hello World!'},         // Static value if not using v-model
  })

  var linenumsObserver = null                       // ResizeObserver for linenums
  var textareaObserver = null                       // ResizeObserver for textarea
  const emit = defineEmits(['save', 'update:modelValue', 'update'])
  const backgroundcolor = ref('transparent')        // Background color of current theme
  const code = ref(null)                            // Reference to code element
  const codearea = ref(null)                        // Reference to codearea div
  const linenums = ref(null)                        // Reference to linenums div
  const linenumswidth = ref('0px')                  // Width of linenums div
  const scrollbarheight = ref('0px')                // Height of textarea scrollbar
  const scrollbarwidth = ref('0px')                 // Width of textarea scrollbar
  const scrollleft = ref('0px')                     // Amount scrolled right
  const scrolltop = ref('0px')                      // Amount scrolled down
  const codeeditor = ref(null)                      // Reference to codeeditor
  const textarea = ref(null)                        // Reference to textarea
  const currentvalue = ref(null)                    // Current value of the editor
  
  const langcls = computed(function() { return `language-${props.language.toLowerCase()}` })
  const numlines = computed(function() { return Math.max(currentvalue.value?.split('\n').length || 1, 1) })

  // Watch Model Value
  // Update currentvalue when modelValue changes
  watch(() => props.modelValue, (newval) => {
    if (newval !== currentvalue.value) {
      currentvalue.value = newval ?? props.value
    }
  }, {immediate: true})

  // Watch Theme
  // Update css variables when theme changes
  watch(() => props.theme, function() {
    updateCssVarables()
  })

  // On Mounted
  // Watch textarea and lineNum resizing
  onMounted(function() {
    if (!props.readonly) {
      textareaObserver = new ResizeObserver(updateCssVarables)
      textareaObserver.observe(textarea.value)
    }
    if (props.showlinenums) {
      linenumsObserver = new ResizeObserver(updateCssVarables)
      linenumsObserver.observe(linenums.value)
    }
  })

  // On Unmounted
  // Disconnect ResizeObservers
  onUnmounted(function() {
    if (textareaObserver) { textareaObserver.disconnect() }
    if (linenumsObserver) { linenumsObserver.disconnect() }
  })

  // Watch Code Value
  // Calls highlight.js
  watchEffect(function() {
    if (code.value == null) { return }
    code.value.textContent = currentvalue.value
    delete code.value.dataset.highlighted
    hljs.highlightElement(code.value)
    code.value.classList.remove('hljs')
  })

  // On Scroll
  // Updates saved scolling state
  const onScroll = function(event) {
    scrolltop.value = `${-event.target.scrollTop}px`
    scrollleft.value = `${-event.target.scrollLeft}px`
  }

  // On Enter
  // Inserts new line adding indentation if needed
  const onEnter = async function() {
    if (props.readonly) { return }
    textedit.indentNewLine(textarea.value, props.tabspaces)
    updateContent(textarea.value.value)
  }

  // On Tab
  // Inserts tab or spaces
  const onTab = async function(event) {
    if (props.readonly) { return }
    textedit.tabIndent(textarea.value, event.shiftKey, props.tabspaces)
    updateContent(textarea.value.value)
  }

  // On Keydown
  // Generic Keydown event
  const onClosingBrace = async function(event) {
    if (props.readonly) { return }
    if ('}])'.includes(event.key)) {
      textedit.insertClosingBrace(textarea.value, event.key, props.tabspaces)
      updateContent(textarea.value.value)
    }
  }

  // Update CSS Variables
  // Variables passed to css for dynamic styling
  const updateCssVarables = function() {
    linenumswidth.value = `${linenums.value?.offsetWidth}px`
    scrollbarwidth.value = props.readonly ? '0px' : `${textarea.value.offsetWidth - textarea.value.clientWidth}px`
    scrollbarheight.value = props.readonly ? '0px' : `${textarea.value.offsetHeight - textarea.value.clientHeight}px`
    backgroundcolor.value = window.getComputedStyle(codearea.value).backgroundColor
  }

  // Update Content
  // Emits the update or simply updates currentvalue.value
  const updateContent = function(newval) {
    // currentvalue.value = newval   /* REMOVE THIS LINE??? */
    emit('update:modelValue', newval)
    emit('update', newval)
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
    --padding: 8px;
    --lineheight: 1.3em;

    font-family: var(--fontfamily-code);
    font-size: 13px;
    height: v-bind(height);
    line-height: var(--lineheight);
    position: relative;
    z-index: 1;

    .codewrap, .codearea, .linenums, textarea, pre, code {
      font-family: inherit !important;
      font-size: inherit !important;
      line-height: inherit !important;
      height: 100%;
    }
    .codewrap.hljs {
      border-radius: 4px;
      padding: 0px;
      height: 100%;
    }
    .codearea {
      /* height: 100%; */
      overflow: hidden;
      position: relative;
      text-align: left;
      width: 100%;
    }
    .linenums {
      box-sizing: border-box;
      min-width: 36px;
      padding-bottom: var(--padding);
      padding-left: 8px;
      padding-right: 8px;
      padding-top: var(--padding);
      position: absolute;
      text-align: right;
      top: v-bind(scrolltop);
      left: 0;
      user-select: none;
      & > div { opacity:0.3; }
    }
    .linenumsbar {
      background-color: currentColor;
      content: ' ';
      display: block;
      height: 100%;
      left: calc(v-bind(linenumswidth) - 1px);
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
      overflow: auto;
      padding: var(--padding);
      position: absolute;
      resize: none;
      top: 0; left: 0;
      white-space: pre;
      width: 100%;
      word-wrap: normal;
      z-index: 2;
    }
    pre {
      border-width: 0px;
      box-sizing: border-box;
      margin-left: 0px;
      margin: 0;
      overflow: hidden;
      padding-bottom: v-bind(scrollbarheight);
      padding-left: 0px;
      padding-right: v-bind(scrollbarwidth);
      padding-top: 0px;
      position: relative;
      width: 100%;
      height: 100%;
    }
    code {
      border-radius: 0;
      box-sizing: border-box;
      display: block;
      height: calc(v-bind(numlines) * var(--lineheight) + var(--padding) * 2);
      left: v-bind(scrollleft);
      margin: 0px;
      overflow-x: visible !important;
      padding: var(--padding) !important;
      position: relative;
      top: v-bind(scrolltop);
    }
    /* Show Line Numbers */
    &.showlinenums textarea,
    &.showlinenums pre {
      margin-left: v-bind(linenumswidth);
      width: calc(100% - v-bind(linenumswidth));
    }
    /* Readonly, allow scrolling pre */
    &.readonly pre { overflow: auto; }
  }
</style>
