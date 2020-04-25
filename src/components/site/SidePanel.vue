<!--
Side Panel - Panel on the left side of the content area used as a secondary
  submenu or search results.
-->
<template>
  <div id='sidepanelwrap'>
    <div id='sidepanel'><slot name='sidepanel'>slot:sidepanel</slot></div>
    <div id='contentarea'><slot name='contentarea'>slot:contentarea</slot></div>
    <Footer/>
  </div>
</template>

<script>
  import Footer from '@/components/site/Footer';
  export default {
    name: 'SidePanel',
    components: {Footer},
  };
</script>

<style lang='scss'>
  #sidepanel {
    background-color: $darkbg-bg0;
    color: $darkbg-fg0;
    font-size: 1rem;
    height: calc(100vh - 60px);
    overflow-y: hidden;
    margin-top: 0px;
    overflow: hidden;
    position: fixed;
    top: 60px;
    width: 300px;

    a,a:visited {
      color: $darkbg-fg0;
      text-decoration: none;
      transition: color 0.2s ease;
      &:hover { color: $darkbg-orange1; }
    }
  }

  #contentarea {
    background-color: $lightbg-bg3;
    box-sizing: border-box;
    color: $lightbg-text;
    font-weight: 300;
    margin-left: 300px;
    margin-top: 60px;
    min-height: calc(100vh - 60px);
    z-index: 28;
  }

  #sidepanelwrap #footer .footerwrap { 
    margin-left: 300px;
  }
</style>


