<template>
  <div class='tooltip-container' ref='container' @mouseenter='onMouseEnter'
    @mouseleave='onMouseLeave' @click='onClick'>
    <div v-if='visible' class='tooltip' ref='tooltip' :class='position' :style='tstyle'>
      <slot name='tooltip'>{{text}}</slot>
    </div>
    <slot></slot>
  </div>
</template>

<script setup>
  import {ref, nextTick, onBeforeUnmount, onMounted} from 'vue'

  var timeout_show = null                             // Timeout for showing tooltip
  var timeout_hide = null                             // Timeout for hiding tooltip
  const container = ref(null)                         // Reference to tooltip container
  const tooltip = ref(null)                           // Reference to tooltip element
  const tstyle = ref({})                              // Dynamic style for tooltip
  const visible = ref(false)                          // Tooltip visibility
  const props = defineProps({
    position: {type:String, default:'top'},           // Tooltip position {topleft,top,topright,righttop,right,rightbottom,etc.}
    delay: {type:Number, default:500},                // Delay before showing tooltip
    text: {type:String, default:null},                // Tooltip text (or define #content slow)
    width: {type:String, default:'max-content'},      // Tooltip width
    trigger: {type:String, default:'hover'},          // Trigger type: {hover, click}
  })

  // On Mounted
  // Setup event listeners
  onMounted(function() {
    if (props.trigger == 'click') {
      document.addEventListener('click', onDocumentClick)
      document.addEventListener('keydown', onKeyDown)
    }
  })

  // On Before Unmount
  // Remove event listeners
  onBeforeUnmount(function() {
    if (props.trigger === 'click') {
      document.removeEventListener('click', onDocumentClick)
      document.removeEventListener('keydown', onKeyDown)
    }
    clearTimeout(timeout_show)
    clearTimeout(timeout_hide)
  })

  // On Click
  // Show the tooltip
  const onClick = async function(event) {
    if (props.trigger != 'click') return
    event.stopPropagation()
    clearTimeout(timeout_show)
    clearTimeout(timeout_hide)
    if (!visible.value) {
      visible.value = true
      await nextTick()
      updateTooltipStyle()
    }
  }

  // On Document Click
  // Hide the tooltip when clicked outside
  const onDocumentClick = function(event) {
    if (props.trigger != 'click' || !visible.value) { return }
    if (container.value && !container.value.contains(event.target) && 
        tooltip.value && !tooltip.value.contains(event.target)) {
      visible.value = false
    }
  }

  // On Key Down
  // Close when pressing escape
  const onKeyDown = function(event) {
    if (props.trigger == 'click' && visible.value && event.key == 'Escape') {
      visible.value = false
    }
  }

  // On Mouse Enter
  // Called when moused over tooltip-container. Waits for
  // props.delay then sets tooltip visisbility to true
  const onMouseEnter = function() {
    if (props.trigger != 'hover') { return }
    clearTimeout(timeout_hide)
    timeout_show = setTimeout(async function() {
      visible.value = true
      await nextTick()
      updateTooltipStyle()
    }, props.delay)
  }

  // On Mouse Leave
  // Clears timeout and sets tooltip visibility to false
  const onMouseLeave = function() {
    if (props.trigger != 'hover') { return }
    clearTimeout(timeout_show)
    timeout_hide = setTimeout(function() {
      visible.value = false
    }, 200)
  }

  // Update Tooltip Style
  // Setsh the width, top and left style properties of the tooltip. To properly
  // calculate the expected size of the tooltop, we render it in the dom with opacity=0
  // then apply the style 'loaded' at the end to trigger opacity=1. 
  const updateTooltipStyle = async function() {
    tooltip.value.style.width = props.width
    await nextTick()
    var cbox = container.value.getBoundingClientRect()
    var tbox = tooltip.value.getBoundingClientRect()
    if (props.position.startsWith('top')) { tooltip.value.style.top = `${-tbox.height - 5}px` }
    if (props.position.startsWith('right')) { tooltip.value.style.left = `${cbox.width + 5}px` }
    if (props.position.startsWith('bottom')) { tooltip.value.style.top = `${cbox.height + 5}px` }
    if (props.position.startsWith('left')) { tooltip.value.style.left = `${-tbox.width - 5}px` }
    if (props.position.length > 6) {
      if (props.position.endsWith('top')) { tooltip.value.style.top = `${(cbox.height / 2) - tbox.height + 15}px` }
      if (props.position.endsWith('right')) { tooltip.value.style.left = `${(cbox.width / 2) - 15}px` }
      if (props.position.endsWith('bottom')) { tooltip.value.style.top = `${(cbox.height / 2) - 15}px` }
      if (props.position.endsWith('left')) { tooltip.value.style.left = `${(cbox.width / 2) - tbox.width + 15}px` }
    } else {
      if (props.position == 'top' || props.position == 'bottom') { tooltip.value.style.left = `${(cbox.width - tbox.width) / 2}px` }
      if (props.position == 'right' || props.position == 'left') { tooltip.value.style.top = `${(cbox.height - tbox.height) / 2}px` }
    }
    tooltip.value.classList.add('loaded')
  }

  // Define Exposed
  defineExpose({
    open: function() { visible.value = true },
    close: function() { visible.value = false },
  })
