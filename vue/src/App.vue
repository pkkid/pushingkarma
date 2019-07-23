<template>
  <div id="app">
    <Navigation/>
    <transition name='fade'>
      <router-view></router-view>
    </transition>
  </div>
</template>

<script>
import Navigation from './components/Navigation.vue';

export default {
  name: 'App',
  components: {Navigation},
}
</script>

<style lang='scss'>
  @import url('https://fonts.googleapis.com/css?family=Montserrat:300,400,500&display=swap');
  @import '@/assets/css/colors.scss';

  body, html {
    background-color: #f8f8f8;
    color: $light-fg0;
    margin: 0px;
    padding: 0px;
    overflow-y: hidden;
  }
  #app {
    font-family: 'Montserrat', Helvetica, Arial, sans-serif;
    text-align: center;
    margin-left: 300px;
    margin-top: 0px;
    padding: 0px;
  }

  .fade-enter-active, .fade-leave-active { transition: opacity .5s; }
  .fade-enter, .fade-leave-to { opacity:0; }
</style>
