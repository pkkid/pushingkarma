<template>
  <div id='navigation' :class='cls'>
    <div class='menu'><ul>
      <li><router-link to='/#home'>Home</router-link></li>
      <li><router-link to='/#about'>About</router-link></li>
      <li><router-link to='/#projects'>Projects</router-link></li>
      <li><router-link to='/notes'>Notes</router-link></li>
    </ul></div>
    <div class='links'><ul>
      <li><a href='https://github.com/pkkid'><i class='mdi mdi-github-box'></i></a></li>
      <li><a href='https://www.linkedin.com/in/shepanski'><i class='mdi mdi-linkedin-box'></i></a></li>
      <li><a href='https://www.facebook.com/mshepanski'><i class='mdi mdi-facebook-box'></i></a></li>
    </ul></div>
  </div>
</template>

<script>
export default {
  name: 'Navigation',
  props: ['cls'],
}
</script>

<style lang='scss'>
  @import url('https://cdnjs.cloudflare.com/ajax/libs/MaterialDesign-Webfont/3.0.39/css/materialdesignicons.min.css');
  @import '@/assets/css/layout.scss';
  $duration: .4s;

  #navigation {
    background-color: $dark-bg0;
    color: $light-bgh;
    height: 100vh;
    left: 0px;
    position: fixed;
    top: 0px;
    width: 300px;
    z-index: 100;
    padding-top: 220px;
    
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
      border-top: 1px solid $dark-bg1;
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
    background-color: $dark-bg0;
    height: 60px;
    width: 100%;
    padding: 0px 0px 0px 300px;
    .menu {
      padding: 0px;
      line-height: 60px;
      li {
        float: left;
        margin-right: 80px;
      }
    }
    .links {
      left: 1000px;
      right: 50px;
      top: 10px;
      width: 200px;
    }
  }
</style>
