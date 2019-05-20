<template>
  <div id='sidenav'>
    <div id='logo'>
      <img class='logo' src='../assets/pk.svg'/><br/>
      PushingKarma
    </div>
    <div class='menuwrap'>
      <ul class='nav'>
        <li><a href='#home'>Home</a></li>
        <li><a href='#about'>About</a></li>
        <li><a href='#services'>Projects</a></li>
        <li><a href='#portfolio'>Notes</a></li>
      </ul>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'SideNav',
    components: {}
  }
</script>

<style lang='scss'>
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
      font-size: 14px;
      letter-spacing: 3px;
      margin-bottom: 50px;
      border-bottom: 1px solid rgba(255,255,255,.1);
      box-sizing: border-box;
      img { width: 130px; margin-bottom: 10px; }
    }
  }
</style>
