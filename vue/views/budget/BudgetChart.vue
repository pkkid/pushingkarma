<template>
  <div class='bignum-panel bignum-btn minichart-wrap'>
    <div ref='chart' class='minichart' :class='{expanded: isExpanded}' @click='openExpanded'>
      <Transition name='chart-fade'>
        <slot :isExpanded='isExpanded' :isReady='isReady'/>
      </Transition>
    </div>
  </div>
</template>

<script setup>
  import {onBeforeUnmount, onMounted, ref, watch} from 'vue'

  const props = defineProps({
    collapseKey: {type:[String, Number, Boolean], default:null},
  })

  const isExpanded = ref(false)     // Whether the chart is expanded
  const isReady = ref(true)         // Whether the chart should render (hidden during resize)
  const chart = ref(null)           // Chart container element (for click-outside close)

  // Open Expanded
  // Open the expanded version of the chart
  const openExpanded = function() {
    isExpanded.value = true
  }

  // On Window Pointer Down
  // Close chart only when clicking outside of it
  const onWindowPointerDown = function(evt) {
    if (!isExpanded.value) { return }
    if (chart.value && !chart.value.contains(evt.target)) {
      isExpanded.value = false
    }
  }

  // On Mounted, Watch, Before Unmount
  // Hide chart during resize transition, then restore it
  onMounted(function() {
    window.addEventListener('pointerdown', onWindowPointerDown)
  })
  watch(isExpanded, function() {
    isReady.value = false
    setTimeout(function() { isReady.value = true }, 200)
  })
  watch(() => props.collapseKey, function() {
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
      &.expanded {
        background-color: var(--lightbg-bg1);
        border-color: var(--lightbg-bg3);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.15);
        height: 210px;
        padding: 12px;
        top: -2px;
        left: -1px;
        width: 420px;
        z-index: 50;
      }
    }
  }

  

  .chart-fade-enter-active { transition: opacity 0.15s ease; }
  .chart-fade-leave-active { transition: opacity 0.1s ease; }
  .chart-fade-enter-from, .chart-fade-leave-to { opacity: 0; }
</style>
