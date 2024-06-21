<template>
  <Navigation />
  App View!
</template>

<script setup>
  import {onMounted} from 'vue'
  import Navigation from '@/views/site/Navigation.vue'

  onMounted(() => checkDevFavicon()) 

  // Check Dev Favicon
  // Updates development favicon if domain is localhost
  const checkDevFavicon = function() {
    if (window.location.hostname == 'localhost') {
      let favicon = document.getElementById('favicon')
      favicon.href = '/static/img/devicon.ico'
    }
  }
</script>

<style scoped>
  
</style>
