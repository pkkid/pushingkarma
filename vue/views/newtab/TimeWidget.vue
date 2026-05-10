<template>
  <div id='timewidget' :class='{fullscreen}'>
    <div class='time'>{{utils.formatDate(now, 'h:mm')}}</div>
    <div class='date'>{{utils.formatDate(now, 'MMMM D, YYYY')}}</div>
  </div>
</template>

<script setup>
  import {onMounted, ref} from 'vue'
  import {utils} from '@/utils'

  const props = defineProps({
    fullscreen: {type: Boolean, default: false},  // True if browser fullscreen
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
    &.fullscreen {
      .time { font-size:12rem; }
      .date { font-size:4rem; }
    }
  }
</style>
