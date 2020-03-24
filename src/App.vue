<template>
  <div id='app' :class='layout'>
    <div id='content'>
      <div id='logo'>
        <router-link to='/#splash'>
          <img src='./assets/img/pk.svg'/><br/>
          <span class='title'>PushingKarma</span>
        </router-link>
        <span v-if='user.id' class='subtext'>
          <a v-if='globals.DEBUG == false' href='http://localhost:8000'>To Development</a>
          <a v-if='globals.DEBUG == true' href='http://pushingkarma.com'>To Production</a>
          - <a href='/api/'>API</a>
        </span>
      </div>
      <transition name='fadein'><router-view/></transition>
    </div>
    <portal-target name='modal-container'/>
    <Notification/>
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
      globals: pathify.sync('global/globals'),
      gauth: pathify.sync('global/gauth'),
      user: pathify.sync('global/user'),
    },
    created: function() {
      this.globals = JSON.parse(document.getElementById('globals').textContent);
      this.init_gauth();
    },
    methods: {
      // Initialize Google Authenticatin service
      // Allows login via Google
      init_gauth: function() {
        var self = this;
        if (this.globals.GOOGLE_ENABLED) {
          gapi.load('auth2', function() {
            self.gauth = gapi.auth2.init({
              client_id: self.globals.GOOGLE_CLIENTID,
              scope: self.globals.GOOGLE_SCOPES
        });});}
      },
    },
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
    color: $darkbg-text;
    height: 220px;
    left: 0px;
    position: fixed;
    top: 0px;
    width: 300px;
    z-index: 30;

    img {
      height: 85px;
      left: 80px;
      position: absolute;
      top: 50px;
      transition: all 0.5s $bounce;
    }
    .title {
      color: $darkbg-text;
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
    .subtext {
      color: darken($darkbg-text, 50%);
      position: absolute;
      font-size: 10px;
      font-weight: 500;
      top: 165px;
      left: 65px;
      transition: all 0.5s $bounce;
      a, a:visited { color: $darkbg-text; opacity:0.6; }
      a:hover { opacity:0.8; }
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
    .subtext { top: 35px; left:100px; }
  }
  .nonav #logo { display:none; }

</style>
