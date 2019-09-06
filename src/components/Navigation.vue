<template>
  <div id='navigation' :class='cls'>
    <div class='menu'><ul>
      <li><router-link to='/#splash'>Home</router-link></li>
      <li><router-link to='/#about'>About</router-link></li>
      <li><router-link to='/#projects'>Projects</router-link></li>
      <li><router-link to='/notes'>Notes</router-link></li>
    </ul></div>
    <div class='links'><ul>
      <li><a href='https://github.com/pkkid'><i class='mdi mdi-github-box'></i></a></li>
      <li><a href='https://www.linkedin.com/in/shepanski'><i class='mdi mdi-linkedin-box'></i></a></li>
      <li><a href='https://www.facebook.com/mshepanski'><i class='mdi mdi-facebook-box'></i></a></li>
      <li><a href='javascript:void(0);' @click='displayAccountModal=true'><i class='mdi mdi-account-circle'></i></a></li>
    </ul></div>
    <Modal v-if='displayAccountModal' @close='displayAccountModal=false'>
      Hi Mom!
    </Modal>
  </div>
</template>

<script>
  import Modal from '@/components/utils/modal';

  export default {
    name: 'Navigation',
    components: {Modal},
    props: ['cls'],

    data: function() {
      return {
        displayAccountModal: false,
      };
    }
  };
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';
  $duration: .4s;

  #navigation {
    color: $light-bgh;
    height: 100vh;
    left: 0px;
    position: fixed;
    top: 0px;
    width: 300px;
    z-index: 99;
    padding-top: 220px;
    background-color: $dark-bg0;
    
    a, a:visited {
      color: $dark-fg0;
      text-decoration: none;
      img, .title { position: absolute; }
      &:hover { color: $dark-orange1; }
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
        font-size: 16px;
        font-weight: 500;
        line-height: 29px;
        padding-bottom: 19px;
        position: relative;
        text-decoration: none;
        text-transform: uppercase;
      }
      a:before {
        background-color: $dark-orange1;
        content: "";
        height: 2px;
        left: 100%;
        margin-left: 10px;
        position: absolute;
        top: 14px;
        transform: translateY(-50%);
        transition: all .3s ease;
        width: 0px;
      }
      a:hover:before { width: 35px; }
    }
    .links {
      bottom: 38px;
      font-size: 22px;
      left: -2px;
      margin-bottom: 10px;
      padding: 0px 20px 0px 60px;
      position: absolute;
      text-align: left;
      width: 100%;
      color: $light-bgh;
      li {
        margin: 0px 15px 0px 0px;
        display: inline-block;
      }
    }
  }

  #navigation.topnav {
    height: 60px;
    width: 100%;
    padding: 0px 20px 0px 320px;
    .menu {
      padding: 0px;
      line-height: 60px;
      li {
        float: left;
        margin-right: 80px;
      }
    }
    .links {
      left: auto;
      line-height: 60px;
      right: 0px;
      top: 0px;
      width: 230px;
    }
  }
</style>
