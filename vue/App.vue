<template>
  <Navigation />
  <div id='content' class='gridbg'>
    <router-view></router-view>
  </div>
</template>

<script setup>
  import {onMounted} from 'vue'
  import Navigation from '@/views/site/Navigation.vue'

  onMounted(function() {
    // Check Dev Favicon
    if (window.location.hostname == 'localhost') {
      let favicon = document.getElementById('favicon')
      favicon.href = '/static/img/devicon.ico'
    }
  })
</script>

<style>
  body { min-height:100vh; }
  #content { min-height:100vh; color:#111; }
  body.leftnav {
    --navwidth: 300px;
    #content { margin-left: var(--navwidth); }
  }
  body.topnav {
    --navheight: 60px;
    #content { padding-top: var(--navheight); }
  }
</style>
