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
  @import url('https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css');
  @import '@/assets/css/layout.scss';

  #app {
    margin-left: 300px;
    margin-top: 0px;
    padding: 0px;
  }

  .fade-enter-active, .fade-leave-active { transition: opacity .5s; }
  .fade-enter, .fade-leave-to { opacity:0; }
</style>
