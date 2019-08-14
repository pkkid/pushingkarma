<template>
  <div id='app' :class='layout'>
    <div id='logo'>
      <router-link to='/#splash'>
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
import {sync} from 'vuex-pathify'

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
  $animate_duration: 0.5s;

  #app {
    margin-top: 0px;
    padding: 0px;
    overflow-y: hidden;
  }

  $animate_duration: .5s;
  #logo {
    border-bottom: 1px solid $dark-bg1;
    height: 220px;
    left: 0px;
    position: fixed;
    top: 0px;
    width: 300px;
    z-index: 999;
    img {
      height: 85px;
      left: 80px;
      position: absolute;
      top: 50px;
      transition: all $animate_duration cubic-bezier(.47,1.64,.41,.8);
    }
    .title {
      font-family: arial;
      font-size: 15px;
      font-weight: bold;
      left: 65px;
      letter-spacing: 4px;
      position: absolute;
      text-transform: uppercase;
      top: 150px;
      transition: all $animate_duration cubic-bezier(.47,1.64,.41,.8);
    }
    a, a:visited { color: $dark-fg0; }
  }

  .topnav #logo {
    padding: 10px 20px;
    height: 61px;
    img { height: 40px; top: 10px; left: 20px; }
    .title { top: 20px; left: 100px; }
  }

  .fade-enter { opacity:0; }
  .fade-enter-active { transition: opacity $animate_duration; }
</style>
