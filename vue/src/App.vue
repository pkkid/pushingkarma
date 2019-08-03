<template>
  <div id='app' :class='layout'>
    <div id='logo'>
      <router-link to='/#home'>
        <img src='./assets/img/pk.svg'/><br/>
        <span class='title'>PushingKarma</span>
      </router-link>
    </div>
    <transition name='fade'>
      <router-view></router-view>
    </transition>
  </div>
</template>

<script>
import { sync } from 'vuex-pathify'

export default {
  name: 'App',
  computed: {
   ...sync('*'),
  },
}
</script>

<style lang='scss'>
  @import url('https://fonts.googleapis.com/css?family=Montserrat:300,400,500&display=swap');
  @import url('https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css');
  @import '@/assets/css/layout.scss';
  $duration: 0.5s;

  #app {
    margin-top: 0px;
    padding: 0px;
  }

  #logo {
    background-color: $dark-bg0;
    height: 220px;
    left: 0px;
    letter-spacing: 4px;
    position: absolute;
    text-transform: uppercase;
    top: 0px;
    transition: all $duration ease;
    width: 300px;
    z-index: 999;
    img {
      height: 85px;
      left: 80px;
      position: absolute;
      top: 50px;
      transition: all $duration ease;
    }
    .title {
      font-family: arial;
      font-size: 15px;
      font-weight: bold;
      left: 65px;
      position: absolute;
      top: 150px;
      transition: all $duration ease;
    }
    a, a:visited { color: $dark-fg0; }
  }

  #logo.topnav {
    padding: 10px 20px;
    height: 60px;
    img { height: 40px; top: 10px; left: 20px; }
    .title { top: 20px; left: 100px; }
  }

  .fade-enter-active, .fade-leave-active { transition: opacity .5s; }
  .fade-enter, .fade-leave-to { opacity:0; }
</style>
