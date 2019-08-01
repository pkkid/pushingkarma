<template>
  <div id='home' class='parallax-wrapper'>
    <div class='header parallax-bg'>
      <div class='photo'><img src='../assets/img/photo.jpg'/></div>
      <div class='name'>Michael <span>Shepanski</span></div>
      <div class='arrow'><a href='#about'><i class='mdi mdi-chevron-double-down'></i></a></div>
    </div>
    <About/>
    <Projects/>
    <Footer/>
  </div>
</template>

<script>
  import About from './HomeAbout.vue'
  import Projects from './HomeProjects.vue'
  import Footer from './Footer.vue'

  export default {
    name: 'Home',
    components: {About, Projects, Footer},
    beforeCreate: function() {
      document.getElementById('navigation').classList.remove('topnav');
    }
  }
</script>

<style lang='scss'>
  @import '@/assets/css/animate.scss';
  @import '@/assets/css/colors.scss';
  @import '@/assets/css/parallax.scss';

  #home {
    margin: 0px;
    padding: 0px;
    color: $light-bgh;
    h3 {
      font-size: 50px;
      margin-top: 0px;
      text-transform: uppercase;
      font-weight: 600;
      border-left: 6px solid $light-orange0;
      padding-left: 25px;
      span {
        font-size: 16px;
        text-transform: none;
        display: block;
        padding-bottom: 3px;
        font-weight: 100;
      }
    }
  }

  #home > .header {
    align-items: center;
    background-color: rgba($dark-bgh, 0.7);
    display: flex;
    flex-direction: column;
    justify-content: center;
    a, a:visited {
      text-decoration: none;
      color: $light-bgh;
    }
    .photo {
      width: 216px;
      height: 216px;
      display: inline-block;
      margin-bottom: 38px;
      img {
        width: 200px;
        border-radius: 100%;
        border: 8px solid rgba($dark-bg3, 0.7);
      }
    }
    .name {
      text-align: center;
      font-family: "Montserrat";
      text-transform: uppercase;
      font-size: 50px;
      font-weight: 300;
      margin-bottom: 100px;
      span { color: $dark-orange1; }
    }
    .arrow {
      animation: bounce 2s infinite;
      font-size: 30px;
      bottom: 5%;
      left: 50%;
      margin-left: -15px;
      position: absolute;
      z-index: 55;
    }
  }
  #home > .header::after {
    background-image: url('../assets/img/sichuan.jpg');
  }
</style>
