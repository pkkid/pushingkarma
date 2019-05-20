<!-- Template -->
<template>
  <div id="app">
    <h1>Hello PushingKarma!</h1>
    <SideNav/>
    <!-- <Splash/>
    <AboutMe/>
    <Projects/> -->
  </div>
</template>

<!-- Script -->
<script>
import SideNav from './components/sidenav.vue'

export default {
  name: 'app',
  components: {
    SideNav
  }
}
</script>

<!-- Styles -->
<style lang='scss'>
  body {
    background-color: #283247;
    color: #f8f8f8;
  }
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    text-align: center;
    margin-left: 300px;
    margin-top: 60px;
    padding: 0px 20px;
  }
</style>
