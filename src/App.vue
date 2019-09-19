<template>
  <div id='app' :class='layout'>
    <div id='content'>
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
    <portal-target name='modal-container'>
    </portal-target>
  </div>
</template>

<script>
  import {sync} from 'vuex-pathify';
  
  export default {
    name: 'App',
    computed: {
      layout: sync('global/layout'),
    },
  };
</script>

<style lang='scss'>
  @import url('https://cdnjs.cloudflare.com/ajax/libs/MaterialDesign-Webfont/4.2.95/css/materialdesignicons.min.css');
  @import url('https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css');
  @import url('https://fonts.googleapis.com/css?family=Montserrat:300,400,500&display=swap');
  @import '@/assets/css/layout.scss';
  $animate_duration: 0.5s;

  #app {
    margin-top: 0px;
    padding: 0px;
    overflow-y: hidden;
  }

  $animate_duration: .5s;
  #logo {
    border-bottom: 1px solid #3c3836;
    height: 220px;
    left: 0px;
    position: fixed;
    top: 0px;
    width: 300px;
    z-index: 98;
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
    a, a:visited { color: #fbf1c7; }
  }

  #content {
    // Border and margin fix margin collapsing
    // when a modal window is open.
    border-top: 1px solid #282828;
    margin-top: -1px;
    transition: filter .3s ease;
  }
  body.modalOpen #content {
    filter: blur(2px);
  }

  .topnav #logo {
    padding: 10px 20px;
    height: 61px;
    img { height: 40px; top: 10px; left: 20px; }
    .title { top: 20px; left: 100px; }
  }
</style>
