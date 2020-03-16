<template>
  <article id='about' class='parallax-static'>
    <h1>About Me <div class='subtext'>My background and motivation</div></h1>
    <div class='photo'><img src='@/assets/img/family.jpg'/></div>
    <div class='aboutme'>
      <h2>I am Michael Shepanski, <span class='accent'>Developer</span></h2>
      <p style='max-width:800px;'>
        I've been developing software in the Boston area for over 14 years,
        using Python since 2004 & Django since early 2009. Web development
        used to be a hobby to me. As web applications started becoming more
        complex and the demand so high, it turned into a full-time job. My
        passion is finding simple and elegant ways to display complex information.
      </p>
    </div>
    <div style='clear:both;'></div>
  </article>
</template>

<style lang='scss'>
  #about {
    .photo {
      float: left;
      border: 10px solid $darkbg-color;
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
    }
  }
</style>
