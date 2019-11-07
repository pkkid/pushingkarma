<template>
  <div id='navigation' class='darkbg' :class='{topnav:cls=="topnav"}'>
    <div class='menu'><ul>
      <li><router-link to='/#splash'>Home</router-link></li>
      <li><router-link to='/#about'>About</router-link></li>
      <li><router-link to='/#projects'>Projects</router-link></li>
      <li><router-link to='/notes'>Notes</router-link></li>
      <li v-if='user.id'><router-link to='/budget'>Budget</router-link></li>
    </ul></div>
    <div class='links'><ul>
      <li><a href='https://github.com/pkkid'><i class='mdi mdi-github-box'></i></a></li>
      <li><a href='https://www.linkedin.com/in/shepanski'><i class='mdi mdi-linkedin-box'></i></a></li>
      <li><a href='https://www.facebook.com/mshepanski'><i class='mdi mdi-facebook-box'></i></a></li>
      <li><a href='javascript:void(0);' @click='$refs.login.display=true'>
        <transition name='bouncein'>
          <i v-if='user.id' class='avatar' key='avatar' :style="{backgroundImage:avatar}"></i>
          <i v-else class='mdi mdi-account-circle' key='icon'></i>
        </transition>
      </a></li>
    </ul></div>
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
      user: pathify.get('global.user'),
    },
    mounted: function() {
      this.$refs.login.updateCurrentUser();
    },
  };
</script>

<style lang='scss'>
  #navigation {
    font-size: 1.6rem;
    height: 100vh;
    left: 0px;
    min-height: 600px;
    padding-top: 220px;
    position: fixed;
    top: 0px;
    width: 300px;
    z-index: 97;
    
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
      bottom: 38px;
      font-size: 1.4em;
      left: -2px;
      margin-bottom: 10px;
      padding: 0px 20px 0px 60px;
      position: absolute;
      text-align: left;
      width: 100%;
      color: $darkbg-link;
      li {
        margin: 0px 15px 0px 0px;
        display: inline-block;
      }
      .avatar {
        background-size: 20px;
        border-radius: 3px;
        display: block;
        height: 20px;
        margin-left: 3px;
        position: relative;
        top: 2px;
        transition: box-shadow 0.2s ease;
        width: 20px;
        &:hover { box-shadow: 0px 0px 8px rgba($darkbg-link, 0.4); }
      }
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
      line-height: 60px;
      right: 0px;
      top: 0px;
      width: 250px;
    }
  }
</style>
