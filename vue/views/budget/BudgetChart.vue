<template>
  <div class='bignum-panel bignum-btn minichart-wrap'>
      <div ref='chart' class='minichart' :class='{expanded: isExpanded, fullscreen: isFullscreen}' :style='expandedStyle' @click='openExpanded'>
      <div v-if='isExpanded' class='chart-controls'>
        <button v-if='canFullscreen && !isFullscreen' class='chart-control-btn' @click.stop='openFullscreen'><i class='mdi mdi-arrow-expand-all'/></button>
        <button v-else-if='canFullscreen' class='chart-control-btn' @click.stop='closeChart'><i class='mdi mdi-close'/></button>
      </div>
      <Transition name='chart-fade'>
        <slot :isExpanded='isExpanded' :isFullscreen='isFullscreen' :isReady='isReady'/>
      </Transition>
    </div>
  </div>
</template>

<script setup>
  import {onBeforeUnmount, onMounted, ref, watch} from 'vue'

  const props = defineProps({
    collapseKey: {type:[String, Number, Boolean], default:null},    // Optional key to watch for changes to auto-collapse the chart (e.g. search string)
    canFullscreen: {type:Boolean, default:false},                   // Whether to show the fullscreen expand button (only if chart has data)
    resetChartOnClick: {type:Boolean, default:true},                // If false, ignore collapseKey changes and keep expanded state after chart-triggered filters
  })

  const isExpanded = ref(false)     // Whether the chart is expanded
  const isFullscreen = ref(false)   // Whether the chart is expanded to near full screen
  const isReady = ref(true)         // Whether the chart should render (hidden during resize)
  const chart = ref(null)           // Chart container element (for click-outside close)
  const expandedStyle = ref({})     // Inline style override to keep expanded chart within viewport

  // Open Expanded
  // Open the expanded version of the chart
  const openExpanded = function() {
    isExpanded.value = true
  }

  // Open Fullscreen
  // Expand the chart to a near-fullscreen view.
  const openFullscreen = function() {
    isExpanded.value = true
    isFullscreen.value = true
  }

  // Close Fullscreen
  // Return from near-fullscreen to the normal expanded size.
  const closeFullscreen = function() {
    isFullscreen.value = false
  }

  // Close Chart
  // Collapse the chart back to its default mini state.
  const closeChart = function() {
    isFullscreen.value = false
    isExpanded.value = false
  }

  // On Window Pointer Down
  // Close chart only when clicking outside of it
  const onWindowPointerDown = function(evt) {
    if (!isExpanded.value) { return }
    if (chart.value && !chart.value.contains(evt.target)) {
      isFullscreen.value = false
      isExpanded.value = false
    }
  }

  // On Mounted, Watch, Before Unmount
  // Hide chart during resize transition, then restore it
  onMounted(function() {
    window.addEventListener('pointerdown', onWindowPointerDown)
  })
  watch([isExpanded, isFullscreen], function() {
    isReady.value = false
    setTimeout(function() { isReady.value = true }, 200)
  })
  watch(isExpanded, function(val) {
    if (!val) { expandedStyle.value = {}; return }
    // Measure wrap position before DOM updates (chart still collapsed, pre-render flush)
    // Expanded chart will sit at wrapLeft - 1px with width 550px
    var wrapRect = chart.value.parentElement.getBoundingClientRect()
    var overflow = (wrapRect.left + 549) - (window.innerWidth - 30)
    expandedStyle.value = overflow > 0 ? {left: `${-1 - overflow}px`} : {}
  })
  watch(() => props.collapseKey, function() {
    if (!props.resetChartOnClick) { return }
    isFullscreen.value = false
    isExpanded.value = false
  })
  onBeforeUnmount(function() {
    window.removeEventListener('pointerdown', onWindowPointerDown)
  })
</script>

<style scoped>
  .minichart-wrap {
    position: relative;
    width: 110px;
    height: 60px;
    flex-shrink: 0;
    .minichart {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      cursor: pointer;
      border-radius: 5px;
      border: 1px solid transparent;
      background-color: transparent;
      padding: 4px;
      box-sizing: border-box;
      transition: all 0.2s ease;
      z-index: 1;
      .chart-controls {
        position: absolute;
        top: 8px;
        right: 8px;
        display: flex;
        gap: 4px;
        z-index: 5;
      }
      .chart-control-btn {
        width: 22px;
        height: 22px;
        /* border: 1px solid var(--lightbg-bg3); */
        background-color: color-mix(in srgb, var(--lightbg-bg1) 88%, transparent);
        color: var(--lightbg-fg2);
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        &:hover {
          background-color: var(--lightbg-bg2);
          color: var(--lightbg-fg1);
        }
        .mdi {
          font-size: 14px;
          line-height: 1;
        }
      }
      &.expanded {
        background-color: var(--lightbg-bg1);
        border-color: var(--lightbg-bg3);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.15);
        height: 300px;
        padding: 15px;
        top: -2px;
        left: -1px;
        width: 550px;
        z-index: 50;
      }
      &.fullscreen {
        position: fixed;
        top: 100px;
        left: 100px;
        width: calc(100vw - 200px);
        height: calc(100vh - 200px);
        max-width: none;
        max-height: none;
        z-index: 200;
      }
    }
  }

  

  .chart-fade-enter-active { transition: opacity 0.15s ease; }
  .chart-fade-leave-active { transition: opacity 0.1s ease; }
  .chart-fade-enter-from, .chart-fade-leave-to { opacity: 0; }
</style>
