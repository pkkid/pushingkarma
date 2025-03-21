<template>
  <div class='tooltip-container' ref='container' @mouseenter='showTooltip' @mouseleave='hideTooltip'>
    <div v-if='visible' class='tooltip' ref='tooltip' :class='position' :style='tstyle'>
      <slot name='tooltip'>{{text}}</slot>
      <div class='tooltip-arrow' :class='position'/>
    </div>
    <slot></slot>
  </div>
</template>

<script setup>
  import {ref, nextTick} from 'vue'

  var timeout = null                                  // Timeout for showing tooltip    
  const container = ref(null)                         // Reference to tooltip container
  const tooltip = ref(null)                           // Reference to tooltip element
  const tstyle = ref({})                              // Dynamic style for tooltip
  const visible = ref(false)                          // Tooltip visibility
  const props = defineProps({
    position: {type:String, default:'top'},           // Tooltip position {topleft,top,topright,righttop,right,rightbottom,etc.}
    delay: {type:Number, default:500},                // Delay before showing tooltip
    text: {type:String, default:null},                // Tooltip text (or define #content slow)
    width: {type:String, default:'max-content'},      // Tooltip width
  })

  // Show Tooltip
  // Called when moused over tooltip-container. Waits for
  // props.delay then sets tooltip visisbility to true
  const showTooltip = function() {
    timeout = setTimeout(async function() {
      visible.value = true
      await nextTick()
      updateTooltipStyle()
    }, props.delay)
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

  // Hide Tooltip
  // Clears timeout and sets tooltip visibility to false
  const hideTooltip = function() {
    clearTimeout(timeout)
    visible.value = false
  }
</script>

<style scoped>
  .tooltip-container {
    --bgcolor: var(--darkbg-bg1);
    position: relative;
    display: inline-block;

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
      z-index: 1000;
      &.loaded { opacity: 1; }
    }
    .tooltip-arrow {
      width: 0;
      height: 0;
      border-style: solid;
      position: absolute;
      border-color: transparent transparent transparent transparent;
      border-width: 5px 5px 5px 5px;
    }
    
    /* Top */
    .tooltip.topleft .tooltip-arrow,
    .tooltip.top .tooltip-arrow,
    .tooltip.topright .tooltip-arrow {
      border-bottom-width: 0px;
      border-top-color: var(--bgcolor);
      transform: translateX(-50%);
    }
    .tooltip.topleft .tooltip-arrow { bottom: -5px; right: 5px; }
    .tooltip.top .tooltip-arrow { bottom: -5px; left: 50%; }
    .tooltip.topright .tooltip-arrow { bottom: -5px; left: 15px; }
    
    /* Right */
    .tooltip.righttop .tooltip-arrow,
    .tooltip.right .tooltip-arrow,
    .tooltip.rightbottom .tooltip-arrow {
      border-left-width: 0px;
      border-right-color: var(--bgcolor);
      transform: translateY(-50%);
    }
    .tooltip.righttop .tooltip-arrow { bottom: 5px; left: -5px; }
    .tooltip.right .tooltip-arrow { top: 50%; left: -5px; }
    .tooltip.rightbottom .tooltip-arrow { top: 15px; left: -5px; }
    
    /* Bottom */
    .tooltip.bottomleft .tooltip-arrow,
    .tooltip.bottom .tooltip-arrow,
    .tooltip.bottomright .tooltip-arrow {
      border-top-width: 0px;
      border-bottom-color: var(--bgcolor);
      transform: translateX(-50%);
    }
    .tooltip.bottomleft .tooltip-arrow { top: -5px; right: 5px; }
    .tooltip.bottom .tooltip-arrow { top: -5px; left: 50%; }
    .tooltip.bottomright .tooltip-arrow { top: -5px; left: 15px; }
    
    /* Left */
    .tooltip.lefttop .tooltip-arrow,
    .tooltip.left .tooltip-arrow,
    .tooltip.leftbottom .tooltip-arrow {
      border-right-width: 0px;
      border-left-color: var(--bgcolor);
      transform: translateY(-50%);
    }
    .tooltip.lefttop .tooltip-arrow { bottom: 5px; right: -5px; }
    .tooltip.left .tooltip-arrow { top: 50%; right: -5px; }
    .tooltip.leftbottom .tooltip-arrow { top: 15px; right: -5px; }
  }
</style>
