<template>
  <div id='home'>
    <Navigation/>
    <Parallax>
      <div id='splash' class='parallax-bg'>
        <div class='photo'><img src='@/assets/img/photo.jpg'/></div>
        <div class='name'>Michael <span>Shepanski</span></div>
        <div class='arrow'><a href='#about'><i class='mdi mdi-chevron-double-down'/></a></div>
      </div>
      <div class='parallax-static homecontent'>
        <About/>
        <Projects/>
      </div>
      <Footer/>
    </Parallax>
  </div>
</template>

<script>
  import Footer from '@/components/site/Footer';
  import Navigation from '@/components/site/Navigation';
  import About from './HomeAbout';
  import Parallax from '@/components/Parallax';
  import Projects from './HomeProjects';

  export default {
    name: 'Home',
    components: {Parallax, About, Projects, Footer, Navigation},
    beforeCreate: function() {
      this.$store.set('global/layout', 'sidenav');
      document.title = `PushingKarma`;
    }
  };
</script>

<style lang='scss'>
  #splash {
    background-color: rgba($darkbg-bg0, 0.5);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    & > div { margin-left: 300px; }
    .photo {
      width: 216px;
      height: 216px;
      display: inline-block;
      margin-bottom: 38px;
      img {
        border-radius: 100%;
        border: 8px solid rgba(#665c54, 0.7);
        width: 200px;
      }
    }
    .name {
      text-align: center;
      text-transform: uppercase;
      font-size: 3rem;
      font-weight: 300;
      margin-bottom: 100px;
      color: $darkbg-fg1;
      span { color: $darkbg-orange1; }
    }
    .arrow {
      animation: bounce 2s infinite;
      bottom: 5%;
      font-size: 1.6rem;
      margin-left: 150px;
      position: absolute;
      z-index: 55;
    }
    a,a:visited { text-decoration:none; color:$darkbg-fg0; }
    &::after { background-image: url('../../assets/img/sichuan.jpg'); }
  }

  #home .homecontent {
    h1 { font-size: 3rem; }
    p { font-size: 1.1rem; }
    margin-left: 300px;
  }
  #home #footer .footerwrap {
    margin-left: 300px;
  }
  
  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }	
    40% { transform: translateY(-15px); }	
    60% { transform: translateY(-8px); }
  }
</style>
