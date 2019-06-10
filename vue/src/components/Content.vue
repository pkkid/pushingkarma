<template>
  <div id='content' class='parallax-wrapper'>
    <div id='home' class='section parallax-bg bg1'>
      Hi Mom!
    </div>
    <div id='about' class='section parallax-static'>
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
  #content {
    margin: 0px;
    padding: 0px;
  }

  .parallax-wrapper {
    height: 100vh;
    overflow-x: hidden;
    overflow-y: auto;
    perspective: 2px;
  }
  .parallax-bg,
  .parallax-static {
    position: relative;
    height: 100vh;
    /* for text formatting. */
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    text-shadow: 0 0 5px #000;
  }
  .parallax-bg::after {
    content: " ";
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: -3px;
    transform: translateZ(-1px) scale(1.5);
    background-size: cover;
    background-position-x: 50%;
    background-position-y: 50%;
    z-index: -1;
  }
  /* The styling for the static div. */
  .parallax-static {
    background: white;
  }

  #home::after {
    background-image: url('../assets/sichuan.jpg');
  }




  // #home .bgimage {
  //   position: absolute;
  //   width: 100%;
  //   top: 0px;
  //   bottom: 0px;
  //   background-image: url('../assets/sichuan.jpg');
  //   background-size: 100%;
  //   background-position-x: 50%;
  //   background-position-y: 50%;
  //   background-attachment: fixed;
  //   margin-left: 300px;
  //   left:-300px;
  // }
  // #home .overlay {
  //   position: absolute;
  //   width: 100%;
  //   top: 0px;
  //   bottom: 0px;
  //   background-color: rgba(0,0,0,.5);
  // }
  // #home .hero {
  //   height: 100vh;
  // }
  // #about {
  //   height: 400px;
  // }
</style>
