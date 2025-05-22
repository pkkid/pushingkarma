<template>
  <div v-if='ready'>
    <router-view v-if='route.name == "newtab"'/>
    <template v-else>
      <Notifications ref='notifications'/>
      <Navigation/>
      <div id='content' class='gridbgx'><router-view/></div>
      <Footer/>
    </template>
  </div>
</template>

<script setup>
  import {onBeforeMount, provide, ref, useTemplateRef} from 'vue'
  import {Notifications} from '@/components'
  import {Footer, Navigation} from '@/views/site'
  import {useAxiosSettings} from '@/composables'
  import {useRoute, useRouter} from 'vue-router'
  import {api, utils} from '@/utils'

  const user = ref(null)                                    // currently logged in user details
  const route = useRoute()                                  // Vue route object
  const router = useRouter()                                // Vue router object
  const ready = ref(false)                                  // True when router is ready  
  const globalvars = ref(null)                              // global variables fetched from the server
  const notifications = useTemplateRef('notifications')     // reference to the notifications component
  const axiosSettings = useAxiosSettings()                  // API settings using our composable
  
  provide('axiosSettings', axiosSettings)                   // Axios settings
  provide('globalvars', {globalvars})                       // Global variables
  provide('user', {user, setUser:function(data) { user.value = data }})   // Current user
  provide('notify', {notify: function(...args) {                          // Send notification
    notifications.value.notify.apply(notifications.value, args)
  }})
  router.isReady().then(() => { ready.value = true })
  
  // On Mounted
  // Setup environment before mounting
  onBeforeMount(async function() {
    // Add browser name to the body for easier css
    var useragent = navigator.userAgent.toLowerCase()
    if (useragent.indexOf('chrome') > -1) { document.body.classList.add('chrome') }
    if (useragent.indexOf('firefox') > -1) { document.body.classList.add('firefox') }
    // Fetch and save global variables
    var {data} = await api.Main.getGlobalVars()
    var userdata = utils.pop(data, 'user')
    user.value = userdata?.id ? userdata : null
    globalvars.value = data
    // Set the development favicon
    if (globalvars.value.DEBUG) {
      let favicon = document.getElementById('favicon')
      favicon.href = '/static/img/devicon.ico'
    }
  })
</script>

<style>
  body { min-height:100vh; overflow-x:hidden; }
  #notifications { top:80px; right:20px; }
  #content { min-height:100vh; }
</style>
