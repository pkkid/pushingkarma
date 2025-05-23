<template>
  <div id='bannerimage'></div>
</template>

<script setup>
  import {computed} from 'vue'

  const props = defineProps({
    banner: {required:true},
    y: {default:0},
  })

  const bannerurl = computed(function() {
    var url = props.banner.replace(/^\[+/, '').replace(/\]+$/, '')
    if (url.startsWith('/')) { return `url(${url})` }
    return `url(/static/notes/PushingKarma/banners/${url})`
  })

  const yposition = computed(function() { return `${props.y * 100}%` })
</script>

<style>
  #bannerimage {
    background-image: v-bind(bannerurl);
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center v-bind(yposition);
    /* mask-image: linear-gradient(to bottom, black 50%, transparent 100%); */
    position: absolute;
    top: 5px;
    left: 5px;
    width: calc(100% - 10px);
    border-radius: 2px;
    box-shadow: 0px 0px 2px #0005;
    height: 170px;
  }
</style>
