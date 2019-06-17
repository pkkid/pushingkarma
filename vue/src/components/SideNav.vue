<template>
  <div id='sidenav'>
    <div id='logo'>
      <img class='logo' src='../assets/img/pk.svg'/><br/>
      PushingKarma
    </div>
    <div class='menuwrap'><ul>
      <li><a href='#home' v-smooth-scroll>Home</a></li>
      <li><a href='#about' v-smooth-scroll>About</a></li>
      <li><a href='#projects' v-smooth-scroll>Projects</a></li>
      <li><a href='#notes'>Notes</a></li>
    </ul></div>
    <div class='linkwrap'><ul>
      <li><a href='https://github.com/pkkid'><i class='mdi mdi-github-box'></i></a></li>
      <li><a href='https://www.linkedin.com/in/shepanski'><i class='mdi mdi-linkedin-box'></i></a></li>
      <li><a href='https://www.facebook.com/mshepanski'><i class='mdi mdi-facebook-box'></i></a></li>
    </ul></div>
  </div>
</template>

<style lang='scss'>
  @import url('https://cdnjs.cloudflare.com/ajax/libs/MaterialDesign-Webfont/3.0.39/css/materialdesignicons.min.css');
  @import '@/assets/css/colors.scss';

  #sidenav {
    background-color: $dark-bg0;
    bottom: 0px;
    color: $light-bgh;
    left: 0px;
    position: fixed;
    top: 0px;
    transition: all .3s ease;
    width: 300px;
    z-index: 100;

    a, a:visited {
      color: $dark-fg0;
      transition: all .3s ease;
      &:hover { color: $dark-orange1; }
    }

    ul {
      margin: 0px;
      padding: 0px;
      list-style-type: none;
      font-family: Montserrat, Arial;
      li {
        margin: 0px;
        text-align: left;
      }
    }

    #logo {
      padding: 50px 20px;
      width: 100%;
      float: left;
      text-align: center;
      text-transform: uppercase;
      font-family: arial;
      font-weight: bold;
      font-size: 15px;
      letter-spacing: 4px;
      margin-bottom: 50px;
      border-bottom: 1px solid $dark-bg1;
      box-sizing: border-box;
      img { width: 130px; margin-bottom: 10px; }
    }

    .menuwrap {
      box-sizing: border-box;
      clear: both;
      float: left;
      height: auto;
      padding: 0px 20px 0px 60px;
      width: 100%;

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
      a:hover:before{ width:35px; }
    }

    .linkwrap {
      bottom: 38px;
      box-sizing: border-box;
      float: left;
      font-size: 22px;
      height: auto;
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
</style>
