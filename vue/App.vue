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
  import {useStorage} from '@/composables'
  import {api, utils} from '@/utils'
  import axios from 'axios'

  const user = ref(null)                                        // currently logged in user details
  const globalvars = ref(null)                                  // global variables fetched from the server
  const countQueries = useStorage('axios.countqueries', false)  // Count queries on the server
  const logQueries = useStorage('axios.logqueries', false)      // Log queries on the server

  provide('user', {user, setUser:(data) => user.value = data })
  provide('globalvars', {globalvars})
  provide('countQueries', {countQueries, setCountQueries:(newval) => setCountQueries(newval) })
  provide('logQueries', {logQueries, setLogQueries:(newval) => setLogQueries(newval)})
  
  // On Mounted
  // Setup environment before mounting
  onBeforeMount(async function() {
    setCountQueries(countQueries.value)
    setLogQueries(logQueries.value)
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

  // Update Count Queries
  // Includes the Count-Queries header in requests
  const setCountQueries = function(newval) {
    countQueries.value = newval
    if (newval) { axios.defaults.headers.common['Count-Queries'] = 'true' }
    else { delete axios.defaults.headers.common['Count-Queries'] }
  }
  
  // Update Log Queries
  // Includes the Log-Queries header in requests
  const setLogQueries = function(newval) {
    logQueries.value = newval
    if (newval) { axios.defaults.headers.common['Log-Queries'] = 'true' }
    else { delete axios.defaults.headers.common['Log-Queries'] }
  }
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
