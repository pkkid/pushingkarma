<template>
  <div id='timewidget' class='widget' :class='{fullscreen, compact}'>
    <div class='time'>{{utils.formatDate(now, 'h:mm')}}</div>
    <div class='date'>{{utils.formatDate(now, 'MMMM D, YYYY')}}</div>
  </div>
</template>

<script setup>
  import {onMounted, ref} from 'vue'
  import {utils} from '@/utils'

  const props = defineProps({
    fullscreen: {type: Boolean, default: false},  // True if browser fullscreen
    compact: {type: Boolean, default: false},     // True in stats layout (no absolute centering)
  })
  const now = ref()                               // Current date and time

  /// Update Time
  // Update the 'now' ref to the current date and time
  const updateTime = async function() {
    now.value = new Date()
  }

  // On Mounted
  // Initialize time and set interval for updates
  onMounted(function() {
    updateTime()
    setInterval(updateTime, 1000)  // 1s
  })
</script>

<style>
  #timewidget {
    position: absolute;
    top: 45%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    .time { font-size:8rem; }
    .date { font-size:3rem; margin-top:-40px; }
    &:not(.compact) {
      background-color: transparent;
    }
    &.compact {
      display: flex;
      flex-direction: column;
      position: static;
      transform: none;
      align-items: center;
      justify-content: center;
      .time { font-size:4em; line-height:1; }
      .date { font-size:1.2em; margin-top:6px; opacity:0.65; }
    }
  }
  #newtab.fullscreen #simple #timewidget {
    .time { font-size: 12rem !important; }
    .date { font-size: 4rem !important; }
  }
</style>
