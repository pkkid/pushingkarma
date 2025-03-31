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
  import {useAxiosSettings, useStorage} from '@/composables'
  import {api, utils} from '@/utils'
  import axios from 'axios'

  const user = ref(null)                                        // currently logged in user details
  const globalvars = ref(null)                                  // global variables fetched from the server
  const axiosSettings = useAxiosSettings()                      // API settings using our composable
  // const countQueries = useStorage('axios.countqueries', false)  // Count queries on the server
  // const logQueries = useStorage('axios.logqueries', false)      // Log queries on the server
  // const saveHistory = useStorage('axios.saveHistory', false)    // Log queries on the server
  
  provide('axiosSettings', axiosSettings)
  provide('globalvars', {globalvars})
  provide('user', {user, setUser:function(data) { user.value = data }})
  // provide('countQueries', {countQueries,
  //   setCountQueries:function(newval) {
  //     countQueries.value = newval
  //     api.setCountQueries(newval)
  //   }
  // })
  // provide('logQueries', {logQueries,
  //   setLogQueries:function(newval) {
  //     logQueries.value = newval
  //     api.setLogQueries(newval)
  //   }
  // })
  
  // On Mounted
  // Setup environment before mounting
  onBeforeMount(async function() {
    // Initialize the axios settings
    // api.setCountQueries(countQueries.value)
    // api.setLogQueries(logQueries.value)
    // Add browser to the body for easier css
    var useragent = navigator.userAgent.toLowerCase()
    if (useragent.indexOf('chrome') > -1) { document.body.classList.add('chrome') }
    if (useragent.indexOf('firefox') > -1) { document.body.classList.add('firefox') }
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
