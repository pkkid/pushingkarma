<template>
  <Modal v-if='display' @close='display=false' :width='"800px"' :padding='"0px"' :escClose=true :bgClose=true>
    <div slot='body'>
      <div id='login'>
        <div class='bgimg'></div>
        <div class='content'>
          <transition name='fadeslow' appear>
            <div v-if='user.id' class='welcome' key='welcome'>

              <!-- Display logged in user info -->
              <div class='avatar' :style="{backgroundImage:avatar}"></div>
              <h3>Welcome {{user.firstName || "You"}}! <span>Great to see you</span></h3>
              <dl>
                <dt>Joined</dt><dd>{{user.date_joined | formatDate('MMM DD, YYYY')}}</dd>
                <dt>Login</dt><dd>{{user.last_login | formatDate('MMM DD, YYYY h:mm a')}}</dd>
                <dt>Email</dt><dd>{{user.email}}</dd>
                <dt>Token</dt><dd>
                  <input type='text' class='auth_token' :value='user.auth_token || "None"' readonly/>
                  <IconButton :icon='"mdi-refresh"' :click='genToken'/>
                </dd>
              </dl>
              <button @click='logout'>Log Out</button>
            </div>
            <div v-else class='loginform' key='loginform'>
              <!-- Display login form -->
              <h3>Login to PushingKarma <span>Amazing things await you</span></h3>
              <img class='google' src='@/assets/img/google_signin.png' @click='gauth_login'/>
              <form @submit.prevent="login">
                <label for='email'>Email Address</label>
                <input type='text' id='email' name='email' v-model='loginform.email' spellcheck='false' autocomplete='off' autofocus='true'/>
                <label for='password'>Password</label>
                <input type='password' id='password' name='password' v-model='loginform.password' autocomplete='off'/>
                <button type='submit' class='primary'>Login</button>
              </form>
            </div>
          </transition>
          <div class='footnote'>
            © 2019 PushingKarma. All Rights Reserved.<br/>
            Sunrise graphic by <a href='https://dribbble.com/shots/3200530-Sunrise-wallpaper'>Louis Coyle</a>.
          </div>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script>
  import md5 from 'js-md5';
  import {sync} from 'vuex-pathify';
  import IconButton from '@/components/IconButton';
  import Modal from '@/components/Modal';
  import {axios, makeRequest} from '@/utils/utils';
  import {DEFAULT_USER} from '@/store.js';

  var API_CURRENT_USER = '/api/user';
  var API_LOGIN = '/api/user/login';
  var API_LOGOUT = '/api/user/logout';
  var API_GENTOKEN = '/api/user/gentoken';

  export default {
    name: 'Navigation',
    components: {IconButton, Modal},
    data: () => ({
      display: false,
      loginform: {
        email: '',
        password: '',
      },
    }),
    computed: {
      avatar: sync('global/avatar'),
      gauth: sync('global/gauth'),
      user: sync('global/user'),
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
      updateCurrentUser: function() {
        let self = this;
        let request = makeRequest(axios.get, API_CURRENT_USER);
        request.xhr.then(function(response) {
          self.user = response.data || DEFAULT_USER;
          console.log('Current user: '+ self.user.email);
        });
      },

      // GAuth Login
      // Login via Google popup box
      gauth_login: function() {
        let self = this;
        this.gauth.grantOfflineAccess().then(function(data) {
          if (data.code) {
            self.login(null, data);
          }
        });
      },

      // Login
      // Login using username/password to Google auth
      login: function(event, data) {
        let self = this;
        data = data || {email:this.loginform.email, password:this.loginform.password};
        let request = makeRequest(axios.post, API_LOGIN, data);
        request.xhr.then(function(response) {
          if (response.data.id) {
            self.display = false;
            self.user = response.data || DEFAULT_USER;
            self.loginform.email = '';
            self.loginform.password = '';
            console.log('Logged in as: '+ self.user.email);
          }
        });
      },

      // Generate Token
      // Generate a new API token
      genToken: function() {
        console.log('gentoken!');
        let self = this;
        let request = makeRequest(axios.post, API_GENTOKEN);
        request.xhr.then(function(response) {
          if (response.data.id) {
            self.user = response.data;
          }
        });
      },

      // Logout
      // Logout of the site
      logout: function() {
        let self = this;
        let request = makeRequest(axios.post, API_LOGOUT);
        request.xhr.then(function() {
          self.user = DEFAULT_USER;
          self.display = false;
        });
      },
    }

  };
</script>

<style lang='scss'>
  #login {
    .bgimg {
      background-image: url('../../assets/img/louiscoyle.png');
      background-size: 550px;
      float: right;
      width: 450px;
      height: 500px;
      background-position: 0px -28px;
      border-top-right-radius: 8px;
      border-bottom-right-radius: 8px;
      box-shadow: inset 0 0 100px rgba($darkbg-color, 0.5);
      position: relative;
      left: 2px;
    }
    .content {
      padding: 20px 30px;
      height: 500px;
      width: 350px;
      color: $lightbg-text;
      h3 {
        font-size: 1.2em;
        padding-left: 0px;
        border-left-width: 0px;
        text-transform: none;
        span { font-size:0.6em; font-weight:500; display:block; }
      }
      .avatar {
        background-size: 80px;
        background-position: center center;
        border-radius: 10px;
        border-bottom: 1px solid #fff;
        box-sizing: content-box;
        display: block;
        height: 80px;
        margin: 10px auto 30px auto;
        width: 80px;
      }
      .google {
        display: block;
        cursor: pointer;
        position: relative;
        right: 2px;
        margin: 20px 0px;
      }
      button {
        width: 100%;
        padding: 10px 20px;
        margin-top: 30px;
      }
      .auth_token {
        padding: 0px;
        width: 190px;
        border: 0px;
        background-color: transparent;
        border-radius: 0px;
        margin-right: 10px;
      }
      .mdi-refresh {
        cursor: pointer;
      }
    }
  }
</style>
