<template>
  <div id='navigation'>
    <div class='logo'>
      <router-link to='/#home'>
        <img src='../assets/img/pk.svg'/><br/>
        <span class='title'>PushingKarma</span>
      </router-link>
    </div>
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

    .logo {
      font-family: arial;
      font-size: 15px;
      font-weight: bold;
      height: 220px;
      letter-spacing: 4px;
      position: relative;
      text-transform: uppercase;
      transition: all $duration ease;
      width: 100%;
      img {
        height: 85px;
        left: 80px;
        top: 50px;
        transition: all $duration ease;
      }
      .title {
        left: 65px;
        top: 150px;
        transition: all $duration ease;
      }
      a, a:visited { color: $dark-fg0; }
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
    .logo {
      padding: 10px 20px;
      height: 60px;
      img { height:40px; top:10px; left:20px; }
      .title { top:20px; left:100px; }
    }
  }
</style>
