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
  @import '@/assets/css/colors.scss';

  // Basic Styles and Colors
  #navigation {
    background-color: $dark-bg0;
    color: $light-bgh;
    z-index: 100;
    a, a:visited {
      color: $dark-fg0;
      transition: all .3s ease;
      text-decoration: none;
      img, .title { position:absolute; }
      &:hover { color: $dark-orange1; }
    }
    ul {
      margin: 0px;
      padding: 0px;
      list-style-type: none;
      font-family: Montserrat, Arial;
      li { margin:0px; }
    }
    // logo
    .logo {
      box-sizing: border-box;
      float: left;
      font-family: arial;
      font-size: 15px;
      font-weight: bold;
      letter-spacing: 4px;
      position: relative;
      text-transform: uppercase;
      width: 300px;
      a, a:visited { color:$dark-fg0; }
      
    }
    // menu
    .menu {
      border-top: 1px solid $dark-bg1;
      box-sizing: border-box;
      float: left;
      padding: 50px 20px 0px 60px;
      width: 300px;
      a {
        display: inline-block;
        font-family: Montserrat, Arial;
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
      a:hover:before { width:35px; }
    }
    // links
    .links {
      bottom: 38px;
      box-sizing: border-box;
      float: left;
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

  // Sizing and Animations
  $duration: .4s;

  #navigation {
    height: 100vh;
    left: 0px;
    position: fixed;
    top: 0px;
    width: 300px;
    transition:
      width $duration ease,
      height $duration $duration ease;
      
    .logo {
      height: 220px;
      transition: all $duration ease;
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
    }
    .menu {
      animation: fademenu .6s;
      position: absolute;
      top: 220px;
      left: 0px;
      transition: all .1s $duration;
    }
  }

  #navigation.topnav {
    width: 100%;
    height: 60px;
    transition:
      height $duration ease,
      width $duration $duration ease;
    .logo {
      padding: 10px 20px;
      height: 60px;
      img { height:40px; top:10px; left:20px; }
      .title { top:20px; left:100px; }
    }
    .menu {
      animation: fademenu .6s;
      // padding-top: 0px;
      // line-height: 60px;
      // width: 600px;
      li { float:left; padding:0px 20px 0px 0px; }
    }
    .links {
      animation: fademenu .6s;
    }
  }

  @keyframes fademenu {
    0% { opacity:1; }
    40% { opacity:0; }
    60% { opacity:0; }
    100% { opacity:1; }
  }



</style>
