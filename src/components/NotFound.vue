<template>
  <div id='notfound'>
    <Navigation :cls="'topnav'" />
    <div class='content'>
      <div class='contentbg'>
        <div class='x404'>404</div>
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
    margin-top: 60px;
    background-color: darken($lightbg-color, 10%);
    

    .contentbg {
      font-size: 30px;
      font-weight: 500;
      height: calc(100vh - 360px);
      min-height: 500px;
      padding: 100px 0px;
      text-align: center;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .x404 {
      font-size: 200px;
      font-weight: bold;
    }
  }
</style>
