<template>
  <div v-if='bannerurl' id='bannerimage'></div>
</template>

<script setup>
  import {computed} from 'vue'

  const props = defineProps({
    banner: {default:null},
    y: {default:0},
  })

  const bannerurl = computed(function() {
    if (!props.banner) { return null }
    var url = props.banner.replace(/^\[+/, '').replace(/\]+$/, '')
    if (url.startsWith('/')) { return `url(${url})` }
    return `url(/static/notes/PushingKarma/banners/${url})`
  })

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
    transition: background-position 30s ease;
    width: calc(100% - 10px);
  }
</style>
