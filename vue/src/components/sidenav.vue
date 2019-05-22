<template>
  <div id='sidenav'>
    <div id='logo'>
      <img class='logo' src='../assets/pk.svg'/><br/>
      PushingKarma
    </div>
    <div class='menuwrap'><ul>
      <li><a href='#home'>Home</a></li>
      <li><a href='#about'>About</a></li>
      <li><a href='#services'>Projects</a></li>
      <li><a href='#portfolio'>Notes</a></li>
    </ul></div>
    <div class='socialwrap'><ul>
      <li><a href='#'><i class='mdi mdi-github-box'>Github</i></a></li>
      <li><a href='#'><i class='mdi mdi-linkedin-box'>LinkedIn</i></a></li>
      <li><a href='#'><i class='mdi mdi-facebook-box'>Facebook</i></a></li>
    </ul></div>
  </div>
</template>

<script>
  export default {
    name: 'SideNav',
  }
</script>

<style lang='scss'>
  @import url('https://cdnjs.cloudflare.com/ajax/libs/MaterialDesign-Webfont/3.0.39/css/materialdesignicons.min.css');
  
  #sidenav {
    background-color: #041230;
    bottom: 0px;
    left: 0px;
    position: fixed;
    top: 0px;
    transition: all .3s ease;
    width: 300px;
    z-index: 100;

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
      border-bottom: 1px solid rgba(255,255,255,.1);
      box-sizing: border-box;
      img { width: 130px; margin-bottom: 10px; }
    }

    .menuwrap {
      width: 100%;
      height: auto;
      clear: both;
      float: left;
      padding: 0px 20px 0px 60px;
      box-sizing: border-box;
      ul {
        margin: 0px;
        padding: 0px;
        list-style-type: none;
        font-family: Montserrat, Arial;
        li {
          margin: 0px;
          text-align: left;
        }
        a {
          text-decoration: none;
          color: #fff;
          font-family: Montserrat, Arial;
          font-size: 16px;
          font-weight: 500;
          text-transform: uppercase;
          position: relative;
          display: inline-block;
          padding-bottom: 19px;
          transition: all .3s ease;
          line-height: 29px;
          font-family: Montserrat, Arial;
        }
        a:before {
          position: absolute;
          content: "";
          height: 2px;
          width: 0px;
          background-color: #E3872D;
          top: 14px;
          transform: translateY(-50%);
          left: 100%;
          margin-left: 10px;
          transition: all .3s ease;
        }
        a:hover { color:#E3872D; }
        a:hover:before{ width:35px; }
      }
    }

  }
</style>