</script>

<style scoped>
  .tooltip-container {
    --bgcolor: var(--darkbg-bg1);
    position: relative;
    display: inline-block;
    user-select: normal;

    .tooltip {
      background-color: var(--bgcolor);
      border-radius: 4px;
      box-shadow: 0 4px 8px #0002, 0 2px 4px #0002;
      color: var(--darkbg-fg1);
      font-size: 12px;
      opacity: 0;
      padding: 5px 10px;
      position: absolute;
      transition: all 0.4s ease;
      z-index: 11;
      &.loaded { opacity: 1; }
    }
    .tooltip::before {
      display: block;
      content: ' ';
      width: 0;
      height: 0;
      border-style: solid;
      position: absolute;
      border-color: transparent transparent transparent transparent;
      border-width: 5px 5px 5px 5px;
    }
    .tooltip.topleft::before,
    .tooltip.top::before,
    .tooltip.topright::before {
      border-bottom-width: 0px;
      border-top-color: var(--bgcolor);
      transform: translateX(-50%);
    }
    .tooltip.topleft::before { bottom: -5px; right: 5px; }
    .tooltip.top::before { bottom: -5px; left: 50%; }
    .tooltip.topright::before { bottom: -5px; left: 15px; }
    
    /* Right */
    .tooltip.righttop::before,
    .tooltip.right::before,
    .tooltip.rightbottom::before {
      border-left-width: 0px;
      border-right-color: var(--bgcolor);
      transform: translateY(-50%);
    }
    .tooltip.righttop::before { bottom: 5px; left: -5px; }
    .tooltip.right::before { top: 50%; left: -5px; }
    .tooltip.rightbottom::before { top: 15px; left: -5px; }
    
    /* Bottom */
    .tooltip.bottomleft::before,
    .tooltip.bottom::before,
    .tooltip.bottomright::before {
      border-top-width: 0px;
      border-bottom-color: var(--bgcolor);
      transform: translateX(-50%);
    }
    .tooltip.bottomleft::before { top: -5px; right: 5px; }
    .tooltip.bottom::before { top: -5px; left: 50%; }
    .tooltip.bottomright::before { top: -5px; left: 15px; }
    
    /* Left */
    .tooltip.lefttop::before,
    .tooltip.left::before,
    .tooltip.leftbottom::before {
      border-right-width: 0px;
      border-left-color: var(--bgcolor);
      transform: translateY(-50%);
    }
    .tooltip.lefttop::before { bottom: 5px; right: -5px; }
    .tooltip.left::before { top: 50%; right: -5px; }
    .tooltip.leftbottom::before { top: 15px; right: -5px; }
  }
</style>
