<template>
  <div id='home'>
    <Navigation/>
    <div class='homecontent parallax-wrapper'>
      <div id='splash' class='header parallax-bg'>
        <div class='photo'><img src='@/assets/img/photo.jpg'/></div>
        <div class='name'>Michael <span>Shepanski</span></div>
        <div id='bouncyarrow'>
          <a href='#about'><i class='mdi mdi-chevron-double-down'></i></a>
        </div>
      </div>
      <About/>
      <Projects/>
      <Footer/>
    </div>
  </div>
</template>

<script>
  import Footer from '@/components/site/Footer';
  import Navigation from '@/components/site/Navigation';
  import About from './HomeAbout';
  import Projects from './HomeProjects';

  export default {
    name: 'Home',
    components: {About, Projects, Footer, Navigation},
    beforeCreate: function() {
      this.$store.set('global/layout', 'sidenav');
    }
  };
</script>

<style lang='scss'>
  #home .homecontent {
    margin-left: 300px;
    padding: 0px;
    font-size: 1rem;
    p { font-size: 1.1rem };
    h1 .subtext { font-size: 1rem; }
  }
  #home .homecontent > .header {
    align-items: center;
    background-color: rgba(#1d2021, 0.5);
    display: flex;
    flex-direction: column;
    justify-content: center;
    &::after { background-image: url('../../assets/img/sichuan.jpg'); }

    a, a:visited {
      text-decoration: none;
      color: #f9f5d7;
    }
    .photo {
      width: 216px;
      height: 216px;
      display: inline-block;
      margin-bottom: 38px;
      img {
        width: 200px;
        border-radius: 100%;
        border: 8px solid rgba(#665c54, 0.7);
      }
    }
    .name {
      text-align: center;
      text-transform: uppercase;
      font-size: 3rem;
      font-weight: 300;
      margin-bottom: 100px;
      color: #f9f5d7;
      span { color: #fe8019; }
    }
  }

  #bouncyarrow {
    animation: bounce 2s infinite;
    font-size: 1.6rem;
    bottom: 5%;
    left: 50%;
    margin-left: -15px;
    position: absolute;
    z-index: 55;
  }
  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }	
    40% { transform: translateY(-15px); }	
    60% { transform: translateY(-8px); }
  }
</style>
