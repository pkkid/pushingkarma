<template>
  <div id='bannerimage'></div>
</template>

<script setup>
  import {computed} from 'vue'
  const props = defineProps({
    banner: {required:true},    // Url to the banner image
    y: {default:0},             // Vertical offset of banner image (0-1)  
  })
  const bannerurl = computed(function() { return `url(${props.banner})` })
  const yposition = computed(function() { return `${props.y * 100}%` })
</script>

<style>
  #bannerimage {
    background-image: v-bind(bannerurl);
    background-position: center v-bind(yposition);
    background-repeat: no-repeat;
    background-size: cover;
    border-radius: 2px;
    box-shadow: inset 0px 0px 50px #0008;
    height: 170px;
    left: 5px;
    position: absolute;
    top: 5px;
    width: calc(100% - 10px);
  }
</style>
