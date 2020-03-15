<template>
  <b-modal :active.sync='display' :width="640" :can-cancel='["escape", "x"]' has-modal-card trap-focus>
    <div id='login' class='card'>
      <div class='card-content'>
        <div class='content'>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit.
          Phasellus nec iaculis mauris. <a>@bulmaio</a>.
          <a>#css</a> <a>#responsive</a>
          <br>
          <small>11:09 PM - 1 Jan 2016</small>
        </div>
      </div>
    </div>
   </b-modal>
</template>

<script>
  import * as api from '@/api';
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
    
    
    // border: 1px solid red;
    // width: 800px;

    // .bgimg {
    //   background-image: url('../../assets/img/louiscoyle.jpg');
    //   background-size: 550px;
    //   float: right;
    //   width: 450px;
    //   height: 500px;
    //   background-position: 0px -28px;
    //   border-top-right-radius: 8px;
    //   border-bottom-right-radius: 8px;
    //   box-shadow: inset 0 0 100px rgba($darkbg-color, 0.5);
    //   position: relative;
    //   left: 2px;
    // }
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
