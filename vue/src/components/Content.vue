<template>
  <div id='content' class='parallax-wrapper'>
    <div id='home' class='parallax-bg'>
      <div class='photowrap'><img src='../assets/photo.jpg'/></div>
      <div class='name'>Michael <span>Shepanski</span></div>
    </div>
    <div id='about' class='parallax-static'>
      Hi Dad!
    </div>
  </div>
</template>

<script>
  export default {
    name: 'SideNav',
  }
</script>

<style lang='scss'>
  @import '@/assets/css/colors.scss';
  @import '@/assets/css/parallax.scss';

  #content {
    margin: 0px;
    padding: 0px;
    color: $light-bgh;
  }

  #home::after {
    background-image: url('../assets/sichuan.jpg');
  }
  #home {
    align-items: center;
    background-color: rgba(21,21,21,0.7);
    display: flex;
    flex-direction: column;
    justify-content: center;
    .photowrap {
      width: 216px;
      height: 216px;
      display: inline-block;
      margin-bottom: 38px;
      img {
        width: 200px;
        border-radius: 100%;
        border: 8px solid rgba(101,92,85,.7);
      }
    }
    .name {
      text-align: center;
      font-family: "Montserrat";
      text-transform: uppercase;
      font-size: 50px;
      font-weight: 300;
      span {
        color: $dark-orange1;
      }
    }
  }

  #about {
    background-color: #eee;
  }

</style>
