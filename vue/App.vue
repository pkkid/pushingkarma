<template>
  <Navigation />
  <div id='content' class='gridbgx'>
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
  body {
    min-height: 100vh;
    overflow-x: hidden;
  }
  #content {
    min-height: 100vh;
    color: #111;
  }
  body.leftnav {
    --navwidth: 300px;
    --navheight: 0px;
    #content {
      margin-left: var(--navwidth);
    }
  }
  body.topnav {
    --navwidth: 0px;
    --navheight: 60px;
    #content {
      padding-top: var(--navheight);
    }
  }
</style>
