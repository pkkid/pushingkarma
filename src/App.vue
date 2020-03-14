<template>
  <div id='app' :class='layout'>
    <div id='content'>
      <div id='logo'>
        <router-link to='/#splash'>
          <img src='./assets/img/pk.svg'/><br/>
          <span class='title'>PushingKarma</span>
        </router-link>
      </div>
      <transition name='fadein'>
        <router-view></router-view>
      </transition>
    </div>
    <portal-target name='modal-container'>
    </portal-target>
    <Notification />
  </div>
</template>

<script>
  /* global gapi */
  import * as pathify from 'vuex-pathify';
  import Notification from '@/components/Notification';
  
  export default {
    name: 'App',
    components: {Notification},
    computed: {
      layout: pathify.sync('global/layout'),
      gauth: pathify.sync('global/gauth'),
    },
    created: function() {
      var self = this;
      var globals = JSON.parse(document.getElementById('globals').textContent);
      if (globals.GAUTH_ENABLED) {
        gapi.load('auth2', function() {
          self.gauth = gapi.auth2.init({
            client_id: globals.GOOGLE_CLIENTID,
            scope: globals.GOOGLE_SCOPES
          });
        });
      }
    }
  };
</script>

<style lang='scss'>
  #app {
    margin-top: 0px;
    padding: 0px;
    overflow-y: hidden;
  }
  #logo {
    $bounce: cubic-bezier(.47,1.64,.41,.8);
    
    border-bottom: 1px solid lighten($darkbg-color, 7%);
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
      transition: all 0.5s $bounce;
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
      transition: all 0.5s $bounce;
    }
    a, a:visited { color: $darkbg-text; }
  }

  #content {
    // Border and margin fix margin collapsing
    // when a modal window is open.
    border-top: 1px solid $darkbg-color;
    margin-top: -1px;
    transition: filter .3s ease;
  }

  .topnav #logo {
    border-bottom-width: 0px;
    padding: 10px 20px;
    height: 61px;
    img { height:40px; top:10px; left:20px; }
    .title { top:20px; left:100px; }
  }
  .nonav #logo { display:none; }

</style>
