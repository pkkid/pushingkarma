<template>
  <div id='navigation' class='darkbg'>
    <div class='menu'>
      <div><router-link to='/#splash'>Home</router-link></div>
      <div><router-link to='/#about'>About</router-link></div>
      <div><router-link to='/#projects'>Projects</router-link></div>
      <div><router-link to='/notes'>Notes</router-link></div>
      <div v-if='user.id'><router-link to='/budget'>Budget</router-link></div>
    </div>
    <div class='links'>
      <div><a href='https://github.com/pkkid'><b-icon icon='github-box'/></a></div>
      <div><a href='https://www.linkedin.com/in/shepanski'><b-icon icon='linkedin-box'/></a></div>
      <div><a href='https://www.facebook.com/mshepanski'><b-icon icon='facebook-box'/></a></div>
      <div class='avatarwrap' @click='$refs.login.display = true' style='cursor:pointer;'>
        <i v-if='user.id' class='avatar' key='avatar' :style="{backgroundImage:avatar}"/>
        <a v-else><b-icon icon='account-circle'/></a>
      </div>
    </div>
    <Login ref='login'/>
  </div>
</template>

<script>
  import * as pathify from 'vuex-pathify';
  import Login from '@/components/site/Login';
  
  export default {
    name: 'Navigation',
    components: {Login},
    props: ['cls'],
    computed: {
      avatar: pathify.sync('global/avatar'),
      user: pathify.sync('global/user'),
    },
    mounted: function() {
      this.$refs.login.updateCurrentUser();
      this.$store.set('global/layout', this.cls);
    },
  };
</script>

<style lang='scss'>
  #navigation {
    font-family: $fontfamily-title;
    font-weight: 400;
    font-size: 16px;
    position: fixed;
    width: 300px;
    height: 100vh;
    top: 0px;
    left: 0px;
    min-height: 600px;
    padding-top: 220px;
    z-index: 29;

    // Main Menu
    .menu {
      padding: 50px 20px 0px 60px;
      font-size: 16px;
      width: 100%;
      a {
        display: inline-block;
        font-weight: 500;
        line-height: 1.6em;
        padding-bottom: 19px;
        position: relative;
        text-decoration: none;
        text-transform: uppercase;
        user-select: none;
      }
      a:before {
        background-color: $darkbg-bg0;
        content: "";
        height: 2px;
        left: 100%;
        margin-left: 10px;
        position: absolute;
        top: 13px;
        transform: translateY(-50%);
        transition: all .3s ease;
        width: 0px;
      }
      a:hover:before {
        width: 35px;
        background-color: $darkbg-link-hover;
      }
    }

    // Social links and Avatar
    .links {
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: absolute;
      bottom: 40px;
      left: 58px;
      width: 130px;
      height: 60px;
    }
    .avatar {
      background-size: 24px;
      border-radius: 3px;
      display: block;
      height: 26px;
      top: -4px;
      position: relative;
      transition: box-shadow 0.2s ease;
      width: 26px;
      padding: 8px;
      border: 1px solid #666;
    }
    .links a { padding:11px 8px 5px 8px; border-radius:3px; }
    .links a:hover { background-color: #444; color: #fbf1c7; transition: background-color 0.2s ease;  }
    .links .avatarwrap { padding:9px 8px 2px 8px; border-radius:3px; }
    .links .avatarwrap:hover { background-color: #444; transition: background-color 0.2s ease; }
  }

  // Top navigation
  .topnav #navigation {
    box-shadow: 0px 1px 2px rgba(0,0,0,0.3);
    height: 60px;
    min-height: 60px;
    min-width: 1200px;
    padding: 0px 20px 0px 320px;
    width: 100%;
    .menu {
      line-height: 60px;
      padding: 0px;
      div { float:left; margin-right:80px; }
    }
    .links {
      left: auto;
      bottom: auto;
      right: 60px;
    }
  }
</style>
