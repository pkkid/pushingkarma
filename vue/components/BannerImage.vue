<template>
  <div id='bannerimage'>
    Banner Image!
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
    position: absolute;
    top: 0px;
    left: 0px;
    width: 100%;
    height: 200px;
  }
</style>
