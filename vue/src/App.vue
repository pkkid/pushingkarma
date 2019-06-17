<!-- Template -->
<template>
  <div id="app">
    <SideNav/>
    <Home/>
  </div>
</template>

<!-- Script -->
<script>
import SideNav from './components/SideNav.vue'
import Home from './components/Home.vue'

export default {
  name: 'app',
  components: {
    SideNav,
    Home,
  }
}
</script>

<!-- Styles -->
<style lang='scss'>
  @import url('https://fonts.googleapis.com/css?family=Montserrat:300,400,500&display=swap');
  @import '@/assets/css/colors.scss';

  body, html {
    background-color: #f8f8f8;
    color: $light-fg0;
    margin: 0px;
    padding: 0px;
  }
  #app {
    font-family: 'Montserrat', Helvetica, Arial, sans-serif;
    text-align: center;
    margin-left: 300px;
    margin-top: 0px;
    padding: 0px;
  }
</style>
