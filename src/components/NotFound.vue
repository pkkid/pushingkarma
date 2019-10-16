<template>
  <div id='notfound'>
    <Navigation :cls="'topnav'" />
    <div class='content'>
      <div style='height: calc(100vh - 60px);'>
        <div>404</div>
        Page not found!
      </div>
      <Footer/>
    </div>
  </div>
</template>

<script>
  import Footer from './Footer';
  import Navigation from './Navigation';

  export default {
    name: 'NotFound',
    components: {Footer, Navigation},
  };
</script>

<style lang='scss'>
  #notfound .content {
    box-sizing: border-box;
    color: $lightbg-text;
    // margin-left: 300px;
    margin-top: 60px;
    background-color: darken($lightbg-color, 10%);
    
  }
</style>
