<template>
  <div id='simple'>
    <LogoWidget :fullscreen='fullscreen'/>
    <TimeWidget :fullscreen='fullscreen'/>
    <NewsWidget :fullscreen='fullscreen'/>
  </div>
</template>

<script setup>
  import LogoWidget from './LogoWidget.vue'
  import NewsWidget from './NewsWidget.vue'
  import TimeWidget from './TimeWidget.vue'

  defineProps({fullscreen: {default: false}})
</script>

<style>
  #simple {
    position: relative;
    width: 100%; height: 100%;
  }
</style>
