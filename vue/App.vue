<template>
  <Navigation />
  <div id='content' class='gridbgx'>
    <router-view></router-view>
  </div>
  <Footer />
</template>

<script setup>
  import {onBeforeMount, provide, ref} from 'vue'
  import {Footer, Navigation} from '@/views/site'
  import {api, utils} from '@/utils'

  const globalvars = ref(null)          // global variables fetched from the server
  const user = ref(null)                // currently logged in user details
  provide('globalvars', {globalvars})
  provide('user', {user, setUser:(data) => user.value = data })

  // On Mounted
  // Setup environment before mounting
  onBeforeMount(async function() {
    // Fetch and save global variables
    var {data} = await api.Main.getGlobalVars()
    var userdata = utils.pop(data, 'user')
    user.value = userdata.id ? userdata : null
    globalvars.value = data
    // Set the development favicon
    if (globalvars.value.DEBUG) {
      let favicon = document.getElementById('favicon')
      favicon.href = '/static/img/devicon.ico'
    }
    // Add browser to the body for easier css
    var useragent = navigator.userAgent.toLowerCase()
    if (useragent.indexOf('chrome') > -1) { document.body.classList.add('chrome') }
    if (useragent.indexOf('firefox') > -1) { document.body.classList.add('firefox') }
  })
</script>

<style>
  body {
    min-height: 100vh;
    overflow-x: hidden;
  }
  #content {
    min-height: 100vh;
  }
</style>
