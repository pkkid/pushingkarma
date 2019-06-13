<template>
  <div id='content' class='parallax-wrapper'>
    <!-- Home -->
    <div id='home' class='parallax-bg'>
      <div class='photo'><img src='../assets/photo.jpg'/></div>
      <div class='name'>Michael <span>Shepanski</span></div>
      <div class='arrow'><i class='mdi mdi-chevron-double-down'></i></div>
    </div>
    <!-- About -->
    <div id='about' class='parallax-static'>
      <h3>About Me <span>My background and motivation</span></h3>
      <div class='photo'><img src='../assets/family.jpg'/></div>
      <div class='aboutme'>
        <h4>I am Michael Shepanski and <span>Developer</span></h4>
        <p>I've been developing software in the Boston area for over 14 years,
          using Python since 2004 & Django since early 2009. Web development
          used to be a hobby to me. As web applications started becoming more
          complex and the demand so high, it turned into a full-time job. My
          passion is finding simple and elegant ways to display complex information.
        </p>
      </div>
      <!-- Projects -->
      <div style='clear:both;'></div>
      <div id='projects' class='parallax-static'>
        <h3>Projects <span>Whats been keeping me busy</span></h3>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'SideNav',
  }
</script>

<style lang='scss'>
  @import '@/assets/css/animate.scss';
  @import '@/assets/css/colors.scss';
  @import '@/assets/css/parallax.scss';

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
    background-color: rgba($dark-bgh, 0.7);
    display: flex;
    flex-direction: column;
    justify-content: center;
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
      span {
        color: $dark-orange1;
      }
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

  #about {
    background-color: #eee;
    color: $dark-bg0;
    padding: 100px 40px;
    text-align: left;
    .photo {
      float: left;
      border: 10px solid $dark-bg0;
      box-sizing: border-box;
      width: 400px;
      height: 300px;
      position: relative;
      top: 20px;
      left: 20px;
      margin-top: 40px;
      img {
        width: 400px;
        position: relative;
        top: -30px;
        left: -30px;
      }
    }
    .aboutme {
      margin-left: 500px;
      margin-right: 50px;
      h4 {
        margin-bottom: 20px;
        font-size: 24px;
        font-weight: 500;
        span {
          color: $light-orange0;
          font-weight: 500;
        }
      }
      p { line-height: 28px; }
    }

    #projects {
      background-color: #eee;
      border-top: 1px solid rgba(0,0,0,0);
      margin-top: 200px;
    }
  }

</style>
