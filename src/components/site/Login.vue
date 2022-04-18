<template>
  <portal to='modal-container'>
    <b-modal :active.sync='display' :width='800' :can-cancel='["escape", "x"]' has-modal-card trap-focus>
      <div id='login' class='card'>
        <div class='bgimg'></div>
        <div class='card-content'>
          <!-- Logged in user info -->
          <article v-if='user.id' class='welcome' key='welcome'>
            <div class='avatar' :style="{backgroundImage:avatar}"></div>
            <h2 style='margin-top:20px;'>Welcome {{user.name || "Back"}}! <div class='subtext'>It's great to see you</div></h2>
            <dl>
              <!-- Basic Account Info -->
              <dt>Joined</dt><dd>{{user.date_joined | formatDate('MMM DD, YYYY')}}</dd>
              <dt>Login</dt><dd>{{user.last_login | formatDate('MMM DD, YYYY h:mm a')}}</dd>
              <dt>Email</dt><dd>{{user.email}}</dd>
              <!-- Google API -->
              <dt>Google</dt>
              <dd v-if='user.google_email'>{{user.google_email}}
                <div class='actions'><a href='#' @click='disconnect("google")'>Disconnect</a></div>
              </dd>
              <dd v-else><a @click='googleLogin'>Not Connected</a></dd>
              <!-- Django APIKey -->
              <dt>Apikey</dt>
              <dd ref='apikey'>
                {{user.auth_token || "None"}}
                <div class='actions'>
                  <a href='#' @click='generateToken'>Regenerate</a>
                  <a href='#' @click='copyToken'>Copy</a>
                </div>
              </dd>
            </dl>
            <b-button type='is-small' @click='logout'>Log Out</b-button>
          </article>
          <!-- Login form -->
          <article v-else class='loginform' key='loginform'>
            <h2>Login to PushingKarma <div class='subtext'>Amazing things await you</div></h2>
            <button v-if='gclient !== null' class='google' @click='googleLogin'>Sign in with Google</button>
            <i v-else class='fake-avatar mdi mdi-account-circle-outline'/>
            <form @submit.prevent="login()">
              <b-field label='Email'><b-input v-model='loginform.email' autocomplete='new-password' spellcheck='false' autofocus='true'/></b-field>
              <b-field label='Password'><b-input v-model='loginform.password' type='password'/></b-field>
              <b-button type='is-primary is-small' native-type='submit'>Login</b-button>
            </form>
          </article>
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
  import {DEFAULT_USER} from '@/store.js';

  export default {
    name: 'Navigation',
    components: {},
    data: () => ({
      display: false,
      loginform: {email:'',  password:''},
    }),
    computed: {
      globals: pathify.get('global/globals'),
      avatar: pathify.sync('global/avatar'),
      gclient: pathify.sync('global/gclient'),
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

      // Google Login
      // Login via Google popup box
      googleLogin: function() {
        let self = this;
        self.gclient.callback = function(data) {
          if (data.code) { self.login({google_code:data.code}); }
        };
        self.gclient.requestCode({prompt: ''});
      },

      // Login
      // Login using username/password to Google auth
      login: async function(payload) {
        payload = payload || {email:this.loginform.email, password:this.loginform.password};
        var {data} = await api.Users.login(payload);
        if (data.id) {
          //this.display = false;
          this.user = data || DEFAULT_USER;
          this.loginform.email = '';
          this.loginform.password = '';
          console.log(`Logged in as ${this.user.email}`);
        }
      },

      // Generate Token
      // Generate a new API token
      generateToken: async function() {
        this.$buefy.dialog.confirm({
          title: 'Generate New Token',
          message: `Are you sure you wish to generate a new API token? This will invalidate the current API token.`,
          confirmText: 'Generate Token',
          focusOn: 'cancel',
          onConfirm: async function() {
            var {data} = await api.Users.generateToken();
            if (data.id) { this.user = data; }
          },
        });
      },

      // Generate Token
      // Generate a new API token
      copyToken: function() {
        utils.copyToClipboard(this.$refs.apikey.innerText);
      },

      // Google Disconnect
      // Disconnect the Google account
      disconnect: async function(provider) {
        var {data} = await api.Users.disconnect(provider);
        if (data.id) { this.user = data; }
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
  .modal .animation-content {
    position: relative;
  }
  .modal .modal-close {
    position: absolute;
    top: 10px;
    right: 8px;
  }
  #login {
    background-color: $lightbg-bg1;
    box-shadow: inset 0 0 5em 1em rgba($lightbg-fg0 ,0.15);
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
      background-color: #f8f8f8;
      background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHhtbG5zPSJo\
        dHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGcgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIj48cGF0aCBkPSJ\
        NMTcuNiA5LjJsLS4xLTEuOEg5djMuNGg0LjhDMTMuNiAxMiAxMyAxMyAxMiAxMy42djIuMmgzYTguOCA4LjggMCAwIDAgMi\
        42LTYuNnoiIGZpbGw9IiM0Mjg1RjQiIGZpbGwtcnVsZT0ibm9uemVybyIvPjxwYXRoIGQ9Ik05IDE4YzIuNCAwIDQuNS0uO\
        CA2LTIuMmwtMy0yLjJhNS40IDUuNCAwIDAgMS04LTIuOUgxVjEzYTkgOSAwIDAgMCA4IDV6IiBmaWxsPSIjMzRBODUzIiBm\
        aWxsLXJ1bGU9Im5vbnplcm8iLz48cGF0aCBkPSJNNCAxMC43YTUuNCA1LjQgMCAwIDEgMC0zLjRWNUgxYTkgOSAwIDAgMCA\
        wIDhsMy0yLjN6IiBmaWxsPSIjRkJCQzA1IiBmaWxsLXJ1bGU9Im5vbnplcm8iLz48cGF0aCBkPSJNOSAzLjZjMS4zIDAgMi\
        41LjQgMy40IDEuM0wxNSAyLjNBOSA5IDAgMCAwIDEgNWwzIDIuNGE1LjQgNS40IDAgMCAxIDUtMy43eiIgZmlsbD0iI0VBN\
        DMzNSIgZmlsbC1ydWxlPSJub256ZXJvIi8+PHBhdGggZD0iTTAgMGgxOHYxOEgweiIvPjwvZz48L3N2Zz4=');
      background-position: 12px 9px;
      background-repeat: no-repeat;
      border-radius: 3px;
      border: none;
      box-shadow: 0 -1px 0 rgba(0, 0, 0, .04), 0 1px 1px rgba(0, 0, 0, .25);
      color: #757575;
      font-weight: 500;
      margin-bottom: 20px;
      padding: 10px 12px 10px 40px;
      transition: background-color .2s ease-in, box-shadow .2s ease-in;
      &:hover {
        background-color: #ffffff;
        box-shadow: 0 -1px 0 rgba(0, 0, 0, .04), 0 2px 4px rgba(0, 0, 0, .25);
      }
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
    dt {
      width: 60px;
    }
    dd {
      overflow: hidden;
      text-overflow: ellipsis;
      width: 220px;
    }
    .actions {
      margin-top: -5px;
      a { color:#777; font-size:0.8em; margin-right:15px; }
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
  }
</style>
