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
import SideNav from './components/SideNav.vue'

export default {
  name: 'app',
  components: {
    SideNav
  }
}
</script>

<!-- Styles -->
<style lang='scss'>
  @import url('https://fonts.googleapis.com/css?family=Montserrat:300,400,500&display=swap');
  @import '@/assets/css/colors.scss';

  body {
    background-color: #f8f8f8;
    color: $light-fg0;
  }
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    text-align: center;
    margin-left: 300px;
    margin-top: 60px;
    padding: 0px 20px;
  }
</style>
