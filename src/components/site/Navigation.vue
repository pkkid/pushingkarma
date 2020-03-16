<template>
  <div id='navigation' class='darkbg' :class='{topnav:cls=="topnav"}'>
    <div class='menu'><ul>
      <li><router-link to='/#splash'>Home</router-link></li>
      <li><router-link to='/#about'>About</router-link></li>
      <li><router-link to='/#projects'>Projects</router-link></li>
      <li><router-link to='/notes'>Notes</router-link></li>
      <li v-if='user.id'><router-link to='/budget'>Budget</router-link></li>
    </ul></div>
    <div class='links'>
      <div><a href='https://github.com/pkkid'><b-icon icon='github-box'/></a></div>
      <div><a href='https://www.linkedin.com/in/shepanski'><b-icon icon='linkedin-box'/></a></div>
      <div><a href='https://www.facebook.com/mshepanski'><b-icon icon='facebook-box'/></a></div>
      <div @click='$refs.login.display = true' style='cursor:pointer;'>
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
    },
  };
</script>

<style lang='scss'>
  #navigation {
    font-family: $font-serif;
    font-size: 16px;
    height: 100vh;
    left: 0px;
    min-height: 600px;
    padding-top: 220px;
    position: fixed;
    top: 0px;
    width: 300px;
    z-index: 29;
    
    a,a:visited {
      img, .title { position: absolute; }
    }
    ul {
      margin: 0px;
      padding: 0px;
      list-style-type: none;
      li { margin: 0px; }
    }
    .menu {
      padding: 50px 20px 0px 60px;
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
        background-color: $darkbg-link-hover;
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
      a:hover:before { width: 35px; }
    }
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
      background-size: 20px;
      border-radius: 3px;
      display: block;
      height: 20px;
      left: 3px;
      position: relative;
      top: -2px;
      transition: box-shadow 0.2s ease;
      width: 20px;
      &:hover { box-shadow: 0px 0px 8px rgba($darkbg-link, 0.4); }
    }
  }

  #navigation.topnav {
    box-shadow: 0px 1px 2px rgba(0,0,0,0.3);
    height: 60px;
    min-height: 60px;
    min-width: 1200px;
    padding: 0px 20px 0px 320px;
    width: 100%;
    .menu {
      line-height: 60px;
      padding: 0px;
      li { float:left; margin-right:80px; }
    }
    .links {
      left: auto;
      bottom: auto;
      right: 60px;
    }
  }
</style>
