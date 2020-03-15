<template>
  <portal to='modal-container'>
    <b-modal :active.sync='display' :width='800' :can-cancel='["escape", "x"]' has-modal-card trap-focus>
      <div id='login' class='card'>
        <div class='bgimg'></div>
        <div class='card-content'>
          <!-- Logged in user info -->
          <div v-if='user.id' class='welcome' key='welcome'>
            <div class='avatar' :style="{backgroundImage:avatar}"></div>
            <h2 style='margin-top:20px;'>Welcome {{user.firstName || "Back"}}! <div class='subtext'>It's great to see you</div></h2>
            <dl>
              <dt>Joined</dt><dd>{{user.date_joined | formatDate('MMM DD, YYYY')}}</dd>
              <dt>Login</dt><dd>{{user.last_login | formatDate('MMM DD, YYYY h:mm a')}}</dd>
              <dt>Email</dt><dd>{{user.email}}</dd>
              <dt>Apikey</dt><dd class='apikey' ref='apikey'>{{user.auth_token || "None"}}</dd>
              <div class='actions'>
                <a href='#' @click='generateToken'>Regenerate</a>
                <a href='#' @click='copyToken'>Copy</a>
              </div>
            </dl>
            <b-button type='is-light' @click='logout'>Log Out</b-button>
          </div>
          <!-- Login form -->
          <div v-else class='loginform' key='loginform'>
            <h2>Login to PushingKarma <div class='subtext'>Amazing things await you</div></h2>
            <img v-if='gauth !== null' class='google' src='@/assets/img/google_signin.png' @click='gauth_login'/>
            <i v-else class='fake-avatar mdi mdi-account-circle-outline'/>
            <form @submit.prevent="login()">
              <b-field label='Email'><b-input v-model='loginform.email' autocomplete='new-password' spellcheck='false' autofocus='true'/></b-field>
              <b-field label='Password'><b-input v-model='loginform.password' type='password'/></b-field>
              <b-button type='is-primary' native-type='submit'>Login</b-button>
            </form>
          </div>
          <!-- Footnote -->
          <div class='footnote'>
            © 2019 PushingKarma. All Rights Reserved.<br/>
            Sunrise graphic by <a href='https://dribbble.com/shots/3200530-Sunrise-wallpaper'>Louis Coyle</a>.
          </div>
        </div>
      </div>
    </b-modal>
  </portal>
</template>

<script>
  import * as api from '@/api';
  import * as utils from '@/utils/utils';
  import * as pathify from 'vuex-pathify';
  import md5 from 'js-md5';
  //import IconButton from '@/components/IconButton';
  //import Modal from '@/components/Modal';
  import {DEFAULT_USER} from '@/store.js';

  export default {
    name: 'Navigation',
    components: {},
    data: () => ({
      display: false,
      loginform: {
        email: '',
        password: '',
      },
    }),
    computed: {
      avatar: pathify.sync('global/avatar'),
      gauth: pathify.sync('global/gauth'),
      user: pathify.sync('global/user'),
    },
    watch: {
      user: function() {
        var hash = md5(this.user.email || '');
        this.avatar = `url('https://www.gravatar.com/avatar/${hash}')`;
      },
    },
    
    methods: {
      // Update Current User
      // Update global/user user in vuex store
      updateCurrentUser: async function() {
        var {data} = await api.Users.getCurrentUser();
        this.user = data;
        console.log(`Logged in as ${this.user.email || 'Guest'}`);
      },

      // GAuth Login
      // Login via Google popup box
      gauth_login: function() {
        let self = this;
        this.gauth.grantOfflineAccess().then(function(data) {
          if (data.code) { self.login(data); }
        });
      },

      // Login
      // Login using username/password to Google auth
      login: async function(payload) {
        payload = payload || {email:this.loginform.email, password:this.loginform.password};
        var {data} = await api.Users.login(payload);
        if (data.id) {
          this.display = false;
          this.user = data || DEFAULT_USER;
          this.loginform.email = '';
          this.loginform.password = '';
          console.log(`Logged in as ${this.user.email}`);
        }
      },

      // Generate Token
      // Generate a new API token
      generateToken: async function() {
        var {data} = await api.Users.generateToken();
        if (data.id) { this.user = data; }
      },

      // Generate Token
      // Generate a new API token
      copyToken: function() {
        utils.copyToClipboard(this.$refs.apikey.innerText);
      },

      // Logout
      // Logout of the site
      logout: async function() {
        await api.Users.logout();
        this.user = DEFAULT_USER;
        this.display = false;
      },
    }

  };
</script>

<style lang='scss'>
  #login {
    background-color: #f8f8f8;
    border-radius: 5px;
    height: 500px;
    position: relative;
    width: 800px;

    .bgimg {
      background-image: url('../../assets/img/louiscoyle.jpg');
      background-position: 0px -28px;
      background-size: 550px;
      border-bottom-right-radius: 5px;
      border-top-right-radius: 5px;
      box-shadow: inset 0 0 100px rgba($darkbg-color, 0.5);
      height: 500px;
      position: absolute;
      right: -2px;
      width: 450px;
    }
    .card-content {
      width: 350px;
    }
    .google {
      cursor: pointer;
      position: relative;
      right: 2px;
      margin: 10px 0px;
    }
    button {
      margin-top: 15px;
      padding-left: 20px;
      padding-right: 20px;
    }
    .avatar {
      background-position: center center;
      background-size: 80px;
      border-bottom: 1px solid #fff;
      border-radius: 10px;
      box-sizing: content-box;
      display: block;
      height: 80px;
      margin: 10px auto 20px auto;
      width: 80px;
    }
    .apikey {
      overflow: hidden;
      text-overflow: ellipsis;
      width: 220px;
    }
    .actions {
      margin-left: 80px;
      line-height: 0.9em;
      a { color:#777; font-size: 0.8em; padding-right:10px; }
      a:hover { color:#333; }
    }
    .footnote {
      bottom: 20px;
      color: $lightbg-text-dim;
      font-size: 0.7em;
      line-height: 1.5;
      position: absolute;
      text-align: center;
      width: 290px;
    }
    


    // .content {
    //   padding: 20px 30px;
    //   height: 500px;
    //   width: 350px;
    //   color: $lightbg-text;
    //   h3 {
    //     font-size: 1.9rem;
    //     padding-left: 0px;
    //     border-left-width: 0px;
    //     text-transform: none;
    //     span { font-size:1.1rem; font-weight:500; display:block; margin-top:3px; }
    //   }
    //   .avatar {
    //     background-size: 80px;
    //     background-position: center center;
    //     border-radius: 10px;
    //     border-bottom: 1px solid #fff;
    //     box-sizing: content-box;
    //     display: block;
    //     height: 80px;
    //     margin: 10px auto 30px auto;
    //     width: 80px;
    //   }
    //   .fake-avatar {
    //     font-size: 4rem;
    //     display: block;
    //     color: #aaa;
    //     text-align: center;
    //   }
    //   .google {
    //     display: block;
    //     cursor: pointer;
    //     position: relative;
    //     right: 2px;
    //     margin: 20px 0px;
    //   }
    //   button {
    //     width: 100%;
    //     padding: 10px 20px;
    //     margin-top: 30px;
    //   }
    //   .auth_token {
    //     padding: 0px;
    //     width: 190px;
    //     border: 0px;
    //     background-color: transparent;
    //     border-radius: 0px;
    //     margin-right: 10px;
    //   }
    //   .mdi-refresh {
    //     cursor: pointer;
    //   }
    // }
  }
</style>
