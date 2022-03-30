<template>
  <div id='app' :class='layout'>
    <div id='content'>
      <div id='logo' class='darkbg'>
        <router-link to='/#splash'>
          <img src='./assets/img/pk.svg'/><br/>
          <span class='title'>PushingKarma</span>
        </router-link>
        <span v-if='user.id' class='subtext'>
          <a v-if='globals.DEBUG == false' href='http://localhost:8000'>To Development</a>
          <a v-if='globals.DEBUG == true' href='http://pushingkarma.com'>To Production</a>
          <span> - </span><a href='/api/' target='api'>API</a>
          <span> - </span><a href='http://pushingkarma.com/notes?noteid=19' target='todo'>Todo</a>
        </span>
      </div>
      <transition name='fadein'><router-view/></transition>
    </div>
    <portal-target name='modal-container'/>
    <Notification/>
  </div>
</template>

<script>
  /* global google */
  import * as pathify from 'vuex-pathify';
  import Notification from '@/components/Notification';

  export default {
    name: 'App',
    components: {Notification},
    computed: {
      layout: pathify.sync('global/layout'),
      globals: pathify.sync('global/globals'),
      gclient: pathify.sync('global/gclient'),
      user: pathify.sync('global/user'),
    },
    created: function() {
      this.globals = JSON.parse(document.getElementById('globals').textContent);
      this.init_google_code_client();
    },
    methods: {
      // Initialize Google Authenticatin service
      // Allows login via Google
      init_google_code_client: function() {
        var self = this;
        if (this.globals.GOOGLE_ENABLED) {
          console.log('Initialize a Code Client');
          self.gclient = google.accounts.oauth2.initCodeClient({
            client_id: self.globals.GOOGLE_CLIENTID,
            scope: self.globals.GOOGLE_SCOPES,
          });
        }
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
    color: $darkbg-fg0;
    font-family: $fontfamily-title;
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
      color: $darkbg-fg0;
      font-size: 15px;
      font-weight: bold;
      left: 62px;
      letter-spacing: 3px;
      position: absolute;
      text-transform: uppercase;
      top: 150px;
      transition: all 0.5s $bounce;
    }
    .subtext {
      color: darken($darkbg-fg0, 50%);
      position: absolute;
      font-size: 10px;
      font-weight: 500;
      top: 165px;
      left: 63px;
      transition: all 0.5s $bounce;
      a,a:visited,span {
        color: $darkbg-fg0;
        opacity: 0.3;
        transition: all .3s ease;
      }
      a:hover { opacity:0.9; }
    }
  }

  .topnav #logo {
    border-bottom-width: 0px;
    padding: 10px 20px;
    height: 60px;
    img { height:40px; top:10px; left:20px; }
    .title { top:21px; left:100px; }
    .subtext { top:36px; left:100px; }
  }
  .nonav #logo { display:none; }

</style>
