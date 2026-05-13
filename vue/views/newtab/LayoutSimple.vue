<template>
  <div id='simple'>
    <WidgetLogo/>
    <WidgetTime/>
    <WidgetNews/>
  </div>
</template>

<script setup>
  import WidgetLogo from './WidgetLogo.vue'
  import WidgetNews from './WidgetNews.vue'
  import WidgetTime from './WidgetTime.vue'
</script>

<style>
  #simple {
    position: relative;
    width: 100%; height: 100%;
  }
</style>
