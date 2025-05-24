<template>
  <div id='bannerimage'></div>
</template>

<script setup>
  import {computed} from 'vue'

  const props = defineProps({
    banner: {required:true},
    y: {default:0},
  })

  // Banner URL
  // Converts the banner property to a URL str
  const bannerurl = computed(function() {
    var url = props.banner.replace(/^\[+/, '').replace(/\]+$/, '')
    if (url.startsWith('/')) { return `url(${url})` }
    return `url(/static/notes/PushingKarma/banners/${url})`
  })

  // Y Position
  // The background image yposition
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
