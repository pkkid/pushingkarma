<template>
  <Modal v-if='display' @close='display=false' :width='"800px"' :padding='"0px"' :escClose=true>
    <div slot='body'>
      <div id='login'>
        <div class='bgimg'></div>
        <div class='content'>
          <div v-if='user.id' class='welcome'>
            <div class='avatar' :style="{backgroundImage:avatar}"></div>
            <h3>Welcome {{user.firstName}}! <span>Great to see you</span></h3>
            <dl>
              <dt>Joined</dt><dd>{{user.dateJoined | formatDate('MMM DD, YYYY')}}</dd>
              <dt>Login</dt><dd>{{user.lastLogin | formatDate('MMM DD, YYYY h:mm a')}}</dd>
              <dt>Email</dt><dd>{{user.email}}</dd>
            </dl>
            <button @click='logout'>Log Out</button>
          </div>
          <div v-else class='loginform'>
            <h3>Login to PushingKarma <span>Amazing things await you</span></h3>
            <img class='google' src='@/assets/img/google_signin.png'/>
            <form @submit.prevent="login">
              <label for='email'>Email Address</label>
              <input type='text' id='email' name='email' v-model='loginform.email' spellcheck='false' autocomplete='off' autofocus='true'/>
              <label for='password'>Password</label>
              <input type='password' id='password' name='password' v-model='loginform.password' autocomplete='off'/>
              <button type='submit'>Login</button>
            </form>
          </div>
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
  import Modal from '@/components/utils/Modal';
  import md5 from 'js-md5';
  import {query} from '@/utils/utils';
  import {sync} from 'vuex-pathify';
  import {DEFAULT_USER} from '@/store.js';

  var USER_FIELDS = 'id email firstName lastName dateJoined lastLogin';
  var QUERY_CURRENT_USER = `query { currentUser { ${USER_FIELDS} }}`;
  var QUERY_LOGIN = `query { login(email:"{email}", password:"{password}") { ${USER_FIELDS} }}`;
  var QUERY_LOGOUT = `query { logout { ${USER_FIELDS} }}`;

  export default {
    name: 'Navigation',
    components: {Modal},
    data: () => ({
      display: false,
      loginform: {
        email: '',
        password: '',
      },
    }),

    computed: {
      user: sync('global/user'),
      avatar: function() {
        return "url('https://www.gravatar.com/avatar/"+ md5(this.user.email) +"')";
      },
    },
    
    methods: {
      // Update Current User - Update global/user user in vuex store
      updateCurrentUser: function() {
        let self = this;
        let request = query(QUERY_CURRENT_USER);
        request.xhr.then(function(response) {
          self.user = response.data.data.currentUser || DEFAULT_USER;
          console.log('Current user: '+ self.user.email);
        });
      },

      // Login - Login using username/password to Google auth
      login: function() {
        let self = this;
        let data = {email:this.loginform.email, password:this.loginform.password};
        let request = query(QUERY_LOGIN, data);
        request.xhr.then(function(response) {
          self.user = response.data.data.login || DEFAULT_USER;
          console.log('Logged in as: '+ self.user.email);
        });
      },

      // Logout - Logout of the site
      logout: function() {
        let self = this;
        let request = query(QUERY_LOGOUT);
        request.xhr.then(function(response) {
          self.user = DEFAULT_USER;
          console.log(response);
        });
      },
    }

  };
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  #login {
    .bgimg {
      background-image: url('../assets/img/louiscoyle.png');
      background-size: 550px;
      float: right;
      width: 450px;
      height: 500px;
      background-position: 0px -28px;
      border-top-right-radius: 8px;
      border-bottom-right-radius: 8px;
      box-shadow: inset 0 0 100px rgba(0,0,0,0.5);
      position: relative;
      left: 2px;
    }

    .content {
      padding: 20px 30px;
      height: 500px;
      width: 350px;
      color: $dark-bg0;
      h3 {
        font-size: 20px;
      }
      h3 span {
        font-size: 13px;
        display: block;
        padding: 3px 0px;
        font-weight: 100;
      }
      dl {
        margin: 10px 0px;
        font-size: 15px;
        line-height: 23px;
        dt {
          width: 60px;
          float: left;
          font-size: 11px;
          margin-right: 10px;
          color: #888;
          text-transform: uppercase;
        }
      }
      .avatar {
        background-size: 80px;
        background-position: center center;
        border-radius: 15px;
        border: 5px solid rgba($light-fg0,0.5);
        box-shadow: 0px 1px 2px rgba(0,0,0,0.3);
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
      label {
        font-size: 13px;
        display: block;
        padding: 3px 0px;
        font-weight: 100;
        margin-top: 10px;
      }
      input {
        width: 100%;
        border-radius: 6px;
        border: 2px solid #ddd;
        background-color: #f8f8f8;
        padding: 10px;
      }
      button {
        background-color: $light-blue1;
        color: $light-bgh;
        width: 100%;
        padding: 12px;
        border-radius: 6px;
        border-width: 0px;
        cursor: pointer;
        margin-top: 30px;
      }
      .footnote {
        position: absolute;
        bottom: 20px;
        text-align: center;
        color: #888;
        font-size: 12px;
        margin-top: 30px;
        width: 290px;
        line-height: 16px;
      }
    }
  }
</style>
