<template>
  <div id='bannerimage'>
  </div>
</template>

<script setup>
  const props = defineProps({
    banner: {required:true},
    y: {default:0},
  })
</script>

<style>
  #bannerimage {
    border: 1px solid red;
  }
</style>
