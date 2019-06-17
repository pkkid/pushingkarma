<template>
  <div id='about' class='parallax-static'>
    <h3>About Me <span>My background and motivation</span></h3>
    <div class='photo'><img src='../assets/img/family.jpg'/></div>
    <div class='aboutme'>
      <h4>I am Michael Shepanski and <span>Developer</span></h4>
      <p>I've been developing software in the Boston area for over 14 years,
        using Python since 2004 & Django since early 2009. Web development
        used to be a hobby to me. As web applications started becoming more
        complex and the demand so high, it turned into a full-time job. My
        passion is finding simple and elegant ways to display complex information.
      </p>
    </div>
    <div style='clear:both;'></div>
  </div>
</template>

<style lang='scss'>
  @import '@/assets/css/colors.scss';

  #about {
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
  }
</style>
